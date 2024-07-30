from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv
import os

def configure():
    load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///feedbacks.db'
db = SQLAlchemy(app)


ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    feedback = db.Column(db.String(500), nullable=False)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form['name']
    email = request.form['email']
    feedback = request.form['feedback']

    new_feedback = Feedback(name=name, email=email, feedback=feedback)
    db.session.add(new_feedback)
    db.session.commit()

    return redirect(url_for('home'))


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('view_feedback'))
        else:
            flash('Invalid credentials. Please try again.')

    return render_template('admin_login.html')


@app.route('/feedbacks')
def view_feedback():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    feedbacks = Feedback.query.all()
    return render_template('feedbacks.html', feedbacks=feedbacks)


@app.route('/delete_feedback/<int:id>')
def delete_feedback(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    feedback_to_delete = Feedback.query.get_or_404(id)
    db.session.delete(feedback_to_delete)
    db.session.commit()

    return redirect(url_for('view_feedback'))


@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
