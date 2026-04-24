DELETE FROM Cities;
DELETE FROM Roads;

INSERT INTO Cities VALUES
(1, 'Таратайка', 15, 25, 43),
(2, 'Угаралитевск', 10, 5, 30),
(3, 'Буханково', 10, 50, 20),
(4, 'Карапулька', 35, 15, 45),
(5, 'Агаповка', 20, 30, 25);

INSERT INTO Roads VALUES
(1, 2),
(1, 3),
(2, 4),
(3, 4),
(4, 5);