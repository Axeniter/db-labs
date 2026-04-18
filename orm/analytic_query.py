from models import *
from database import get_session
from sqlalchemy import func, case, String, select, and_
from sqlalchemy.orm import aliased
from datetime import datetime, date


def get_revenue_for_period(session, start_date: date, end_date: date):
    """Выручка за период"""
    
    daily_stats = session.query(
        func.strftime('%Y-%m-%d', FinancialTransaction.transaction_date).label('day'),
        func.sum(
            case(
                (FinancialTransactionType.name == 'Доход', FinancialTransaction.amount),
                else_=0
            )
        ).label('revenue'),
        func.sum(
            case(
                (FinancialTransactionType.name == 'Расход', FinancialTransaction.amount),
                else_=0
            )
        ).label('expense')
    ).join(
        FinancialTransaction.transaction_type
    ).filter(
        FinancialTransaction.transaction_date.between(start_date, end_date)
    ).group_by(
        func.strftime('%Y-%m-%d', FinancialTransaction.transaction_date)
    ).cte('daily_stats')
    
    daily_results = session.query(
        daily_stats.c.day.label('day'),
        daily_stats.c.revenue.label('revenue'),
        daily_stats.c.expense.label('expense'),
        (daily_stats.c.revenue - daily_stats.c.expense).label('profit')
    ).all()
    
    totals = session.query(
        func.sum(daily_stats.c.revenue).label('total_revenue'),
        func.sum(daily_stats.c.expense).label('total_expense'),
        (func.sum(daily_stats.c.revenue) - func.sum(daily_stats.c.expense)).label('total_profit')
    ).first()
    
    return {
        'daily': [
            {
                'day': row.day,
                'revenue': row.revenue,
                'expense': row.expense,
                'profit': row.profit
            }
            for row in daily_results
        ],
        'total': {
            'revenue': float(totals.total_revenue or 0),
            'expense': float(totals.total_expense or 0),
            'profit': float(totals.total_profit or 0)
        }
    }


def get_popular_dishes(session, start_date: date, end_date: date):
    """Популярные блюда за период"""
    
    cancelled_status = session.query(OrderStatus).filter(
        OrderStatus.name == 'Отменён'
    ).first()
    
    results = session.query(
        MenuItem.name.label('dish_name'),
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.count(func.distinct(OrderItem.order_id)).label('orders_count'),
        func.sum(OrderItem.item_cost * OrderItem.quantity).label('total_revenue')
    ).join(
        OrderItem.menu_item
    ).join(
        OrderItem.order
    ).filter(
        Order.created_at.between(start_date, end_date),
        Order.status != cancelled_status
    ).group_by(
        MenuItem.id, MenuItem.name
    ).order_by(
        func.sum(OrderItem.quantity).desc()
    ).all()
    
    return [
        {
            'dish_name': row.dish_name,
            'total_quantity': row.total_quantity,
            'orders_count': row.orders_count,
            'total_revenue': row.total_revenue
        }
        for row in results
    ]


def get_available_portions(session):
    """Сколько блюд можно приготовить из ингредиентов на складе"""
    
    results = session.query(
        MenuItem.name.label('dish'),
        func.floor(
            func.min(IngredientInventory.quantity / RecipeItem.quantity)
        ).label('count_of_portions')
    ).join(
        MenuItem.recipe_items
    ).join(
        RecipeItem.ingredient
    ).join(
        Ingredient.inventory
    ).filter(
        MenuItem.is_available == True,
        IngredientInventory.quantity > 0
    ).group_by(
        MenuItem.id, MenuItem.name
    ).order_by(
        func.floor(func.min(IngredientInventory.quantity / RecipeItem.quantity))
    ).all()
    
    return [
        {
            'dish': row.dish,
            'count_of_portions': row.count_of_portions
        }
        for row in results
    ]


