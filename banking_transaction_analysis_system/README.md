# Banking Transaction Analysis System

An educational Python + MySQL project using **synthetic data only**. It records deposits and withdrawals, produces account/monthly summaries, computes transaction statistics, and creates charts.

> **Important:** This is a classroom simulation, not a real banking platform. Balances are calculated from demo transactions and are not real account balances. The unusual-activity rule only flags transactions for human review; it does not assert fraud.

## Features
- MySQL tables for customers, accounts, and transactions
- Add synthetic customers/accounts and record deposits/withdrawals
- Validate transaction type and positive amount
- Prevent demo withdrawals that exceed the simulated balance
- Account-wise and monthly reports
- NumPy statistics and Pandas groupings
- Matplotlib charts saved to `reports/`
- Basic local demo access control: write actions ask for a demo admin PIN
- CSV report exports

## 1. Requirements
- Python 3.10 or newer
- MySQL Server 8.x (running locally)
- MySQL Workbench is optional

## 2. Create the database
Open MySQL Workbench or the MySQL command line and run:

```sql
SOURCE C:/path/to/banking_transaction_analysis_system/sql/schema.sql;
```

Replace the path with the actual path to this project's `sql/schema.sql`. In Workbench, you can also open `sql/schema.sql` and click the lightning-bolt Execute button.

The script creates the database `banking_analysis` and the three required tables.

## 3. Configure Python
Open a terminal in the project folder.

### Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, use:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Edit `.env` and enter your own local MySQL username/password. Do not commit `.env` to Git.

Example:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=banking_analysis
DB_USER=root
DB_PASSWORD=your_mysql_password
ADMIN_PIN=2468
```

`ADMIN_PIN` is only a simple classroom demo gate, not production-grade authentication.

## 4. Seed synthetic sample data
With the virtual environment active:
```powershell
py seed.py
```
The seed script adds demo records only if the sample customer names are not already present.

## 5. Run the application
```powershell
py app.py
```

Use the menu:
1. View account summaries
2. View monthly report
3. Add a synthetic customer and account (admin PIN)
4. Record a deposit/withdrawal (admin PIN)
5. Export reports and generate charts (admin PIN)
6. Show transactions flagged for review
0. Exit

For testing, the sample database includes fictional names and transaction descriptions. Enter a positive amount. The app prevents a withdrawal greater than the simulated balance.

## 6. Generated outputs
After choosing **Export reports and generate charts**, check:
- `reports/account_summary.csv`
- `reports/monthly_summary.csv`
- `reports/transaction_type_totals.png`
- `reports/monthly_transaction_trend.png`
- `reports/review_flags.csv`

These are generated outputs. CSVs and charts are not committed to Git by default.

## 7. Push the project to GitHub
First, create a **new empty repository** on GitHub (do not add README/license if you already have them here). Then in PowerShell, from this project folder:

```powershell
git init
git add .
git status
git commit -m "Initial banking transaction analysis project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/banking-transaction-analysis-system.git
git push -u origin main
```

Replace the URL with your own repository URL. If Git says `remote origin already exists`, run:
```powershell
git remote -v
git remote set-url origin https://github.com/YOUR-USERNAME/banking-transaction-analysis-system.git
```

### Before pushing
- Check that `.env` is not listed by `git status`.
- Never upload database passwords, real customer information, credentials, or private keys.
- If Git is not installed, install Git for Windows and reopen PowerShell.
- If Git asks you to sign in, follow the browser authentication prompt.

## Troubleshooting
- **Can't connect to MySQL:** Check that MySQL Server is running, port is `3306`, and `.env` credentials are correct.
- **`ModuleNotFoundError`:** Activate `.venv` and run `py -m pip install -r requirements.txt`.
- **`Access denied for user`:** Check `DB_USER` and `DB_PASSWORD` in `.env`.
- **Charts do not appear:** They are saved as PNG files in `reports/`; open them from File Explorer.
