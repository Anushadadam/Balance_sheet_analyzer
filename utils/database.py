# utils/database.py
import sqlite3

DB_NAME = "data/financial_data.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False) # check_same_thread for Streamlit
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    """Creates the necessary tables if they don't exist and populates initial data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS companies (id INTEGER PRIMARY KEY, name TEXT UNIQUE, group_name TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS user_company_access (user_id INTEGER, company_id INTEGER, PRIMARY KEY (user_id, company_id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS financial_data (id INTEGER PRIMARY KEY, company_id INTEGER, year INTEGER, metric TEXT, value REAL, source_document TEXT, UNIQUE(company_id, year, metric))")

    # --- POPULATE INITIAL DATA (if tables are empty) ---
    if cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('analyst', 'password123', 'analyst'))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('jio_ceo', 'password123', 'ceo'))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('ambani', 'password123', 'top_management'))

    if cursor.execute("SELECT COUNT(*) FROM companies").fetchone()[0] == 0:
        cursor.execute("INSERT INTO companies (name, group_name) VALUES (?, ?)", ('Reliance Jio', 'Reliance'))
        cursor.execute("INSERT INTO companies (name, group_name) VALUES (?, ?)", ('Reliance Retail', 'Reliance'))

    if cursor.execute("SELECT COUNT(*) FROM user_company_access").fetchone()[0] == 0:
        cursor.execute("INSERT INTO user_company_access (user_id, company_id) VALUES ((SELECT id FROM users WHERE username='jio_ceo'), (SELECT id FROM companies WHERE name='Reliance Jio'))")

    conn.commit()
    conn.close()

def get_user(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def get_user_accessible_companies(user_id, role):
    conn = get_db_connection()
    if role == 'top_management' or role == 'analyst':
        companies = conn.execute('SELECT * FROM companies ORDER BY name').fetchall()
    elif role == 'ceo':
        companies = conn.execute('SELECT c.* FROM companies c JOIN user_company_access uca ON c.id = uca.company_id WHERE uca.user_id = ?', (user_id,)).fetchall()
    else:
        companies = []
    conn.close()
    return companies

def get_all_companies():
    conn = get_db_connection()
    companies = conn.execute('SELECT * FROM companies ORDER BY name').fetchall()
    conn.close()
    return companies

def save_financial_data(company_id, year, metrics, source_document):
    conn = get_db_connection()
    cursor = conn.cursor()
    for metric, value in metrics.items():
        try:
            cleaned_value = float(str(value).replace(',', '').replace('(', '-').replace(')', ''))
        except (ValueError, TypeError):
            cleaned_value = None
        if cleaned_value is not None:
            cursor.execute('INSERT OR REPLACE INTO financial_data (company_id, year, metric, value, source_document) VALUES (?, ?, ?, ?, ?)', (company_id, year, metric, cleaned_value, source_document))
    conn.commit()
    conn.close()

def get_company_financials(company_id):
    conn = get_db_connection()
    data = conn.execute('SELECT year, metric, value FROM financial_data WHERE company_id = ? ORDER BY year, metric', (company_id,)).fetchall()
    conn.close()
    return data