from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        activity TEXT,
        accommodation TEXT,
        nights INTEGER,
        expectations TEXT
    )''')
    conn.commit()
    conn.close()

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    activity = request.form['activity']
    accommodation = request.form['accommodation']
    nights = request.form['nights']
    expectations = request.form['expectations']

    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute("INSERT INTO clients (name, activity, accommodation, nights, expectations) VALUES (?, ?, ?, ?, ?)",
              (name, activity, accommodation, nights, expectations))
    conn.commit()
    conn.close()
    return "Thank you! Your details have been submitted."

if __name__ == '__main__':
    init_db()
app.run(host='0.0.0.0', port=5000 , debug=True)