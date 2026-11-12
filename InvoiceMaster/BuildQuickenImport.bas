Attribute VB_Name = "BuildQuickenImport"
Option Explicit

Public Sub BuildQuickenImport()

    Dim wsSrc As Worksheet
    Dim wsOut As Worksheet

    Dim headerRow As Long
    Dim firstDataRow As Long
    Dim lastDataRow As Long
    Dim outRow As Long
    Dim r As Long

    Dim currentInvoice As String
    Dim invoiceNumber As String
    Dim nextInvoice As String
    Dim isLastInvoiceRow As Boolean
    Dim invoiceCount As Long

    Dim invoiceTotal As Currency

    ' Invoice-level adjustment totals
    Dim shippingTotal As Currency
    Dim discountTotal As Currency
    Dim otherFeeTotal As Currency
    Dim taxTotal As Currency
    Dim importFeeTotal As Currency
    Dim pointsTotal As Currency
    Dim giftCardTotal As Currency

    ' Amount already emitted for each adjustment
    Dim shippingAllocated As Currency
    Dim discountAllocated As Currency
    Dim otherFeeAllocated As Currency
    Dim taxAllocated As Currency
    Dim importFeeAllocated As Currency
    Dim pointsAllocated As Currency
    Dim giftCardAllocated As Currency

    ' Resolve columns by heading
    Dim colInvoice As Long
    Dim colInvoiceDate As Long
    Dim colCategory As Long
    Dim colCategoryTotal As Long
    Dim colMemo As Long
    Dim colInvoiceTotal As Long

    Dim colShipping As Long
    Dim colShippingFlag As Long
    Dim colProratedShipping As Long

    Dim colDiscount As Long
    Dim colDiscountFlag As Long
    Dim colProratedDiscount As Long

    Dim colOtherFee As Long
    Dim colOtherFeeFlag As Long
    Dim colProratedOther As Long

    Dim colTax As Long
    Dim colTaxFlag As Long
    Dim colProratedTax As Long

    Dim colImportFee As Long
    Dim colImportFlag As Long
    Dim colProratedImport As Long

    Dim colPoints As Long
    Dim colPointsFlag As Long
    Dim colProratedPoints As Long

    Dim colGiftCard As Long
    Dim colGiftCardFlag As Long
    Dim colProratedGiftCard As Long

    Set wsSrc = ThisWorkbook.Worksheets("Invoice Summary")
    Set wsOut = ThisWorkbook.Worksheets("Quicken Export")

    headerRow = 1
    firstDataRow = headerRow + 1

    colInvoice = FindHeaderColumn(wsSrc, headerRow, "Invoice #")
    colInvoiceDate = FindHeaderColumn(wsSrc, headerRow, "Invoice Date")
    colCategory = FindHeaderColumn(wsSrc, headerRow, "Category")
    colCategoryTotal = _
    wsSrc.PivotTables("InvoiceTable") _
         .DataFields("Sum of Total") _
         .DataRange.Column
    colMemo = FindHeaderColumn(wsSrc, headerRow, "Memo")
    colInvoiceTotal = FindHeaderColumn(wsSrc, headerRow, "Total")

    colShipping = FindHeaderColumn(wsSrc, headerRow, "Shipping")
    colShippingFlag = FindHeaderColumn(wsSrc, headerRow, "ShipFlag")
    colProratedShipping = FindHeaderColumn(wsSrc, headerRow, "Prorated Shipping")

    colDiscount = FindHeaderColumn(wsSrc, headerRow, "Discount")
    colDiscountFlag = FindHeaderColumn(wsSrc, headerRow, "DiscountFlag")
    colProratedDiscount = FindHeaderColumn(wsSrc, headerRow, "Prorated Discount")

    colOtherFee = FindHeaderColumn(wsSrc, headerRow, "Other Fee")
    colOtherFeeFlag = FindHeaderColumn(wsSrc, headerRow, "OtherFlag")
    colProratedOther = FindHeaderColumn(wsSrc, headerRow, "Prorated Other")

    colTax = FindHeaderColumn(wsSrc, headerRow, "Tax")
    colTaxFlag = FindHeaderColumn(wsSrc, headerRow, "TaxFlag")
    colProratedTax = FindHeaderColumn(wsSrc, headerRow, "Prorated Tax")

    colImportFee = FindHeaderColumn(wsSrc, headerRow, "Import Fee")
    colImportFlag = FindHeaderColumn(wsSrc, headerRow, "ImportFlag")
    colProratedImport = FindHeaderColumn(wsSrc, headerRow, "Prorated Import")

    colPoints = FindHeaderColumn(wsSrc, headerRow, "Points")
    colPointsFlag = FindHeaderColumn(wsSrc, headerRow, "PointFlag")
    colProratedPoints = FindHeaderColumn(wsSrc, headerRow, "Prorated Points")

    colGiftCard = FindHeaderColumn(wsSrc, headerRow, "Gift Card")
    colGiftCardFlag = FindHeaderColumn(wsSrc, headerRow, "GCFlag")
    colProratedGiftCard = FindHeaderColumn(wsSrc, headerRow, "Prorated GiftCard")

    lastDataRow = wsSrc.Cells(wsSrc.Rows.Count, colInvoice).End(xlUp).Row

    wsOut.Cells.ClearContents
    outRow = 1
    currentInvoice = vbNullString
    
    Dim payee As String

    payee = Trim$(InputBox( _
        "Enter the Payee for this export batch:", _
        "Quicken Export Payee", _
        "YAMI" _
    ))
    
    If Len(payee) = 0 Then
        MsgBox "Export cancelled: Payee is required.", vbExclamation
        Exit Sub
    End If

    invoiceCount = 0
    For r = firstDataRow To lastDataRow

        invoiceNumber = Trim$(CStr(wsSrc.Cells(r, colInvoice).value))

        If Len(invoiceNumber) = 0 Then
            GoTo NextRow
        End If
        
        If StrComp(invoiceNumber, "Grand Total", vbTextCompare) = 0 _
            Or StrComp(invoiceNumber, "(blank)", vbTextCompare) = 0 Then
            GoTo NextRow
        End If

        If Len(invoiceNumber) = 0 Then
            GoTo NextRow
        End If

        ' Start a new invoice
        If invoiceNumber <> currentInvoice Then
            invoiceCount = invoiceCount + 1

            currentInvoice = invoiceNumber

            invoiceTotal = NzCurrency(wsSrc.Cells(r, colInvoiceTotal).value)

            shippingTotal = NzCurrency(wsSrc.Cells(r, colShipping).value)
            discountTotal = NzCurrency(wsSrc.Cells(r, colDiscount).value)
            otherFeeTotal = NzCurrency(wsSrc.Cells(r, colOtherFee).value)
            taxTotal = NzCurrency(wsSrc.Cells(r, colTax).value)
            importFeeTotal = NzCurrency(wsSrc.Cells(r, colImportFee).value)
            pointsTotal = NzCurrency(wsSrc.Cells(r, colPoints).value)
            giftCardTotal = NzCurrency(wsSrc.Cells(r, colGiftCard).value)

            shippingAllocated = 0
            discountAllocated = 0
            otherFeeAllocated = 0
            taxAllocated = 0
            importFeeAllocated = 0
            pointsAllocated = 0
            giftCardAllocated = 0

            WriteNewTransaction _
                wsOut, _
                outRow, _
                wsSrc.Cells(r, colInvoiceDate).value, _
                payee, _
                invoiceTotal, _
                currentInvoice

        End If

        ' Determine whether this is the last category row for this invoice
        If r = lastDataRow Then
            isLastInvoiceRow = True
        Else
            nextInvoice = Trim$(CStr(wsSrc.Cells(r + 1, colInvoice).value))
            isLastInvoiceRow = (nextInvoice <> currentInvoice)
        End If

        ' Ordinary merchandise/category split
        WriteSplitIfNonZero _
            wsOut, _
            outRow, _
            CStr(wsSrc.Cells(r, colCategory).value), _
            NzCurrency(wsSrc.Cells(r, colCategoryTotal).value), _
            CStr(wsSrc.Cells(r, colMemo).value)

        ' Invoice-level adjustments allocated to this category

        EmitAllocatedSplit _
            wsOut, outRow, _
            CStr(wsSrc.Cells(r, colCategory).value), _
            "Freight", _
            IsTrue(wsSrc.Cells(r, colShippingFlag).value), _
            NzCurrency(wsSrc.Cells(r, colProratedShipping).value), _
            shippingTotal, shippingAllocated, _
            isLastInvoiceRow

        EmitAllocatedSplit _
            wsOut, outRow, _
            CStr(wsSrc.Cells(r, colCategory).value), _
            "Discount", _
            IsTrue(wsSrc.Cells(r, colDiscountFlag).value), _
            NzCurrency(wsSrc.Cells(r, colProratedDiscount).value), _
            discountTotal, discountAllocated, _
            isLastInvoiceRow

        EmitAllocatedSplit _
            wsOut, outRow, _
            CStr(wsSrc.Cells(r, colCategory).value), _
            "Other Fee", _
            IsTrue(wsSrc.Cells(r, colOtherFeeFlag).value), _
            NzCurrency(wsSrc.Cells(r, colProratedOther).value), _
            otherFeeTotal, otherFeeAllocated, _
            isLastInvoiceRow

        EmitAllocatedSplit _
            wsOut, outRow, _
            CStr(wsSrc.Cells(r, colCategory).value), _
            "Sales Tax Charged", _
            IsTrue(wsSrc.Cells(r, colTaxFlag).value), _
            NzCurrency(wsSrc.Cells(r, colProratedTax).value), _
            taxTotal, taxAllocated, _
            isLastInvoiceRow

        EmitAllocatedSplit _
            wsOut, outRow, _
            CStr(wsSrc.Cells(r, colCategory).value), _
            "Import Fee", _
            IsTrue(wsSrc.Cells(r, colImportFlag).value), _
            NzCurrency(wsSrc.Cells(r, colProratedImport).value), _
            importFeeTotal, importFeeAllocated, _
            isLastInvoiceRow

        EmitAllocatedSplit _
            wsOut, outRow, _
            CStr(wsSrc.Cells(r, colCategory).value), _
            "Points", _
            IsTrue(wsSrc.Cells(r, colPointsFlag).value), _
            NzCurrency(wsSrc.Cells(r, colProratedPoints).value), _
            pointsTotal, pointsAllocated, _
            isLastInvoiceRow

        EmitAllocatedSplit _
            wsOut, outRow, _
            CStr(wsSrc.Cells(r, colCategory).value), _
            "Gift Card", _
            IsTrue(wsSrc.Cells(r, colGiftCardFlag).value), _
            NzCurrency(wsSrc.Cells(r, colProratedGiftCard).value), _
            giftCardTotal, giftCardAllocated, _
            isLastInvoiceRow

        ' Final integrity check for this invoice
        If isLastInvoiceRow Then
            WriteSaveTransaction wsOut, outRow
            
            ValidateInvoiceAllocations _
                currentInvoice, _
                shippingTotal, shippingAllocated, _
                discountTotal, discountAllocated, _
                otherFeeTotal, otherFeeAllocated, _
                taxTotal, taxAllocated, _
                importFeeTotal, importFeeAllocated, _
                pointsTotal, pointsAllocated, _
                giftCardTotal, giftCardAllocated
        End If

