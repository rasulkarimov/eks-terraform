from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
import sqlite3
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql import func

# to for testing hpa
import cpu_loadtest

app = Flask(__name__)

# TODO define in env
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres1:postgres1@postgres:5432/posts_api"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class PostsModel(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    title = db.Column(db.String())
    content = db.Column(db.String())
    def __init__(self, title, content):
        self.title = title
        self.content = content
    def __repr__(self):
        return f"<Car {self.name}>"


@app.route('/')
def index():
    posts = PostsModel.query.all()
    return render_template('index.html', posts=posts)

@app.route('/<int:post_id>')
def post(post_id):
    post = PostsModel.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route('/create', methods=('GET','POST'))
def create():
    if request.method == 'POST':
      title = request.form['title']
      content = request.form['content']
      new_post = PostsModel(title=title, content=content)

      if not title:
        flash('Title is required!')
      else:
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = PostsModel.query.get_or_404(id)

    if request.method == 'POST':
      post.title = request.form['title']
      post.content = request.form['content']

      if not post.title:
        flash('Title is required!')
      else:
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = PostsModel.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('"{}" was successfully deleted!'.format(post.title))
    return redirect(url_for('index'))

@app.route('/testhpa')
def testhpa():
    cpu_loadtest.main()

if __name__=="__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    app.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
