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

-- сколько блюд можно приготовить из ингридиентов на складе
SELECT 
    mi.name AS dish,
    FLOOR(MIN(ii.quantity / ri.quantity)) AS count_of_portions
FROM RecipeItems AS ri
JOIN MenuItems AS mi ON ri.menu_item_id = mi.id
JOIN IngredientInventory AS ii ON ri.ingredient_id = ii.ingredient_id
WHERE mi.is_available = 1
GROUP BY mi.id, mi.name
ORDER BY count_of_portions;

-- блюда, которые часто заказывают вместе
SELECT 
    mi1.name AS dish_1,
    mi2.name AS dish_2,
    COUNT(DISTINCT oi1.order_id) AS count_of_joint_orders
FROM OrderItems AS oi1
JOIN OrderItems AS oi2 ON oi1.order_id = oi2.order_id AND oi1.menu_item_id < oi2.menu_item_id
JOIN MenuItems AS mi1 ON oi1.menu_item_id = mi1.id
JOIN MenuItems AS mi2 ON oi2.menu_item_id = mi2.id
GROUP BY mi1.id, mi2.id, mi1.name, mi2.name
HAVING count_of_joint_orders >= 1  
ORDER BY count_of_joint_orders DESC;

-- свободные столы на текущий момент
SELECT 
    t.number,
    t.capacity,
    t.location
FROM Tables AS t
WHERE t.is_available = 1  
  AND t.id NOT IN (
      SELECT tr.table_id
      FROM TableReservations AS tr
      WHERE tr.reservation_date = DATE('now')
        AND tr.reservation_time <= TIME('now', 'localtime')
        AND datetime(tr.reservation_date || ' ' || tr.reservation_time, '+' || tr.duration_minutes || ' minutes') > datetime('now', 'localtime')
  )
  AND t.id NOT IN (
      SELECT DISTINCT di.table_id
      FROM DineIns AS di
      JOIN Orders AS o ON o.id = di.order_id
      WHERE o.status_id NOT IN (5, 6)  
        AND DATE(o.created_at) = DATE('now')
  )
ORDER BY t.capacity, t.number;
