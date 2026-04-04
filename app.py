from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime
import os

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

# --- NEW: Configure Upload Folder ---
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Creates the folder if it doesn't exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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


# --- Image Upload Route ---
@app.route('/upload_image', methods=['POST'])
def upload_image():
    # 1. Check if a file was sent
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        # 2. Sanitize the filename to prevent path traversal
        filename = secure_filename(file.filename)

        # 3. Optionally scope uploads to a per-post subfolder.
        #    Validate post_id is a real ObjectId to block path-traversal attempts.
        post_id = request.args.get('post_id', '').strip()
        try:
            if post_id:
                ObjectId(post_id)  # raises InvalidId if not a valid 24-hex string
                subfolder = os.path.join(app.config['UPLOAD_FOLDER'], post_id)
                static_path = f'uploads/{post_id}/{filename}'
            else:
                subfolder = app.config['UPLOAD_FOLDER']
                static_path = f'uploads/{filename}'
        except InvalidId:
            return jsonify({'error': 'Invalid post_id'}), 400

        # 4. Create the subfolder if needed and save the file
        os.makedirs(subfolder, exist_ok=True)
        file.save(os.path.join(subfolder, filename))

        # 5. Return an absolute URL path so TinyMCE (convert_urls:false) stores it correctly
        image_url = url_for('static', filename=static_path)
        return jsonify({'location': image_url})