Attribute VB_Name = "RefreshMockDeskReports"

Sub RefreshMockDeskReports()
    ' rough helper macro for the Excel side of the project
    ' put this in a workbook if you want to refresh the output CSVs quickly

    Dim folderPath As String
    folderPath = ThisWorkbook.Path & "\outputs\"

    Application.ScreenUpdating = False

    Call ImportCsvToSheet(folderPath & "position_report.csv", "Position Report")
    Call ImportCsvToSheet(folderPath & "pnl_report.csv", "PnL Report")
    Call ImportCsvToSheet(folderPath & "risk_summary.csv", "Risk Summary")
    Call ImportCsvToSheet(folderPath & "dealer_quote_comparison.csv", "Dealer Quotes")
    Call ImportCsvToSheet(folderPath & "limit_breaches.csv", "Limit Breaches")

    Application.ScreenUpdating = True

    MsgBox "reports refreshed - check the tabs"
End Sub

Sub ImportCsvToSheet(csvPath As String, sheetName As String)
    Dim ws As Worksheet
    Dim qt As QueryTable

    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets(sheetName)
    On Error GoTo 0

    If ws Is Nothing Then
        Set ws = ThisWorkbook.Worksheets.Add
        ws.Name = sheetName
    End If

    ws.Cells.Clear

    If Dir(csvPath) = "" Then
        ws.Range("A1").Value = "missing file: " & csvPath
        Exit Sub
    End If

    Set qt = ws.QueryTables.Add(Connection:="TEXT;" & csvPath, Destination:=ws.Range("A1"))
    With qt
        .TextFileParseType = xlDelimited
        .TextFileCommaDelimiter = True
        .Refresh BackgroundQuery:=False
        .Delete
    End With

    ws.Rows(1).Font.Bold = True
    ws.Columns.AutoFit
End Sub
