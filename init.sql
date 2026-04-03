CREATE TABLE IF NOT EXISTS Roles
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(30) NOT NULL UNIQUE,
    salary DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS MenuCategories
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(30) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS OrderStatuses
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Shifts
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(30) NOT NULL UNIQUE,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
);

CREATE TABLE IF NOT EXISTS SupplyStatuses
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS DeliveryStatuses
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS PaymentTypes
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS LoyaltyTransactionTypes
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Units
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(10) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS IngredientOperationTypes
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS FinancialTransactionTypes
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS FinancialTransactionsCategories
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS FinancialTransactions
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_type_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    category_id INTEGER,
    
    FOREIGN KEY (transaction_type_id) REFERENCES FinancialTransactionTypes(id),
    FOREIGN KEY (category_id) REFERENCES FinancialTransactionsCategories(id)
);

CREATE TABLE IF NOT EXISTS LoyaltyTiers
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(30) NOT NULL UNIQUE,
    min_spent DECIMAL(10,2) NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Employees
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(255) UNIQUE,
    hire_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT 1,

    FOREIGN KEY (role_id) REFERENCES Roles (id)
);

CREATE TABLE IF NOT EXISTS MenuItems
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    calories INTEGER,
    is_available BOOLEAN DEFAULT 1,
    
    FOREIGN KEY (category_id) REFERENCES MenuCategories (id)
);

CREATE TABLE IF NOT EXISTS Ingredients
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    name VARCHAR(30) NOT NULL UNIQUE,
    quantity DECIMAL(10,3) DEFAULT 0,

    FOREIGN KEY (unit_id) REFERENCES Units (id)
);

CREATE TABLE IF NOT EXISTS RecipeItems
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_item_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,
    quantity DECIMAL(10,3) NOT NULL,

    FOREIGN KEY (menu_item_id) REFERENCES MenuItems (id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients (id),
    FOREIGN KEY (unit_id) REFERENCES Units (id),
    UNIQUE(menu_item_id, ingredient_id)  
);

CREATE TABLE IF NOT EXISTS Tables
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number INTEGER NOT NULL UNIQUE,
    capacity INTEGER NOT NULL,
    location VARCHAR(30),
    is_available BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS TableReservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_id INTEGER NOT NULL,
    customer_phone VARCHAR(20),
    reservation_date DATE NOT NULL,
    reservation_time TIME NOT NULL,
    duration_minutes INTEGER DEFAULT 120,
    created_by_employee_id INTEGER NOT NULL,
    
    FOREIGN KEY (table_id) REFERENCES Tables(id),
    FOREIGN KEY (created_by_employee_id) REFERENCES Employees(id)
);

CREATE TABLE IF NOT EXISTS Orders
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    status_id INTEGER NOT NULL,
    payment_type_id INTEGER NOT NULL,
    total_cost DECIMAL(10,2) DEFAULT 0,
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    closed_at DATETIME,
    financial_transaction_id INTEGER,

    FOREIGN KEY (status_id) REFERENCES OrderStatuses(id),
    FOREIGN KEY (payment_type_id) REFERENCES PaymentTypes(id),
    FOREIGN KEY (customer_id) REFERENCES Customers(id),
    FOREIGN KEY (financial_transaction_id) REFERENCES FinancialTransactions(id)
);

CREATE TABLE IF NOT EXISTS CourierCompanies
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS Couriers
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    is_free BOOLEAN DEFAULT 1,
    company_id INTEGER,

    FOREIGN KEY (company_id) REFERENCES CourierCompanies (id)
);

CREATE TABLE IF NOT EXISTS Deliveries
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    address VARCHAR(200) NOT NULL,
    courier_id INTEGER NOT NULL,
    delivery_status_id INTEGER NOT NULL,

    FOREIGN KEY (order_id) REFERENCES Orders (id),
    FOREIGN KEY (courier_id) REFERENCES Couriers (id),
    FOREIGN KEY (delivery_status_id) REFERENCES DeliveryStatuses (id)
);

CREATE TABLE IF NOT EXISTS DineIns
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    table_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders (id),
    FOREIGN KEY (table_id) REFERENCES Tables (id),
    FOREIGN KEY (employee_id) REFERENCES Employees (id)
);

