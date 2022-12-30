CREATE TABLE conferences(
    id int PRIMARY KEY NOT NULL,
    name VARCHAR(100) NOT NULL,
    league_id VARCHAR(10) NOT NULL,

    FOREIGN KEY (league_id) REFERENCES leagues (id)
);