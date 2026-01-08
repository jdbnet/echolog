import os
import pytz
import logging
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime, date as datedate, datetime as dt
from dotenv import load_dotenv

load_dotenv()

__version__ = os.getenv('VERSION', 'unknown')

app = Flask(__name__)

TIMEZONE = os.getenv('TZ', 'UTC')
tz = pytz.timezone(TIMEZONE)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'defaultsecret')
app.config['LOGIN_ENABLED'] = os.getenv('LOGIN_ENABLED', 'false').lower() == 'true'

# Database configuration
DB_TYPE = os.getenv('DB_TYPE', 'mysql').lower()

if DB_TYPE == 'mysql':
    import mysql.connector
    mysql_config = {
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'database': os.getenv('MYSQL_DATABASE', 'echolog')
    }
elif DB_TYPE == 'sqlite':
    SQLITE_DB = os.getenv('SQLITE_DB', 'echolog.db')
else:
    raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}. Use 'sqlite' or 'mysql'")

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

def get_db_connection():
    if DB_TYPE == 'mysql':
        return mysql.connector.connect(**mysql_config)
    elif DB_TYPE == 'sqlite':
        conn = sqlite3.connect(SQLITE_DB)
        conn.row_factory = sqlite3.Row
        return conn

def dict_from_row(row):
    """Convert database row to dictionary"""
    if DB_TYPE == 'mysql':
        return row
    elif DB_TYPE == 'sqlite':
        return dict(row) if row else None

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    if DB_TYPE == 'mysql':
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entry (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            content TEXT NOT NULL
        );
        """)
    elif DB_TYPE == 'sqlite':
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            content TEXT NOT NULL
        );
        """)
    conn.commit()
    cursor.close()
    conn.close()

def calculate_streak():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT date FROM journal_entry ORDER BY date DESC")
    if DB_TYPE == 'mysql':
        dates = [row[0] for row in cursor.fetchall()]
    elif DB_TYPE == 'sqlite':
        dates = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    if not dates:
        return 0
    streak = 0
    today = datetime.now(tz).date()
    from datetime import timedelta
    for i, entry_date in enumerate(dates):
        # entry_date is a date object or string, ensure date object
        if isinstance(entry_date, str):
            entry_date = dt.strptime(entry_date, "%Y-%m-%d").date()
        if i == 0:
            # First entry: must be today or yesterday to start streak
            if entry_date == today:
                streak = 1
            elif entry_date == today - timedelta(days=1):
                streak = 1
                today = entry_date
            else:
                break
        else:
            expected = today - timedelta(days=1)
            if entry_date == expected:
                streak += 1
                today = entry_date
            else:
                break
    return streak

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 7
    offset = (page - 1) * per_page
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if DB_TYPE == 'mysql':
        cursor.execute("SELECT SQL_CALC_FOUND_ROWS * FROM journal_entry ORDER BY date DESC LIMIT %s OFFSET %s", (per_page, offset))
        entries = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS() as total")
        total = cursor.fetchone()['total']
    elif DB_TYPE == 'sqlite':
        cursor.execute("SELECT COUNT(*) as total FROM journal_entry")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM journal_entry ORDER BY date DESC LIMIT ? OFFSET ?", (per_page, offset))
        entries = [dict_from_row(row) for row in cursor.fetchall()]
    
    today = datetime.now(tz).date().isoformat()
    cursor.execute("SELECT * FROM journal_entry WHERE date = ?" if DB_TYPE == 'sqlite' else "SELECT * FROM journal_entry WHERE date = %s", (today,))
    todays_entry = cursor.fetchone()
    if DB_TYPE == 'sqlite' and todays_entry:
        todays_entry = dict_from_row(todays_entry)
    
    cursor.close()
    conn.close()
    has_prev = page > 1
    has_next = offset + per_page < total
    now = datetime.now(tz)
    streak = calculate_streak()
    return render_template('index.html', entries=entries, today=today, page=page, has_prev=has_prev, has_next=has_next, now=now, todays_entry=todays_entry, streak=streak, version=__version__)

