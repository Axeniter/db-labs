from sqlalchemy import (Column, Integer, String, Boolean, 
    DateTime, Date, Time, Text, ForeignKey, DECIMAL, UniqueConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Role(Base):
    __tablename__ = 'Roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, unique=True)
    hourly_rate = Column(DECIMAL(10, 2))
    
    employees = relationship('Employee', back_populates='role')


class MenuCategory(Base):
    __tablename__ = 'MenuCategories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    
    menu_items = relationship('MenuItem', back_populates='category')


class OrderStatus(Base):
    __tablename__ = 'OrderStatuses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)
    
    orders = relationship('Order', back_populates='status')


class DineInStatus(Base):
    __tablename__ = 'DineInStatuses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)
    
    dine_ins = relationship('DineIn', back_populates='status')


class Shift(Base):
    __tablename__ = 'Shifts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, unique=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    schedules = relationship('EmployeeSchedule', back_populates='shift')


class SupplyStatus(Base):
    __tablename__ = 'SupplyStatuses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)
    
    supplier_orders = relationship('SupplierOrder', back_populates='status')


class DeliveryStatus(Base):
    __tablename__ = 'DeliveryStatuses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)
    
    deliveries = relationship('Delivery', back_populates='delivery_status')


class PaymentType(Base):
    __tablename__ = 'PaymentTypes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    
    orders = relationship('Order', back_populates='payment_type')


class LoyaltyTransactionType(Base):
    __tablename__ = 'LoyaltyTransactionTypes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)
    
    transactions = relationship('LoyaltyTransaction', back_populates='transaction_type')


class Unit(Base):
    __tablename__ = 'Units'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(10), nullable=False, unique=True)
    
    inventory = relationship('IngredientInventory', back_populates='unit')
    recipe_items = relationship('RecipeItem', back_populates='unit')
    supplier_prices = relationship('SupplierPrice', back_populates='unit')
    supplier_order_items = relationship('SupplierOrderItem', back_populates='unit')
    operation_items = relationship('IngredientOperationItem', back_populates='unit')


class IngredientOperationType(Base):
    __tablename__ = 'IngredientOperationTypes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)
    
    operation_items = relationship('IngredientOperationItem', back_populates='operation_type')


class FinancialTransactionType(Base):
    __tablename__ = 'FinancialTransactionTypes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)
    
    transactions = relationship('FinancialTransaction', back_populates='transaction_type')


class FinancialTransactionCategory(Base):
    __tablename__ = 'FinancialTransactionsCategories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, unique=True)
    
    transactions = relationship('FinancialTransaction', back_populates='category')


class LoyaltyTier(Base):
    __tablename__ = 'LoyaltyTiers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, unique=True)
    min_spent = Column(DECIMAL(10, 2), nullable=False)
    discount_percent = Column(DECIMAL(5, 2), default=0)
    cashback_percent = Column(DECIMAL(5, 2), default=0)
    
    customers = relationship('Customer', back_populates='last_achieved_tier')


class FinancialTransaction(Base):
    __tablename__ = 'FinancialTransactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_type_id = Column(Integer, ForeignKey('FinancialTransactionTypes.id'), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    transaction_date = Column(DateTime, default=datetime.now)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('FinancialTransactionsCategories.id'))
    
    transaction_type = relationship('FinancialTransactionType', back_populates='transactions')
    category = relationship('FinancialTransactionCategory', back_populates='transactions')
    orders = relationship('Order', back_populates='financial_transaction')
    supplier_orders = relationship('SupplierOrder', back_populates='financial_transaction')
    salaries = relationship('Salary', back_populates='financial_transaction')


class Employee(Base):
    __tablename__ = 'Employees'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('Roles.id'), nullable=False)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    phone = Column(String(20), unique=True)
    email = Column(String(255), unique=True)
    hire_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    
    role = relationship('Role', back_populates='employees')
    dine_ins = relationship('DineIn', back_populates='employee')
    supplier_orders = relationship('SupplierOrder', back_populates='employee')
    ingredient_operations = relationship('IngredientOperation', back_populates='employee')
    schedules = relationship('EmployeeSchedule', back_populates='employee')
    time_trackers = relationship('TimeTracker', back_populates='employee')
    salaries = relationship('Salary', back_populates='employee')
    table_reservations = relationship('TableReservation', back_populates='created_by_employee')


