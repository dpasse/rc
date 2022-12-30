CREATE TABLE divisions(
    id int PRIMARY KEY NOT NULL,
    name VARCHAR(100) NOT NULL,
    conference_id int NOT NULL,

    FOREIGN KEY (conference_id) REFERENCES conferences (id)
);