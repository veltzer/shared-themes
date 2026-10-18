#!/usr/bin/env python
"""Generate docx/<theme>.docx, one Word reference document per light palette, from themes.yaml.

Each file is a reference document for pandoc (`--reference-doc`): an empty
document whose styles.xml defines every style pandoc's docx writer uses,
recolored with the shared tokens and set in the token fonts. The styles
follow the layout of pandoc's own default reference document; only colors,
fonts, the heading rule, the quote bar and the code and table shading are
ours. Pandoc adds the syntax-highlighting styles itself.

Only light palettes get one. Pandoc keeps a reference document's styles but
not its page background, so a dark palette would put its light text on
Word's white page.

Word has no alpha channel, so translucent tokens are composited over the
theme's `bg` (themes_common.opaque_colors). A .docx does not embed the
fonts: the styles name the token families, and fontTable.xml describes
them so a reader without them gets a matching sans and monospace.

The zip is written stored (uncompressed) with fixed timestamps, so the same
themes.yaml always produces the same bytes and the committed copy can be
checked for drift.
"""

from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import quoteattr

from themes_common import (
    ROOT,
    check_declared_outputs,
    font_family,
    is_light,
    load_themes,
    opaque_colors,
)

DOCX_DIR = ROOT / "docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

CONTENT_TYPES = XML_DECL + (
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    '<Override PartName="/word/fontTable.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>'
    "</Types>"
)

PACKAGE_RELS = XML_DECL + (
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
    'Target="word/document.xml"/>'
    "</Relationships>"
)

DOCUMENT_RELS = XML_DECL + (
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
    'Target="styles.xml"/>'
    '<Relationship Id="rId2" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" '
    'Target="fontTable.xml"/>'
    "</Relationships>"
)

DOCUMENT = XML_DECL + f'<w:document xmlns:w="{W_NS}"><w:body><w:p/></w:body></w:document>'


def fonts_xml(family: str) -> str:
    return f'<w:rFonts w:ascii={quoteattr(family)} w:hAnsi={quoteattr(family)} w:eastAsia={quoteattr(family)} w:cs={quoteattr(family)}/>'


def style(
    kind: str,
    style_id: str,
    name: str,
    *,
    based_on: str | None = None,
    next_: str | None = None,
    link: str | None = None,
    default: bool = False,
    custom: bool = False,
    ppr: str = "",
    rpr: str = "",
    extra: str = "",
) -> str:
    attrs = f'w:type="{kind}"'
    if default:
        attrs += ' w:default="1"'
    if custom:
        attrs += ' w:customStyle="1"'
    attrs += f' w:styleId="{style_id}"'
    parts = [f"<w:style {attrs}>", f"<w:name w:val={quoteattr(name)}/>"]
    if based_on:
        parts.append(f'<w:basedOn w:val="{based_on}"/>')
    if next_:
        parts.append(f'<w:next w:val="{next_}"/>')
    if link:
        parts.append(f'<w:link w:val="{link}"/>')
    parts.append("<w:qFormat/>")
    if ppr:
        parts.append(f"<w:pPr>{ppr}</w:pPr>")
    if rpr:
        parts.append(f"<w:rPr>{rpr}</w:rPr>")
    parts.append(extra)
    parts.append("</w:style>")
    return "".join(parts)


def color(rgb: str) -> str:
    return f'<w:color w:val="{rgb}"/>'


def size(half_points: int) -> str:
    return f'<w:sz w:val="{half_points}"/><w:szCs w:val="{half_points}"/>'


# Heading sizes (half-points), spacing (twips) and italics, as in pandoc's
# default reference document.
HEADINGS: list[tuple[int, int | None, int, int, bool]] = [
    # level, size, space before, space after, italic
    (1, 40, 360, 80, False),
    (2, 32, 160, 80, False),
    (3, 28, 160, 80, False),
    (4, None, 80, 40, True),
    (5, None, 80, 40, False),
    (6, None, 40, 0, True),
    (7, None, 40, 0, False),
    (8, None, 0, 0, True),
    (9, None, 0, 0, False),
]


