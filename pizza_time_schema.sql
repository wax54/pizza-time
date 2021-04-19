DROP DATABASE IF EXISTS pizza_time;
CREATE DATABASE pizza_time;
\c pizza_time;

CREATE TABLE users (
id SERIAL PRIMARY KEY,
name TEXT,
username TEXT NOT NULL UNIQUE,
Token TEXT NOT NULL
);

CREATE TABLE customers ( 
id SERIAL PRIMARY KEY,
name TEXT NOT NULL
);

CREATE TABLE notes (
cust_id INT REFERENCES customers ON DELETE CASCADE,
user_id INT REFERENCES users ON DELETE CASCADE,
note TEXT NOT NULL,
PRIMARY KEY(cust_id, user_id)
);

CREATE TABLE deliveries (
id SERIAL PRIMARY KEY,
date DATE NOT NULL,
driver_id INT REFERENCES users
);

CREATE TABLE orders (
id SERIAL PRIMARY KEY ,
date DATE NOT NULL,
num INT NOT NULL, 
tip FLOAT DEFAULT 0,
cust_id INT REFERENCES customers ON DELETE SET NULL,
del_id INT REFERENCES deliveries ON DELETE CASCADE
);

CREATE TABLE schedules (
id SERIAL PRIMARY KEY,
u_id INT NOT NULL REFERENCES users ON DELETE CASCADE,
pag_code INT NOT NULL,
shift_start TIMESTAMP NOT NULL, 
shift_end TIMESTAMP NOT NULL,
shift_type varchar(20) 
);

CREATE INDEX schedule_pag_code_idx ON schedules (u_id, pag_code);
CREATE INDEX order_idx ON orders (date, num);





