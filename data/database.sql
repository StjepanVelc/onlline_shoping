-- InnoDB + UTF8MB4
SET NAMES utf8mb4;
SET sql_require_primary_key = OFF;

-- USERS
CREATE TABLE users (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL,
  country VARCHAR(50) NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_users_username UNIQUE (username),
  CONSTRAINT uq_users_email    UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- PRODUCTS
CREATE TABLE products (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  price DECIMAL(10,2) NOT NULL,
  stock INT NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT chk_products_price CHECK (price >= 0),
  CONSTRAINT chk_products_stock CHECK (stock >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ORDERS
CREATE TABLE orders (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id INT UNSIGNED NOT NULL,
  address VARCHAR(200) NOT NULL,
  status ENUM('pending','paid','shipped','cancelled') NOT NULL DEFAULT 'pending',
  order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  total_amount DECIMAL(10,2) DEFAULT NULL,
  PRIMARY KEY (id),
  CONSTRAINT fk_orders_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ORDER_ITEMS
CREATE TABLE order_items (
  order_id INT UNSIGNED NOT NULL,
  product_id INT UNSIGNED NOT NULL,
  quantity INT NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (order_id, product_id),
  CONSTRAINT fk_items_order
    FOREIGN KEY (order_id) REFERENCES orders(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_items_product
    FOREIGN KEY (product_id) REFERENCES products(id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT chk_items_qty CHECK (quantity > 0),
  CONSTRAINT chk_items_price CHECK (price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Indeksi za optimizaciju upita
-- USERS
CREATE INDEX idx_users_country ON users(country);

-- PRODUCTS
CREATE INDEX idx_products_price ON products(price);

-- ORDERS
CREATE INDEX idx_orders_user_date   ON orders(user_id, order_date DESC);
CREATE INDEX idx_orders_status_date ON orders(status, order_date);

-- ORDER_ITEMS
-- dodatni indeks za upite "sve narudžbe za proizvod X":
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- Administrativne napomene
CREATE ADMINISTRATIVE NOTE = 'Database schema for e-commerce platform with users, products, orders, and order items.';

-- ADMIN TABLE OF CONTENTS
-- MySQL 8.0 varijanta
CREATE TABLE IF NOT EXISTS admins (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  username VARCHAR(100) NOT NULL UNIQUE,
  email    VARCHAR(255) NOT NULL UNIQUE,
  privileges JSON NOT NULL,
  PRIMARY KEY (id)
);

-- 1) napravi
INSERT INTO admins (username, email, privileges)
VALUES ('stjepan', 'stjepan@example.com', '["access_data","manage_users"]') RETURNING id;

-- 2) pročitaj
SELECT id, username, email, privileges FROM admins WHERE username='stjepan';

-- 3) update privilegija
UPDATE admins SET privileges='["access_data"]'::jsonb WHERE username='stjepan';

-- 4) delete (po želji)
DELETE FROM admins WHERE username='stjepan';
