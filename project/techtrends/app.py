import sqlite3

from flask import Flask, render_template, request, url_for, redirect, flash
import config
import logging.config
from werkzeug.exceptions import abort

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('app')

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    config.counter += 1
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error(f"Article with id {post_id} not found")
        return render_template('404.html'), 404
    else:
        app.logger.info(f"Article {post['title']} retrieved")
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    logger.info("Retrieving the about us page")
    return render_template('about.html')


# Add heatlhz endpoint
@app.route('/healthz')
def healthz():
    return {"result": "OK - healthy"}, 200


@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    # get amounts of posts in the databasse
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    # get amount of connections to the database
    return {"db_connection_count": config.counter, "post_count": len(posts)}, 200


# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()
            logger.info(f"Successfully created article {request.form['title']}")
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":

    app.run(host='0.0.0.0', port='3111')
