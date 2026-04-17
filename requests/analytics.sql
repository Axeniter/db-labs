-- выручка за период (апрель 2026)
WITH daily_stats AS (
    SELECT 
        DATE(ft.transaction_date) AS day,
        SUM(CASE WHEN ftt.name = 'Доход' THEN ft.amount ELSE 0 END) AS revenue,
        SUM(CASE WHEN ftt.name = 'Расход' THEN ft.amount ELSE 0 END) AS expense
    FROM FinancialTransactions AS ft
    JOIN FinancialTransactionTypes AS ftt ON ft.transaction_type_id = ftt.id
    WHERE ft.transaction_date BETWEEN '2026-04-01' AND '2026-04-30'
    GROUP BY DATE(ft.transaction_date)
)
SELECT 
    CAST(day AS TEXT) AS day,
    revenue,
    expense,
    revenue - expense AS profit
FROM daily_stats

UNION ALL

SELECT 
    'Всего за период',
    SUM(revenue),
    SUM(expense),
    SUM(revenue) - SUM(expense)
FROM daily_stats;

-- популярные блюда за период (апрель 2026)
SELECT 
    mi.name AS dish_name,
    SUM(oi.quantity) AS total_quantity,
    COUNT(DISTINCT oi.order_id) AS orders_count,
    SUM(oi.item_cost * oi.quantity) AS total_revenue
FROM OrderItems AS oi
JOIN MenuItems AS mi ON oi.menu_item_id = mi.id
JOIN Orders AS o ON oi.order_id = o.id
WHERE o.created_at BETWEEN '2026-04-01' AND '2026-04-30'
    AND o.status_id != (SELECT id FROM OrderStatuses WHERE name = 'Отменён')
GROUP BY mi.id, mi.name
ORDER BY total_quantity DESC;