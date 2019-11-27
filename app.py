from flask import Flask , url_for , render_template , request , redirect , session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.secret_key="eaintkyiphyu"


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
    
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String,nullable=False)
    email = db.Column(db.String,nullable=False)
    password = db.Column(db.String,nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String,nullable=False)
    author = db.Column(db.String,nullable=False)
    content = db.Column(db.String,nullable=False)
    image = db.Column(db.String)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)


@app.route("/")
def home():
    return render_template("home.html",posts=Post.query.all())

@app.route("/register",methods=["POST","GET"])
def register():
    if request.method == "POST":
        re_name = request.form["name"]
        re_email = request.form["email"]
        re_pswd = request.form["password"]
        en_pswd = bcrypt.generate_password_hash(re_pswd)
        new_user = User(username = re_name ,email = re_email , password = en_pswd)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/")

    else:
        return render_template("user/register.html")

@app.route("/login",methods = ["POST","GET"])
def login():
    if request.method == "POST":
        lo_email = request.form["email"]
        lo_pswd = request.form["password"]

        login_user = User.query.filter_by(email = lo_email).first()
        if bcrypt.check_password_hash(login_user.password,lo_pswd):
            session["username"] = login_user.username
            session["email"] = login_user.email
            return redirect("/member")
        else:
            return "Something is Wrong"
    else:
        return render_template("user/login.html")

@app.route("/member")
def member():
    if session["username"] != None:
        return render_template("member.html",posts=Post.query.all())
    else:
        return redirect("/login")

@app.route("/logout")
def logout():
    session["username"] = None
    session["email"] = None
    return redirect("/")

@app.route("/post/create",methods=["POST","GET"])
def createPost():
    if session["username"] != None:
        if request.method == "POST":
            author = request.form["author"]
            title = request.form["title"]
            content = request.form["content"]
            file = request.files["image"]
            new_post = Post(title = title , author = author , content = content , image = file.filename)
            db.session.add(new_post)
            db.session.commit()
            return redirect("/member")

        else:
            return render_template("post/create.html")
    else:
        return redirect("/login")

@app.route("/detail,<id>")
def detail(id):
    post = Post.query.get(id)
    return render_template("post/detail.html",post = post)

@app.route("/post/delete,<id>")
def deletePost(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect("/member")

@app.route("/post/edit<id>",methods=["POST","GET"])
def editPost(id):
    if request.method == "POST":
        post = Post.query.get(id)
        post.author = request.form["author"]
        post.title = request.form["title"]
        post.content = request.form["content"]
        file = request.files["image"]
        if file:
            post.image = file.filename
        db.session.commit()
        return redirect("/member")

    else:
        post = Post.query.get(id)
        return render_template("post/edit.html",post=post)


if __name__ == "__main__":
    app.run(debug=True)