def styles_xml(c: dict[str, str], sans: str, mono: str) -> str:
    out: list[str] = [
        XML_DECL,
        f'<w:styles xmlns:w="{W_NS}">',
        "<w:docDefaults><w:rPrDefault><w:rPr>",
        fonts_xml(sans),
        color(c["text-primary"]),
        size(24),
        '<w:lang w:val="en-US" w:eastAsia="en-US" w:bidi="ar-SA"/>',
        "</w:rPr></w:rPrDefault>",
        '<w:pPrDefault><w:pPr><w:spacing w:after="200"/></w:pPr></w:pPrDefault>',
        "</w:docDefaults>",
        style("paragraph", "Normal", "Normal", default=True),
        style("character", "DefaultParagraphFont", "Default Paragraph Font", default=True),
        style(
            "paragraph", "BodyText", "Body Text", based_on="Normal", link="BodyTextChar",
            ppr='<w:spacing w:before="180" w:after="180"/>',
        ),
        style("character", "BodyTextChar", "Body Text Char", based_on="DefaultParagraphFont", link="BodyText", custom=True),
        style("paragraph", "FirstParagraph", "First Paragraph", based_on="BodyText", next_="BodyText", custom=True),
        style(
            "paragraph", "Compact", "Compact", based_on="BodyText", custom=True,
            ppr='<w:spacing w:before="36" w:after="36"/>',
        ),
        style(
            "paragraph", "Title", "Title", based_on="Normal", next_="BodyText",
            ppr='<w:spacing w:after="80" w:line="240" w:lineRule="auto"/><w:contextualSpacing/><w:jc w:val="center"/>',
            rpr=color(c["text-primary"]) + size(56),
        ),
        style(
            "paragraph", "Subtitle", "Subtitle", based_on="Title", next_="BodyText",
            rpr=color(c["text-secondary"]) + '<w:spacing w:val="15"/>' + size(28),
        ),
        style(
            "paragraph", "Author", "Author", based_on="Title", next_="BodyText", custom=True,
            ppr="<w:keepNext/><w:keepLines/>", rpr=color(c["text-secondary"]) + size(24),
        ),
        style(
            "paragraph", "Date", "Date", based_on="Title", next_="BodyText",
            ppr="<w:keepNext/><w:keepLines/>", rpr=color(c["text-secondary"]) + size(24),
        ),
        style(
            "paragraph", "AbstractTitle", "Abstract Title", based_on="Normal", next_="Abstract", custom=True,
            ppr='<w:keepNext/><w:keepLines/><w:spacing w:before="300" w:after="0"/><w:jc w:val="center"/>',
            rpr="<w:b/>" + size(20),
        ),
        style(
            "paragraph", "Abstract", "Abstract", based_on="Normal", next_="BodyText", custom=True,
            ppr='<w:keepNext/><w:keepLines/><w:spacing w:before="100" w:after="300"/>',
            rpr=size(20),
        ),
        style("paragraph", "Bibliography", "Bibliography", based_on="Normal", next_="Bibliography"),
    ]
    for level, half_points, before, after, italic in HEADINGS:
        # Headings in the accent, as on the sites; levels 6-9 recede.
        rpr = color(c["accent"] if level <= 5 else c["text-secondary"])
        if level <= 3:
            # Bold, as on the sites and in the LaTeX theme.
            rpr += "<w:b/><w:bCs/>"
        if italic:
            rpr += "<w:i/><w:iCs/>"
        if half_points is not None:
            rpr += size(half_points)
        ppr = f'<w:keepNext/><w:keepLines/><w:spacing w:before="{before}" w:after="{after}"/>'
        if level == 2:
            # The rule under the section headings, as on the sites.
            ppr += f'<w:pBdr><w:bottom w:val="single" w:sz="4" w:space="1" w:color="{c["border-subtle"]}"/></w:pBdr>'
        ppr += f'<w:outlineLvl w:val="{level - 1}"/>'
        out.append(style(
            "paragraph", f"Heading{level}", f"heading {level}", based_on="Normal", next_="BodyText",
            link=f"Heading{level}Char", ppr=ppr, rpr=rpr,
        ))
        out.append(style(
            "character", f"Heading{level}Char", f"Heading {level} Char", based_on="DefaultParagraphFont",
            link=f"Heading{level}", custom=True, rpr=rpr,
        ))
    quote_ppr = (
        '<w:pBdr><w:left w:val="single" w:sz="18" w:space="8" w:color="{accent}"/></w:pBdr>'
        '<w:shd w:val="clear" w:color="auto" w:fill="{surface}"/>'
        '<w:spacing w:before="100" w:after="100"/><w:ind w:firstLine="0" w:left="480" w:right="480"/>'
    ).format(accent=c["accent"], surface=c["bg-surface"])
    out += [
        style(
            "paragraph", "BlockText", "Block Text", based_on="BodyText", next_="BodyText",
            ppr=quote_ppr, rpr=color(c["text-secondary"]),
        ),
        style("paragraph", "FootnoteText", "Footnote Text", based_on="Normal", next_="FootnoteText"),
        style(
            "paragraph", "FootnoteBlockText", "Footnote Block Text", based_on="FootnoteText", next_="FootnoteText",
            ppr='<w:spacing w:before="100" w:after="100"/><w:ind w:firstLine="0" w:left="480" w:right="480"/>',
        ),
        style(
            "table", "Table", "Table", default=True,
            extra=(
                "<w:tblPr>"
                '<w:tblInd w:w="0" w:type="dxa"/>'
                "<w:tblBorders>"
                + "".join(
                    f'<w:{side} w:val="single" w:sz="4" w:space="0" w:color="{c["border"]}"/>'
                    for side in ("top", "left", "bottom", "right", "insideH", "insideV")
                )
                + "</w:tblBorders>"
                '<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="108" w:type="dxa"/>'
                '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/></w:tblCellMar>'
                "</w:tblPr>"
                '<w:tblStylePr w:type="firstRow">'
                '<w:tblPr><w:jc w:val="left"/><w:tblInd w:w="0" w:type="dxa"/></w:tblPr>'
                '<w:trPr><w:jc w:val="left"/></w:trPr>'
                f'<w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="{c["bg-surface"]}"/><w:vAlign w:val="bottom"/></w:tcPr>'
                "</w:tblStylePr>"
            ),
        ),
        style(
            "paragraph", "DefinitionTerm", "Definition Term", based_on="Normal", next_="Definition", custom=True,
            ppr='<w:keepNext/><w:keepLines/><w:spacing w:after="0"/>', rpr="<w:b/>",
        ),
        style("paragraph", "Definition", "Definition", based_on="Normal", custom=True),
        style(
            "paragraph", "Caption", "Caption", based_on="Normal",
            ppr='<w:spacing w:before="0" w:after="120"/>', rpr="<w:i/>" + color(c["text-secondary"]),
        ),
        style("paragraph", "TableCaption", "Table Caption", based_on="Caption", custom=True, ppr="<w:keepNext/>"),
        style("paragraph", "ImageCaption", "Image Caption", based_on="Caption", custom=True),
        style("paragraph", "Figure", "Figure", based_on="Normal", custom=True),
        style("paragraph", "CaptionedFigure", "Captioned Figure", based_on="Figure", custom=True, ppr="<w:keepNext/>"),
        style(
            "character", "VerbatimChar", "Verbatim Char", based_on="BodyTextChar", custom=True,
            rpr=fonts_xml(mono) + size(22) + f'<w:shd w:val="clear" w:color="auto" w:fill="{c["bg-surface"]}"/>',
        ),
        style("character", "SectionNumber", "Section Number", based_on="BodyTextChar", custom=True),
        style(
            "character", "FootnoteReference", "Footnote Reference", based_on="BodyTextChar",
            rpr='<w:vertAlign w:val="superscript"/>',
        ),
        style("character", "Hyperlink", "Hyperlink", based_on="BodyTextChar", rpr=color(c["accent"])),
        style(
            "paragraph", "TOCHeading", "TOC Heading", based_on="Heading1", next_="BodyText",
            ppr='<w:spacing w:before="240" w:line="259" w:lineRule="auto"/><w:outlineLvl w:val="9"/>',
            rpr='<w:b w:val="0"/><w:bCs w:val="0"/>' + color(c["accent"]),
        ),
        "</w:styles>",
    ]
    return "".join(out)