NextRow:
    Next r

    MsgBox "Quicken export staging complete: " & _
           invoiceCount & " invoices processed " & vbCr & _
           CStr(outRow - 1) & " command rows created.", _
           vbInformation

End Sub


Private Function FindHeaderColumn( _
    ByVal ws As Worksheet, _
    ByVal headerRow As Long, _
    ByVal headerText As String _
) As Long

    Dim lastCol As Long
    Dim c As Long
    Dim displayedValue As String

    lastCol = ws.Cells(headerRow, ws.Columns.Count).End(xlToLeft).Column

    For c = 1 To lastCol
        displayedValue = Trim$(CStr(ws.Cells(headerRow, c).value))

        If StrComp(displayedValue, headerText, vbTextCompare) = 0 Then
            FindHeaderColumn = c
            Exit Function
        End If
    Next c

    Err.Raise vbObjectError + 1000, _
              "FindHeaderColumn", _
              "Required column not found: " & headerText

End Function

Private Function NzCurrency(ByVal value As Variant) As Currency

    If IsError(value) Then
        NzCurrency = 0
    ElseIf IsEmpty(value) Then
        NzCurrency = 0
    ElseIf Len(Trim$(CStr(value))) = 0 Then
        NzCurrency = 0
    ElseIf IsNumeric(value) Then
        NzCurrency = CCur(value)
    Else
        NzCurrency = 0
    End If

