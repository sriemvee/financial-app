# Auto-Categorization Logic for Expenses

import pandas as pd

class ExpenseCategorizer:
    def __init__(self, expense_data):
        self.expense_data = expense_data

    def categorize_expenses(self):
        categorized_data = []
        for index, row in self.expense_data.iterrows():
            category = self.determine_category(row['description'])
            categorized_data.append({'amount': row['amount'], 'description': row['description'], 'category': category})
        return pd.DataFrame(categorized_data)

    def determine_category(self, description):
        # Basic categorization logic based on keywords
        if 'restaurant' in description.lower():
            return 'Dining'
        elif 'uber' in description.lower() or 'taxi' in description.lower():
            return 'Transportation'
        elif 'grocery' in description.lower():
            return 'Groceries'
        elif 'salary' in description.lower():
            return 'Income'
        else:
            return 'Other'

# Sample usage
# data = pd.DataFrame({'amount': [100, 50, 200], 'description': ['Restaurant dinner', 'Uber ride', 'Monthly salary']})
# categorizer = ExpenseCategorizer(data)
# categorized = categorizer.categorize_expenses()
# print(categorized)