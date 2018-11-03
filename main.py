from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blogabuild@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    #specify data fields into columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

def get_blogs():
    return db.session.query(Blog.title, Blog.body).all()

def blog_empty(blog):
    if blog == '':
        return True

@app.route('/blog', methods=['GET'])
def index():
    return render_template('index.html', title="Blog Post", blogs=get_blogs())
        
@app.route('/newpost', methods=['GET'])
def newpost():
    return render_template('newpost.html', title="New Post")

@app.route("/blog", methods=['POST'])
def add_blog():
    # look inside the request to figure out what the user typed
    blog_title = request.form['blog_title']
    blog_content = request.form['blog_content']
    blog_title_error = ''
    blog_content_error = ''

    if blog_empty(blog_title) and blog_empty(blog_content):
        return render_template('newpost.html', title="New Post", blog_title_error = 'Blog Title Invalid', blog_content_error = 'Blog Body Invalid')
    
    elif blog_empty(blog_title):
        return render_template('newpost.html', title="New Post", blog_title_error = 'Blog Title Invalid', blog_content=blog_content)

    elif blog_empty(blog_content):
        return render_template('newpost.html', title="New Post", blog_content_error = 'Blog Body Invalid', blog_title=blog_title)

    else:
        blog = Blog(blog_title, blog_content)
        db.session.add(blog)
        db.session.commit()
        return redirect('/blog')


if __name__ == '__main__':
    app.run()