End Function

Private Function IsTrue(ByVal value As Variant) As Boolean

    If VarType(value) = vbBoolean Then
        IsTrue = CBool(value)
    Else
        IsTrue = (UCase$(Trim$(CStr(value))) = "TRUE")
    End If

End Function

Private Sub EmitAllocatedSplit( _
    ByVal ws As Worksheet, _
    ByRef outRow As Long, _
    ByVal category As String, _
    ByVal memo As String, _
    ByVal appliesToCategory As Boolean, _
    ByVal worksheetAllocation As Currency, _
    ByVal invoiceAdjustmentTotal As Currency, _
    ByRef amountAllocated As Currency, _
    ByVal isLastInvoiceRow As Boolean _
)

    Dim splitAmount As Currency

    If invoiceAdjustmentTotal = 0 Then Exit Sub
    If Not appliesToCategory Then Exit Sub

    If isLastInvoiceRow Then
        ' Force final allocation to reconcile exactly to invoice value.
        splitAmount = invoiceAdjustmentTotal - amountAllocated
    Else
        splitAmount = worksheetAllocation
    End If

    If splitAmount = 0 Then Exit Sub

    WriteSplitIfNonZero _
        ws, _
        outRow, _
        category, _
        splitAmount, _
        memo

    amountAllocated = amountAllocated + splitAmount

