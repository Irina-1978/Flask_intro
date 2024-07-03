from flaskr.auth import login_required
from flaskr.db import get_db
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.exceptions import abort

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute('SELECT * FROM posts JOIN users ON posts.author_id=users.id ORDER BY created_at DESC').fetchall()

    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        
        error = None

        if not title:
            error = "Title is required"

        if error is not None:
            flash (error)
        else:
            db = get_db()
            db.execute('INSERT INTO posts (title,body,author_id) VALUES (?,?,?)', (title, body, g.user['id']))
            db.commit()
            return redirect(url_for('blog.index'))
    
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        "SELECT posts.id, title, body,created_at, author_id, username FROM posts JOIN users ON author_id=users.id WHERE posts.id=?", (id,)).fetchone()
    
    if post is None:
        abort(404, f"Post id {id} does not exist")
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    return post

@bp.route('/<int:id>/update', methods=('GET','POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']      
        error=None

        if not title:
            error = "Title is required" 

        if error is not None:
            flash(error)
        else:
            db= get_db()
            db.execute('UPDATE posts SET title=?, body=? WHERE id = ? ', (title, body, id))
            db.commit()
            return redirect(url_for('blog.index' ))
    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM posts WHERE id=?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))