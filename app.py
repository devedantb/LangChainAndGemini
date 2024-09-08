import os
import secrets
import json
from modules.geminiChain import GetDataFromPDFandAnswer
from modules.readpdf import readPDF
from modules.pdfOps import save_uploaded_file, delete_file
from functools import wraps
from hashlib import sha256
from flask import Flask, redirect, render_template, request, session, jsonify
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus

username = quote_plus('<username>')
password = quote_plus('<password>')

load_dotenv()
# MONGO_URI = os.getenv("MONGO_URI")
mongo_password = quote_plus(os.getenv("mongo_password"))
mongo_username = quote_plus(os.getenv("mongo_username"))
## modify your URI by refering >> https://www.mongodb.com/docs/atlas/troubleshoot-connection/
MONGO_URI = f"mongodb+srv://{mongo_username}:{mongo_password}@cluster0.8ftxc77.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client.langchain


app = Flask(__name__)

secret_key = secrets.token_hex(32)

app.secret_key = secret_key


def login_first(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "username" in session:
            return func(*args, **kwargs)
        else:
            return redirect("/login")

    return wrapper


@app.route("/")
@login_first
def main():
    return redirect("/home")


@app.route("/logout")
@login_first
def logout():
    if "username" in session:
        session.pop("username")
    return redirect("/home")


@app.route("/register", methods=["POST", "GET"])
def register_user():
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        password = password.encode()
        password = sha256(password).hexdigest()
        request_data = {
            "name": name,
            "username": username,
            "password": password,
            "pdf": {},
        }

        getUser = db.users.find_one({"username": username})
        if getUser is None:
            db.users.insert_one(request_data)
            return redirect("/home")
        else:
            return render_template(
                "register.html",
                error_message="Username already exists. Try another one or log in instead.",
            )
    else:
        return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def user_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.users.find_one({"username": username})

        # If user doesn't exist or password is incorrect, show error message
        if (
            user is None
            or user.get("password") != sha256(password.encode()).hexdigest()
        ):
            return render_template(
                "login.html", error_message="Invalid username or password"
            )

        # If username and password are correct, set the session
        session["username"] = username
        return redirect("/home")
    else:
        return render_template("login.html")


@app.route("/home", methods=["GET", "POST"])
@login_first
def home():
    username = session["username"]
    getUser = db.users.find_one({"username": username})
    getUser.pop("password", None)

    return render_template(
        "home.html",
        message="Login successful",
        data=getUser,
        pdf_list=getUser.get("pdf", []),
    )


def add_pdf_data(username, file_name, data):
    userdata = db.users.find_one({"username": username})
    userdata["pdf"][file_name] = data
    pdfToUpdate = userdata["pdf"]
    db.users.update_one({"username": username}, {"$set": {"pdf": pdfToUpdate}})


@app.route("/upload", methods=["POST", "GET"])
@login_first
def upload_file():
    if request.method == "POST":
        try:
            file = request.files["file"]
            if file.mimetype != "application/pdf":
                return jsonify({"message": "Only PDF files are allowed"}), 400

            if "username" in session:
                username = session["username"]
                contents = file.read()
                filename = secure_filename(file.filename)
                saved_filepath = save_uploaded_file(contents, filename)
                text = readPDF(saved_filepath)
                delete_file(saved_filepath)
                add_pdf_data(username, saved_filepath[4:], text)
                return redirect("/home")
            else:
                return jsonify({"message": "Incorrect username or password"}), 400
        except Exception as e:
            return jsonify({"message": f"An error occurred: {str(e)}"}), 500
    else:
        return render_template("upload.html")


@app.route("/delete/<pdf>")
@login_first
def delete_pdf(pdf):
    username = session.get("username")
    getUserData = db.users.find_one({"username": username})
    if pdf in getUserData.get("pdf", {}):
        getUserData["pdf"].pop(pdf)
        db.users.update_one(
            {"username": username}, {"$set": {"pdf": getUserData["pdf"]}}
        )
    return redirect("/home")


def get_pdf_data(pdf_name: str, username):
    userData = db.users.find_one({"username": username})
    pdf_data = userData["pdf"][pdf_name]
    return pdf_data


@app.route("/getanswer", methods=["POST", "GET"])
@login_first
def get_ans_from_pdf():
    if request.method == "POST":
        try:
            if "username" in session:
                username = session["username"]
                pdf_name = request.form.get("pdf_name")
                prompt = request.form.get("prompt")
                pdf_data = get_pdf_data(
                    pdf_name, username
                )  # Assuming get_pdf_data retrieves PDF data
                answer = GetDataFromPDFandAnswer(
                    pdf_name, prompt, pdf_data
                )  # Assuming this function returns a result
                result_value = answer
                getUser = db.users.find_one({"username": username})
                getUser.pop("password", None)

                return render_template(
                    "getans.html",
                    data=getUser,
                    answer=result_value,
                    pdf_list=getUser.get("pdf", []),
                    pdf_name=pdf_name,
                )
        except Exception as e:
            return jsonify({"message": f"An error occurred: {str(e)}"}), 500
    else:
        username = session["username"]
        getUser = db.users.find_one({"username": username})
        getUser.pop("password", None)
        return render_template(
            "getans.html",
            data=getUser,
            pdf_list=getUser.get("pdf", []),
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)