from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import csv
import io
from datetime import datetime
import sqlite3
import re

router = APIRouter(prefix="/csv-import", tags=["csv-import"])

class CSVImportResponse(BaseModel):
    import_batch_id: int
    total_rows: int
    imported_count: int
    skipped_count: int
    duplicates_found: int
    message: str

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

def parse_date(date_str):
    """Convert DD/MM/YYYY to YYYY-MM-DD"""
    try:
        return datetime.strptime(date_str.strip(), '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError:
        return None

def categorize_transaction(remarks, user_id=1):
    """
    Auto-categorize transaction based on remarks
    Rules based on your mapping:
    - BIL/NEFT/.*Rent → Rent
    - ATD/Auto Debit CC → Credit Card Payment
    - NEFT-.*SALARY → Income
    - BIL/Home Loan → Home Loan
    - To RD or TO PPF → Investments
    - CAM/.*CASH WDL → Miscellaneous
    - ACH/NSE → Investments
    - INF/IWISH → Savings
    - UPI/.* → Extract merchant name
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Category mapping
    category_map = {
        'rent': 'Rent',
        'credit_card_payment': 'Credit Card Payment',
        'home_loan': 'Home Loan',
        'investments': 'Investments',
        'savings': 'Savings',
        'miscellaneous': 'Miscellaneous',
    }
    
    category_id = None
    category_name = 'Miscellaneous'  # default
    need_type = 'want'  # default
    mode = 'bank_transfer'  # default
    
    remarks_upper = remarks.upper()
    
    # Income detection
    if 'SALARY' in remarks_upper:
        cursor.execute("SELECT id FROM categories WHERE name = 'Salary' AND user_id = ?", (user_id,))
        result = cursor.fetchone()
        category_id = result[0] if result else None
        category_name = 'Salary'
        need_type = 'income'
        mode = 'bank_transfer'
    
    # Rent
    elif 'RENT' in remarks_upper and 'NEFT' in remarks_upper:
        cursor.execute("SELECT id FROM categories WHERE name = 'Rent' AND user_id = ?", (user_id,))
        result = cursor.fetchone()
        category_id = result[0] if result else None
        category_name = 'Rent'
        need_type = 'need'
        mode = 'bank_transfer'
    
    # Credit Card Payment
    elif 'ATD' in remarks_upper and 'AUTO DEBIT CC' in remarks_upper:
        cursor.execute("SELECT id FROM categories WHERE name = 'Credit Card Payment' AND user_id = ?", (user_id,))
        result = cursor.fetchone()
        category_id = result[0] if result else None
        category_name = 'Credit Card Payment'
        need_type = 'need'
        mode = 'bank_transfer'
    
    # Home Loan
    elif 'HOME LOAN' in remarks_upper and 'EMI' in remarks_upper:
        cursor.execute("SELECT id FROM categories WHERE name = 'Home Loan' AND user_id = ?", (user_id,))
        result = cursor.fetchone()
        category_id = result[0] if result else None
        category_name = 'Home Loan'
        need_type = 'need'
        mode = 'bank_transfer'
    
    # Investments (RD, PPF, NSE)
    elif any(x in remarks_upper for x in ['TO RD', 'TO PPF', 'ACH/NSE']):
        cursor.execute("SELECT id FROM categories WHERE name = 'Investments' AND user_id = ?", (user_id,))
        result = cursor.fetchone()
        category_id = result[0] if result else None
        category_name = 'Investments'
        need_type = 'want'
        mode = 'bank_transfer'
    
    # Savings
    elif 'IWISH' in remarks_upper:
        cursor.execute("SELECT id FROM categories WHERE name = 'Savings' AND user_id = ?", (user_id,))
        result = cursor.fetchone()
        category_id = result[0] if result else None
        category_name = 'Savings'
        need_type = 'want'
        mode = 'bank_transfer'
    
    # Cash Withdrawal
    elif 'CASH WDL' in remarks_upper or 'CAM' in remarks_upper:
        cursor.execute("SELECT id FROM categories WHERE name = 'Miscellaneous' AND user_id = ?", (user_id,))
        result = cursor.fetchone()
        category_id = result[0] if result else None
        category_name = 'Miscellaneous'
        need_type = 'want'
        mode = 'cash'
    
    # UPI transactions
    elif 'UPI/' in remarks_upper:
        mode = 'upi'
        # Try to extract merchant from UPI remarks
        # Extract merchant name for further categorization
        cursor.execute("SELECT id FROM categories WHERE name = 'Miscellaneous' AND user_id = ?", (user_id,))
        result = cursor.fetchone()
        category_id = result[0] if result else None
        category_name = 'Miscellaneous'
    
    # Check auto-categorization rules as fallback
    if category_id is None:
        cursor.execute(
            "SELECT c.id, c.name FROM auto_categorization_rules acr "
            "JOIN categories c ON acr.category_id = c.id "
            "WHERE user_id = ? AND UPPER(c.name) LIKE ? LIMIT 1",
            (user_id, '%' + category_name.upper() + '%')
        )
        result = cursor.fetchone()
        if result:
            category_id = result[0]
            category_name = result[1]
    
    conn.close()
    
    return {
        'category_id': category_id,
        'category_name': category_name,
        'need_type': need_type,
        'mode': mode
    }

def detect_duplicate(user_id, amount, date, description):
    """Check if transaction already exists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id FROM expenses WHERE user_id = ? AND amount = ? AND date = ? AND note LIKE ?",
        (user_id, amount, date, f'%{description}%')
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and import CSV file"""
    try:
        # Read file
        content = await file.read()
        text = content.decode('utf-8')
        
        # Parse CSV
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        
        if not rows:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user_id (default to 1 for now, should come from auth)
        user_id = 1
        
        # Create import batch
        cursor.execute(
            "INSERT INTO import_batches (user_id, filename, total_rows, imported_count, skipped_count, duplicates_found) "
            "VALUES (?, ?, ?, 0, 0, 0)",
            (user_id, file.filename, len(rows))
        )
        conn.commit()
        batch_id = cursor.lastrowid
        
        imported_count = 0
        skipped_count = 0
        duplicates_found = 0
        errors = []
        
        # Process each row
        for idx, row in enumerate(rows, 1):
            try:
                # Map CSV columns to our format
                # Expected columns: Value Date, Transaction Date, Withdrawal Amount(INR), Deposit Amount(INR), Transaction Remarks, Balance(INR)
                
                value_date = row.get('Value Date', '').strip()
                transaction_date = row.get('Transaction Date', '').strip()
                withdrawal = row.get('Withdrawal Amount(INR)', '0').strip()
                deposit = row.get('Deposit Amount(INR)', '0').strip()
                remarks = row.get('Transaction Remarks', '').strip()
                
                # Parse date
                date_str = parse_date(transaction_date or value_date)
                if not date_str:
                    skipped_count += 1
                    errors.append(f"Row {idx}: Invalid date format")
                    continue
                
                # Determine amount and type (expense vs income)
                if withdrawal and float(withdrawal) > 0:
                    amount = float(withdrawal)
                    transaction_type = 'expense'
                elif deposit and float(deposit) > 0:
                    amount = float(deposit)
                    transaction_type = 'income'
                else:
                    skipped_count += 1
                    continue
                
                # Check for duplicates
                if detect_duplicate(user_id, amount, date_str, remarks):
                    duplicates_found += 1
                    skipped_count += 1
                    continue
                
                # Categorize
                categorization = categorize_transaction(remarks, user_id)
                
                if transaction_type == 'expense':
                    # Insert expense
                    cursor.execute(
                        "INSERT INTO expenses (user_id, amount, date, category_id, mode, need_type, note, source, import_batch_id) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            user_id,
                            amount,
                            date_str,
                            categorization['category_id'],
                            categorization['mode'],
                            categorization['need_type'],
                            remarks,
                            'csv_import',
                            batch_id
                        )
                    )
                else:  # income
                    # For income, we need to find or create an income source
                    # Extract source from remarks
                    source_name = remarks.split('/')[0] if '/' in remarks else 'CSV Import'
                    
                    cursor.execute(
                        "SELECT id FROM income_sources WHERE name = ?",
                        (source_name,)
                    )
                    source_result = cursor.fetchone()
                    
                    if not source_result:
                        cursor.execute(
                            "INSERT INTO income_sources (name, description, type) VALUES (?, ?, ?)",
                            (source_name, f"Imported from CSV: {remarks}", 'other')
                        )
                        conn.commit()
                        source_id = cursor.lastrowid
                    else:
                        source_id = source_result[0]
                    
                    cursor.execute(
                        "INSERT INTO income (user_id, amount, date, source_id, note) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (user_id, amount, date_str, source_id, remarks)
                    )
                
                conn.commit()
                imported_count += 1
                
            except Exception as e:
                skipped_count += 1
                errors.append(f"Row {idx}: {str(e)}")
                continue
        
        # Update batch with final counts
        cursor.execute(
            "UPDATE import_batches SET imported_count = ?, skipped_count = ?, duplicates_found = ? WHERE id = ?",
            (imported_count, skipped_count, duplicates_found, batch_id)
        )
        conn.commit()
        conn.close()
        
        message = f"CSV import completed. Imported: {imported_count}, Skipped: {skipped_count}, Duplicates: {duplicates_found}"
        if errors:
            message += f"\nErrors: {'; '.join(errors[:5])}"  # Show first 5 errors
        
        return {
            "import_batch_id": batch_id,
            "total_rows": len(rows),
            "imported_count": imported_count,
            "skipped_count": skipped_count,
            "duplicates_found": duplicates_found,
            "message": message
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to import CSV: {str(e)}")

@router.get("/batches")
async def get_import_batches():
    """Get all import batches"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, filename, total_rows, imported_count, skipped_count, duplicates_found, import_date "
        "FROM import_batches ORDER BY import_date DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@router.get("/batches/{batch_id}")
async def get_import_batch(batch_id: int):
    """Get a specific import batch"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, filename, total_rows, imported_count, skipped_count, duplicates_found, import_date "
        "FROM import_batches WHERE id = ?"
        , (batch_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return dict(row)

@router.delete("/batches/{batch_id}")
async def delete_import_batch(batch_id: int):
    """Delete an import batch and its expenses"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Delete associated expenses
        cursor.execute("DELETE FROM expenses WHERE import_batch_id = ?", (batch_id,))
        
        # Delete batch
        cursor.execute("DELETE FROM import_batches WHERE id = ?", (batch_id,))
        
        conn.commit()
        conn.close()
        
        return {"batch_id": batch_id, "status": "deleted"}
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
