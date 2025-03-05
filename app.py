from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'

# Supabase configuration
supabase_url = "https://rfvbyzumbdmofkcyywoj.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJmdmJ5enVtYmRtb2ZrY3l5d29qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA4MzgwNjYsImV4cCI6MjA1NjQxNDA2Nn0.sPUY74XDEDtAA1IbS8H_Wqu_sTq_gR62zsY9wpBREkM"
supabase: Client = create_client(supabase_url, supabase_key)

@app.route('/')
def index():
    try:
        response = supabase.table('members').select('*').execute()
        members = response.data
        today = datetime.today().date()

        for member in members:
            # Calculate membership status
            try:
                end_date = datetime.strptime(member['end_date'], "%Y-%m-%d").date()
                member['status'] = (
                    "Expired" if end_date < today else
                    "Near Expiry" if (end_date - today).days <= 7 else
                    "Active"
                )
            except Exception:
                member['status'] = "Invalid Date"

            # Format dates for display
            for date_field in ['join_date', 'end_date']:
                try:
                    dt = datetime.strptime(member[date_field], "%Y-%m-%d")
                    member[date_field] = dt.strftime("%d/%m/%Y")
                except:
                    pass

        return render_template('index.html', members=members)

    except Exception as e:
        flash(f'Error loading members: {str(e)}', 'error')
        return render_template('index.html', members=[])

@app.route('/add_member', methods=['POST'])
def add_member():
    try:
        member_data = {
            'name': request.form['name'],
            'email': request.form['email'].strip().lower(),  # Normalize email
            'phone': request.form['phone'],
            'join_date': request.form['join_date'],
            'end_date': request.form['end_date']
        }

        # Validate dates
        join_date = datetime.strptime(member_data['join_date'], "%Y-%m-%d")
        end_date = datetime.strptime(member_data['end_date'], "%Y-%m-%d")

        if end_date < join_date:
            flash('Error: Expiry date cannot be before join date', 'error')
            return redirect(url_for('index'))

        # Check for existing email
        existing = supabase.table('members').select('email').eq('email', member_data['email']).execute()

        if existing.data:
            flash('Error: Email already exists in system', 'error')
            return redirect(url_for('index'))

        # Insert new member
        response = supabase.table('members').insert(member_data).execute()

        # Check for Supabase errors
        if hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)

        flash('Member added successfully!', 'success')

    except Exception as e:
        error_msg = str(e)
        if '23505' in error_msg:
            flash('Error: This email address is already registered', 'error')
        else:
            flash(f'Error adding member: {error_msg}', 'error')

    return redirect(url_for('index'))

@app.route('/delete_member/<int:member_id>')
def delete_member(member_id):
    try:
        supabase.table('members').delete().eq('id', member_id).execute()
        flash('Member deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting member: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    if request.method == 'GET':
        response = supabase.table('members').select('*').eq('id', member_id).execute()
        member = response.data[0] if response.data else None

        if not member:
            flash('Member not found', 'error')
            return redirect(url_for('index'))

        # Format dates for edit form
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
            'end_date': request.form['end_date']
        }

        try:
            supabase.table('members').update(updated_data).eq('id', member_id).execute()
            flash('Member updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating member: {str(e)}', 'error')

        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
