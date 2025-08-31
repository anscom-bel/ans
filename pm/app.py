import random
import string
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from bcrypt import gensalt, hashpw, checkpw

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///password_manager.db'
app.config['SECRET_KEY'] = 'a_very_secret_key_that_should_be_changed'
db = SQLAlchemy(app)

class PasswordEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_password', methods=['GET', 'POST'])
def add_password():
    if request.method == 'POST':
        website = request.form['website']
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = hashpw(password.encode('utf-8'), gensalt())
        
        new_entry = PasswordEntry(website=website, username=username, password=hashed_password.decode('utf-8'))
        db.session.add(new_entry)
        db.session.commit()
        
        flash('Password added successfully!', 'success')
        return redirect(url_for('view_passwords'))
    
    return render_template('add_password.html')

@app.route('/view_passwords')
def view_passwords():
    entries = PasswordEntry.query.all()
    return render_template('view_passwords.html', entries=entries)

@app.route('/generate_password', methods=['GET', 'POST'])
def generate_password():
    generated_password = None
    if request.method == 'POST':
        length = int(request.form.get('length', 12))
        
        characters = ''
        if request.form.get('upper'):
            characters += string.ascii_uppercase
        if request.form.get('lower'):
            characters += string.ascii_lowercase
        if request.form.get('digits'):
            characters += string.digits
        if request.form.get('special'):
            characters += string.punctuation
            
        if not characters:
            flash('Please select at least one character type.', 'danger')
            return render_template('generate_password.html')

        generated_password = ''.join(random.choice(characters) for _ in range(length))
        
    return render_template('generate_password.html', password=generated_password)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)