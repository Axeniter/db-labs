
BEGIN TRANSACTION;

INSERT INTO TableReservations (
    table_id,
    customer_phone,
    reservation_date,
    reservation_time,
    duration_minutes,
    created_by_employee_id
)
SELECT 
    5,
    '+79161234567',
    '2026-04-20',
    '19:00:00',
    120,
    6
WHERE NOT EXISTS (
    SELECT 1 
    FROM TableReservations AS tr
    WHERE tr.table_id = 5
      AND tr.reservation_date = '2026-04-20'
      AND (
          tr.reservation_time < TIME('19:00:00', '+120 minutes')
          AND 
          TIME(tr.reservation_time, '+' || tr.duration_minutes || ' minutes') > '19:00:00'
      )
)
AND EXISTS (
    SELECT 1 FROM Tables WHERE id = 5 AND is_available = 1
);

SELECT changes() AS rows_inserted;

COMMIT;

SELECT 
    t.number AS table_number,
    t.capacity AS table_capacity,
    t.location AS table_location,
    tr.reservation_date AS reservation_date,
    tr.reservation_time AS reservation_time_start,
    TIME(tr.reservation_time, '+' || tr.duration_minutes || ' minutes') AS reservation_time_end,
    tr.customer_phone AS customer_phone,
    e.first_name || ' ' || e.last_name AS created_by
FROM TableReservations AS tr
JOIN Tables AS t ON tr.table_id = t.id
JOIN Employees AS e ON tr.created_by_employee_id = e.id
WHERE tr.table_id = 5 
  AND tr.reservation_date = '2026-04-20'
  AND tr.reservation_time = '19:00:00'
  AND tr.customer_phone = '+79161234567'
LIMIT 1;