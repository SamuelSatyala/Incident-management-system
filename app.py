from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Simple static login (for project)
        if username == "admin" and password == "admin":
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return "Invalid Credentials"

    return render_template('login.html')

@app.route('/guest')
def guest():
    session['user'] = "guest"
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------- HOME ----------------
@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    incidents = conn.execute('SELECT * FROM incidents').fetchall()
    conn.close()

    return render_template('index.html', incidents=incidents)

# ---------------- CREATE ----------------
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        priority = request.form['priority']
        status = request.form['status']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO incidents (title, description, priority, status) VALUES (?, ?, ?, ?)',
            (title, description, priority, status)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('create.html')

# ---------------- UPDATE ----------------
@app.route('/update/<int:id>', methods=('GET', 'POST'))
def update(id):
    conn = get_db_connection()
    incident = conn.execute('SELECT * FROM incidents WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        priority = request.form['priority']
        status = request.form['status']

        conn.execute(
            'UPDATE incidents SET title=?, description=?, priority=?, status=? WHERE id=?',
            (title, description, priority, status, id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    conn.close()
    return render_template('update.html', incident=incident)

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM incidents WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)