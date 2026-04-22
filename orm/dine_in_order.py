from models import *
from database import get_session
from sqlalchemy import func, select
from decimal import Decimal
from utils import print_table
from typing import Optional, List, Dict


def create_order(
    session,
    customer_phone: str,
    items: List[Dict],
    order_type: str,                       # "dine_in" или "delivery"
    payment_type_id: int = 1,
    comment: Optional[str] = None,
    table_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    address: Optional[str] = None,
    courier_id: Optional[int] = None
):
    """Создание заказа (зал или доставка)"""
    
    customer_id = session.execute(
        select(Customer.id).where(Customer.phone == customer_phone)
    ).scalar()
    
    new_order = Order(
        customer_id=customer_id,
        status_id=1,
        payment_type_id=payment_type_id,
        total_cost=0,
        to_pay=0,
        comment=comment
    )
    
    session.add(new_order)
    session.flush()
    
    for item in items:
        price = session.execute(
            select(MenuItem.price).where(MenuItem.id == item["menu_item_id"])
        ).scalar()
        
        order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=item["menu_item_id"],
            item_cost=price,
            quantity=item["quantity"]
        )
        session.add(order_item)
    
    session.flush()
    
    total_cost = session.execute(
        select(func.sum(OrderItem.item_cost * OrderItem.quantity))
        .where(OrderItem.order_id == new_order.id)
    ).scalar() or 0
    
    discount_percent = session.execute(
        select(func.coalesce(LoyaltyTier.discount_percent, 0))
        .select_from(Customer)
        .join(Customer.last_achieved_tier)
        .where(Customer.id == customer_id)
    ).scalar() or 0
    
    to_pay = round(total_cost * (1 - discount_percent / Decimal('100')), 2)
    
    new_order.total_cost = total_cost
    new_order.to_pay = to_pay
    
    if order_type == "dine_in":
        if not table_id or not employee_id:
            return
        
        dine_in = DineIn(
            order_id=new_order.id,
            table_id=table_id,
            employee_id=employee_id,
            status_id=1
        )
        session.add(dine_in)
        
    elif order_type == "delivery":
        if not address or not courier_id:
            return
        
        delivery = Delivery(
            order_id=new_order.id,
            address=address,
            courier_id=courier_id,
            delivery_status_id=1
        )
        session.add(delivery)
        
    else:
        return
    
    session.commit()
    
    if order_type == "dine_in":
        order_info = session.execute(
            select(
                Order.id.label("order_id"),
                func.strftime('%Y-%m-%d %H:%M:%S', Order.created_at).label("created_at"),
                OrderStatus.name.label("status"),
                PaymentType.name.label("payment_type"),
                Table.number.label("table_number"),
                func.concat(Employee.first_name, " ", Employee.last_name).label("waiter"),
                Order.comment.label("comment"),
                Order.total_cost.label("total_cost"),
                Order.to_pay.label("to_pay"),
                func.concat(Customer.first_name, " ", Customer.last_name).label("customer"),
                Customer.phone.label("customer_phone")
            )
            .join(Order.status)
            .join(Order.payment_type)
            .join(Order.dine_in)
            .join(DineIn.table)
            .join(DineIn.employee)
            .outerjoin(Order.customer)
            .where(Order.id == new_order.id)
        ).mappings().first()
    else:
        order_info = session.execute(
            select(
                Order.id.label("order_id"),
                func.strftime('%Y-%m-%d %H:%M:%S', Order.created_at).label("created_at"),
                OrderStatus.name.label("status"),
                PaymentType.name.label("payment_type"),
                Delivery.address.label("delivery_address"),
                DeliveryStatus.name.label("delivery_status"),
                func.concat(Courier.first_name, " ", Courier.last_name).label("courier"),
                Order.comment.label("comment"),
                Order.total_cost.label("total_cost"),
                Order.to_pay.label("to_pay"),
                func.concat(Customer.first_name, " ", Customer.last_name).label("customer"),
                Customer.phone.label("customer_phone")
            )
            .join(Order.status)
            .join(Order.payment_type)
            .join(Order.delivery)
            .join(Delivery.delivery_status)
            .join(Delivery.courier)
            .outerjoin(Order.customer)
            .where(Order.id == new_order.id)
        ).mappings().first()
    
    items_info = session.execute(
        select(
            MenuItem.name.label("item"),
            OrderItem.quantity.label("quantity"),
            OrderItem.item_cost.label("price_per_item"),
            (OrderItem.quantity * OrderItem.item_cost).label("total_price")
        )
        .join(OrderItem.menu_item)
        .where(OrderItem.order_id == new_order.id)
    ).mappings().all()
    
    return {
        "order": order_info,
        "items": items_info
    }


def main():
    """Тестирование запроса"""
    
    with get_session() as session:
        items = [
            {"menu_item_id": 6, "quantity": 1},  # Пятиэтажный бургер
            {"menu_item_id": 4, "quantity": 1},  # Картофель три
            {"menu_item_id": 1, "quantity": 2},  # Кола
            {"menu_item_id": 7, "quantity": 1}   # Сырный торт
        ]
        
        result = create_order(
            session,
            customer_phone='+79161234567',
            items=items,
            order_type='dine_in',
            table_id=3,
            employee_id=7,
            comment='ам ам ам'
        )

        if result:
            print_table([result["order"]], "Заказ")
            print_table(result["items"], "Позиции заказа")
        else:
            print("Не получилось создать заказ")


if __name__ == "__main__":
    main()