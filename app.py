from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'  # Required for flash messages

# Supabase configuration
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
        except Exception as e:
            member['status'] = "Invalid Date"
        
        # Format dates for display
        for date_field in ['join_date', 'end_date']:
            try:
                dt = datetime.strptime(member[date_field], "%Y-%m-%d")
                member[date_field] = dt.strftime("%d/%m/%Y")
            except Exception as e:
                pass

    return render_template('index.html', members=members)

@app.route('/add_member', methods=['POST'])
def add_member():
    member_data = {
        'name': request.form['name'],
        'email': request.form['email'],
        'join_date': request.form['join_date'],
        'end_date': request.form['end_date'],
        'phone': request.form['phone'],
        'membership_type': request.form['membership_type']
    }
    
    try:
        supabase.table('members').insert(member_data).execute()
        flash('Member added successfully!', 'success')
    except Exception as e:
        flash('Error adding member: ' + str(e), 'error')
    
    return redirect(url_for('index'))

@app.route('/delete_member/<int:member_id>')
def delete_member(member_id):
    try:
        supabase.table('members').delete().eq('id', member_id).execute()
        flash('Member deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting member: ' + str(e), 'error')
    
    return redirect(url_for('index'))

@app.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    if request.method == 'GET':
        response = supabase.table('members').select('*').eq('id', member_id).execute()
        member = response.data[0] if response.data else None
        
        if not member:
            flash('Member not found', 'error')
            return redirect(url_for('index'))
            
        # Convert dates to HTML date input format
        for date_field in ['join_date', 'end_date']:
            try:
                dt = datetime.strptime(member[date_field], "%Y-%m-%d")
                member[date_field] = dt.strftime("%Y-%m-%d")
            except:
                pass
        
        return render_template('edit_member.html', member=member)
    
    if request.method == 'POST':
        updated_data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'join_date': request.form['join_date'],
            'end_date': request.form['end_date'],
            'membership_type': request.form['membership_type']
        }
        
        try:
            supabase.table('members').update(updated_data).eq('id', member_id).execute()
            flash('Member updated successfully!', 'success')
        except Exception as e:
            flash('Error updating member: ' + str(e), 'error')
        
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)