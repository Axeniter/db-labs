from models import *
from database import get_session
from sqlalchemy import func, case, String, select, and_, desc
from sqlalchemy.orm import aliased
from datetime import datetime, date
from utils import print_table


def get_revenue_for_period(session, start_date: date, end_date: date):
    """Выручка за период"""
    
    daily_stats = (
        select(
            func.date(FinancialTransaction.transaction_date).label("day"),
            func.sum(
                case(
                    (FinancialTransactionType.name == "Доход", FinancialTransaction.amount),
                    else_=0
                )
            ).label("revenue"),
            func.sum(
                case(
                    (FinancialTransactionType.name == "Расход", FinancialTransaction.amount),
                    else_=0
                )
            ).label("expense")
        )
        .join(FinancialTransaction.transaction_type)
        .where(FinancialTransaction.transaction_date.between(start_date, end_date))
        .group_by(func.date(FinancialTransaction.transaction_date))
        .subquery()
    )
    
    daily_results = (
        select(
            daily_stats.c.day,
            daily_stats.c.revenue,
            daily_stats.c.expense,
            func.round(daily_stats.c.revenue - daily_stats.c.expense, 2).label("profit")
        )
        .order_by(daily_stats.c.day)
    )
    
    result = session.execute(daily_results).mappings().all()
    
    total_revenue = sum(r["revenue"] or 0 for r in result)
    total_expense = sum(r["expense"] or 0 for r in result)
    
    result.append({
        "day": "Всего за период",
        "revenue": total_revenue,
        "expense": total_expense,
        "profit": total_revenue - total_expense
    })
    
    return result


def get_popular_dishes(session, start_date: date, end_date: date):
    """Популярные блюда за период"""
    
    cancelled_status = (
        select(OrderStatus.id)
        .where(OrderStatus.name == "Отменён")
        .scalar_subquery()
    )
    
    result = (
        select(
            MenuItem.name.label("dish_name"),
            func.sum(OrderItem.quantity).label("total_quantity"),
            func.count(func.distinct(OrderItem.order_id)).label("orders_count"),
            func.round(
                func.sum(OrderItem.item_cost * OrderItem.quantity),
                2
            ).label("total_revenue")
        )
        .join(OrderItem.menu_item)
        .join(OrderItem.order)
        .where(Order.created_at.between(start_date, end_date))
        .where(Order.status_id != cancelled_status)
        .group_by(MenuItem.id, MenuItem.name)
        .order_by(desc("total_quantity"))
    )
    
    return session.execute(result).mappings().all()


def get_available_portions(session):
    """Сколько блюд можно приготовить из ингредиентов на складе"""
    
    result = (
        select(
            MenuItem.name.label("dish"),
            func.floor(
                func.min(IngredientInventory.quantity / RecipeItem.quantity)
            ).label("count_of_portions")
        )
        .join(RecipeItem.menu_item)
        .join(RecipeItem.ingredient)
        .join(Ingredient.inventory)
        .where(MenuItem.is_available == True)
        .where(RecipeItem.quantity > 0)
        .where(IngredientInventory.quantity > 0)
        .group_by(MenuItem.id, MenuItem.name)
        .order_by("count_of_portions")
    )
    
    return session.execute(result).mappings().all()


def get_dishes_bought_together(session):
    """Блюда, которые часто заказывают вместе"""
    
    oi1 = aliased(OrderItem)
    oi2 = aliased(OrderItem)
    mi1 = aliased(MenuItem)
    mi2 = aliased(MenuItem)
    
    result = (
        select(
            mi1.name.label("dish_1"),
            mi2.name.label("dish_2"),
            func.count(func.distinct(oi1.order_id)).label("count_of_joint_orders")
        )
        .select_from(oi1)
        .join(oi2, and_(
            oi1.order_id == oi2.order_id,
            oi1.menu_item_id < oi2.menu_item_id
        ))
        .join(mi1, oi1.menu_item)
        .join(mi2, oi2.menu_item)
        .group_by(mi1.id, mi2.id, mi1.name, mi2.name)
        .having(func.count(func.distinct(oi1.order_id)) >= 1)
        .order_by(desc("count_of_joint_orders"))
    )
    
    return session.execute(result).mappings().all()


