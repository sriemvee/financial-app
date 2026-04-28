CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, group_name TEXT NOT NULL, user_id INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE);

CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, amount REAL NOT NULL, date DATE NOT NULL, category_id INTEGER, mode TEXT NOT NULL, need_type TEXT NOT NULL, note TEXT, source TEXT DEFAULT 'manual', import_batch_id INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL, FOREIGN KEY (import_batch_id) REFERENCES import_batches(id) ON DELETE SET NULL);

CREATE TABLE IF NOT EXISTS import_batches (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, filename TEXT NOT NULL, total_rows INTEGER, imported_count INTEGER, skipped_count INTEGER, duplicates_found INTEGER, import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE);

CREATE TABLE IF NOT EXISTS auto_categorization_rules (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, keyword TEXT NOT NULL, category_id INTEGER NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE);

CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
CREATE INDEX IF NOT EXISTS idx_expenses_category_id ON expenses(category_id);
CREATE INDEX IF NOT EXISTS idx_expenses_import_batch_id ON expenses(import_batch_id);
CREATE INDEX IF NOT EXISTS idx_categories_user_id ON categories(user_id);
CREATE INDEX IF NOT EXISTS idx_import_batches_user_id ON import_batches(user_id);

-- Income Sources (e.g., ICICI_SRINI_SALARY, UPI_SRINI, etc.)
CREATE TABLE IF NOT EXISTS income_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    type TEXT,  -- salary, freelance, investment, bonus, transfer, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Expense Sources (e.g., Srini's UPI, Amazon Credit Card, etc.)
CREATE TABLE IF NOT EXISTS expense_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    type TEXT,  -- upi, credit_card, debit_card, wallet, etc.
    owner TEXT,  -- who owns this source (Srini, Jaya, Joint, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Income table
CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    source_id INTEGER NOT NULL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (source_id) REFERENCES income_sources(id)
);

-- Update expenses table to use expense_sources
ALTER TABLE expenses ADD COLUMN expense_source_id INTEGER;
