from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from werkzeug.exceptions import abort
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime

def get_post(post_id):
    # Catch InvalidId in case the user types a bad ID in the URL
    try:
        # Use find_one() to get a single dictionary (or None), not a cursor
        post = collection.find_one({"_id": ObjectId(post_id)})
    except InvalidId:
        abort(404)
        
    if post is None:
        abort(404)

    post['id'] = str(post['_id'])
    return post

app = Flask(__name__)
client = MongoClient('localhost', 27017)
app.config['SECRET_KEY']= '123'
db = client['blog']
collection = db['posts']

@app.route('/')
def index():
    post_collection = []
    
    search_query = request.args.get('q')

    if search_query:
        posts = collection.find({"title": {"$regex": search_query, "$options": "i"}})
    else:
        posts = collection.find()

    for post in posts:
        post['id'] = str(post['_id'])
        post_collection.append(post)

    return render_template('index.html', posts=post_collection, search_query=search_query)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/<string:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!', 'danger')
        else:
            collection.insert_one({
                'title': title, 
                'content': content,
                'created': datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            flash('Post created successfully!', 'success')
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<string:post_id>/edit', methods=('GET', 'POST'))
def edit(post_id):
    post = get_post(post_id)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            collection.update_one(
                {'_id': ObjectId(post_id)},
                {'$set': {'title': title, 'content': content}}
            )
            return redirect(url_for('index'))
    return render_template('edit.html', post=post)

@app.route('/<string:post_id>/delete', methods=('POST',))
def delete(post_id):
    post = get_post(post_id)
    collection.delete_one({"_id": ObjectId(post_id)})
    flash(f'"{post["title"]}" was successfully deleted!', 'success') # Uncommented and updated
    return redirect(url_for('index'))