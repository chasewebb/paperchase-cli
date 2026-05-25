---
name: docx
description: Use when reading, writing, or manipulating Word (.docx) files — including report generation, mail merge, template-driven documents, table insertion, styled output, header/footer manipulation, or batch document production. Triggers on "Word document", ".docx", "mail merge", "python-docx", "docxtpl", "generate report", "MS Word", "DOCX template".
---

# Word/.docx document specialist

You are operating as a document engineer. Default to **python-docx** for cell-level construction and **docxtpl** for templated/mail-merge workflows.

## Decision: which library

| Task | Library | Why |
|------|---------|-----|
| Build doc from scratch | `python-docx` | Direct API over the Office Open XML |
| Fill a designer-built `.docx` template with data | `docxtpl` (uses Jinja2 syntax in the doc) | Designers can edit the .docx; you fill variables |
| Convert from Markdown | `pandoc` CLI | Best fidelity for headings/lists/code |
| PDF output | `docx2pdf` (uses Word/LibreOffice) OR pandoc → wkhtmltopdf | Pure-Python PDF from docx doesn't exist with high fidelity |
| Extract text only (search/indexing) | `python-docx` paragraphs OR `docx2txt` | docx2txt is one-shot, no formatting |

Install: `pip install python-docx docxtpl`.

## Canonical patterns

### Build a doc with styled headings, paragraphs, tables
```python
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

d = Document()

# Title
t = d.add_heading("Q4 2026 Performance Review", level=0)
t.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Paragraph with mixed formatting
p = d.add_paragraph()
p.add_run("Revenue grew ").bold = False
run = p.add_run("42%")
run.bold = True
run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)
p.add_run(" year-over-year.")

# Table
tbl = d.add_table(rows=1, cols=3)
tbl.style = "Light Grid Accent 1"
hdr = tbl.rows[0].cells
hdr[0].text, hdr[1].text, hdr[2].text = "Region", "Q4", "YoY %"
for region, q4, yoy in [("NA", "$1.2M", "+22%"), ("EMEA", "$890K", "+38%")]:
    row = tbl.add_row().cells
    row[0].text, row[1].text, row[2].text = region, q4, yoy

d.save("report.docx")
```

### Template-driven (docxtpl) — designer builds the .docx, you fill it
The designer puts Jinja syntax inside the document text:
```
Dear {{ client_name }},

Your invoice total is {{ amount }}.

{% for item in line_items %}
- {{ item.description }}: {{ item.cost }}
{% endfor %}
```

Then in code:
```python
from docxtpl import DocxTemplate
doc = DocxTemplate("invoice-template.docx")
doc.render({
    "client_name": "Acme Corp",
    "amount": "$4,200",
    "line_items": [
        {"description": "AI agency retainer (Dec)", "cost": "$3,500"},
        {"description": "Skill library setup",       "cost": "$700"},
    ],
})
doc.save("invoice-acme-2026-12.docx")
```

This is the **mail merge pattern** — one template, N output files.

### Headers, footers, page numbers
```python
section = d.sections[0]
header = section.header
hp = header.paragraphs[0]
hp.text = "Confidential — Q4 2026 Review"
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT

# Page number in footer (raw XML — python-docx has no built-in helper)
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
fp = section.footer.paragraphs[0]
run = fp.add_run()
fld = OxmlElement("w:fldSimple")
fld.set(qn("w:instr"), "PAGE")
run._r.append(fld)
```

### Insert an image with caption
```python
d.add_picture("chart.png", width=Inches(5.5))
cap = d.add_paragraph()
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = cap.add_run("Figure 1. Q4 revenue by region")
run.italic = True
run.font.size = Pt(9)
```

### Read existing document
```python
d = Document("contract.docx")
for p in d.paragraphs:
    if "TERMINATION" in p.text:
        print(p.text)
for tbl in d.tables:
    for row in tbl.rows:
        print([c.text for c in row.cells])
```

## Gotchas

- **Styles must already exist in the document** before applying. If you use `paragraph.style = "Custom Heading"` and that style isn't defined in the doc, python-docx silently falls back. Start from a template that has your styles defined.
- **Tracked changes** don't survive python-docx — it strips revisions on save. Use `lxml` direct XML manipulation if you need to preserve them.
- **Tables and paragraphs interleave** in the body but `d.paragraphs` and `d.tables` are SEPARATE iterables in document order — to walk the body in true order, iterate `d.element.body.iter()` and check tag names.
- **Bullet/numbered lists** require the "List Bullet" / "List Number" styles — `d.add_paragraph("foo", style="List Bullet")`. The style must exist (always does in default Word, may not in stripped templates).
- **Page breaks** vs **section breaks**: `run.add_break(WD_BREAK.PAGE)` for page; sections need raw XML.
- **Font size unit is Pt(n)**, not int. Same for `Inches`, `Cm`, `Mm`, `Emu`. Don't pass raw ints to size/width.
- **docxtpl renders before save** — calling `doc.render(ctx)` mutates the template object. To render multiple times, re-instantiate `DocxTemplate(path)` each iteration.
- **Macro-enabled docs (.docm)**: python-docx can open them but writing as `.docm` requires `keep_vba` flag and won't generate new macros.

## Conversion

```bash
# Markdown → docx (best fidelity)
pandoc README.md -o readme.docx --reference-doc=template.docx

# docx → PDF (needs Word or LibreOffice)
soffice --headless --convert-to pdf report.docx

# docx → plain text
python -c "import docx2txt; print(docx2txt.process('contract.docx'))" > contract.txt
```

## When the task is "generate N personalized documents"

Default mail-merge skeleton:

```python
from docxtpl import DocxTemplate
import csv, pathlib

template = DocxTemplate("template.docx")
out_dir = pathlib.Path("out"); out_dir.mkdir(exist_ok=True)

with open("recipients.csv") as f:
    for row in csv.DictReader(f):
        doc = DocxTemplate("template.docx")   # re-instantiate per row
        doc.render(row)
        doc.save(out_dir / f"{row['client_id']}.docx")
```

## Anti-patterns

- ❌ Concatenating raw `<w:p>` XML strings → use python-docx API; manual XML is brittle and breaks Word.
- ❌ Setting `run.bold = False` and expecting it to override inherited style — it sets the run's bold to "explicitly false", which is correct, but won't override paragraph-level styles that themselves cascade.
- ❌ Calling `doc.save()` on docxtpl template before `doc.render()` → saves an empty/unrendered file.
- ❌ Generating PDFs in CI via `docx2pdf` on Linux without LibreOffice → silently fails. Use `soffice` directly.
