BEGIN TRANSACTION;

-- создание заказа
INSERT INTO Orders (customer_id, status_id, payment_type_id, total_cost, to_pay, comment)
VALUES (
    (SELECT id FROM Customers WHERE phone = '+79161234567'),  -- customer_id (если номера нет в программе лояльности, то NULL)
    1,                                                        -- status_id = "В ожидании"
    1,                                                        -- payment_type_id = "Наличные"
    0,
    0,
    'быстро быстро, супер срочно'
);

-- временная таблица с айди заказа
CREATE TEMP TABLE temp_order_id AS
SELECT last_insert_rowid() AS order_id;

-- создание позиций заказа
INSERT INTO OrderItems (order_id, menu_item_id, item_cost, quantity)
SELECT 
    (SELECT order_id FROM temp_order_id),
    mi.id,
    mi.price,
    q.quantity
FROM (
    SELECT 6 AS id, 1 AS quantity UNION ALL -- Пятиэтажный бургер
    SELECT 4, 1 UNION ALL                   -- Картофель три
    SELECT 1, 2 UNION ALL                   -- Кола
    SELECT 7, 1                             -- Сырный торт
) AS q
JOIN MenuItems mi ON q.id = mi.id;

-- вычисление стоимости заказа и сколько к оплате
UPDATE Orders 
SET 
    total_cost = (
        SELECT SUM(item_cost * quantity) 
        FROM OrderItems 
        WHERE order_id = (SELECT order_id FROM temp_order_id)
    ),
    to_pay = ROUND(
        (
            SELECT SUM(item_cost * quantity) 
            FROM OrderItems 
            WHERE order_id = (SELECT order_id FROM temp_order_id)
        ) * (1 - COALESCE(
            (SELECT lt.discount_percent 
             FROM Customers c
             LEFT JOIN LoyaltyTiers lt ON c.last_achieved_tier_id = lt.id
             WHERE c.id = Orders.customer_id),
            0
        ) / 100.0),
        2
    )
WHERE id = (SELECT order_id FROM temp_order_id);

-- привязка стола к столу и официанту
INSERT INTO DineIns (order_id, table_id, employee_id)
VALUES ((SELECT order_id FROM temp_order_id), 3, 7);

COMMIT;

-- информация о заказе
SELECT 
    o.id AS order_id,
    o.created_at AS created_at,
    os.name AS status,
    pt.name AS payment_type,
    t.number AS table_number,
    e.first_name || ' ' || e.last_name AS waiter,
    o.comment AS comment,
    o.total_cost AS total_cost,
    c.first_name || ' ' || c.last_name AS customer,
    c.phone AS customer_phone
FROM Orders AS o
JOIN OrderStatuses AS os ON o.status_id = os.id
JOIN PaymentTypes AS pt ON o.payment_type_id = pt.id
JOIN DineIns AS di ON o.id = di.order_id
JOIN Tables AS t ON di.table_id = t.id
JOIN Employees AS e ON di.employee_id = e.id
LEFT JOIN Customers AS c ON o.customer_id = c.id
WHERE o.id = (SELECT order_id FROM temp_order_id);

SELECT
    mi.name AS item,
    oi.quantity AS quantity,
    oi.item_cost AS price_per_item,
    (oi.quantity * oi.item_cost) AS sum
FROM OrderItems AS oi
JOIN MenuItems AS mi ON oi.menu_item_id = mi.id
WHERE oi.order_id = (SELECT order_id FROM temp_order_id);

DROP TABLE IF EXISTS temp_order_id;