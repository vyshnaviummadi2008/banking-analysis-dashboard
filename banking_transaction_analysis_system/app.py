import os
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv
from db import fetch_all, execute, get_connection
from analytics import account_summary, monthly_summary, export_reports, review_flags

load_dotenv()

def money(value):
    return f"{float(value or 0):,.2f}"

def admin_check():
    expected = os.getenv("ADMIN_PIN", "2468")
    entered = input("Demo admin PIN: ").strip()
    if entered != expected:
        print("Access denied.")
        return False
    return True

def show_accounts():
    df = account_summary()
    if df.empty:
        print("No accounts found. Run seed.py or add a customer/account.")
        return
    print("\nACCOUNT SUMMARY (balances are simulated)")
    print(df.to_string(index=False))

def show_monthly():
    df = monthly_summary()
    if df.empty:
        print("No transactions found.")
    else:
        print("\nMONTHLY SUMMARY")
        print(df.to_string(index=False))

def add_customer_account():
    if not admin_check():
        return
    name = input("Synthetic customer display name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    account_type = input("Account type (SAVINGS/CURRENT): ").strip().upper()
    if account_type not in ("SAVINGS", "CURRENT"):
        print("Invalid account type.")
        return
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO customers (display_name) VALUES (%s)", (name,))
        customer_id = cur.lastrowid
        cur.execute("INSERT INTO accounts (customer_id, account_type) VALUES (%s, %s)",
                    (customer_id, account_type))
        conn.commit()
        print(f"Created synthetic customer ID {customer_id} and account ID {cur.lastrowid}.")
    except Exception as exc:
        conn.rollback()
        print(f"Could not create record: {exc}")
    finally:
        conn.close()

def record_transaction():
    if not admin_check():
        return
    try:
        account_id = int(input("Account ID: ").strip())
    except ValueError:
        print("Account ID must be a number.")
        return
    kind = input("Type (DEPOSIT/WITHDRAWAL): ").strip().upper()
    if kind not in ("DEPOSIT", "WITHDRAWAL"):
        print("Invalid transaction type.")
        return
    try:
        amount = Decimal(input("Positive amount: ").strip())
        if not amount.is_finite() or amount <= 0 or amount > Decimal("9999999999.99"):
            raise InvalidOperation
        amount = amount.quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        print("Enter a valid positive amount with at most two decimal places.")
        return
    description = input("Description (synthetic/demo only, optional): ").strip()[:255] or None

    try:
        rows = fetch_all("""
            SELECT COALESCE(SUM(CASE WHEN transaction_type='DEPOSIT' THEN amount
                                     WHEN transaction_type='WITHDRAWAL' THEN -amount END),0) AS balance
            FROM transactions WHERE account_id=%s
        """, (account_id,))
        account_exists = fetch_all("SELECT account_id FROM accounts WHERE account_id=%s", (account_id,))
        if not account_exists:
            print("Account ID not found.")
            return
        balance = Decimal(str(rows[0]["balance"] or 0))
        if kind == "WITHDRAWAL" and amount > balance:
            print(f"Withdrawal rejected: simulated balance is {money(balance)}.")
            return
        execute("""
            INSERT INTO transactions (account_id, transaction_type, amount, description_optional)
            VALUES (%s, %s, %s, %s)
        """, (account_id, kind, str(amount), description))
        print("Transaction recorded in the demo database.")
    except Exception as exc:
        print(f"Database operation failed: {exc}")

def show_review_flags():
    df = review_flags()
    if df.empty:
        print("No transactions currently meet the demo review rule.")
    else:
        print("\nREVIEW FLAGS — flags are not fraud determinations")
        print(df.to_string(index=False))

def main():
    print("BANKING TRANSACTION ANALYSIS SYSTEM")
    print("Educational simulation only | Synthetic data only")
    while True:
        print("""
1. View account summaries
2. View monthly report
3. Add synthetic customer/account (admin PIN)
4. Record deposit/withdrawal (admin PIN)
5. Export CSV reports and generate charts (admin PIN)
6. Show transactions flagged for review
0. Exit
""")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            show_accounts()
        elif choice == "2":
            show_monthly()
        elif choice == "3":
            add_customer_account()
        elif choice == "4":
            record_transaction()
        elif choice == "5":
            if admin_check():
                try:
                    export_reports()
                except Exception as exc:
                    print(f"Could not generate reports: {exc}")
        elif choice == "6":
            show_review_flags()
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Select 0-6.")

if __name__ == "__main__":
    main()
