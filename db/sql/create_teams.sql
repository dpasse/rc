CREATE TABLE teams(
    id int PRIMARY KEY NOT NULL,
    league_id VARCHAR(10) NOT NULL,
    location VARCHAR(100) NOT NULL,
    nickname VARCHAR(50) NOT NULL,

    FOREIGN KEY (league_id) REFERENCES leagues (id)
);