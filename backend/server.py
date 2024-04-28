import os
import uuid

from bs4 import BeautifulSoup
from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from itsdangerous.url_safe import URLSafeTimedSerializer
from config import debug_status, whitelist_origins
from flask_cors import CORS, cross_origin
import logging

# set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


from explainer import text

app = Flask(__name__)
CORS(app, origins=whitelist_origins)
_ = load_dotenv(find_dotenv())
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('DB_PROD_USERNAME')}:{os.getenv('DB_PROD_PASSWORD')}"
    f"@{os.getenv('DB_PROD_HOSTNAME')}:5432/{os.getenv('DB_PROD_DB_NAME')}"
)
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS")
app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL")
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["RESET_PASSWORD_SECRET"] = bytes(
    os.getenv("RESET_PASSWORD_SECRET"), encoding="utf-8"
)
app.config["SECRET_KEY"] = os.urandom(16)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)


class Users(UserMixin, db.Model):
    user_id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    email = db.Column(db.String)
    password = db.Column(db.String)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password.encode("utf-8")).decode(
            "utf-8"
        )

    def check_password(self, password):
        if not password or not self.password:
            return False
        return bcrypt.check_password_hash(self.password, password.encode("utf-8"))

    def get_reset_token(self):
        serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        return serializer.dumps(self.email)

    def get_id(self):
        return self.user_id

    @staticmethod
    def verify_reset_token(token, expiration=3600):
        s = URLSafeTimedSerializer(app.config["RESET_PASSWORD_SECRET"])
        try:
            email = s.loads(token, max_age=expiration)
        except:
            return False
        return email


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.route("/test")
def test():
    return "Success!"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(email=request.form["email"]).first()
        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect(url_for("test"))
        else:
            return "Invalid username or password"
    return "Login Page"


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return "Logged out"


@app.route("/test_form")
def test_form():
    return render_template("test_form.html")


@app.route("/reset_token/<token>", methods=["GET", "POST"])
def reset_token(token):
    email = Users.verify_reset_token(token)
    if not email:
        return "Invalid or expired token"
    user = Users.query.filter_by(email=email).first()
    if not user:
        return "User not found"
    if request.method == "POST":
        user.set_password(request.form["password"])
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("reset_password.html", token=token)


def send_reset_email(user, token):
    msg = Message(
        "Password Reset Request", sender="noreply@demo.com", recipients=[user.email]
    )
    msg.body = f"""To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
"""
    mail.send(msg)


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        user = Users.query.filter_by(email=request.form["email"]).first()
        if user:
            token = user.get_reset_token()
            send_reset_email(user, token)
    return "Forgot Password Page"


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        new_user = Users(email=request.form["email"])
        new_user.set_password(request.form["password"])
        print(new_user)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return "Create Account Page"


# @login_requiredß
@app.route("/explain_news", methods=["POST"])
def explain_news():
    try:
        logging.info("are we here?")
        logging.info("From debug")
        html_string = request.get_json().get("html_string", "")
        explanation = text.get_news_explanation(html_string)
        logging.info("explanation")
        logging.info(explanation)
        return jsonify({"explanation": explanation})
    except Exception as e:
        logging.info(e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True, port=4000)