class MenuItem(Base):
    __tablename__ = 'MenuItems'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('MenuCategories.id'), nullable=False)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    calories = Column(Integer)
    is_available = Column(Boolean, default=True)
    
    category = relationship('MenuCategory', back_populates='menu_items')
    recipe_items = relationship('RecipeItem', back_populates='menu_item')
    order_items = relationship('OrderItem', back_populates='menu_item')


class Ingredient(Base):
    __tablename__ = 'Ingredients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, unique=True)
    
    inventory = relationship('IngredientInventory', back_populates='ingredient', uselist=False)
    recipe_items = relationship('RecipeItem', back_populates='ingredient')
    supplier_prices = relationship('SupplierPrice', back_populates='ingredient')
    supplier_order_items = relationship('SupplierOrderItem', back_populates='ingredient')
    operation_items = relationship('IngredientOperationItem', back_populates='ingredient')


class IngredientInventory(Base):
    __tablename__ = 'IngredientInventory'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ingredient_id = Column(Integer, ForeignKey('Ingredients.id'), nullable=False, unique=True)
    unit_id = Column(Integer, ForeignKey('Units.id'), nullable=False)
    quantity = Column(DECIMAL(10, 3), default=0)
    
    ingredient = relationship('Ingredient', back_populates='inventory')
    unit = relationship('Unit', back_populates='inventory')


class RecipeItem(Base):
    __tablename__ = 'RecipeItems'
    __table_args__ = (UniqueConstraint('menu_item_id', 'ingredient_id'),)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_item_id = Column(Integer, ForeignKey('MenuItems.id'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('Ingredients.id'), nullable=False)
    unit_id = Column(Integer, ForeignKey('Units.id'), nullable=False)
    quantity = Column(DECIMAL(10, 3), nullable=False)
    
    menu_item = relationship('MenuItem', back_populates='recipe_items')
    ingredient = relationship('Ingredient', back_populates='recipe_items')
    unit = relationship('Unit', back_populates='recipe_items')


class Table(Base):
    __tablename__ = 'Tables'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Integer, nullable=False, unique=True)
    capacity = Column(Integer, nullable=False)
    location = Column(String(30))
    is_available = Column(Boolean, default=True)
    
    dine_ins = relationship('DineIn', back_populates='table')
    reservations = relationship('TableReservation', back_populates='table')


class TableReservation(Base):
    __tablename__ = 'TableReservations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey('Tables.id'), nullable=False)
    customer_phone = Column(String(20))
    reservation_date = Column(Date, nullable=False)
    reservation_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, default=120)
    created_by_employee_id = Column(Integer, ForeignKey('Employees.id'), nullable=False)
    
    table = relationship('Table', back_populates='reservations')
    created_by_employee = relationship('Employee', back_populates='table_reservations')


class Customer(Base):
    __tablename__ = 'Customers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(20), nullable=False, unique=True)
    first_name = Column(String(30))
    last_name = Column(String(30))
    email = Column(String(255))
    birth_date = Column(Date)
    registration_date = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    total_spent = Column(DECIMAL(10, 2), default=0)
    total_orders = Column(Integer, default=0)
    last_achieved_tier_id = Column(Integer, ForeignKey('LoyaltyTiers.id'))
    
    last_achieved_tier = relationship('LoyaltyTier', back_populates='customers')
    orders = relationship('Order', back_populates='customer')
    loyalty_transactions = relationship('LoyaltyTransaction', back_populates='customer')