def font_table_xml(sans: str, mono: str) -> str:
    return XML_DECL + (
        f'<w:fonts xmlns:w="{W_NS}">'
        f'<w:font w:name={quoteattr(sans)}><w:family w:val="swiss"/><w:pitch w:val="variable"/></w:font>'
        f'<w:font w:name={quoteattr(mono)}><w:family w:val="modern"/><w:pitch w:val="fixed"/></w:font>'
        "</w:fonts>"
    )


def write_docx(path: Path, parts: list[tuple[str, str]]) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as zf:
        for name, text in parts:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o644 << 16
            zf.writestr(info, text.encode("utf-8"))


def main() -> int:
    data = load_themes()
    sans = font_family(data.base["font-sans"])
    mono = font_family(data.base["font-mono"])
    if DOCX_DIR.exists():
        shutil.rmtree(DOCX_DIR)
    DOCX_DIR.mkdir()
    written = []
    for code, tokens in data.themes.items():
        if not is_light(tokens):
            continue
        path = DOCX_DIR / f"{code}.docx"
        write_docx(path, [
            ("[Content_Types].xml", CONTENT_TYPES),
            ("_rels/.rels", PACKAGE_RELS),
            ("word/document.xml", DOCUMENT),
            ("word/_rels/document.xml.rels", DOCUMENT_RELS),
            ("word/styles.xml", styles_xml(opaque_colors(tokens), sans, mono)),
            ("word/fontTable.xml", font_table_xml(sans, mono)),
        ])
        written.append(path)
    if data.default not in {path.stem for path in written}:
        sys.exit(f"the default theme {data.default!r} is not light, so it has no reference document")
    check_declared_outputs(written)
    print(f"wrote {DOCX_DIR.relative_to(ROOT)}/ ({len(written)} Word reference documents)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
