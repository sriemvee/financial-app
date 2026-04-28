INSERT INTO users (username, email, password_hash) VALUES 
  ('demo_user', 'demo@example.com', 'hashed_password_123'), 
  ('test_user', 'test@example.com', 'hashed_password_456'); 

INSERT INTO categories (name, group_name, user_id) VALUES 
  ('Groceries', 'household', 1), 
  ('Dining', 'household', 1), 
  ('Transportation', 'household', 1), 
  ('Utilities', 'household', 1), 
  ('Rent', 'household', 1), 
  ('Salary', 'income', 1), 
  ('Bonus', 'income', 1), 
  ('Entertainment', 'personal', 1), 
  ('Shopping', 'personal', 1), 
  ('Healthcare', 'personal', 1), 
  ('Education', 'official', 1), 
  ('Office Supplies', 'official', 1), 
  ('Insurance', 'financial', 1), 
  ('Investments', 'financial', 1), 
  ('Miscellaneous', 'misc', 1); 

INSERT INTO expenses (user_id, amount, date, category_id, mode, need_type, note) VALUES 
  (1, 45.50, '2026-04-20', 1, 'credit_card', 'need', 'Weekly groceries'), 
  (1, 25.00, '2026-04-21', 2, 'cash', 'want', 'Lunch with friends'), 
  (1, 15.50, '2026-04-21', 3, 'debit_card', 'need', 'Uber ride to office'), 
  (1, 120.00, '2026-04-15', 4, 'bank_transfer', 'need', 'Monthly electricity bill'), 
  (1, 1500.00, '2026-04-01', 5, 'bank_transfer', 'need', 'Monthly rent'), 
  (1, 3000.00, '2026-04-01', 6, 'bank_transfer', 'income', 'Monthly salary'), 
  (1, 500.00, '2026-04-10', 7, 'bank_transfer', 'income', 'Performance bonus'), 
  (1, 30.00, '2026-04-18', 8, 'credit_card', 'want', 'Movie tickets'), 
  (1, 75.00, '2026-04-19', 9, 'credit_card', 'want', 'New shirt'), 
  (1, 50.00, '2026-04-22', 10, 'debit_card', 'need', 'Doctor consultation'); 

INSERT INTO auto_categorization_rules (user_id, keyword, category_id) VALUES 
  (1, 'grocery', 1), 
  (1, 'restaurant', 2), 
  (1, 'uber', 3), 
  (1, 'taxi', 3), 
  (1, 'netflix', 8), 
  (1, 'amazon', 9), 
  (1, 'hospital', 10), 
  (1, 'pharmacy', 10);

-- Income Sources
INSERT INTO income_sources (name, description, type) VALUES
('ICICI_SRINI_SALARY', 'Srini Salary from ICICI', 'salary'),
('ICICI_SRINI_BONUS', 'Srini Bonus from ICICI', 'bonus'),
('HDFC_JAYA_SALARY', 'Jaya Salary from HDFC', 'salary'),
('SBI_JAYA_FREELANCE', 'Jaya Freelance Income from SBI', 'freelance'),
('JOINT_SAVINGS', 'Joint Family Income', 'transfer');

-- Expense Sources
INSERT INTO expense_sources (name, description, type, owner) VALUES
('UPI_SRINI', 'Srini UPI', 'upi', 'Srini'),
('UPI_JAYA', 'Jaya UPI', 'upi', 'Jaya'),
('AMAZON_CC', 'Amazon Credit Card', 'credit_card', 'Joint'),
('ICICI_CC', 'ICICI Credit Card', 'credit_card', 'Joint'),
('HDFC_DC', 'HDFC Debit Card', 'debit_card', 'Joint'),
('CASH_SRINI', 'Srini Cash', 'wallet', 'Srini'),
('CASH_JAYA', 'Jaya Cash', 'wallet', 'Jaya');