CREATE TABLE IF NOT EXISTS OrderItems
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    item_cost DECIMAL(10,2) DEFAULT 0,
    quantity INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    cooked_at DATETIME,

    FOREIGN KEY (order_id) REFERENCES Orders (id),
    FOREIGN KEY (menu_item_id) REFERENCES MenuItems (id)
);

CREATE TABLE IF NOT EXISTS Suppliers 
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    phone VARCHAR(20),
    email VARCHAR(255),
    address VARCHAR(100),
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS SupplierPrices
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,
    price_per_unit DECIMAL(10,2) NOT NULL,
    
    FOREIGN KEY (supplier_id) REFERENCES Suppliers (id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients (id),
    FOREIGN KEY (unit_id) REFERENCES Units (id),
    UNIQUE(supplier_id, ingredient_id)
);

CREATE TABLE IF NOT EXISTS SupplierOrders
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivery_date DATETIME,
    status_id INTEGER NOT NULL,
    total_cost DECIMAL(10,2) DEFAULT 0,
    financial_transaction_id INTEGER,
    
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(id),
    FOREIGN KEY (employee_id) REFERENCES Employees(id),
    FOREIGN KEY (status_id) REFERENCES SupplyStatuses(id),
    FOREIGN KEY (financial_transaction_id) REFERENCES FinancialTransactions(id)
);

CREATE TABLE IF NOT EXISTS SupplierOrderItems
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_order_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,
    quantity DECIMAL(10,3) NOT NULL,
    price_per_unit DECIMAL(10,2) NOT NULL,
    total_cost DECIMAL(10,2) NOT NULL,
    
    FOREIGN KEY (supplier_order_id) REFERENCES SupplierOrders(id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(id),
    FOREIGN KEY (unit_id) REFERENCES Units(id)
);

CREATE TABLE IF NOT EXISTS IngredientOperations
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (employee_id) REFERENCES Employees(id)
);

CREATE TABLE IF NOT EXISTS IngredientOperationItems
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    operation_type_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,
    amount DECIMAL(10,3) DEFAULT 0,

    FOREIGN KEY (operation_id) REFERENCES IngredientOperations(id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(id),
    FOREIGN KEY (operation_type_id) REFERENCES IngredientOperationTypes(id),
    FOREIGN KEY (unit_id) REFERENCES Units(id)
);

CREATE TABLE IF NOT EXISTS EmployeeSchedules
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    shift_id INTEGER NOT NULL,
    work_date DATE NOT NULL,
    is_working BOOLEAN DEFAULT 1,
    
    FOREIGN KEY (employee_id) REFERENCES Employees (id),
    FOREIGN KEY (shift_id) REFERENCES Shifts (id),
    UNIQUE(employee_id, work_date)
);

CREATE TABLE IF NOT EXISTS TimeTrackers
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    check_in DATETIME NOT NULL,
    check_out DATETIME,
    break_start DATETIME,
    break_end DATETIME,
    
    FOREIGN KEY (employee_id) REFERENCES Employees (id)
);

CREATE TABLE IF NOT EXISTS LoyaltyTransactions
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_id INTEGER,
    points_amount DECIMAL(10,2) NOT NULL,
    transaction_type_id INTEGER NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_id) REFERENCES Customers(id),
    FOREIGN KEY (order_id) REFERENCES Orders(id),
    FOREIGN KEY (transaction_type_id) REFERENCES LoyaltyTransactionTypes(id)
);

CREATE TABLE IF NOT EXISTS Salaries
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    base_salary DECIMAL(10,2) NOT NULL,
    bonuses DECIMAL(10,2) DEFAULT 0,
    deductions DECIMAL(10,2) DEFAULT 0,
    total_paid DECIMAL(10,2) NOT NULL,
    total_hours INTEGER NOT NULL,
    payment_date DATE,
    is_paid BOOLEAN DEFAULT 0,
    financial_transaction_id INTEGER,
    
    FOREIGN KEY (employee_id) REFERENCES Employees(id),
    FOREIGN KEY (financial_transaction_id) REFERENCES FinancialTransactions(id)
);