import os
import json
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def index():
    prep = mongo.db.preparation.find()
    return render_template("index.html", preparation=prep)


@app.route("/get_recipes")
def get_recipes():
    prep = mongo.db.preparation.find()
    gred = mongo.db.ingredients.find()
    return render_template("newrecipes.html", preparation=prep, ingredients=gred)


@app.route("/recipes")
def recipes():
    data = []
    with open("data/recipes.json", "r") as json_data:
        data = json.load(json_data)
    return render_template(
        "recipes.html", header="Perfect Recipes",  subheader="for Gluttony & Self Loathing", recipe=data)


@app.route("/recipes/<ingredients_prep>")
def recipes_recipe(ingredients_prep):
    recipe = {}
    with open("data/recipes.json", "r") as json_data:
        data=json.load(json_data)
        for obj in data:
            if obj["url"] == ingredients_prep:
                recipe = obj
    return render_template(
        "ingredients.html", ingredients=recipe, header="Lets Get Cooking")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        
        existing_email = mongo.db.chefs.find_one(
            {"email": request.form.get("email").lower()})

        if existing_email:
            
            if check_password_hash(
                existing_email["password"], request.form.get("password")):
                    session["chef"] = request.form.get("email").lower()
                    flash("Welcome back, we've missed you!")
                    return redirect(url_for(
                        "profile", chef=["chef"]))
            else:
                
                flash("Incorrect Email and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Email and/or Password")
            return redirect(url_for("login"))
    return render_template(
        "login.html", header="Log In Below",  subheader="We've Missed You!")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        
        existing_email = mongo.db.chefs.find_one(
            {"email": request.form.get("email").lower()})

        if existing_email:
            flash("This email is already linked to an account!")
            return redirect(url_for("signup"))

        signup = {
            "firstName": request.form.get("firstname"),
            "lastName": request.form.get("lastname"),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.chefs.insert_one(signup)

        
        session["chef"] = request.form.get("email").lower()
        flash("Welcome to the Family, {}!".format(
            request.form.get("firstname")))
        return redirect(url_for("profile", chef=["chef"]))
            
        
    return render_template("signup.html", header="Create an Account!")


@app.route("/profile/<chef>", methods=["GET", "POST"])
def profile(chef):
    
    chef = mongo.db.chefs.find_one(
        {"email": session["chef"]})
    return render_template("profile.html", chef=chef)


@app.route("/logout")
def logout():
    
    flash("Cya Later, We'll Miss You!")
    session.pop("chef")
    return redirect(url_for("login"))


@app.route("/create_recipe")
def create_recipe():
    return render_template("createrecipe.html")
if __name__ == "__main__":
    app.run(
            host=os.environ.get("IP", "0.0.0.0"),
            port=int(os.environ.get("PORT", "5000")),
            debug=True)