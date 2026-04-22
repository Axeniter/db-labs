from models import *
from database import get_session
from sqlalchemy import func, select, update
from utils import print_table
from datetime import datetime
from decimal import Decimal


def close_order(session):
    """Закрыть первый заказ в статусе 'Готов'"""
    
    ready_status_id = session.execute(
        select(OrderStatus.id)
        .where(OrderStatus.name == 'Готов')
    ).scalar()
    
    completed_status_id = session.execute(
        select(OrderStatus.id)
        .where(OrderStatus.name == 'Завершён')
    ).scalar()
    
    order = session.execute(
        select(Order)
        .where(Order.status_id == ready_status_id)
        .order_by(Order.created_at)
        .limit(1)
    ).scalar_one_or_none()
    
    if not order:
        print("Нет заказов в статусе 'Готов'")
        return None
    
    delivery = session.execute(
        select(Delivery)
        .where(Delivery.order_id == order.id)
    ).scalar_one_or_none()
    
    if delivery:
        delivered_status_id = session.execute(
            select(DeliveryStatus.id)
            .where(DeliveryStatus.name == 'Доставлен')
        ).scalar()
        
        session.execute(
            update(Delivery)
            .where(Delivery.order_id == order.id)
            .values(delivery_status_id=delivered_status_id)
        )
    
    income_type_id = session.execute(
        select(FinancialTransactionType.id)
        .where(FinancialTransactionType.name == 'Доход')
    ).scalar()
    
    sales_category_id = session.execute(
        select(FinancialTransactionCategory.id)
        .where(FinancialTransactionCategory.name == 'Продажи')
    ).scalar()
    
    financial_transaction = FinancialTransaction(
        transaction_type_id=income_type_id,
        amount=order.to_pay,
        description=f'Оплата заказа {order.id}',
        category_id=sales_category_id
    )
    session.add(financial_transaction)
    session.flush()
    
    session.execute(
        update(Order)
        .where(Order.id == order.id)
        .values(
            status_id=completed_status_id,
            closed_at=datetime.now(),
            financial_transaction_id=financial_transaction.id
        )
    )
    
    if order.customer_id:
        session.execute(
            update(Customer)
            .where(Customer.id == order.customer_id)
            .values(
                total_spent=Customer.total_spent + order.total_cost,
                total_orders=Customer.total_orders + 1
            )
        )
        
        new_tier = session.execute(
            select(LoyaltyTier.id)
            .where(LoyaltyTier.min_spent <= select(Customer.total_spent).where(Customer.id == order.customer_id).scalar_subquery())
            .order_by(LoyaltyTier.min_spent.desc())
            .limit(1)
        ).scalar()
        
        if new_tier:
            session.execute(
                update(Customer)
                .where(Customer.id == order.customer_id)
                .values(last_achieved_tier_id=new_tier)
            )
        
        customer = session.execute(
            select(Customer)
            .where(Customer.id == order.customer_id)
        ).scalar_one()
        
        accrual_type_id = session.execute(
            select(LoyaltyTransactionType.id)
            .where(LoyaltyTransactionType.name == 'Начисление')
        ).scalar()
        
        if customer.last_achieved_tier:
            cashback_amount = round(order.total_cost * customer.last_achieved_tier.cashback_percent / Decimal('100'), 2)
            
            loyalty_transaction = LoyaltyTransaction(
                customer_id=order.customer_id,
                order_id=order.id,
                points_amount=cashback_amount,
                transaction_type_id=accrual_type_id,
                description=f"{customer.last_achieved_tier.cashback_percent}% кешбэк с заказа на {order.total_cost} рублей (уровень {customer.last_achieved_tier.name})",
                created_at=datetime.now()
            )
            session.add(loyalty_transaction)
    
    session.commit()
    
    order_info = session.execute(
        select(
            Order.id.label("order_id"),
            OrderStatus.name.label("order_status"),
            func.strftime('%Y-%m-%d %H:%M:%S', Order.created_at).label("order_created"),
            func.strftime('%Y-%m-%d %H:%M:%S', Order.closed_at).label("closed_at"),
            func.round(
                (func.julianday(Order.closed_at) - func.julianday(Order.created_at)) * 24 * 60
            ).label("total_minutes"),
            Order.total_cost.label("total_cost"),
            Order.to_pay.label("paid_amount"),
            PaymentType.name.label("payment_type"),
            FinancialTransaction.amount.label("financial_amount"),
            FinancialTransactionType.name.label("financial_type"),
            FinancialTransactionCategory.name.label("financial_category"),
            FinancialTransaction.id.label("financial_transaction_id")
        )
        .select_from(Order)
        .join(Order.status)
        .join(Order.payment_type)
        .join(Order.financial_transaction)
        .join(FinancialTransaction.transaction_type)
        .join(FinancialTransaction.category)
        .where(Order.id == order.id)
    ).mappings().first()
    
    items_info = session.execute(
        select(
            MenuItem.name.label("dish"),
            OrderItem.quantity.label("quantity"),
            OrderItem.item_cost.label("price"),
            (OrderItem.quantity * OrderItem.item_cost).label("total_price")
        )
        .select_from(OrderItem)
        .join(OrderItem.menu_item)
        .where(OrderItem.order_id == order.id)
        .order_by(OrderItem.created_at)
    ).mappings().all()
    
    customer_info = None
    if order.customer_id:
        accrual_type_id = session.execute(
            select(LoyaltyTransactionType.id)
            .where(LoyaltyTransactionType.name == 'Начисление')
        ).scalar()
        
        customer_info = session.execute(
            select(
                func.concat(Customer.first_name, ' ', Customer.last_name).label("customer"),
                Customer.phone.label("customer_phone"),
                Customer.total_spent.label("total_spent_all_time"),
                Customer.total_orders.label("total_orders_all_time"),
                LoyaltyTier.name.label("current_loyalty_tier"),
                LoyaltyTier.discount_percent.label("discount_percent"),
                LoyaltyTier.cashback_percent.label("cashback_percent"),
                LoyaltyTransaction.points_amount.label("earned_cashback"),
                LoyaltyTransaction.description.label("cashback_description")
            )
            .select_from(Order)
            .join(Order.customer)
            .join(Customer.last_achieved_tier)
            .join(Order.loyalty_transactions)
            .where(
                Order.id == order.id,
                LoyaltyTransaction.transaction_type_id == accrual_type_id
            )
        ).mappings().first()
    
    delivery_info = None
    if delivery:
        delivery_info = session.execute(
            select(
                DeliveryStatus.name.label("delivery_status"),
                Delivery.address.label("delivery_address"),
                func.concat(Courier.first_name, ' ', Courier.last_name).label("courier")
            )
            .select_from(Delivery)
            .join(Delivery.delivery_status)
            .join(Delivery.courier)
            .where(Delivery.order_id == order.id)
        ).mappings().first()
    
    return {
        "order": order_info,
        "items": items_info,
        "customer": customer_info,
        "delivery": delivery_info
    }


def main():
    """Тестирование запроса"""
    
    with get_session() as session:
        result = close_order(session)
        
        if result:
            print_table([result["order"]], "Информация о заказе")
            print_table(result["items"], "Состав заказа")
            
            if result["customer"]:
                print_table([result["customer"]], "Информация о клиенте и бонусах")
            
            if result["delivery"]:
                print_table([result["delivery"]], "Информация о доставке")
        else:
            print("Не удалось закрыть заказ")


if __name__ == "__main__":
    main()