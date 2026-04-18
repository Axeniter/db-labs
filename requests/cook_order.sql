BEGIN TRANSACTION;

-- находим последний заказ в статусе "В ожидании"
CREATE TEMP TABLE temp_order_id AS
SELECT id AS order_id
FROM Orders
WHERE status_id = (SELECT id FROM OrderStatuses WHERE name = 'В ожидании')
ORDER BY created_at DESC
LIMIT 1;

-- меняем статус заказа на "Готовится"
UPDATE Orders
SET status_id = (SELECT id FROM OrderStatuses WHERE name = 'Готовится')
WHERE id = (SELECT order_id FROM temp_order_id);

-- списываем ингредиенты со склада
INSERT INTO IngredientOperations (employee_id) VALUES (4); -- Алиса Кий 

-- временная таблица с ингредиентной операцией
CREATE TEMP TABLE temp_operation_id AS
SELECT last_insert_rowid() AS operation_id;

-- списываем каждый ингредиент
INSERT INTO IngredientOperationItems (operation_id, ingredient_id, operation_type_id, unit_id, amount)
SELECT 
    (SELECT operation_id FROM temp_operation_id),
    ri.ingredient_id,
    (SELECT id FROM IngredientOperationTypes WHERE name = 'Использование'),
    ri.unit_id,
    SUM(ri.quantity * oi.quantity) AS total_amount
FROM OrderItems AS oi
JOIN RecipeItems AS ri ON oi.menu_item_id = ri.menu_item_id
WHERE oi.order_id = (SELECT order_id FROM temp_order_id)
GROUP BY ri.ingredient_id, ri.unit_id;

-- обновляем остатки на складе
UPDATE IngredientInventory
SET quantity = quantity - (
    SELECT ioi.amount
    FROM IngredientOperationItems AS ioi
    WHERE ioi.operation_id = (SELECT operation_id FROM temp_operation_id)
    AND ioi.ingredient_id = IngredientInventory.ingredient_id
    AND ioi.unit_id = IngredientInventory.unit_id
)
WHERE ingredient_id IN (
    SELECT ingredient_id
    FROM IngredientOperationItems
    WHERE operation_id = (SELECT operation_id FROM temp_operation_id)
);

COMMIT;

-- информация о заказе
SELECT 
    o.id AS order_id,
    os.name AS order_status,
    o.created_at AS order_created,
    DATETIME('now') AS cooking_started,
    CASE 
        WHEN d.id IS NOT NULL THEN 'Доставка: ' || d.address
        WHEN di.id IS NOT NULL THEN 'В зале: стол ' || t.number
    END AS order_type,
    c.first_name || ' ' || c.last_name AS customer,
    c.phone AS customer_phone
FROM Orders AS o
JOIN OrderStatuses AS os ON o.status_id = os.id
LEFT JOIN Deliveries AS d ON o.id = d.order_id
LEFT JOIN DineIns AS di ON o.id = di.order_id
LEFT JOIN Tables AS t ON di.table_id = t.id
LEFT JOIN Customers AS c ON o.customer_id = c.id
WHERE o.id = (SELECT order_id FROM temp_order_id);

-- состав заказа
SELECT 
    mi.name AS dish,
    oi.quantity AS quantity,
    oi.item_cost AS price,
    (oi.quantity * oi.item_cost) AS total_price,
    GROUP_CONCAT(i.name || ': ' || (ri.quantity * oi.quantity) || ' ' || u.name, ', ') AS ingredients_used
FROM OrderItems AS oi
JOIN MenuItems AS mi ON oi.menu_item_id = mi.id
LEFT JOIN RecipeItems AS ri ON mi.id = ri.menu_item_id
LEFT JOIN Ingredients AS i ON ri.ingredient_id = i.id
LEFT JOIN Units AS u ON ri.unit_id = u.id
WHERE oi.order_id = (SELECT order_id FROM temp_order_id)
GROUP BY oi.id, mi.name, oi.quantity, oi.item_cost
ORDER BY mi.name;

-- остатки ингредиентов
SELECT 
    i.name AS ingredient,
    ii.quantity AS current_stock,
    u.name AS unit
FROM IngredientInventory AS ii
JOIN Ingredients AS i ON ii.ingredient_id = i.id
JOIN Units AS u ON ii.unit_id = u.id
WHERE ii.ingredient_id IN (
    SELECT DISTINCT ri.ingredient_id
    FROM OrderItems AS oi
    JOIN RecipeItems AS ri ON oi.menu_item_id = ri.menu_item_id
    WHERE oi.order_id = (SELECT order_id FROM temp_order_id)
)
ORDER BY ii.quantity ASC;

-- очищаем временные таблицы
DROP TABLE IF EXISTS temp_order_id;
DROP TABLE IF EXISTS temp_operation_id;