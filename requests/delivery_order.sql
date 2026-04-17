BEGIN TRANSACTION;

-- создание заказа
INSERT INTO Orders (customer_id, status_id, payment_type_id, total_cost, to_pay, comment)
VALUES (
    (SELECT id FROM Customers WHERE phone = '+79163456789'),  -- customer_id (Каша Производная)
    1,                                                        -- status_id = "В ожидании"
    2,                                                        -- payment_type_id = "Банковская карта"
    0,
    0,
    'у вас 30 минут'
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
    SELECT 6 AS id, 2 AS quantity UNION ALL  -- Пятиэтажный бургер x2
    SELECT 4, 1 UNION ALL                    -- Картофель три
    SELECT 1, 3 UNION ALL                    -- Кола x3
    SELECT 2, 2                              -- Кофе x2
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

-- привязка к доставке
INSERT INTO Deliveries (order_id, address, courier_id, delivery_status_id)
VALUES (
    (SELECT order_id FROM temp_order_id), 
    'г. Новобобёрск, ул. Баробенко 42, кв 17', 
    3,                                                        -- courier_id = Олег Бородатый
    1                                                         -- delivery_status_id = "Собирается"
);

COMMIT;

-- информация о заказе
SELECT 
    o.id AS order_id,
    o.created_at AS created_at,
    os.name AS status,
    pt.name AS payment_type,
    d.address AS delivery_address,
    ds.name AS delivery_status,
    c2.first_name || ' ' || c2.last_name AS courier,
    cc.name AS courier_company,
    o.comment AS comment,
    o.total_cost AS total_cost,
    o.to_pay AS to_pay,
    c.first_name || ' ' || c.last_name AS customer,
    c.phone AS customer_phone
FROM Orders AS o
JOIN OrderStatuses AS os ON o.status_id = os.id
JOIN PaymentTypes AS pt ON o.payment_type_id = pt.id
JOIN Deliveries AS d ON o.id = d.order_id
JOIN DeliveryStatuses AS ds ON d.delivery_status_id = ds.id
JOIN Couriers AS c2 ON d.courier_id = c2.id
LEFT JOIN CourierCompanies AS cc ON c2.company_id = cc.id
LEFT JOIN Customers AS c ON o.customer_id = c.id
WHERE o.id = (SELECT order_id FROM temp_order_id);
SELECT
    mi.name AS item,
    oi.quantity AS quantity,
    oi.item_cost AS price_per_item,
    (oi.quantity * oi.item_cost) AS total_price
FROM OrderItems AS oi
JOIN MenuItems AS mi ON oi.menu_item_id = mi.id
WHERE oi.order_id = (SELECT order_id FROM temp_order_id);

DROP TABLE IF EXISTS temp_order_id;