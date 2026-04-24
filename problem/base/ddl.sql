CREATE TABLE IF NOT EXISTS Cities (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    rubies INTEGER NOT NULL,
    emeralds INTEGER NOT NULL,
    sapphires INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS Roads (
    from_city_id INTEGER REFERENCES Cities(id),
    to_city_id INTEGER REFERENCES Cities(id),

    PRIMARY KEY (from_city_id, to_city_id)
);