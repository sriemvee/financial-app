SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount DECIMAL(10, 2) NOT NULL,
    category_id INTEGER NOT NULL,
    payment_mode VARCHAR(50),
    need_type VARCHAR(50),
    expense_date DATE NOT NULL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS recurring_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id INTEGER NOT NULL,
    frequency VARCHAR(20),
    next_occurrence DATE,
    FOREIGN KEY (expense_id) REFERENCES expenses(id)
);

CREATE TABLE IF NOT EXISTS csv_imports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255),
    imported_count INTEGER,
    skipped_count INTEGER,
    duplicates_found INTEGER,
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

SEED_SQL = """
INSERT INTO categories (name, description) VALUES
('Groceries', 'Food and grocery shopping'),
('Dining', 'Restaurants and food delivery'),
('Transportation', 'Gas, public transport, taxi'),
('Entertainment', 'Movies, games, hobbies'),
('Utilities', 'Electricity, water, internet'),
('Healthcare', 'Medical expenses and medicines'),
('Shopping', 'Clothing and general shopping'),
('Rent', 'Housing and rent payments'),
('Insurance', 'Health and other insurance'),
('Miscellaneous', 'Other expenses');
"""
