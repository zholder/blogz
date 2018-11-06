from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:PvTKOZxheUHO95P4@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    #specify data fields into columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    pub_date = db.Column(db.DateTime)


    def __init__(self, title, body, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

def get_blogs():
    return db.session.query(Blog.title, Blog.body, Blog.id).order_by(Blog.pub_date.desc()).all()

def blog_empty(blog):
    if blog == '':
        return True

@app.route('/blog', methods=['GET'])
def index():
    id = request.args.get('id')
    if id is None:
        blogs=get_blogs()
        return render_template("index.html", blogs=blogs)
    else:
        title=db.session.query(Blog.title).filter_by(id=id).first()
        body=db.session.query(Blog.body).filter_by(id=id).first()
        #.first allows a value to return from the query
        #grab 0th item in tuple that returns
        return render_template("blog.html", title=title[0],body=body[0])

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
        return redirect('/blog?id='+str(blog.id))
   

if __name__ == '__main__':
    app.run()