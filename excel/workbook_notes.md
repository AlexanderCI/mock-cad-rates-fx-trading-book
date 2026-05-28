# Excel workbook notes

I did not include a heavy Excel workbook because GitHub handles code and CSVs better.

The idea is simple:

1. Run `python src/main.py`
2. Open Excel
3. Create a workbook in the repo folder
4. Import `excel/vba_refresh_report.bas`
5. Run `RefreshMockDeskReports`

The macro pulls the output CSVs into separate sheets.

For a real version I would probably add:

- a front tab with the valuation date
- a small PnL bridge
- conditional formatting on limit breaches
- a dealer quote table
- a button to refresh the CSVs

I kept the workbook side light because the Python code is the real project here.
