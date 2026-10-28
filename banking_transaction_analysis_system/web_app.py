
from flask import Flask, render_template_string
from db import fetch_all

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Banking Analysis Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            margin: 0;
            color: #1e293b;
        }
        header {
            background: #123b70;
            color: white;
            padding: 25px;
            text-align: center;
        }
        main {
            max-width: 1100px;
            margin: 25px auto;
            padding: 15px;
        }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .card, .panel {
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 3px 12px #00000010;
        }
        .amount {
            font-size: 24px;
            font-weight: bold;
            color: #123b70;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }
        th, td {
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
            text-align: left;
        }
        th { background: #eaf0f8; }
        .table-wrap { overflow-x: auto; }
        .error {
            background: #fee2e2;
            color: #991b1b;
            padding: 15px;
            border-radius: 8px;
        }
        footer {
            text-align: center;
            padding: 20px;
            color: #64748b;
        }
    </style>
</head>
<body>
<header>
    <h1>Banking Transaction Analysis System</h1>
    <p>Account Management & Financial Analytics</p>
</header>

<main>
    <h2>Dashboard</h2>

    {% if error %}
        <div class="error">
            Unable to load MySQL data: {{ error }}
            <p>Check your database connection and table names.</p>
        </div>
    {% else %}
        <div class="cards">
            <div class="card">
                <h3>Total Accounts</h3>
                <div class="amount">{{ accounts|length }}</div>
            </div>
            <div class="card">
                <h3>Total Deposits</h3>
                <div class="amount">₹{{ "%.2f"|format(total_deposits) }}</div>
            </div>
            <div class="card">
                <h3>Total Withdrawals</h3>
                <div class="amount">₹{{ "%.2f"|format(total_withdrawals) }}</div>
            </div>
        </div>

        <section class="panel">
            <h2>Account Summaries</h2>
            <div class="table-wrap">
            <table>
                <tr>
                    <th>Account ID</th>
                    <th>Customer</th>
                    <th>Account Type</th>
                    <th>Deposits (₹)</th>
                    <th>Withdrawals (₹)</th>
                    <th>Balance (₹)</th>
                </tr>
                {% for a in accounts %}
                <tr>
                    <td>{{ a.account_id }}</td>
                    <td>{{ a.display_name }}</td>
                    <td>{{ a.account_type }}</td>
                    <td>{{ "%.2f"|format(a.deposits or 0) }}</td>
                    <td>{{ "%.2f"|format(a.withdrawals or 0) }}</td>
                    <td>{{ "%.2f"|format(a.balance or 0) }}</td>
                </tr>
                {% else %}
                <tr><td colspan="6">No accounts found.</td></tr>
                {% endfor %}
            </table>
            </div>
        </section>

        <section class="panel">
            <h2>Recent Transactions</h2>
            <div class="table-wrap">
            <table>
                <tr>
                    <th>Transaction ID</th>
                    <th>Account ID</th>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Amount (₹)</th>
                    <th>Description</th>
                </tr>
                {% for t in transactions %}
                <tr>
                    <td>{{ t.transaction_id }}</td>
                    <td>{{ t.account_id }}</td>
                    <td>{{ t.transaction_date }}</td>
                    <td>{{ t.transaction_type }}</td>
                    <td>{{ "%.2f"|format(t.amount) }}</td>
                    <td>{{ t.description or "-" }}</td>
                </tr>
                {% else %}
                <tr><td colspan="6">No transactions found.</td></tr>
                {% endfor %}
            </table>
            </div>
        </section>
    {% endif %}
    <p>Educational demo using synthetic data only.</p>
</main>
<footer>Banking Transaction Analysis System | Student Project</footer>
</body>
</html>
"""


@app.route("/")
def home():
    try:
        accounts = fetch_all("""
            SELECT
                a.account_id,
                c.display_name,
                a.account_type,
                COALESCE(SUM(
                    CASE WHEN UPPER(t.transaction_type) = 'DEPOSIT'
                    THEN t.amount ELSE 0 END
                ), 0) AS deposits,
                COALESCE(SUM(
                    CASE WHEN UPPER(t.transaction_type) = 'WITHDRAWAL'
                    THEN t.amount ELSE 0 END
                ), 0) AS withdrawals,
                COALESCE(SUM(
                    CASE
                        WHEN UPPER(t.transaction_type) = 'DEPOSIT'
                        THEN t.amount
                        WHEN UPPER(t.transaction_type) = 'WITHDRAWAL'
                        THEN -t.amount
                        ELSE 0
                    END
                ), 0) AS balance
            FROM accounts a
            JOIN customers c ON c.customer_id = a.customer_id
            LEFT JOIN transactions t ON t.account_id = a.account_id
            GROUP BY a.account_id, c.display_name, a.account_type
            ORDER BY a.account_id
        """)

        transactions = fetch_all("""
            SELECT transaction_id, account_id, transaction_date,
                   transaction_type, amount,
                   description_optional AS description
            FROM transactions
            ORDER BY transaction_id DESC
            LIMIT 20
        """)

        total_deposits = sum(float(a["deposits"] or 0) for a in accounts)
        total_withdrawals = sum(float(a["withdrawals"] or 0) for a in accounts)

        return render_template_string(
            HTML,
            accounts=accounts,
            transactions=transactions,
            total_deposits=total_deposits,
            total_withdrawals=total_withdrawals,
            error=None
        )

    except Exception as e:
        app.logger.exception("Unable to load dashboard")
        return render_template_string(
            HTML,
            accounts=[],
            transactions=[],
            total_deposits=0,
            total_withdrawals=0,
            error=str(e)
        ), 500


if __name__ == "__main__":
    app.run(debug=True)
