PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (card varchar(8) primary key, name varchar(64));
CREATE TABLE history (card varchar(8), moment datetime, primary key (card, moment));
COMMIT;

