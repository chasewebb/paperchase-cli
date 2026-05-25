---
name: xlsx
description: Use when reading, writing, or manipulating Excel (.xlsx, .xls) files — including data extraction, report generation, formula injection, formatting, pivots, charts, or batch transformations across many sheets. Triggers on "Excel", "spreadsheet", ".xlsx", "xls", "Google Sheets export", "pivot table", "VLOOKUP", "openpyxl", "pandas to Excel".
---

# Excel/Spreadsheet specialist

You are operating as a spreadsheet engineer. Default to **openpyxl** for cell-level control, **pandas** for tabular data, and **xlsxwriter** for write-only files with heavy formatting.

## Decision: which library

| Task | Library | Why |
|------|---------|-----|
| Tabular read → analyze → write | `pandas` (uses openpyxl under the hood) | Fastest for dataframes |
| Cell-level formatting, styles, formulas | `openpyxl` | Read AND write, preserves existing file |
| New file with charts + conditional formatting | `xlsxwriter` | Best formatting API; write-only |
| Read `.xls` (old format) | `xlrd==1.2.0` or convert via LibreOffice CLI | Modern xlrd dropped xlsx support |
| 100k+ rows, streaming | `openpyxl` read-only mode + `write_only=True` | Avoids loading whole workbook in memory |

Install once: `pip install openpyxl pandas xlsxwriter`.

## Canonical patterns

### Read with pandas (preserves dtypes)
```python
import pandas as pd
df = pd.read_excel("file.xlsx", sheet_name="Q4 2026", dtype={"order_id": str})
# all sheets at once:
all_sheets = pd.read_excel("file.xlsx", sheet_name=None)  # dict {sheet_name: df}
```

### Write with formatting (xlsxwriter)
```python
with pd.ExcelWriter("report.xlsx", engine="xlsxwriter") as w:
    df.to_excel(w, sheet_name="Sales", index=False)
    wb, ws = w.book, w.sheets["Sales"]
    money = wb.add_format({"num_format": "$#,##0.00"})
    ws.set_column("C:C", 14, money)
    ws.freeze_panes(1, 0)
    ws.autofilter(0, 0, len(df), len(df.columns) - 1)
```

### Modify existing file without losing formulas (openpyxl)
```python
from openpyxl import load_workbook
wb = load_workbook("existing.xlsx")  # keep_vba=True to preserve macros
ws = wb["Summary"]
ws["B2"] = "=SUM(B3:B100)"           # write formula as string
ws["B2"].number_format = "$#,##0.00"
wb.save("existing.xlsx")
```

### Pivot tables — generate values directly
openpyxl can't create native pivots reliably. Two options:
1. **Compute pivot in pandas, write as a static table**: `df.pivot_table(index='region', columns='quarter', values='revenue', aggfunc='sum').to_excel(...)` — simple and reliable.
2. **Use xlwings** if a live pivot is required (requires Excel installed).

### Charts
```python
# xlsxwriter
chart = wb.add_chart({"type": "column"})
chart.add_series({
    "name":       "='Sales'!$B$1",
    "categories": "='Sales'!$A$2:$A$13",
    "values":     "='Sales'!$B$2:$B$13",
})
ws.insert_chart("D2", chart)
```

## Gotchas

- **Dates are serial numbers** in Excel. `pd.read_excel` auto-converts; raw openpyxl returns `datetime` objects only if the cell `number_format` declares a date.
- **Merged cells** when reading: openpyxl reads the value from the top-left cell only; the rest return `None`. Use `ws.unmerge_cells()` first if you need rectangular data.
- **Formula cells** read as the formula string by default. Use `load_workbook(data_only=True)` to get the last-cached calculated value — but ONLY if Excel saved the file (Python won't compute formulas).
- **Large files** (>50MB): always use `read_only=True` (openpyxl) or `write_only=True` (xlsxwriter); regular mode loads everything into RAM.
- **Column letters vs indices**: openpyxl uses 1-indexed numbers AND letters (`ws.cell(row=1, column=1)` == `ws["A1"]`). Convert via `openpyxl.utils.get_column_letter(n)`.
- **Sheet protection**: `ws.protection.sheet = True` blocks edits but doesn't encrypt — use `msoffcrypto-tool` for actual password protection.
- **Number precision**: Excel uses IEEE 754 doubles → max safe integer is 2^53. Store big IDs as strings (`dtype={"id": str}`).
- **Default font and column width** in `xlsxwriter` are tiny — set defaults: `wb.formats[0].set_font_size(11); ws.set_default_row(20)`.

## Conversion shortcuts

```bash
# xlsx → csv  (no Python needed, uses LibreOffice headless)
soffice --headless --convert-to csv file.xlsx --outdir ./out

# csv → xlsx with sane formatting
python -c "import pandas as pd; pd.read_csv('in.csv').to_excel('out.xlsx', index=False)"

# Quick sheet listing
python -c "import openpyxl; print(openpyxl.load_workbook('file.xlsx', read_only=True).sheetnames)"
```

## When the task is "generate a report"

Default report skeleton — copy and modify:

```python
import pandas as pd
from datetime import date

df = pd.read_excel("source.xlsx", sheet_name="data")
summary = df.groupby("category")["revenue"].agg(["sum", "mean", "count"]).reset_index()

with pd.ExcelWriter(f"report-{date.today()}.xlsx", engine="xlsxwriter") as w:
    df.to_excel(w, sheet_name="Raw", index=False)
    summary.to_excel(w, sheet_name="Summary", index=False)
    wb = w.book
    title = wb.add_format({"bold": True, "font_size": 14, "bg_color": "#1F4E78", "font_color": "white"})
    money = wb.add_format({"num_format": "$#,##0.00"})
    for sheet in ("Raw", "Summary"):
        ws = w.sheets[sheet]
        ws.set_row(0, 22, title)
        ws.freeze_panes(1, 0)
```

## Anti-patterns

- ❌ Loading a 200MB workbook with default openpyxl mode just to read one column → use `read_only=True` or convert to CSV first.
- ❌ Writing formulas as Python strings without `=` prefix → they store as text, won't compute.
- ❌ Trusting `df.to_excel(...)` to give nice formatting → it doesn't; always pair with xlsxwriter.
- ❌ Iterating with `for cell in ws.iter_rows()` and modifying — openpyxl can't always handle in-flight edits; collect changes, then apply.
