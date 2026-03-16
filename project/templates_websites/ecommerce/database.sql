-- E-commerce Store Database
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(100) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Sample Products
INSERT INTO products (name, price, description, category) VALUES
('Smartphone', 299.99, 'Latest tech smartphone with amazing features', 'Electronics'),
('Smart Watch', 199.99, 'Advanced fitness tracking smartwatch', 'Wearables'),
('Laptop', 899.99, 'High-performance laptop for work and gaming', 'Electronics'),
('Headphones', 99.99, 'Premium wireless headphones with noise cancellation', 'Audio'),
('Camera', 499.99, 'Professional digital camera', 'Photography'),
('Keyboard', 79.99, 'Mechanical gaming keyboard', 'Peripherals');
