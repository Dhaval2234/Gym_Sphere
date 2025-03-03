from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from supabase import create_client, Client

app = Flask(__name__)

supabase_url = "https://rfvbyzumbdmofkcyywoj.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJmdmJ5enVtYmRtb2ZrY3l5d29qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA4MzgwNjYsImV4cCI6MjA1NjQxNDA2Nn0.sPUY74XDEDtAA1IbS8H_Wqu_sTq_gR62zsY9wpBREkM"
supabase: Client = create_client(supabase_url, supabase_key)

@app.route('/')
def index():
    response = supabase.table('members').select('*').execute()
    members = response.data
    today = datetime.today().date()
    
    for member in members:
        try:
            end_date = datetime.strptime(member['end_date'], "%Y-%m-%d").date()
            member['status'] = (
                "Expired" if end_date < today else
                "Near Expiry" if (end_date - today).days <= 7 else
                "Active"
            )
        except Exception:
            member['status'] = "Invalid Date"
        
        for date_field in ['join_date', 'end_date']:
            try:
                dt = datetime.strptime(member[date_field], "%Y-%m-%d")
                member[date_field] = dt.strftime("%d %m %Y")
            except Exception:
                pass

    return render_template('index.html', members=members)

@app.route('/add_member', methods=['POST'])
def add_member():
    member_data = {
        'name': request.form['name'],
        'email': request.form['email'],
        'join_date': request.form['join_date'],
        'end_date': request.form['end_date'],
        'phone': request.form['phone']  # Match Supabase column name
    }
    supabase.table('members').insert(member_data).execute()
    return redirect(url_for('index'))

@app.route('/delete_member/<int:member_id>')
def delete_member(member_id):
    supabase.table('members').delete().eq('id', member_id).execute()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)