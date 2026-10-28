from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from db import fetch_all

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

def transaction_frame():
    rows = fetch_all("""
        SELECT t.transaction_id, t.account_id, c.display_name,
               t.transaction_date, t.transaction_type, t.amount,
               t.description_optional
        FROM transactions t
        JOIN accounts a ON a.account_id = t.account_id
        JOIN customers c ON c.customer_id = a.customer_id
        ORDER BY t.transaction_date
    """)
    df = pd.DataFrame(rows)
    if not df.empty:
        df["transaction_date"] = pd.to_datetime(df["transaction_date"])
        df["amount"] = pd.to_numeric(df["amount"])
    return df

def account_summary():
    rows = fetch_all("""
        SELECT a.account_id, c.display_name, a.account_type,
               COALESCE(SUM(CASE WHEN t.transaction_type='DEPOSIT' THEN t.amount ELSE 0 END),0) AS total_deposits,
               COALESCE(SUM(CASE WHEN t.transaction_type='WITHDRAWAL' THEN t.amount ELSE 0 END),0) AS total_withdrawals,
               COALESCE(SUM(CASE WHEN t.transaction_type='DEPOSIT' THEN t.amount
                                 WHEN t.transaction_type='WITHDRAWAL' THEN -t.amount ELSE 0 END),0) AS simulated_balance,
               COUNT(t.transaction_id) AS transaction_count
        FROM accounts a
        JOIN customers c ON c.customer_id = a.customer_id
        LEFT JOIN transactions t ON t.account_id = a.account_id
        GROUP BY a.account_id, c.display_name, a.account_type
        ORDER BY a.account_id
    """)
    return pd.DataFrame(rows)

def monthly_summary():
    df = transaction_frame()
    if df.empty:
        return pd.DataFrame(columns=["month", "transaction_type", "transaction_count", "total_amount"])
    df["month"] = df["transaction_date"].dt.to_period("M").astype(str)
    return (df.groupby(["month", "transaction_type"], as_index=False)
              .agg(transaction_count=("transaction_id", "count"),
                   total_amount=("amount", "sum"))
              .sort_values(["month", "transaction_type"]))

def review_flags():
    df = transaction_frame()
    if df.empty:
        return df
    # Simple demo rule: flag any single transaction of 50,000 or more.
    # This is only a review flag, not a claim of fraud.
    flagged = df[df["amount"] >= 50000].copy()
    if not flagged.empty:
        flagged["review_reason"] = "Amount is at or above the demo review threshold (50000)"
    return flagged

def export_reports():
    accounts = account_summary()
    monthly = monthly_summary()
    df = transaction_frame()
    flags = review_flags()

    accounts.to_csv(REPORT_DIR / "account_summary.csv", index=False)
    monthly.to_csv(REPORT_DIR / "monthly_summary.csv", index=False)
    flags.to_csv(REPORT_DIR / "review_flags.csv", index=False)

    if df.empty:
        print("No transactions found. CSV reports were created; charts skipped.")
        return

    totals = (df.groupby("transaction_type")["amount"].sum()
                .reindex(["DEPOSIT", "WITHDRAWAL"], fill_value=0))
    plt.figure(figsize=(7, 5))
    totals.plot(kind="bar")
    plt.title("Deposits vs Withdrawals")
    plt.xlabel("Transaction type")
    plt.ylabel("Total amount")
    plt.tight_layout()
    plt.savefig(REPORT_DIR / "transaction_type_totals.png", dpi=150)
    plt.close()

    df["month"] = df["transaction_date"].dt.to_period("M").astype(str)
    trend = df.groupby(["month", "transaction_type"])["amount"].sum().unstack(fill_value=0)
    trend.plot(kind="line", marker="o", figsize=(8, 5))
    plt.title("Monthly Transaction Trend")
    plt.xlabel("Month")
    plt.ylabel("Total amount")
    plt.tight_layout()
    plt.savefig(REPORT_DIR / "monthly_transaction_trend.png", dpi=150)
    plt.close()

    values = df["amount"].to_numpy(dtype=float)
    print(f"Transactions: {len(values)}")
    print(f"Mean amount: {np.mean(values):.2f}")
    print(f"Median amount: {np.median(values):.2f}")
    print(f"Standard deviation: {np.std(values):.2f}")
    print(f"Reports and charts saved in: {REPORT_DIR.resolve()}")
