import boto3
import re
from botocore.client import Config
from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime
import os

#debug load-balancer
import socket

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


def extract_first_image(html_content):
    """Pull the first <img src="..."> URL from HTML content for use as a card thumbnail."""
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html_content or '')
    return match.group(1) if match else None

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
    sort_order = request.args.get('sort', 'newest')

    collection.create_index([("title", "text"), ("content", "text")])

    query_filter = {}
    if search_query:
        query_filter = { "$text": { "$search": search_query } }

    # Sort by _id (which embeds a timestamp) — newest first by default
    sort_direction = 1 if sort_order == 'oldest' else -1
    posts = collection.find(query_filter).sort('_id', sort_direction)

    for post in posts:
        post['id'] = str(post['_id'])
        post['thumbnail'] = extract_first_image(post.get('content', ''))
        post_collection.append(post)

    return render_template('index.html', posts=post_collection, search_query=search_query)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/<string:post_id>')
def post(post_id):
    post = get_post(post_id)

    # Find the previous and next posts (by _id order) for navigation
    prev_post = collection.find_one(
        {"_id": {"$lt": ObjectId(post_id)}},
        sort=[("_id", -1)]
    )
    next_post = collection.find_one(
        {"_id": {"$gt": ObjectId(post_id)}},
        sort=[("_id", 1)]
    )

    if prev_post:
        prev_post['id'] = str(prev_post['_id'])
    if next_post:
        next_post['id'] = str(next_post['_id'])

    return render_template('post.html', post=post, prev_post=prev_post, next_post=next_post)

@app.route('/create', methods=('GET', 'POST'))
def create():
    # Generate a draft ID once when the page first loads.
    # It is carried through the form as a hidden field so it survives
    # a failed validation re-render, keeping uploaded images consistent.
    draft_id = request.form.get('draft_id') or str(ObjectId())

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tag = request.form['tag']

        if not title:
            flash('Title is required!', 'danger')
        else:
            # Use draft_id as the MongoDB _id so the post ID matches
            # the MinIO subfolder where its images are already stored.
            collection.insert_one({
                '_id': ObjectId(draft_id),
                'title': title,
                'content': content,
                'created': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'tag': tag
            })
            flash('Post created successfully!', 'success')
            return redirect(url_for('index'))

    return render_template('create.html', draft_id=draft_id)


@app.route('/discard_draft/<string:draft_id>', methods=['POST'])
def discard_draft(draft_id):
    # Validate before touching MinIO to block path-traversal attempts.
    try:
        ObjectId(draft_id)
    except InvalidId:
        abort(400)

    # Delete every object uploaded under this draft's subfolder.
    response = s3_client.list_objects_v2(Bucket='blog-image', Prefix=f'{draft_id}/')
    for obj in response.get('Contents', []):
        s3_client.delete_object(Bucket='blog-image', Key=obj['Key'])

    return redirect(url_for('index'))


@app.route('/<string:post_id>/edit', methods=('GET', 'POST'))
def edit(post_id):
    post = get_post(post_id)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tag = request.form['tag']

        if not title:
            flash('Title is required!')
        else:
            collection.update_one(
                {'_id': ObjectId(post_id)},
                {'$set': {'title': title, 'content': content, 'tag': tag}}
            )
            return redirect(url_for('index'))
    return render_template('edit.html', post=post)

@app.route('/<string:post_id>/delete', methods=('POST',))
def delete(post_id):
    post = get_post(post_id)
    collection.delete_one({"_id": ObjectId(post_id)})
    flash(f'"{post["title"]}" was successfully deleted!', 'success')
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


@app.route('/debug/info')
def debug_info():
    return jsonify({
        "status": "healthy",
        "handled_by_host": socket.gethostname()
    })