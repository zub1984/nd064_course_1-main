import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

dbCount = 0
def addCounter():
     global dbCount
     dbCount = dbCount + 1 
     return dbCount

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    addCounter()
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
    app.logger.debug('Main request recevied')
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)
    
# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    app.logger.debug('Fetch individual article.')
    post = get_post(post_id)
    if post is None:
      app.logger.error('Article not found, post_id=%s , return 404 page.',post_id)
      return render_template('404.html'), 404
    else:
      app.logger.info('Article retrieved, post_id=%s',post_id)
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.debug('About us page is retrieved.')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    app.logger.debug('Received new post.')
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            app.logger.info('Title is required!')
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('Post inserted, title=%s',title)
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthcheck():
    app.logger.debug('Received healthz request.')
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('healthz request successfull')
    return response

@app.route('/metrics')
def metrics():
    app.logger.debug('Metrics request received.')
    connection = get_db_connection()
    post_count = len(connection.execute('SELECT * FROM posts').fetchall())
    connection.close()
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"db_connection_count":dbCount,"post_count":post_count}}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Metrics request successfull')
    return response

# start the application on port 3111
if __name__ == "__main__":
    ## stream logs to a file
    db_connection_count = 0
    logging.basicConfig(level=logging.DEBUG,format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
        ]
    )
    
    app.run(host='0.0.0.0', port='3111', debug=True)
  

