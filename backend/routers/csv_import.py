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

def get_or_create_category(name, group_name, user_id=1):
    """Get category by name, create if doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id FROM categories WHERE name = ? AND user_id = ?",
        (name, user_id)
    )
    result = cursor.fetchone()
    
    if result:
        category_id = result[0]
    else:
        # Create category if it doesn't exist
        cursor.execute(
            "INSERT INTO categories (name, group_name, user_id) VALUES (?, ?, ?)",
            (name, group_name, user_id)
        )
        conn.commit()
        category_id = cursor.lastrowid
    
    conn.close()
    return category_id

def categorize_transaction(remarks, user_id=1):
    """
    Auto-categorize transaction based on remarks
    """
    remarks_upper = remarks.upper()
    
    category_name = 'Miscellaneous'  # default
    group_name = 'misc'
    need_type = 'want'  # default
    mode = 'bank_transfer'  # default
    
    # Income detection - SALARY, BONUS
    if any(x in remarks_upper for x in ['SALARY', 'NEFT-', 'IMPS']):
        category_name = 'Salary'
        group_name = 'income'
        need_type = 'income'
        mode = 'bank_transfer'
    
    # Rent
    elif 'RENT' in remarks_upper and ('BIL' in remarks_upper or 'NEFT' in remarks_upper):
        category_name = 'Rent'
        group_name = 'household'
        need_type = 'need'
        mode = 'bank_transfer'
    
    # Credit Card Payment
    elif 'ATD' in remarks_upper and 'AUTO DEBIT' in remarks_upper and 'CC' in remarks_upper:
        category_name = 'Credit Card Payment'
        group_name = 'financial'
        need_type = 'need'
        mode = 'bank_transfer'
    
    # Home Loan
    elif 'HOME LOAN' in remarks_upper and 'EMI' in remarks_upper:
        category_name = 'Home Loan'
        group_name = 'financial'
        need_type = 'need'
        mode = 'bank_transfer'
    
    # Insurance (LIC, LIFE, etc.)
    elif any(x in remarks_upper for x in ['LIFEINSURA', 'INSURANCE', 'LIC']):
        category_name = 'Insurance'
        group_name = 'financial'
        need_type = 'need'
        mode = 'bank_transfer'
    
    # Investments (RD, PPF, NSE, ACH)
    elif any(x in remarks_upper for x in ['TO RD', 'TO PPF', 'ACH/NSE', 'NSE CLEARING']):
        category_name = 'Investments'
        group_name = 'financial'
        need_type = 'want'
        mode = 'bank_transfer'
    
    # Savings (IWISH, CONTRIBUTION)
    elif any(x in remarks_upper for x in ['IWISH', 'CONTRIBUTION']):
        category_name = 'Savings'
        group_name = 'financial'
        need_type = 'want'
        mode = 'bank_transfer'
    
    # Cash Withdrawal
    elif any(x in remarks_upper for x in ['CASH WDL', 'CAM/', 'NFS/CASH']):
        category_name = 'Cash Withdrawal'
        group_name = 'misc'
        need_type = 'want'
        mode = 'cash'
    
    # UPI transactions
    elif 'UPI/' in remarks_upper:
        mode = 'upi'
        # Try to extract merchant category from UPI remarks
        if any(x in remarks_upper for x in ['SWIGGY', 'ZOMATO', 'FOOD']):
            category_name = 'Dining'
            group_name = 'personal'
        elif any(x in remarks_upper for x in ['AMAZON', 'FLIPKART', 'SHOPPING']):
            category_name = 'Shopping'
            group_name = 'personal'
        elif any(x in remarks_upper for x in ['NETFLIX', 'SPOTIFY', 'ENTERTAINMENT']):
            category_name = 'Entertainment'
            group_name = 'personal'
        elif any(x in remarks_upper for x in ['FUEL', 'PETROL', 'GAS']):
            category_name = 'Transportation'
            group_name = 'personal'
        else:
            category_name = 'Miscellaneous'
            group_name = 'misc'
    
    category_id = get_or_create_category(category_name, group_name, user_id)
    
    return {
        'category_id': category_id,
        'category_name': category_name,
        'need_type': need_type,
        'mode': mode
    }

def detect_duplicate(user_id, amount, date, description):
    """Check if exact transaction already exists (using full description)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check for EXACT match - same date, amount, AND exact same description
    cursor.execute(
        "SELECT id FROM expenses WHERE user_id = ? AND amount = ? AND date = ? AND note = ?",
        (user_id, amount, date, description)
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
        
        print(f"✅ Read {len(rows)} rows from CSV")
        
        if not rows:
            raise HTTPException(status_code=400, detail="CSV file is empty")

        # Remove BOM from column names
        if rows:
            first_row = rows[0]
            cleaned_keys = {}
            for key in first_row.keys():
                cleaned_key = key.lstrip('\ufeff')  # Remove BOM
                cleaned_keys[cleaned_key] = first_row[key]
            
            # Rebuild rows with cleaned column names
            cleaned_rows = []
            for row in rows:
                cleaned_row = {}
                for key in row.keys():
                    cleaned_key = key.lstrip('\ufeff')
                    cleaned_row[cleaned_key] = row[key]
                cleaned_rows.append(cleaned_row)
            rows = cleaned_rows
            
        # Debug: Print column names
        print(f"✅ Column names: {list(rows[0].keys())}")
        
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
        print(f"✅ Created batch {batch_id}")
        
        imported_count = 0
        skipped_count = 0
        duplicates_found = 0
        errors = []
        
        # Process each row
        for idx, row in enumerate(rows, 1):
            try:
                # Clean up row values
                value_date = (row.get('Value Date', '') or '').strip()
                transaction_date = (row.get('Transaction Date', '') or '').strip() or value_date
                withdrawal = (row.get('Withdrawal Amount(INR)', '') or '').strip().replace(',', '')
                deposit = (row.get('Deposit Amount(INR)', '') or '').strip().replace(',', '')
                remarks = (row.get('Transaction Remarks', '') or '').strip()
                
                if idx <= 3:  # Print first 3 rows for debugging
                    print(f"\n📋 Row {idx}:")
                    print(f"   value_date: '{value_date}'")
                    print(f"   transaction_date: '{transaction_date}'")
                    print(f"   withdrawal: '{withdrawal}'")
                    print(f"   deposit: '{deposit}'")
                    print(f"   remarks: '{remarks[:60]}'")
                
                # Skip empty rows
                if not remarks or not transaction_date:
                    if idx <= 3:
                        print(f"   ❌ Skipped: empty remarks or date")
                    skipped_count += 1
                    continue
                
                # Parse date
                date_str = parse_date(transaction_date)
                if idx <= 3:
                    print(f"   parsed_date: '{date_str}'")
                
                if not date_str:
                    if idx <= 3:
                        print(f"   ❌ Skipped: invalid date format")
                    skipped_count += 1
                    errors.append(f"Row {idx}: Invalid date format '{transaction_date}'")
                    continue
                
                # Determine amount and type (expense vs income)
                amount = None
                transaction_type = None
                
                try:
                    if withdrawal and float(withdrawal) > 0:
                        amount = float(withdrawal)
                        transaction_type = 'expense'
                    elif deposit and float(deposit) > 0:
                        amount = float(deposit)
                        transaction_type = 'income'
                except ValueError as ve:
                    if idx <= 3:
                        print(f"   ❌ Skipped: invalid amount format - {ve}")
                    skipped_count += 1
                    errors.append(f"Row {idx}: Invalid amount format")
                    continue
                
                if not amount or not transaction_type:
                    if idx <= 3:
                        print(f"   ❌ Skipped: no amount or type")
                    skipped_count += 1
                    continue
                
                if idx <= 3:
                    print(f"   ✅ Amount: {amount}, Type: {transaction_type}")
                
                # Check for duplicates
                if detect_duplicate(user_id, amount, date_str, remarks):
                    duplicates_found += 1
                    skipped_count += 1
                    if idx <= 3:
                        print(f"   ❌ Skipped: duplicate found")
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
                    # Extract source name from remarks (first part before /)
                    source_name = remarks.split('/')[0] if '/' in remarks else 'CSV Import'
                    source_name = source_name.strip()
                    
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
                if idx <= 3:
                    print(f"   ✅ Imported successfully")
                
            except Exception as e:
                skipped_count += 1
                errors.append(f"Row {idx}: {str(e)}")
                print(f"   ❌ Exception: {str(e)}")
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
            message += f"\nFirst 5 errors: {'; '.join(errors[:5])}"
        
        print(f"\n✅ Final counts - Imported: {imported_count}, Skipped: {skipped_count}, Duplicates: {duplicates_found}")
        
        return {
            "import_batch_id": batch_id,
            "total_rows": len(rows),
            "imported_count": imported_count,
            "skipped_count": skipped_count,
            "duplicates_found": duplicates_found,
            "message": message
        }
    
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
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
    
    # Format the import_date for display
    result = []
    for row in rows:
        row_dict = dict(row)
        if row_dict['import_date']:
            try:
                # Parse the timestamp and format it nicely
                dt = datetime.strptime(row_dict['import_date'], '%Y-%m-%d %H:%M:%S')
                row_dict['import_date'] = dt.strftime('%d-%b-%Y %H:%M')  # e.g., "29-Apr-2026 08:19"
            except:
                pass  # If parsing fails, keep original
        result.append(row_dict)
    
    return result

@router.get("/batches/{batch_id}")
async def get_import_batch(batch_id: int):
    """Get a specific import batch"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, filename, total_rows, imported_count, skipped_count, duplicates_found, import_date "
        "FROM import_batches WHERE id = ?",
        (batch_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    row_dict = dict(row)
    if row_dict['import_date']:
        try:
            dt = datetime.strptime(row_dict['import_date'], '%Y-%m-%d %H:%M:%S')
            row_dict['import_date'] = dt.strftime('%d-%b-%Y %H:%M')
        except:
            pass
    
    return row_dict

@router.delete("/batches/{batch_id}")
async def delete_import_batch(batch_id: int):
    """Delete an import batch and its expenses"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Delete associated expenses
        cursor.execute("DELETE FROM expenses WHERE import_batch_id = ?", (batch_id,))
        
        # Delete associated income
        cursor.execute(
            "DELETE FROM income WHERE id IN (SELECT id FROM income WHERE user_id = 1 AND date IN "
            "(SELECT date FROM expenses WHERE import_batch_id = ?))",
            (batch_id,)
        )
        
        # Delete batch
        cursor.execute("DELETE FROM import_batches WHERE id = ?", (batch_id,))
        
        conn.commit()
        conn.close()
        
        return {"batch_id": batch_id, "status": "deleted"}
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
