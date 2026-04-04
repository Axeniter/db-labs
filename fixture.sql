INSERT INTO Roles (name, hourly_rate) VALUES
('Администратор', 1500.00),
('Менеджер', 700.00),
('Шеф-повар', 900.00),
('Повар', 600.00),
('Официант', 500.00),
('Бармен', 700.00);

INSERT INTO MenuCategories (name, is_active) VALUES 
('Холодные напитки', 1),
('Горячие напитки', 1),
('Алкогольные напитки', 1),
('Закуски', 1),
('Супы', 1),
('Основные блюда', 1),
('Десерты', 1);

INSERT INTO OrderStatuses (name) VALUES 
('В ожидании'),
('Подтверждён'),
('Готовится'),
('Готов'),
('Подан'),
('Завершён'),
('Отменён');

INSERT INTO Shifts (name, start_time, end_time) VALUES 
('Утренняя', '08:00:00', '16:00:00'),
('Дневная', '12:00:00', '20:00:00'),
('Вечерняя', '16:00:00', '00:00:00'),
('Ночная', '00:00:00', '08:00:00');

INSERT INTO SupplyStatuses (name) VALUES 
('Заказано'),
('В пути'),
('Доставлено'),
('Отменено');

INSERT INTO DeliveryStatuses (name) VALUES 
('В ожидании'),
('Назначен курьер'),
('Забран'),
('В пути'),
('Доставлен'),
('Отменён');

INSERT INTO PaymentTypes (name, is_active) VALUES 
('Наличные', 1),
('Банковская карта', 1),
('QR код', 1);

INSERT INTO LoyaltyTransactionTypes (name) VALUES 
('Начисление'),
('Списание'),
('Сгорание');

INSERT INTO Units (name) VALUES 
('кг'),
('г'),
('л'),
('мл'),
('шт'),
('уп'),
('бутылка'),
('стакан');

INSERT INTO IngredientOperationTypes (name) VALUES 
('Закупка'),
('Использование'),
('Возврат');

INSERT INTO FinancialTransactionTypes (name) VALUES 
('Доход'),
('Расход');

INSERT INTO FinancialTransactionsCategories (name) VALUES 
('Продажи'),
('Заработная плата'),
('Закупка ингредиентов'),
('Аренда'),
('Маркетинг'),
('Обслуживание'),
('Налоги'),
('Прочее');

INSERT INTO LoyaltyTiers (name, min_spent, discount_percent, cashback_percent) VALUES 
('Микрочелик', 0.00, 0.00, 5.00),
('Челик', 2500.00, 5.00, 5.00),
('Типок', 5000.00, 10.00, 10.00),
('Типсон', 10000.00, 15.00, 15.00),
