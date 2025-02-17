from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Database initialization
def init_db():
    conn = sqlite3.connect("gym.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test1 (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT NOT NULL,
            JOIN_DATE TEXT NOT NULL,
            END_DATE TEXT NOT NULL,
            MOBILE_NUM TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Convert string date to proper format
def format_datetime(value, format='%Y-%m-%d'):
    try:
        return datetime.strptime(value, '%Y-%m-%d').strftime(format)
    except ValueError:
        return "Invalid Date"

# Get subscription status
def get_subscription_status(end_date):
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    today = datetime.today()
    if end_date < today:
        return "Expired"
    elif (end_date - today) <= timedelta(days=7):  # Near expiry if within 7 days
        return "Near Expiry"
    else:
        return "Active"

# Register the filter for Jinja2
app.jinja_env.filters['strftime'] = format_datetime

@app.route("/")
def index():
    conn = sqlite3.connect("gym.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test1 ORDER BY END_DATE ASC")  # Sort by end date (ascending)
    members = cursor.fetchall()
    conn.close()

    # Convert to list of dictionaries for easy access in Jinja
    members_list = []
    for member in members:
        members_list.append({
            "id": member[0],
            "name": member[1],
            "join_date": member[2],
            "end_date": format_datetime(member[3]),  # Apply formatting
            "mobile_num": member[4],
            "status": get_subscription_status(member[3])  # Add status
        })

    return render_template("index.html", members=members_list)

@app.route("/add_member", methods=["POST"])
def add_member():
    name = request.form["name"]
    join_date = request.form["join_date"]
    end_date = request.form["end_date"]
    mobile_num = request.form["mobile_num"]

    conn = sqlite3.connect("gym.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO test1 (NAME, JOIN_DATE, END_DATE, MOBILE_NUM) VALUES (?, ?, ?, ?)", 
                   (name, join_date, end_date, mobile_num))
    conn.commit()
    conn.close()
    
    return redirect(url_for("index"))

@app.route("/delete_member/<int:member_id>", methods=["GET"])
def delete_member(member_id):
    conn = sqlite3.connect("gym.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM test1 WHERE ID = ?", (member_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()  # Ensure the database is initialized
    app.run(debug=True)