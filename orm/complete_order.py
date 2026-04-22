from models import *
from database import get_session
from sqlalchemy import func, select, update, case
from utils import print_table
from datetime import datetime


def complete_order(session):
    """Завершить приготовление первого заказа в статусе 'Готовится'"""
    
    cooking_status_id = session.execute(
        select(OrderStatus.id)
        .where(OrderStatus.name == 'Готовится')
    ).scalar()
    
    ready_status_id = session.execute(
        select(OrderStatus.id)
        .where(OrderStatus.name == 'Готов')
    ).scalar()
    
    order_id = session.execute(
        select(Order.id)
        .where(Order.status_id == cooking_status_id)
        .order_by(Order.created_at)
        .limit(1)
    ).scalar()
    
    if not order_id:
        print("Нет заказов в статусе 'Готовится'")
        return None
    
    session.execute(
        update(Order)
        .where(Order.id == order_id)
        .values(status_id=ready_status_id)
    )
    
    session.execute(
        update(OrderItem)
        .where(OrderItem.order_id == order_id)
        .values(cooked_at=datetime.now())
    )
    
    delivery = session.execute(
        select(Delivery)
        .where(Delivery.order_id == order_id)
    ).scalar_one_or_none()
    
    dine_in = session.execute(
        select(DineIn)
        .where(DineIn.order_id == order_id)
    ).scalar_one_or_none()
    
    if delivery:
        picked_up_status_id = session.execute(
            select(DeliveryStatus.id)
            .where(DeliveryStatus.name == 'Забран')
        ).scalar()
        
        session.execute(
            update(Delivery)
            .where(Delivery.order_id == order_id)
            .values(delivery_status_id=picked_up_status_id)
        )
    
    if dine_in:
        served_status_id = session.execute(
            select(DineInStatus.id)
            .where(DineInStatus.name == 'Подано')
        ).scalar()
        
        session.execute(
            update(DineIn)
            .where(DineIn.order_id == order_id)
            .values(status_id=served_status_id)
        )
    
    session.commit()
    
    order_info = session.execute(
        select(
            Order.id.label("order_id"),
            OrderStatus.name.label("order_status"),
            func.strftime('%Y-%m-%d %H:%M:%S', Order.created_at).label("order_created"),
            func.strftime('%Y-%m-%d %H:%M:%S', 
                select(func.max(OrderItem.cooked_at))
                .where(OrderItem.order_id == order_id)
                .scalar_subquery()
            ).label("cooking_finished"),
            func.round(
                (func.julianday('now') - func.julianday(Order.created_at)) * 24 * 60
            ).label("total_minutes"),
            case(
                (Delivery.id.isnot(None), 'Доставка'),
                (DineIn.id.isnot(None), 'В зале'),
                else_='Неизвестно'
            ).label("order_type"),
            case(
                (Delivery.id.isnot(None), Delivery.address),
                (DineIn.id.isnot(None), 
                func.concat('Стол ', func.cast(Table.number, String), ' (', Table.location, ')')),
                else_='Неизвестно'
            ).label("destination"),
            func.concat(Customer.first_name, ' ', Customer.last_name).label("customer"),
            Customer.phone.label("customer_phone"),
            Order.total_cost.label("total_cost"),
            Order.to_pay.label("to_pay"),
            PaymentType.name.label("payment_type")
        )
        .join(Order.status)
        .join(Order.payment_type)
        .outerjoin(Order.delivery)
        .outerjoin(Order.dine_in)
        .outerjoin(DineIn.table)
        .outerjoin(Order.customer)
        .where(Order.id == order_id)
    ).mappings().first()
    
    items_info = session.execute(
        select(
            MenuItem.name.label("dish"),
            OrderItem.quantity.label("quantity"),
            OrderItem.item_cost.label("price"),
            (OrderItem.quantity * OrderItem.item_cost).label("total_price"),
            func.strftime('%Y-%m-%d %H:%M:%S', OrderItem.created_at).label("ordered_at"),
            func.strftime('%Y-%m-%d %H:%M:%S', OrderItem.cooked_at).label("cooked_at"),
            func.round(
                (func.julianday(OrderItem.cooked_at) - func.julianday(OrderItem.created_at)) * 24 * 60
            ).label("cooking_minutes")
        )
        .join(OrderItem.menu_item)
        .where(OrderItem.order_id == order_id)
        .order_by(OrderItem.created_at)
    ).mappings().all()
    
    courier_info = None
    if delivery:
        courier_info = session.execute(
            select(
                func.concat(Courier.first_name, ' ', Courier.last_name).label("courier"),
                Courier.phone.label("courier_phone"),
                CourierCompany.name.label("courier_company"),
                Delivery.address.label("delivery_address"),
                DeliveryStatus.name.label("delivery_status")
            )
            .join(Delivery.courier)
            .join(Courier.company)
            .join(Delivery.delivery_status)
            .where(Delivery.order_id == order_id)
        ).mappings().first()
    
    dine_in_info = None
    if dine_in:
        dine_in_info = session.execute(
            select(
                func.concat(Employee.first_name, ' ', Employee.last_name).label("waiter"),
                Table.number.label("table_number"),
                Table.location.label("table_location"),
                DineInStatus.name.label("dine_in_status")
            )
            .join(DineIn.employee)
            .join(DineIn.table)
            .join(DineIn.status)
            .where(DineIn.order_id == order_id)
        ).mappings().first()
    
    return {
        "order": order_info,
        "items": items_info,
        "courier": courier_info,
        "dine_in": dine_in_info
    }


def main():
    """Тестирование запроса"""
    
    with get_session() as session:
        result = complete_order(session)
        
        if result:
            print_table([result["order"]], "Информация о заказе")
            print_table(result["items"], "Состав заказа")
            
            if result["courier"]:
                print_table([result["courier"]], "Информация о доставке")
            
            if result["dine_in"]:
                print_table([result["dine_in"]], "Информация о заказе в зале")
        else:
            print("Не удалось завершить приготовление заказа")


if __name__ == "__main__":
    main()