CREATE TABLE leagues(
    id VARCHAR(10) PRIMARY KEY NOT NULL,
    name VARCHAR(100) NOT NULL,
    parent_id VARCHAR(10),

    FOREIGN KEY (parent_id) REFERENCES leagues (id)
);