def get_free_tables(session, target_datetime: datetime = None):
    """Свободные столы на указанный момент времени"""
    
    if target_datetime is None:
        target_datetime = datetime.now()
    
    target_date = target_datetime.date()
    target_time = target_datetime.time()
    
    active_reservations = (
        select(TableReservation.table_id)
        .where(TableReservation.reservation_date == target_date)
        .where(TableReservation.reservation_time <= target_time)
        .where(
            func.datetime(
                func.concat(TableReservation.reservation_date, " ", TableReservation.reservation_time),
                "+" + func.cast(TableReservation.duration_minutes, String) + " minutes"
            ) > target_datetime
        )
    )
    
    active_dine_ins = (
        select(DineIn.table_id)
        .join(DineIn.order)
        .where(func.date(Order.created_at) == target_date)
        .where(Order.created_at <= target_datetime)
        .where(Order.status_id.notin_([5, 6]))
        .where(Order.closed_at.is_(None))
    )
    
    result = (
        select(
            Table.number.label("number"),
            Table.capacity.label("capacity"),
            Table.location.label("location")
        )
        .where(Table.is_available == True)
        .where(Table.id.notin_(active_reservations))
        .where(Table.id.notin_(active_dine_ins))
        .order_by(Table.number)
    )
    
    return session.execute(result).mappings().all()


def get_weekly_statistics(session):
    """Статистика по дням недели"""
    
    daily_stats = (
        select(
            func.date(Order.created_at).label("date"),
            func.strftime("%w", Order.created_at).label("day_number"),
            func.count().label("orders_per_day"),
            func.sum(Order.to_pay).label("revenue_per_day"),
            func.avg(Order.to_pay).label("average_check_per_day")
        )
        .group_by(func.date(Order.created_at))
        .subquery()
    )
    
    result = (
        select(
            case(
                (daily_stats.c.day_number == "0", "Воскресенье"),
                (daily_stats.c.day_number == "1", "Понедельник"),
                (daily_stats.c.day_number == "2", "Вторник"),
                (daily_stats.c.day_number == "3", "Среда"),
                (daily_stats.c.day_number == "4", "Четверг"),
                (daily_stats.c.day_number == "5", "Пятница"),
                (daily_stats.c.day_number == "6", "Суббота")
            ).label("week_day"),
            func.avg(daily_stats.c.orders_per_day).label("average_orders"),
            func.avg(daily_stats.c.revenue_per_day).label("average_revenue"),
            func.avg(daily_stats.c.average_check_per_day).label("average_check")
        )
        .group_by(daily_stats.c.day_number)
        .order_by(daily_stats.c.day_number)
    )
    
    return session.execute(result).mappings().all()


def get_delivered_ingredients(session, start_date: date, end_date: date):
    """Ингредиенты, прибывшие на склад за определенный период"""
    
    delivered_status = (
        select(SupplyStatus.id)
        .where(SupplyStatus.name == "Доставлено")
        .scalar_subquery()
    )
    
    result = (
        select(
            Ingredient.name.label("ingredient"),
            func.sum(SupplierOrderItem.quantity).label("quantity_of_delivered"),
            Unit.name.label("unit"),
            func.count(func.distinct(SupplierOrderItem.supplier_order_id)).label("count_of_supplies"),
            func.round(func.sum(SupplierOrderItem.total_cost), 2).label("money_spent")
        )
        .join(SupplierOrderItem.ingredient)
        .join(SupplierOrderItem.unit)
        .join(SupplierOrderItem.supplier_order)
        .where(SupplierOrder.delivery_date.between(start_date, end_date))
        .where(SupplierOrder.status_id == delivered_status)
        .group_by(Ingredient.id, Ingredient.name, Unit.name)
        .order_by(desc("quantity_of_delivered"))
    )
    
    return session.execute(result).mappings().all()


def main():
    """Тестирования запросов"""
    
    with get_session() as session:
        start_date = date(2026, 4, 1)
        end_date = date(2026, 4, 30)
        
        result = get_revenue_for_period(session, start_date, end_date)
        print_table(result, "Выручка за апрель 2026")
        
        result = get_popular_dishes(session, start_date, end_date)
        print_table(result, "Популярные блюда за апрель 2026")
        
        result = get_available_portions(session)
        print_table(result, "Сколько блюд можно приготовить из ингредиентов на складе")
        
        result = get_dishes_bought_together(session)
        print_table(result, "Блюда, которые часто заказывают вместе")
        
        result = get_free_tables(session)
        print_table(result, "Свободные столы на текущий момент")

        result = get_weekly_statistics(session)
        print_table(result, "Статистика по дням недели")
        
        result = get_delivered_ingredients(session, start_date, end_date)
        print_table(result, "Ингредиенты, прибывшие на склад за апрель 2026")


if __name__ == "__main__":
    main()