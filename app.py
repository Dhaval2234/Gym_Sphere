from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym_members.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    join_date = db.Column(db.String(10), nullable=False)
    end_date = db.Column(db.String(10), nullable=False)
    mobile_num = db.Column(db.String(15), nullable=False)
    status = db.Column(db.String(20), nullable=False)

@app.route('/')
def index():
    members = Member.query.all()
    today = datetime.today().date()
    for m in members:
        # Calculate subscription status based on end_date (assumed format: yyyy-mm-dd)
        try:
            ed = datetime.strptime(m.end_date, "%Y-%m-%d").date()
            if ed < today:
                m.status = "Expired"
            elif (ed - today).days <= 7:
                m.status = "Near Expiry"
            else:
                m.status = "Active"
        except Exception:
            m.status = "Invalid Date"
        
        # Format join_date to dd mm yyyy
        try:
            jd = datetime.strptime(m.join_date, "%Y-%m-%d")
            m.join_date = jd.strftime("%d %m %Y")
        except Exception:
            pass
        
        # Format end_date to dd mm yyyy
        try:
            edt = datetime.strptime(m.end_date, "%Y-%m-%d")
            m.end_date = edt.strftime("%d %m %Y")
        except Exception:
            pass

    return render_template('index.html', members=members)

@app.route('/add_member', methods=['POST'])
def add_member():
    name = request.form['name']
    join_date = request.form['join_date']
    end_date = request.form['end_date']
    mobile_num = request.form['mobile_num']
    status = 'Active'
    
    new_member = Member(name=name, join_date=join_date, end_date=end_date, mobile_num=mobile_num, status=status)
    db.session.add(new_member)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_member/<int:member_id>')
def delete_member(member_id):
    member = Member.query.get(member_id)
    if member:
        db.session.delete(member)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