class Order(Base):
    __tablename__ = 'Orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('Customers.id'))
    status_id = Column(Integer, ForeignKey('OrderStatuses.id'), nullable=False)
    payment_type_id = Column(Integer, ForeignKey('PaymentTypes.id'), nullable=False)
    total_cost = Column(DECIMAL(10, 2), default=0)
    to_pay = Column(DECIMAL(10, 2), default=0)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    closed_at = Column(DateTime)
    financial_transaction_id = Column(Integer, ForeignKey('FinancialTransactions.id'))
    
    customer = relationship('Customer', back_populates='orders')
    status = relationship('OrderStatus', back_populates='orders')
    payment_type = relationship('PaymentType', back_populates='orders')
    financial_transaction = relationship('FinancialTransaction', back_populates='orders')
    delivery = relationship('Delivery', back_populates='order', uselist=False)
    dine_in = relationship('DineIn', back_populates='order', uselist=False)
    order_items = relationship('OrderItem', back_populates='order')
    loyalty_transactions = relationship('LoyaltyTransaction', back_populates='order')


class CourierCompany(Base):
    __tablename__ = 'CourierCompanies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    
    couriers = relationship('Courier', back_populates='company')


class Courier(Base):
    __tablename__ = 'Couriers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    phone = Column(String(20), unique=True)
    is_free = Column(Boolean, default=True)
    company_id = Column(Integer, ForeignKey('CourierCompanies.id'))
    
    company = relationship('CourierCompany', back_populates='couriers')
    deliveries = relationship('Delivery', back_populates='courier')


class Delivery(Base):
    __tablename__ = 'Deliveries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('Orders.id'), nullable=False)
    address = Column(String(200), nullable=False)
    courier_id = Column(Integer, ForeignKey('Couriers.id'), nullable=False)
    delivery_status_id = Column(Integer, ForeignKey('DeliveryStatuses.id'), nullable=False)
    
    order = relationship('Order', back_populates='delivery')
    courier = relationship('Courier', back_populates='deliveries')
    delivery_status = relationship('DeliveryStatus', back_populates='deliveries')


class DineIn(Base):
    __tablename__ = 'DineIns'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('Orders.id'), nullable=False)
    table_id = Column(Integer, ForeignKey('Tables.id'), nullable=False)
    employee_id = Column(Integer, ForeignKey('Employees.id'), nullable=False)
    status_id = Column(Integer, ForeignKey('DineInStatuses.id'), nullable=False)
    
    order = relationship('Order', back_populates='dine_in')
    table = relationship('Table', back_populates='dine_ins')
    employee = relationship('Employee', back_populates='dine_ins')
    status = relationship('DineInStatus', back_populates='dine_ins')


class OrderItem(Base):
    __tablename__ = 'OrderItems'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('Orders.id'), nullable=False)
    menu_item_id = Column(Integer, ForeignKey('MenuItems.id'), nullable=False)
    item_cost = Column(DECIMAL(10, 2), default=0)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    cooked_at = Column(DateTime)
    
    order = relationship('Order', back_populates='order_items')
    menu_item = relationship('MenuItem', back_populates='order_items')


class Supplier(Base):
    __tablename__ = 'Suppliers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(String(100))
    is_active = Column(Boolean, default=True)
    
    prices = relationship('SupplierPrice', back_populates='supplier')
    orders = relationship('SupplierOrder', back_populates='supplier')


class SupplierPrice(Base):
    __tablename__ = 'SupplierPrices'
    __table_args__ = (UniqueConstraint('supplier_id', 'ingredient_id'),)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey('Suppliers.id'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('Ingredients.id'), nullable=False)
    unit_id = Column(Integer, ForeignKey('Units.id'), nullable=False)
    price_per_unit = Column(DECIMAL(10, 2), nullable=False)
    
    supplier = relationship('Supplier', back_populates='prices')
    ingredient = relationship('Ingredient', back_populates='supplier_prices')
    unit = relationship('Unit', back_populates='supplier_prices')


