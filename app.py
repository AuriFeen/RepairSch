from flask import Flask, request, jsonify, render_template
import sqlite3
import os
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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
        "message": f"Γεια σας. Το ρολοί σας είναι έτοιμο, μπορείτε νασ το πάρετε από την Αγίου Ανδρέου 79 κάθε μέρα 9-2! ."
    }
    try:
        # Added a 5-second timeout so the dashboard doesn't freeze if the phone is offline
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
    with get_db_connection() as conn:
        tasks = conn.execute('SELECT * FROM repairs').fetchall()
    return jsonify([dict(t) for t in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    if not data.get('name') or not data.get('phone'):
        return jsonify({"error": "Name and phone required"}), 400
        
    with get_db_connection() as conn:
        conn.execute('INSERT INTO repairs (name, phone, details, status) VALUES (?, ?, ?, ?)',
                     (data['name'], data['phone'], data['details'], 'active'))
        conn.commit()
    return jsonify({"status": "success"})

@app.route('/api/tasks/<int:task_id>/move', methods=['PUT'])
def move_task(task_id):
    data = request.json
    new_status = data['status']
    sms_sent = False
    
    with get_db_connection() as conn:
        task = conn.execute('SELECT * FROM repairs WHERE id = ?', (task_id,)).fetchone()
        if not task:
            return jsonify({"error": "Task not found"}), 404
            
        # Update the status in the database
        conn.execute('UPDATE repairs SET status = ? WHERE id = ?', (new_status, task_id))
        conn.commit()
        
        # AUTOMATIC SMS LOGIC: Only send if moving TO pickup queue FROM somewhere else
        if new_status == 'pickup' and task['status'] != 'pickup':
            sms_sent = send_sms(task['phone'], task['name'])
            
    return jsonify({"status": "success", "sms_sent": sms_sent})

@app.route('/api/tasks/trash', methods=['DELETE'])
def empty_trash():
    with get_db_connection() as conn:
        conn.execute("DELETE FROM repairs WHERE status = 'trash'")
        conn.commit()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
