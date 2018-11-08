from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:PvTKOZxheUHO95P4@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGc'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner, pub_date=None):
        self.title = title
        self.body = body
        self.owner = owner
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

def get_blogs():
    return db.session.query(Blog.title, Blog.body, Blog.id).order_by(Blog.pub_date.desc()).all()

def is_empty(item):
    if item == '':
        return True

def too_short(item, num):
    if len(item) < int(num):
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
    blog_owner = User.query.filter_by(username=session['username']).first()

    if is_empty(blog_title) and is_empty(blog_content):
        return render_template('newpost.html', title="New Post", blog_title_error = 'Blog Title Invalid', blog_content_error = 'Blog Body Invalid')
    
    elif is_empty(blog_title):
        return render_template('newpost.html', title="New Post", blog_title_error = 'Blog Title Invalid', blog_content=blog_content)

    elif is_empty(blog_content):
        return render_template('newpost.html', title="New Post", blog_content_error = 'Blog Body Invalid', blog_title=blog_title)

    else:
        blog = Blog(blog_title, blog_content, blog_owner)
        db.session.add(blog)
        db.session.commit()
        return redirect('/blog?id='+str(blog.id))

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        #.form because it is a post, if it was a get it would be .args. could also use form.get. .get handles null values and returns None
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        username_error = ''
        password_error = ''
        verify_error = ''
        

        if not existing_user and password == verify and len(password)>0 and not too_short(password,3) and not too_short(username,3):
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect ('/newpost')
        else:     

            if existing_user:
                username_error='User already exists'
            if is_empty(username):
                username_error='User name empty'
            if is_empty(password):
                password_error='Password empty'
            if is_empty(verify):
                verify_error='Verify Password empty'
            if password != verify:
                verify_error='''Passwords don't match'''
            if too_short(username, 3):
                username_error = "User name too short"
            if too_short(password, 3):
                password_error = "Password too short"

            return render_template('signup.html', username=username, username_error=username_error, password_error=password_error, verify_error=verify_error )



    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect ('/newpost')
        elif user and password != user.password:
            flash('Password incorrect')
            return redirect('/login')
        elif not user:
            flash('Username does not exist')
            return redirect('/login')
    
    return render_template('login.html')

if __name__ == '__main__':
    app.run()