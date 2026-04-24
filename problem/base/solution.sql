WITH RECURSIVE
paths AS (
    SELECT 
        c.id AS cur_id,
        c.name AS cur_name,
        c.name AS path,
        0 AS step
    FROM Cities c
    WHERE c.name = 'Таратайка'
    
    UNION ALL
    
    SELECT 
        c.id,
        c.name,
        p.path || ' -> ' || c.name,
        p.step + 1
    FROM paths p
    JOIN Roads r ON r.from_city_id = p.cur_id
    JOIN Cities c ON c.id = r.to_city_id
    WHERE INSTR(p.path, c.name) = 0
),
full_paths AS (
    SELECT path, step FROM paths WHERE cur_name = 'Агаповка'
),
city_steps AS (
    SELECT 
        fp.path,
        0 AS step,
        SUBSTR(fp.path, 1, INSTR(fp.path || ' -> ', ' -> ') - 1) AS city_name,
        SUBSTR(fp.path, INSTR(fp.path || ' -> ', ' -> ') + 4) AS rest_path
    FROM full_paths fp
    
    UNION ALL
    
    SELECT 
        cs.path,
        cs.step + 1,
        SUBSTR(cs.rest_path, 1, INSTR(cs.rest_path || ' -> ', ' -> ') - 1) AS city_name,
        SUBSTR(cs.rest_path, INSTR(cs.rest_path || ' -> ', ' -> ') + 4) AS rest_path
    FROM city_steps cs
    WHERE cs.city_name != ''
),
city_values AS (
    SELECT 
        cs.path,
        cs.city_name,
        cs.step,
        MAX(0, c.rubies - cs.step) AS ruby_val,
        MAX(0, c.emeralds - cs.step) AS emerald_val,
        MAX(0, c.sapphires - cs.step) AS sapphire_val
    FROM city_steps cs
    JOIN Cities c ON c.name = cs.city_name
    WHERE cs.city_name != ''
),
combinations AS (
    SELECT 
        r.path,
        r.city_name AS ruby_city,
        e.city_name AS emerald_city,
        s.city_name AS sapphire_city,
        r.ruby_val + e.emerald_val + s.sapphire_val AS total_jewelry,
        (SELECT COUNT(DISTINCT city_name) FROM city_steps cs2 WHERE cs2.path = r.path) AS city_count
    FROM city_values r
    JOIN city_values e ON r.path = e.path
    JOIN city_values s ON r.path = s.path
),
best AS (
    SELECT *
    FROM combinations
    WHERE total_jewelry = (SELECT MAX(total_jewelry) AS max_val FROM combinations)
)
SELECT 
    path,
    total_jewelry,
    ruby_city,
    emerald_city,
    sapphire_city
FROM best
WHERE city_count = (SELECT MIN(city_count) AS min_count FROM best)
ORDER BY 
    path ASC,
    ruby_city ASC,
    emerald_city ASC,
    sapphire_city ASC