End Sub

Private Sub WriteNewTransaction( _
    ByVal ws As Worksheet, _
    ByRef outRow As Long, _
    ByVal rawInvoiceDate As Variant, _
    ByVal payee As String, _
    ByVal invoiceTotal As Currency, _
    ByVal memo As String _
)
    Dim invoiceDate As String
    invoiceDate = Trim$(Split(rawInvoiceDate, ",")(0))

    ws.Cells(outRow, 1).value = "NewTransaction"
    ws.Cells(outRow, 2).value = invoiceDate             'Format$(invoiceDate, "mm/dd/yy")
    ws.Cells(outRow, 3).value = payee
    ws.Cells(outRow, 4).value = invoiceTotal
    ws.Cells(outRow, 5).value = UCase(payee) & " Invoice: " & memo & " - " & invoiceDate

    outRow = outRow + 1

End Sub

Private Sub WriteSplitIfNonZero( _
    ByVal ws As Worksheet, _
    ByRef outRow As Long, _
    ByVal category As String, _
    ByVal amount As Currency, _
    ByVal memo As String _
)

    If amount = 0 Then Exit Sub

    ws.Cells(outRow, 1).value = "Split"
    ws.Cells(outRow, 2).value = category
    ws.Cells(outRow, 3).value = amount
    ws.Cells(outRow, 4).value = memo

    outRow = outRow + 1

End Sub

Private Sub WriteSaveTransaction( _
    ByVal ws As Worksheet, _
    ByRef outRow As Long _
)

    ws.Cells(outRow, 1).value = "SaveTransaction"
    outRow = outRow + 1

End Sub

Private Sub ValidateInvoiceAllocations( _
    ByVal invoiceNumber As String, _
    ByVal shippingTotal As Currency, _
    ByVal shippingAllocated As Currency, _
    ByVal discountTotal As Currency, _
    ByVal discountAllocated As Currency, _
    ByVal otherFeeTotal As Currency, _
    ByVal otherFeeAllocated As Currency, _
    ByVal taxTotal As Currency, _
    ByVal taxAllocated As Currency, _
    ByVal importFeeTotal As Currency, _
    ByVal importFeeAllocated As Currency, _
    ByVal pointsTotal As Currency, _
    ByVal pointsAllocated As Currency, _
    ByVal giftCardTotal As Currency, _
    ByVal giftCardAllocated As Currency _
)

    If shippingTotal <> shippingAllocated Then
        Err.Raise vbObjectError + 1100, , _
            "Invoice " & invoiceNumber & _
            ": shipping allocation does not reconcile."
    End If

    If discountTotal <> discountAllocated Then
        Err.Raise vbObjectError + 1101, , _
            "Invoice " & invoiceNumber & _
            ": discount allocation does not reconcile."
    End If

    If otherFeeTotal <> otherFeeAllocated Then
        Err.Raise vbObjectError + 1102, , _
            "Invoice " & invoiceNumber & _
            ": other-fee allocation does not reconcile."
    End If

    If taxTotal <> taxAllocated Then
        Err.Raise vbObjectError + 1103, , _
            "Invoice " & invoiceNumber & _
            ": tax allocation does not reconcile."
    End If

    If importFeeTotal <> importFeeAllocated Then
        Err.Raise vbObjectError + 1104, , _
            "Invoice " & invoiceNumber & _
            ": import-fee allocation does not reconcile."
    End If

    If pointsTotal <> pointsAllocated Then
        Err.Raise vbObjectError + 1105, , _
            "Invoice " & invoiceNumber & _
            ": points allocation does not reconcile."
    End If

    If giftCardTotal <> giftCardAllocated Then
        Err.Raise vbObjectError + 1106, , _
            "Invoice " & invoiceNumber & _
            ": gift-card allocation does not reconcile."
    End If

End Sub

