import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:secret@mysql-db/guestbook_db')
app.config['SECRET_KEY'] = 'devops_secret_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

# Task B: The User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    password_hash = db.Column(db.String(128))
    comments = db.relationship('Comment', backref='commenter', lazy=True)

# Task B: The Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
    posted = db.Column(db.DateTime, default=datetime.utcnow)
    commenter_id = db.Column(db.Integer, db.ForeignKey('users.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/guestbook', methods=['GET', 'POST'])
def guestbook():
    if request.method == 'POST':
        if current_user.is_authenticated:
            new_comment = Comment(content=request.form["comment"], commenter=current_user)
            db.session.add(new_comment)
            db.session.commit()
        return redirect(url_for('guestbook'))

    all_comments = Comment.query.order_by(Comment.posted.desc()).all()
    return render_template('guestbook.html', comments=all_comments)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password_hash == request.form['password']:
            login_user(user)
            return redirect(url_for('guestbook'))
        return render_template('login_page.html', error=True)
    return render_template('login_page.html', error=False)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('guestbook'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)