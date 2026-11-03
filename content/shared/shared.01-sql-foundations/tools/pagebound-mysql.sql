-- Pagebound for MySQL 8 (MySQL Workbench). Run once in an empty schema:  CREATE DATABASE pagebound; USE pagebound;
-- Differences from the SQLite file: DATE columns, DOUBLE for money, table-level FOREIGN KEY (MySQL ignores inline REFERENCES).

CREATE TABLE authors (
    author_id INT PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    country   VARCHAR(50)
);

CREATE TABLE books (
    book_id   INT PRIMARY KEY,
    title     VARCHAR(200) NOT NULL,
    author_id INT NOT NULL,
    category  VARCHAR(50) NOT NULL,
    price     DOUBLE NOT NULL,
    published DATE NOT NULL,
    pages     INT,                    -- NULL when unknown
    FOREIGN KEY (author_id) REFERENCES authors (author_id)
);

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    city        VARCHAR(100),         -- NULL when unknown
    joined      DATE NOT NULL
);

CREATE TABLE orders (
    order_id    INT PRIMARY KEY,
    customer_id INT NOT NULL,
    ordered     DATE NOT NULL,
    status      VARCHAR(20) NOT NULL, -- 'shipped', 'pending' or 'cancelled'
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);

CREATE TABLE order_items (
    order_id   INT NOT NULL,
    book_id    INT NOT NULL,
    qty        INT NOT NULL,
    unit_price DOUBLE NOT NULL,       -- price at the time of the order
    PRIMARY KEY (order_id, book_id),
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (book_id) REFERENCES books (book_id)
);

CREATE TABLE employees (
    emp_id     INT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    manager_id INT,
    dept       VARCHAR(50) NOT NULL,
    salary     INT NOT NULL,
    FOREIGN KEY (manager_id) REFERENCES employees (emp_id)
);

CREATE TABLE daily_sales (
    day    DATE NOT NULL,
    store  VARCHAR(50) NOT NULL,
    amount DOUBLE NOT NULL
);

INSERT INTO authors VALUES
    (1, 'Maya Rao',  'India'),
    (2, 'Tom Hale',  'UK'),
    (3, 'Lena Voss', 'Germany'),
    (4, 'Ken Ito',   'Japan'),
    (5, 'Sara Cole', 'UK'),
    (6, 'Omar Diaz', 'Spain');

INSERT INTO books VALUES
    (1,  'The Quiet River',   1, 'fiction', 12.50, '2019-03-14', 320),
    (2,  'Code by Hand',      2, 'tech',    39.00, '2021-06-01', 450),
    (3,  'Salt and Stars',    1, 'fiction',  9.99, '2022-11-20', NULL),
    (4,  'Data Gardens',      3, 'tech',    45.50, '2020-01-15', 510),
    (5,  'Little Atlas',      4, 'kids',     7.25, '2018-09-09',  64),
    (6,  'Mountain Letters',  3, 'fiction', 14.00, '2023-02-02', 280),
    (7,  'Cook Slowly',       5, 'cooking', 22.00, '2021-10-10', 200),
    (8,  'Night Trains',      2, 'fiction', 11.00, '2017-05-05', 350),
    (9,  'Tiny Robots',       4, 'kids',     8.50, '2022-04-04', NULL),
    (10, 'SQL Basics',        3, 'tech',    29.00, '2024-01-10', 380);

INSERT INTO customers VALUES
    (1, 'Asha Nair',    'Pune',   '2022-01-05'),
    (2, 'Ben Okoye',    'Lagos',  '2022-03-18'),
    (3, 'Chloe Martin', NULL,     '2022-07-30'),
    (4, 'Dev Patel',    'Pune',   '2023-02-11'),
    (5, 'Elif Demir',   'Ankara', '2023-05-21'),
    (6, 'Farid Khan',   NULL,     '2023-09-09'),
    (7, 'Gita Rao',     'Mumbai', '2024-01-02'),
    (8, 'Hugo Brandt',  'Berlin', '2024-03-15');

INSERT INTO orders VALUES
    (1,  1, '2024-01-10', 'shipped'),
    (2,  1, '2024-02-14', 'shipped'),
    (3,  2, '2024-02-20', 'cancelled'),
    (4,  3, '2024-03-01', 'shipped'),
    (5,  4, '2024-03-05', 'pending'),
    (6,  2, '2024-03-18', 'shipped'),
    (7,  5, '2024-04-02', 'shipped'),
    (8,  1, '2024-04-20', 'pending'),
    (9,  7, '2024-05-11', 'shipped'),
    (10, 4, '2024-05-30', 'shipped');

INSERT INTO order_items VALUES
    (1,  1,  1, 12.50),
    (1,  2,  1, 39.00),
    (2,  3,  2,  9.99),
    (3,  4,  1, 45.50),
    (4,  1,  1, 12.50),
    (4,  5,  3,  7.25),
    (5,  10, 1, 29.00),
    (5,  2,  1, 39.00),
    (6,  6,  1, 14.00),
    (6,  8,  2, 11.00),
    (7,  7,  1, 19.80),
    (8,  9,  2,  8.50),
    (8,  5,  1,  7.25),
    (9,  4,  1, 45.50),
    (9,  10, 1, 29.00),
    (10, 3,  1,  9.99),
    (10, 6,  1, 14.00),
    (10, 1,  2, 12.50);

INSERT INTO employees VALUES
    (1, 'Priya Shah', NULL, 'exec',  150000),
    (2, 'Marco Lee',  1,    'eng',   110000),
    (3, 'Nina Park',  1,    'sales',  95000),
    (4, 'Omar Said',  2,    'eng',    90000),
    (5, 'Lucy Chen',  2,    'eng',    90000),
    (6, 'Raj Mehta',  3,    'sales',  70000),
    (7, 'Ivy Cruz',   3,    'sales',  72000),
    (8, 'Sam Wu',     4,    'eng',    65000);

INSERT INTO daily_sales VALUES
    ('2024-06-01', 'north', 120.0),
    ('2024-06-02', 'north',  80.0),
    ('2024-06-03', 'north',  95.5),
    ('2024-06-05', 'north',  60.0),
    ('2024-06-06', 'north', 150.0),
    ('2024-06-01', 'south',  70.0),
    ('2024-06-02', 'south',  70.0),
    ('2024-06-04', 'south', 200.0),
    ('2024-06-05', 'south',  40.0),
    ('2024-06-06', 'south',  90.0);
