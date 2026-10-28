from db import get_connection

CUSTOMERS = [
    ("Aarav Demo", "SAVINGS", [
        ("DEPOSIT", 12000, "Demo opening deposit"),
        ("WITHDRAWAL", 1500, "Demo grocery expense"),
        ("DEPOSIT", 7000, "Demo salary credit"),
    ]),
    ("Diya Sample", "SAVINGS", [
        ("DEPOSIT", 25000, "Demo opening deposit"),
        ("WITHDRAWAL", 4000, "Demo utility bills"),
        ("WITHDRAWAL", 800, "Demo transport"),
    ]),
    ("Kabir Example", "CURRENT", [
        ("DEPOSIT", 80000, "Demo business receipt"),
        ("WITHDRAWAL", 12000, "Demo supplier payment"),
        ("DEPOSIT", 52000, "Demo invoice receipt - review threshold example"),
    ]),
]

def main():
    conn = get_connection()
    try:
        cur = conn.cursor()
        for name, account_type, transactions in CUSTOMERS:
            cur.execute("SELECT customer_id FROM customers WHERE display_name=%s", (name,))
            found = cur.fetchone()
            if found:
                print(f"Skipping existing sample customer: {name}")
                continue
            cur.execute("INSERT INTO customers (display_name) VALUES (%s)", (name,))
            customer_id = cur.lastrowid
            cur.execute(
                "INSERT INTO accounts (customer_id, account_type) VALUES (%s, %s)",
                (customer_id, account_type),
            )
            account_id = cur.lastrowid
            for kind, amount, description in transactions:
                cur.execute("""
                    INSERT INTO transactions
                    (account_id, transaction_type, amount, description_optional)
                    VALUES (%s, %s, %s, %s)
                """, (account_id, kind, amount, description))
        conn.commit()
        print("Synthetic sample data is ready.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
