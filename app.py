from flask import Flask, request, jsonify, render_template
import sqlite3
import random
import os
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Note: Ensure you have a 'templates' folder and put 'dash.html' inside it
DB_FILE = os.path.join(BASE_DIR, 'repairs.db')
GATEWAY_URL = "http://192.168.1.47:8080/send-sms"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS repairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                custom_id TEXT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                details TEXT,
                status TEXT NOT NULL DEFAULT 'active'
            )
        ''')
        conn.commit()

def send_sms(phone, name):
    payload = {
        "number": phone,
        "message": f"Γεια σας, το ρολόι σας είναι έτοιμο. Μπορείτε να έρθετε να το παραλάβετε από την Αγίου Ανδρέου 79 κάθε μέρα 9 με 2! -Σας ευχαριστώ πολύ, Παναγιώτης Κωτσάκης"
    }
    try:
        response = requests.post(GATEWAY_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"SMS Gateway Error: {e}")
        return False

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('dash.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    # Only returns active and pickup tasks (excludes archive)
    q = request.args.get('q', '')
    with get_db_connection() as conn:
        if q:
            tasks = conn.execute(
                "SELECT * FROM repairs WHERE status != 'archive' AND (name LIKE ? OR phone LIKE ? OR custom_id LIKE ?)", 
                (f'%{q}%', f'%{q}%', f'%{q}%')
            ).fetchall()
        else:
            tasks = conn.execute("SELECT * FROM repairs WHERE status != 'archive'").fetchall()
            
    return jsonify([dict(t) for t in tasks])

@app.route('/api/archive', methods=['GET'])
def get_archive():
    # Only returns archived tasks
    q = request.args.get('q', '')
    with get_db_connection() as conn:
        if q:
            tasks = conn.execute(
                "SELECT * FROM repairs WHERE status = 'archive' AND (name LIKE ? OR phone LIKE ? OR custom_id LIKE ?)", 
                (f'%{q}%', f'%{q}%', f'%{q}%')
            ).fetchall()
        else:
            tasks = conn.execute("SELECT * FROM repairs WHERE status = 'archive'").fetchall()
            
    return jsonify([dict(t) for t in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    if not data.get('name') or not data.get('phone'):
        return jsonify({"error": "Name and phone required"}), 400
        
    custom_id = str(random.randint(10000, 99999))
        
    with get_db_connection() as conn:
        conn.execute('INSERT INTO repairs (custom_id, name, phone, details, status) VALUES (?, ?, ?, ?, ?)',
                     (custom_id, data['name'], data['phone'], data['details'], 'active'))
        conn.commit()
    return jsonify({"status": "success", "custom_id": custom_id})

@app.route('/api/tasks/<int:task_id>/move', methods=['PUT'])
def move_task(task_id):
    data = request.json
    new_status = data['status']
    sms_sent = False
    
    with get_db_connection() as conn:
        task = conn.execute('SELECT * FROM repairs WHERE id = ?', (task_id,)).fetchone()
        if not task:
            return jsonify({"error": "Task not found"}), 404
            
        conn.execute('UPDATE repairs SET status = ? WHERE id = ?', (new_status, task_id))
        conn.commit()
        
        # SMS logic
        if new_status == 'pickup' and task['status'] != 'pickup':
            sms_sent = send_sms(task['phone'], task['name'])
            
    return jsonify({"status": "success", "sms_sent": sms_sent})

@app.route('/api/archive/clear', methods=['DELETE'])
def clear_archive():
    with get_db_connection() as conn:
        conn.execute("DELETE FROM repairs WHERE status = 'archive'")
        conn.commit()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
