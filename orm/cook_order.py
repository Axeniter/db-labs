from models import *
from database import get_session
from sqlalchemy import func, select, update, case
from utils import print_table
from datetime import datetime


def cook_order(session, employee_id: int):
    """Начать готовку первого заказа в статусе 'В ожидании'"""
    
    pending_status_id = session.execute(
        select(OrderStatus.id)
        .where(OrderStatus.name == 'В ожидании')
    ).scalar()
    
    cooking_status_id = session.execute(
        select(OrderStatus.id)
        .where(OrderStatus.name == 'Готовится')
    ).scalar()
    

    using_operation_id = session.execute(
        select(IngredientOperationType.id)
        .where(IngredientOperationType.name == 'Использование')
    ).scalar()
    
    order_id = session.execute(
        select(Order.id)
        .where(Order.status_id == pending_status_id)
        .order_by(Order.created_at)
        .limit(1)
    ).scalar()
    
    if not order_id:
        print("Нет заказов в статусе 'В ожидании'")
        return None
    
    session.execute(
        update(Order)
        .where(Order.id == order_id)
        .values(status_id=cooking_status_id)
    )
    
    ingredient_operation = IngredientOperation(
        employee_id=employee_id
    )
    session.add(ingredient_operation)
    session.flush()
    
    ingredients_to_deduct = session.execute(
        select(
            RecipeItem.ingredient_id,
            RecipeItem.unit_id,
            func.sum(RecipeItem.quantity * OrderItem.quantity).label('total_amount')
        )
        .join(OrderItem, OrderItem.menu_item_id == RecipeItem.menu_item_id)
        .where(OrderItem.order_id == order_id)
        .group_by(RecipeItem.ingredient_id, RecipeItem.unit_id)
    ).all()
    
    for ingredient_id, unit_id, amount in ingredients_to_deduct:
        operation_item = IngredientOperationItem(
            operation_id=ingredient_operation.id,
            ingredient_id=ingredient_id,
            operation_type_id=using_operation_id,
            unit_id=unit_id,
            amount=amount
        )
        session.add(operation_item)
    
    session.flush()
    
    for ingredient_id, unit_id, amount in ingredients_to_deduct:
        session.execute(
            update(IngredientInventory)
            .where(
                IngredientInventory.ingredient_id == ingredient_id,
                IngredientInventory.unit_id == unit_id
            )
            .values(quantity=IngredientInventory.quantity - amount)
        )
    
    session.commit()
    
    order_info = session.execute(
        select(
            Order.id.label("order_id"),
            OrderStatus.name.label("order_status"),
            func.strftime('%Y-%m-%d %H:%M:%S', Order.created_at).label("order_created"),
            func.strftime('%Y-%m-%d %H:%M:%S', datetime.now()).label("cooking_started"),
                case(
                    (Delivery.id.isnot(None), func.concat('Доставка: ', Delivery.address)),
                    (DineIn.id.isnot(None), func.concat('В зале: стол ', func.cast(Table.number, String))),
                    else_="Неизвестно"
                ).label("order_type"),
            func.concat(Customer.first_name, " ", Customer.last_name).label("customer"),
            Customer.phone.label("customer_phone")
        )
        .join(Order.status)
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
            func.group_concat(
                func.concat(
                    Ingredient.name, ': ',
                    func.printf('%.3f', RecipeItem.quantity * OrderItem.quantity), ' ',
                    Unit.name
                ), ', '
            ).label("ingredients_used")
        )
        .join(OrderItem.menu_item)
        .outerjoin(MenuItem.recipe_items)
        .outerjoin(RecipeItem.ingredient)
        .outerjoin(RecipeItem.unit)
        .where(OrderItem.order_id == order_id)
        .group_by(
            OrderItem.id, 
            MenuItem.name, 
            OrderItem.quantity, 
            OrderItem.item_cost
        )
        .order_by(MenuItem.name)
    ).mappings().all()
    
    inventory_info = session.execute(
        select(
            Ingredient.name.label("ingredient"),
            IngredientInventory.quantity.label("current_stock"),
            Unit.name.label("unit")
        )
        .join(IngredientInventory.ingredient)
        .join(IngredientInventory.unit)
        .where(
            IngredientInventory.ingredient_id.in_(
                select(RecipeItem.ingredient_id.distinct())
                .join(OrderItem, OrderItem.menu_item_id == RecipeItem.menu_item_id)
                .where(OrderItem.order_id == order_id)
            )
        )
        .order_by(IngredientInventory.quantity.asc())
    ).mappings().all()
    
    return {
        "order": order_info,
        "items": items_info,
        "inventory": inventory_info
    }


def main():
    """Тестирование запроса"""
    
    with get_session() as session:
        result = cook_order(session, employee_id=4)
        
        if result:
            print_table([result["order"]], "Информация о заказе")
            print_table(result["items"], "Состав заказа")
            print_table(result["inventory"], "Остатки ингредиентов после списания")
        else:
            print("Не удалось начать приготовление заказа")


if __name__ == "__main__":
    main()