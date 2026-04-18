BEGIN TRANSACTION;

-- находим заказ в статусе "Готов"
CREATE TEMP TABLE temp_order_id AS
SELECT id AS order_id
FROM Orders
WHERE status_id = (SELECT id FROM OrderStatuses WHERE name = 'Готов')
ORDER BY created_at ASC
LIMIT 1;

-- если доставка - меняем статус на "Доставлен"
UPDATE Deliveries
SET delivery_status_id = (SELECT id FROM DeliveryStatuses WHERE name = 'Доставлен')
WHERE order_id = (SELECT order_id FROM temp_order_id);

-- создаем финансовую транзакцию
INSERT INTO FinancialTransactions (transaction_type_id, amount, transaction_date, description, category_id)
SELECT 
    (SELECT id FROM FinancialTransactionTypes WHERE name = 'Доход'),
    o.to_pay,
    DATETIME('now'),
    'Оплата заказа ' || o.id,
    (SELECT id FROM FinancialTransactionsCategories WHERE name = 'Продажи')
FROM Orders AS o
WHERE o.id = (SELECT order_id FROM temp_order_id);

-- сохраняем айди финансовой транзакции
CREATE TEMP TABLE temp_financial_id AS
SELECT last_insert_rowid() AS financial_id;

-- обновляем заказ: статус "Завершён", время закрытия, привязываем финансовую транзакцию
UPDATE Orders
SET 
    status_id = (SELECT id FROM OrderStatuses WHERE name = 'Завершён'),
    closed_at = DATETIME('now'),
    financial_transaction_id = (SELECT financial_id FROM temp_financial_id)
WHERE id = (SELECT order_id FROM temp_order_id);

-- обновляем статистику клиента
UPDATE Customers
SET 
    total_spent = total_spent + (
        SELECT total_cost FROM Orders WHERE id = (SELECT order_id FROM temp_order_id)
    ),
    total_orders = total_orders + 1
WHERE id = (
    SELECT customer_id FROM Orders WHERE id = (SELECT order_id FROM temp_order_id)
)
AND (
    SELECT customer_id FROM Orders WHERE id = (SELECT order_id FROM temp_order_id)
) IS NOT NULL;

-- обновляем уровень лояльности клиента
UPDATE Customers
SET last_achieved_tier_id = (
    SELECT id FROM LoyaltyTiers 
    WHERE min_spent <= (
        SELECT total_spent FROM Customers WHERE id = Customers.id
    )
    ORDER BY min_spent DESC
    LIMIT 1
)
WHERE id = (
    SELECT customer_id FROM Orders WHERE id = (SELECT order_id FROM temp_order_id)
)
AND (
    SELECT customer_id FROM Orders WHERE id = (SELECT order_id FROM temp_order_id)
) IS NOT NULL;

-- начисляем кешбэк клиенту
INSERT INTO LoyaltyTransactions (customer_id, order_id, points_amount, transaction_type_id, description, created_at)
SELECT 
    o.customer_id,
    o.id,
    ROUND(o.total_cost * lt.cashback_percent / 100.00, 2),
    (SELECT id FROM LoyaltyTransactionTypes WHERE name = 'Начисление'),
    lt.cashback_percent || '% кешбэк с заказа на ' || o.total_cost || ' рублей (уровень ' || lt.name || ')',
    DATETIME('now')
FROM Orders AS o
JOIN Customers AS c ON o.customer_id = c.id
JOIN LoyaltyTiers AS lt ON c.last_achieved_tier_id = lt.id
WHERE o.id = (SELECT order_id FROM temp_order_id);

COMMIT;

-- информация о заказе
SELECT 
    o.id AS order_id,
    os.name AS order_status,
    o.created_at AS order_created,
    o.closed_at AS closed_at,
    ROUND((JULIANDAY(o.closed_at) - JULIANDAY(o.created_at)) * 24 * 60) AS total_minutes,
    o.total_cost AS total_cost,
    o.to_pay AS paid_amount,
    pt.name AS payment_type,
    ft.amount AS financial_amount,
    ftt.name AS financial_type,
    ftc.name AS financial_category,
    ft.id AS financial_transaction_id
FROM Orders AS o
JOIN OrderStatuses AS os ON o.status_id = os.id
JOIN PaymentTypes AS pt ON o.payment_type_id = pt.id
JOIN FinancialTransactions AS ft ON o.financial_transaction_id = ft.id
JOIN FinancialTransactionTypes AS ftt ON ft.transaction_type_id = ftt.id
JOIN FinancialTransactionsCategories AS ftc ON ft.category_id = ftc.id
WHERE o.id = (SELECT order_id FROM temp_order_id);

SELECT 
    mi.name AS dish,
    oi.quantity AS quantity,
    oi.item_cost AS price,
    (oi.quantity * oi.item_cost) AS total_price
FROM OrderItems AS oi
JOIN MenuItems AS mi ON oi.menu_item_id = mi.id
WHERE oi.order_id = (SELECT order_id FROM temp_order_id)
ORDER BY oi.created_at;

-- информация о клиенте и начисленных бонусах (если он учавствует в программе лояльности)
SELECT 
    c.first_name || ' ' || c.last_name AS customer,
    c.phone AS customer_phone,
    c.total_spent AS total_spent_all_time,
    c.total_orders AS total_orders_all_time,
    lt.name AS current_loyalty_tier,
    lt.discount_percent AS discount_percent,
    lt.cashback_percent AS cashback_percent,
    ltrans.points_amount AS earned_cashback,
    ltrans.description AS cashback_description
FROM Orders AS o
JOIN Customers AS c ON o.customer_id = c.id
JOIN LoyaltyTiers AS lt ON c.last_achieved_tier_id = lt.id
JOIN LoyaltyTransactions AS ltrans ON ltrans.order_id = o.id 
AND ltrans.transaction_type_id = (SELECT id FROM LoyaltyTransactionTypes WHERE name = 'Начисление')
WHERE o.id = (SELECT order_id FROM temp_order_id)
AND o.customer_id IS NOT NULL;

-- информация о доставке (если была доставка)
SELECT 
    ds.name AS delivery_status,
    d.address AS delivery_address,
    c2.first_name || ' ' || c2.last_name AS courier
FROM Deliveries AS d
JOIN DeliveryStatuses AS ds ON d.delivery_status_id = ds.id
JOIN Couriers AS c2 ON d.courier_id = c2.id
WHERE d.order_id = (SELECT order_id FROM temp_order_id);

-- очищаем временные таблицы
DROP TABLE IF EXISTS temp_order_id;
DROP TABLE IF EXISTS temp_financial_id;