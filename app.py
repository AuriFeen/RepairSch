from flask import Flask, request, jsonify, render_template
import sqlite3, random

app = Flask(__name__)
DB_FILE = 'repairs.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS repairs 
            (id INTEGER PRIMARY KEY, custom_id TEXT, name TEXT, phone TEXT, details TEXT, status TEXT)''')

@app.route('/')
def index(): 
    return render_template('dash.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    q = request.args.get('q', '')
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        tasks = conn.execute("SELECT * FROM repairs WHERE status IN ('active', 'pickup') AND (name LIKE ? OR phone LIKE ? OR custom_id LIKE ?)", 
                             (f'%{q}%', f'%{q}%', f'%{q}%')).fetchall()
        return jsonify([dict(t) for t in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    custom_id = str(random.randint(10000, 99999))
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('INSERT INTO repairs (custom_id, name, phone, details, status) VALUES (?,?,?,?,?)',
                     (custom_id, data['name'], data['phone'], data['details'], 'active'))
    return jsonify({"status": "success"})

@app.route('/api/tasks/<int:task_id>/move', methods=['PUT'])
def move_task(task_id):
    new_status = request.json['status']
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('UPDATE repairs SET status = ? WHERE id = ?', (new_status, task_id))
    return jsonify({"status": "success", "sms_sent": True})

@app.route('/api/archive', methods=['GET'])
def get_archive():
    q = request.args.get('q', '')
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        tasks = conn.execute("SELECT * FROM repairs WHERE status = 'archive' AND (name LIKE ? OR phone LIKE ? OR custom_id LIKE ?)", 
                             (f'%{q}%', f'%{q}%', f'%{q}%')).fetchall()
        return jsonify([dict(t) for t in tasks])

@app.route('/api/archive/clear', methods=['DELETE'])
def clear_archive():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM repairs WHERE status = 'archive'")
    return jsonify({"status": "success"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
