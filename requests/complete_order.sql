BEGIN TRANSACTION;

-- находим первый заказ в статусе "Готовится"
CREATE TEMP TABLE temp_order_id AS
SELECT id AS order_id
FROM Orders
WHERE status_id = (SELECT id FROM OrderStatuses WHERE name = 'Готовится')
ORDER BY created_at ASC
LIMIT 1;

-- меняем статус заказа на "Готов"
UPDATE Orders
SET status_id = (SELECT id FROM OrderStatuses WHERE name = 'Готов')
WHERE id = (SELECT order_id FROM temp_order_id);

-- отмечаем все позиции заказа как приготовленные
UPDATE OrderItems
SET cooked_at = DATETIME('now')
WHERE order_id = (SELECT order_id FROM temp_order_id);

-- если это доставка - меняем статус доставки на "Забран"
UPDATE Deliveries
SET delivery_status_id = (SELECT id FROM DeliveryStatuses WHERE name = 'Забран')
WHERE order_id = (SELECT order_id FROM temp_order_id);

-- если это зал - меняем статус dine_in на "Подано"
UPDATE DineIns
SET status_id = (SELECT id FROM DineInStatuses WHERE name = 'Подано')
WHERE order_id = (SELECT order_id FROM temp_order_id);

COMMIT;

-- информация о заказе
SELECT 
    o.id AS order_id,
    os.name AS order_status,
    o.created_at AS order_created,
    (SELECT MAX(cooked_at) FROM OrderItems WHERE order_id = o.id) AS cooking_finished,
    ROUND((JULIANDAY('now') - JULIANDAY(o.created_at)) * 24 * 60) AS total_minutes,
    CASE 
        WHEN d.id IS NOT NULL THEN 'Доставка'
        WHEN di.id IS NOT NULL THEN 'В зале'
    END AS order_type,
    CASE 
        WHEN d.id IS NOT NULL THEN d.address
        WHEN di.id IS NOT NULL THEN 'Стол ' || t.number || ' (' || t.location || ')'
    END AS destination,
    c.first_name || ' ' || c.last_name AS customer,
    c.phone AS customer_phone,
    o.total_cost AS total_cost,
    o.to_pay AS to_pay,
    pt.name AS payment_type
FROM Orders AS o
JOIN OrderStatuses AS os ON o.status_id = os.id
JOIN PaymentTypes AS pt ON o.payment_type_id = pt.id
LEFT JOIN Deliveries AS d ON o.id = d.order_id
LEFT JOIN DeliveryStatuses AS ds ON d.delivery_status_id = ds.id
LEFT JOIN DineIns AS di ON o.id = di.order_id
LEFT JOIN DineInStatuses AS dis ON di.status_id = dis.id
LEFT JOIN Tables AS t ON di.table_id = t.id
LEFT JOIN Customers AS c ON o.customer_id = c.id
WHERE o.id = (SELECT order_id FROM temp_order_id);

SELECT 
    mi.name AS dish,
    oi.quantity AS quantity,
    oi.item_cost AS price,
    (oi.quantity * oi.item_cost) AS total_price,
    oi.created_at AS ordered_at,
    oi.cooked_at AS cooked_at,
    ROUND((JULIANDAY(oi.cooked_at) - JULIANDAY(oi.created_at)) * 24 * 60) AS cooking_minutes
FROM OrderItems AS oi
JOIN MenuItems AS mi ON oi.menu_item_id = mi.id
WHERE oi.order_id = (SELECT order_id FROM temp_order_id)
ORDER BY oi.created_at;

-- информация о курьере (если доставка)
SELECT 
    c2.first_name || ' ' || c2.last_name AS courier,
    c2.phone AS courier_phone,
    cc.name AS courier_company,
    d.address AS delivery_address,
    ds.name AS delivery_status
FROM Deliveries AS d
JOIN Couriers AS c2 ON d.courier_id = c2.id
JOIN CourierCompanies AS cc ON c2.company_id = cc.id
JOIN DeliveryStatuses AS ds ON d.delivery_status_id = ds.id
WHERE d.order_id = (SELECT order_id FROM temp_order_id);

-- информация об официанте и столе (если в зале)
SELECT 
    e.first_name || ' ' || e.last_name AS waiter,
    t.number AS table_number,
    t.location AS table_location,
    dis.name AS dine_in_status
FROM DineIns AS di
JOIN Employees AS e ON di.employee_id = e.id
JOIN Tables AS t ON di.table_id = t.id
JOIN DineInStatuses AS dis ON di.status_id = dis.id
WHERE di.order_id = (SELECT order_id FROM temp_order_id);

-- очищаем временную таблицу
DROP TABLE IF EXISTS temp_order_id;