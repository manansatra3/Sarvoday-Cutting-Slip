==Working===
SELECT r.[Receipt ID]
	,r.[Receipt Date]
	,r.[Total Qty]
	,r.[Total Coth Qty]
	,i.[Full Item Name]
	,p.[Party Name]
	,s.[School Name]
FROM ((Receipts AS r INNER JOIN Items AS i ON r.[Item Id] = i.[Item Id]) INNER JOIN Party AS p ON r.[Party Id] = p.[Party Id]) LEFT JOIN Schools AS s ON r.[School Id] = s.[School Id]
WHERE IIF(NOT ISNULL([Enter the receipt ID]), r.[Receipt ID] = [Enter the receipt ID],
	IIF(NOT ISNULL([Enter Item Name]), r.[Item Id] = [Enter Item Name], r.[Item Id]) AND
		IIF(NOT ISNULL([Enter Party Name]), r.[Party Id] = [Enter Party Name], r.[Party Id]) AND
			IIF(NOT ISNULL([Enter School Name]), r.[School Id] = [Enter School Name], r.[School Id])
)

=======================================
Trial
=======================================

SELECT r.[Receipt ID]
	,r.[Receipt Date]
	,r.[Total Qty]
	,r.[Total Coth Qty]
	,i.[Full Item Name]
	,p.[Party Name]
	,s.[School Name]
FROM ((Receipts AS r INNER JOIN Items AS i ON r.[Item Id] = i.[Item Id]) INNER JOIN Party AS p ON r.[Party Id] = p.[Party Id]) LEFT JOIN Schools AS s ON r.[School Id] = s.[School Id]
WHERE IIF(NOT ISNULL([Forms]![Search]![Enter the receipt ID]), r.[Receipt ID] = [Forms]![Search]![Enter the receipt ID],
	IIF(NOT ISNULL([Forms]![Search]![Enter Item Name]), r.[Item Id] = [Forms]![Search]![Enter Item Name], r.[Item Id]) AND
		IIF(NOT ISNULL([Forms]![Search]![Enter Party Name]), r.[Party Id] = [Forms]![Search]![Enter Party Name], r.[Party Id]) AND
			IIF(NOT ISNULL([Forms]![Search]![Enter School Name]), r.[School Id] = [Forms]![Search]![Enter School Name], r.[School Id])
)