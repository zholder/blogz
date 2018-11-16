from models import User, Blog
from app import app, db
from flask import request, redirect, render_template, session, flash, url_for
from hashutils import make_pw_hash, check_pw_hash

POSTS_PER_PAGE = 5  

def get_user_blogs(id):
    return db.session.query(Blog.title, Blog.body, Blog.id, Blog.pub_date, User.username).\
    filter_by(owner_id=id).\
    join (User).\
    order_by(Blog.pub_date.desc())

def get_blogs():
    return db.session.query(Blog.title, Blog.body, Blog.id, Blog.pub_date, User.username).\
    join (User).\
    order_by(Blog.pub_date.desc())
    
def get_author(id):
    return db.session.query(User.username).\
            join(Blog).\
            filter_by(id=id).\
            first()
            
def is_empty(item):
    if item == '':
        return True

def too_short(item, num):
    if len(item) < int(num):
        return True

@app.before_request    
def require_login():
    allowed_routes = ['index', 'list_blogs', 'login', 'signup', 'static']
    print(session)
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
def index():
    page = request.args.get('page', 1, type=int)
    users = db.session.query(User.username, User.id).order_by(User.id).paginate(page, POSTS_PER_PAGE, False)
    next_url = url_for('index', page=users.next_num) \
        if users.has_next else None
    prev_url = url_for('index', page=users.prev_num) \
        if users.has_prev else None
    return render_template("index.html", users=users.items, next_url=next_url,prev_url=prev_url)

@app.route('/blog', methods=['GET'])
def list_blogs():
    id = request.args.get('id')
    user = request.args.get('user')
    page = request.args.get('page', 1, type=int)
    user_id = db.session.query(User.id).filter_by(username=user)

    if id is None and user is None:
        blogs=get_blogs().paginate(page, POSTS_PER_PAGE, False)

        next_url = url_for('list_blogs', page=blogs.next_num) \
            if blogs.has_next else None
        prev_url = url_for('list_blogs', page=blogs.prev_num) \
            if blogs.has_prev else None

        return render_template("listblogs.html", blogs=blogs.items, next_url=next_url, prev_url=prev_url)
        
    elif id != None:
        title=db.session.query(Blog.title).filter_by(id=id).first()
        body=db.session.query(Blog.body).filter_by(id=id).first()
        pub_date=db.session.query(Blog.pub_date).filter_by(id=id).first()

        author=db.session.query(User.username).\
            join(Blog).\
            filter_by(id=id).\
            first()
        return render_template("blog.html", title=title[0],body=body[0],author=author[0],pub_date=pub_date[0])
    
    else:
        blogs=get_user_blogs(user_id).paginate(page, POSTS_PER_PAGE, False)
        next_url = url_for('list_blogs', page=blogs.next_num) \
            if blogs.has_next else None
        prev_url = url_for('list_blogs', page=blogs.prev_num) \
            if blogs.has_prev else None

        return render_template("listblogs.html", blogs=blogs.items, next_url=next_url, prev_url=prev_url)

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
    username_error = ''
    password_error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash('Hello, '+ session['username'] + "!")
            return redirect ('/newpost')
        elif user and not check_pw_hash(password, user.pw_hash):
            password_error = 'Password incorrect'
            return render_template('login.html', username=username, password_error=password_error)
        elif not user:
            username_error = 'Username does not exist'
            return render_template('login.html', username_error=username_error)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    flash('Goodbye, '+ session['username'] + "!")
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()