class SupplierOrder(Base):
    __tablename__ = 'SupplierOrders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey('Suppliers.id'), nullable=False)
    employee_id = Column(Integer, ForeignKey('Employees.id'), nullable=False)
    order_date = Column(DateTime, default=datetime.now)
    delivery_date = Column(DateTime)
    status_id = Column(Integer, ForeignKey('SupplyStatuses.id'), nullable=False)
    total_cost = Column(DECIMAL(10, 2), default=0)
    financial_transaction_id = Column(Integer, ForeignKey('FinancialTransactions.id'))
    
    supplier = relationship('Supplier', back_populates='orders')
    employee = relationship('Employee', back_populates='supplier_orders')
    status = relationship('SupplyStatus', back_populates='supplier_orders')
    financial_transaction = relationship('FinancialTransaction', back_populates='supplier_orders')
    order_items = relationship('SupplierOrderItem', back_populates='supplier_order')


class SupplierOrderItem(Base):
    __tablename__ = 'SupplierOrderItems'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_order_id = Column(Integer, ForeignKey('SupplierOrders.id'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('Ingredients.id'), nullable=False)
    unit_id = Column(Integer, ForeignKey('Units.id'), nullable=False)
    quantity = Column(DECIMAL(10, 3), nullable=False)
    price_per_unit = Column(DECIMAL(10, 2), nullable=False)
    total_cost = Column(DECIMAL(10, 2), nullable=False)
    
    supplier_order = relationship('SupplierOrder', back_populates='order_items')
    ingredient = relationship('Ingredient', back_populates='supplier_order_items')
    unit = relationship('Unit', back_populates='supplier_order_items')


class IngredientOperation(Base):
    __tablename__ = 'IngredientOperations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('Employees.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    employee = relationship('Employee', back_populates='ingredient_operations')
    operation_items = relationship('IngredientOperationItem', back_populates='operation')


class IngredientOperationItem(Base):
    __tablename__ = 'IngredientOperationItems'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    operation_id = Column(Integer, ForeignKey('IngredientOperations.id'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('Ingredients.id'), nullable=False)
    operation_type_id = Column(Integer, ForeignKey('IngredientOperationTypes.id'), nullable=False)
    unit_id = Column(Integer, ForeignKey('Units.id'), nullable=False)
    amount = Column(DECIMAL(10, 3), default=0)
    
    operation = relationship('IngredientOperation', back_populates='operation_items')
    ingredient = relationship('Ingredient', back_populates='operation_items')
    operation_type = relationship('IngredientOperationType', back_populates='operation_items')
    unit = relationship('Unit', back_populates='operation_items')


class EmployeeSchedule(Base):
    __tablename__ = 'EmployeeSchedules'
    __table_args__ = (UniqueConstraint('employee_id', 'work_date'),)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('Employees.id'), nullable=False)
    shift_id = Column(Integer, ForeignKey('Shifts.id'), nullable=False)
    work_date = Column(Date, nullable=False)
    is_working = Column(Boolean, default=True)
    
    employee = relationship('Employee', back_populates='schedules')
    shift = relationship('Shift', back_populates='schedules')


class TimeTracker(Base):
    __tablename__ = 'TimeTrackers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('Employees.id'), nullable=False)
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime)
    
    employee = relationship('Employee', back_populates='time_trackers')


class LoyaltyTransaction(Base):
    __tablename__ = 'LoyaltyTransactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('Customers.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('Orders.id'))
    points_amount = Column(DECIMAL(10, 2), nullable=False)
    transaction_type_id = Column(Integer, ForeignKey('LoyaltyTransactionTypes.id'), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    customer = relationship('Customer', back_populates='loyalty_transactions')
    order = relationship('Order', back_populates='loyalty_transactions')
    transaction_type = relationship('LoyaltyTransactionType', back_populates='transactions')


class Salary(Base):
    __tablename__ = 'Salaries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('Employees.id'), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    base_salary = Column(DECIMAL(10, 2), nullable=False)
    bonuses = Column(DECIMAL(10, 2), default=0)
    deductions = Column(DECIMAL(10, 2), default=0)
    total_paid = Column(DECIMAL(10, 2), nullable=False)
    total_hours = Column(Integer, nullable=False)
    payment_date = Column(Date)
    is_paid = Column(Boolean, default=False)
    financial_transaction_id = Column(Integer, ForeignKey('FinancialTransactions.id'))
    
    employee = relationship('Employee', back_populates='salaries')
    financial_transaction = relationship('FinancialTransaction', back_populates='salaries')