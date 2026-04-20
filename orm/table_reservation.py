from models import *
from database import get_session
from sqlalchemy import func, select, and_
from datetime import date, time
from utils import print_table


def create_table_reservation(
    session,
    table_id: int,
    customer_phone: str,
    reservation_date: date,
    reservation_time: time,
    duration_minutes: int,
    created_by_employee_id: int
):
    """Бронирование стола"""
    
    end_time = func.time(
        func.datetime(
            func.concat(reservation_date, " ", reservation_time),
            f"+{duration_minutes} minutes"
        )
    )
    
    conflict_exists = (
        select(TableReservation.id)
        .where(TableReservation.table_id == table_id)
        .where(TableReservation.reservation_date == reservation_date)
        .where(
            and_(
                TableReservation.reservation_time < end_time,
                func.time(
                    func.datetime(
                        func.concat(TableReservation.reservation_date, " ", TableReservation.reservation_time),
                        "+" + func.cast(TableReservation.duration_minutes, String) + " minutes"
                    )
                ) > reservation_time
            )
        )
    )
    
    if session.execute(conflict_exists).first():
        return None
    
    table_available = (
        select(Table.id)
        .where(Table.id == table_id)
        .where(Table.is_available == True)
    )
    
    if not session.execute(table_available).scalar():
        return None
    
    new_reservation = TableReservation(
        table_id=table_id,
        customer_phone=customer_phone,
        reservation_date=reservation_date,
        reservation_time=reservation_time,
        duration_minutes=duration_minutes,
        created_by_employee_id=created_by_employee_id
    )
    
    session.add(new_reservation)
    session.flush()
    
    result_query = (
        select(
            Table.number.label("table_number"),
            Table.capacity.label("table_capacity"),
            Table.location.label("table_location"),
            TableReservation.reservation_date,
            TableReservation.reservation_time.label("reservation_time_start"),
            func.time(
                func.datetime(
                    func.concat(TableReservation.reservation_date, " ", TableReservation.reservation_time),
                    "+" + func.cast(TableReservation.duration_minutes, String) + " minutes"
                )
            ).label("reservation_time_end"),
            TableReservation.customer_phone,
            func.concat(Employee.first_name, " ", Employee.last_name).label("created_by")
        )
        .join(TableReservation.table)
        .join(TableReservation.created_by_employee)
        .where(TableReservation.id == new_reservation.id)
    )

    result = session.execute(result_query).mappings().first()
    session.commit()
    
    return result


def main():
    """Тестирование запроса"""
    
    with get_session() as session:
        result = create_table_reservation(
            session,
            table_id=5,
            customer_phone='+79161234567',
            reservation_date=date(2026, 4, 26),
            reservation_time=time(19, 0, 0),
            duration_minutes=120,
            created_by_employee_id=2
        )
        
        if result:
            print_table([result], "Бронирование создано")
        else:
            print("Не получилось создать бронирование")


if __name__ == "__main__":
    main()