# Recurring Expense Detection Logic

from typing import List, Dict
from datetime import datetime, timedelta

class RecurringExpenseDetector:
    def __init__(self, expenses: List[Dict]):
        self.expenses = expenses

    def detect_recurring(self, min_occurrences: int = 3, tolerance_days: int = 5):
        """
        Detect recurring expenses based on:
        - Same merchant/description
        - Similar amount (within 10% tolerance)
        - Regular frequency (monthly, weekly, etc.)
        """
        recurring_groups = {}
        
        # Group expenses by merchant
        for expense in self.expenses:
            merchant = expense.get('merchant', expense.get('description', ''))
            if merchant not in recurring_groups:
                recurring_groups[merchant] = []
            recurring_groups[merchant].append(expense)
        
        # Analyze groups for recurring patterns
        recurring_expenses = []
        for merchant, group in recurring_groups.items():
            if len(group) >= min_occurrences:
                # Check if amounts are similar
                amounts = [e['amount'] for e in group]
                avg_amount = sum(amounts) / len(amounts)
                
                if self._amounts_similar(amounts, avg_amount):
                    # Check frequency
                    frequency = self._detect_frequency(group)
                    if frequency:
                        recurring_expenses.append({
                            'merchant': merchant,
                            'avg_amount': round(avg_amount, 2),
                            'frequency': frequency,
                            'occurrences': len(group),
                            'category': group[0].get('category', 'Miscellaneous')
                        })
        
        return recurring_expenses

    def _amounts_similar(self, amounts: List[float], avg: float, tolerance: float = 0.1) -> bool:
        """Check if all amounts are within tolerance of average"""
        for amount in amounts:
            if abs(amount - avg) / avg > tolerance:
                return False
        return True

    def _detect_frequency(self, group: List[Dict]) -> str:
        """Detect frequency pattern (daily, weekly, monthly, etc.)"""
        if len(group) < 2:
            return None
        
        # Sort by date
        sorted_group = sorted(group, key=lambda x: x.get('date', ''))
        
        # Calculate intervals between transactions
        intervals = []
        for i in range(1, len(sorted_group)):
            try:
                date1 = datetime.fromisoformat(sorted_group[i-1]['date'])
                date2 = datetime.fromisoformat(sorted_group[i]['date'])
                interval = (date2 - date1).days
                intervals.append(interval)
            except:
                pass
        
        if not intervals:
            return None
        
        avg_interval = sum(intervals) / len(intervals)
        
        # Classify frequency
        if 1 <= avg_interval <= 2:
            return 'daily'
        elif 5 <= avg_interval <= 9:
            return 'weekly'
        elif 28 <= avg_interval <= 32:
            return 'monthly'
        elif 90 <= avg_interval <= 95:
            return 'quarterly'
        elif 365 <= avg_interval <= 370:
            return 'yearly'
        else:
            return f'every_{int(avg_interval)}_days'