@app.route('/add', methods=['POST'])
def add_entry():
    date = request.form.get('date', datetime.now(tz).strftime('%Y-%m-%d'))
    content = request.form.get('content', '')
    if content.strip():
        conn = get_db_connection()
        cursor = conn.cursor()
        param_marker = "?" if DB_TYPE == 'sqlite' else "%s"
        cursor.execute(f"SELECT id FROM journal_entry WHERE date = {param_marker}", (date,))
        existing = cursor.fetchone()
        if existing:
            cursor.execute(f"UPDATE journal_entry SET content = {param_marker} WHERE date = {param_marker}", (content, date))
        else:
            cursor.execute(f"INSERT INTO journal_entry (date, content) VALUES ({param_marker}, {param_marker})", (date, content))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/entry_for_date')
def entry_for_date():
    date = request.args.get('date')
    if not date:
        return jsonify({'content': ''})
    conn = get_db_connection()
    cursor = conn.cursor()
    param_marker = "?" if DB_TYPE == 'sqlite' else "%s"
    cursor.execute(f"SELECT content FROM journal_entry WHERE date = {param_marker}", (date,))
    entry = cursor.fetchone()
    cursor.close()
    conn.close()
    if DB_TYPE == 'sqlite':
        content = entry[0] if entry else ''
    else:
        content = entry['content'] if entry else ''
    return jsonify({'content': content})

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    date = request.args.get('date', None)
    conn = get_db_connection()
    cursor = conn.cursor()
    if DB_TYPE == 'mysql':
        sql = "SELECT * FROM journal_entry WHERE 1=1"
        params = []
        if query:
            sql += " AND content LIKE %s"
            params.append(f"%{query}%")
        if date:
            sql += " AND date = %s"
            params.append(date)
        sql += " ORDER BY date DESC"
        cursor.execute(sql, params)
        entries = cursor.fetchall()
    elif DB_TYPE == 'sqlite':
        sql = "SELECT * FROM journal_entry WHERE 1=1"
        params = []
        if query:
            sql += " AND content LIKE ?"
            params.append(f"%{query}%")
        if date:
            sql += " AND date = ?"
            params.append(date)
        sql += " ORDER BY date DESC"
        cursor.execute(sql, params)
        entries = [dict_from_row(row) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    today = datetime.now(tz).date().isoformat()
    now = datetime.now(tz)
    page = 1
    has_prev = False
    has_next = False
    return render_template('index.html', entries=entries, today=today, now=now, page=page, has_prev=has_prev, has_next=has_next, version=__version__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not app.config['LOGIN_ENABLED']:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == os.getenv('LOGIN_USERNAME', 'admin') and password == os.getenv('LOGIN_PASSWORD', 'admin'):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.before_request
def require_login():
    if app.config['LOGIN_ENABLED'] and not session.get('logged_in') and request.endpoint not in ['login', 'static']:
        return redirect(url_for('login'))

@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    param_marker = "?" if DB_TYPE == 'sqlite' else "%s"
    
    if request.method == 'POST':
        date = request.form.get('date')
        content = request.form.get('content')
        cursor.execute(f"UPDATE journal_entry SET date={param_marker}, content={param_marker} WHERE id={param_marker}", (date, content, entry_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    else:
        cursor.execute(f"SELECT * FROM journal_entry WHERE id={param_marker}", (entry_id,))
        entry = cursor.fetchone()
        cursor.close()
        conn.close()
        if not entry:
            return redirect(url_for('index'))
        if DB_TYPE == 'sqlite':
            entry = dict_from_row(entry)
        return render_template('edit.html', entry=entry)

@app.route('/edit_modal', methods=['POST'])
def edit_entry_modal():
    entry_id = request.form.get('id')
    date = request.form.get('date')
    content = request.form.get('content')
    if entry_id and date and content:
        conn = get_db_connection()
        cursor = conn.cursor()
        param_marker = "?" if DB_TYPE == 'sqlite' else "%s"
        cursor.execute(f"UPDATE journal_entry SET date={param_marker}, content={param_marker} WHERE id={param_marker}", (date, content, entry_id))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    param_marker = "?" if DB_TYPE == 'sqlite' else "%s"
    cursor.execute(f"DELETE FROM journal_entry WHERE id={param_marker}", (entry_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))

init_db()
logging.info('EchoLog started up successfully.')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')