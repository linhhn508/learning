import boto3
from botocore.client import Config
from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime
import os

MONGODB_HOST = os.environ["MONGODB_HOST"]
MINIO_URL = os.environ["MINIO_URL"]
MINIO_USR = os.environ["MINIO_USR"]
MINIO_PWD = os.environ["MINIO_PWD"]
# Public URL the *browser* uses to load images — may differ from MINIO_URL
# when MinIO is on a private Docker network (e.g. http://test-minio:9000)
# but exposed to the host on a different address (e.g. http://localhost:9000).
MINIO_PUBLIC_URL = os.environ.get("MINIO_PUBLIC_URL", MINIO_URL)

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
client = MongoClient(MONGODB_HOST)
app.config['SECRET_KEY']= '123'

db = client['blog']
collection = db['posts']

s3_client = boto3.client('s3',
    endpoint_url=MINIO_URL,
    aws_access_key_id=MINIO_USR,
    aws_secret_access_key=MINIO_PWD,
    # addressing_style='path' is required for MinIO — without it boto3 may generate
    # virtual-hosted-style URLs (blog-image.localhost:9000) that MinIO can't route.
    config=Config(signature_version='s3v4', s3={'addressing_style': 'path'}),
    region_name='us-east-1'
)

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

        # 3. Scope uploads into a per-post subfolder when post_id is provided
        #    (edit page), or a flat folder for new posts (create page).
        #    Always validate post_id as a real ObjectId to block path-traversal.
        post_id = request.args.get('post_id', '').strip()
        if post_id:
            try:
                ObjectId(post_id)  # raises InvalidId if not a valid 24-hex string
            except InvalidId:
                return jsonify({'error': 'Invalid post_id'}), 400
            object_key = f"{post_id}/{filename}"
        else:
            object_key = filename

        s3_client.upload_fileobj(
            file,
            'blog-image',
            object_key,
            ExtraArgs={'ContentType': file.content_type}
        )

        image_url = f"{MINIO_PUBLIC_URL}/blog-image/{object_key}"
        return jsonify({'location': image_url})