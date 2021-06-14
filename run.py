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
    recipe = mongo.db.recipes.find()
    return render_template("index.html", header="Important Notice", recipes=recipe)


@app.route("/get_recipes")
def get_recipes():
    recipe = list(mongo.db.recipes.find())
    return render_template("recipes.html", header="Perfect Recipes", subheader="for Gluttony & Self Loathing", recipes=recipe)


@app.route("/instructions/<recipe_id>")
def instructions(recipe_id):
    """
    Display view_sandwich page.
    Fetch sandwich by database id from
    MongoDB sandwiches collection.
    Returns:
    template: view_sandwich.html.
    """
    recipes = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("instructions.html", recipes=recipes)


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
                        "index", chef=["chef"]))
            else:
                
                flash("Incorrect Email and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Email and/or Password")
            return redirect(url_for("login"))
    return render_template(
        "login.html", header="Log In!")


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
        return redirect(url_for("index", chef=["chef"]))
            
        
    return render_template("signup.html", header="Create an Account!")


@app.route("/profile/<chef>", methods=["GET", "POST"])
def profile(chef):
    chef = mongo.db.chefs.find_one(
        {"email": session["chef"]})
    return render_template("profile.html", header="This is Chef Master,", chef=chef)


@app.route("/logout")
def logout():
    
    flash("Cya Later, We'll Miss You!")
    session.pop("chef")
    return redirect(url_for("login"))


@app.route("/create_recipe", methods=["GET", "POST"])
def create_recipe():
    if request.method == "POST":
        recipe = {
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "ingredients": request.form.get("ingredients"),
            "instructions": request.form.get("instructions"),
            "image_url": request.form.get("image_url"),
            "created_by": session["chef"]
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe Successfully Added")
        return redirect(url_for("get_recipes"))
    recipe = mongo.db.recipes.find().sort("title", 1)
    return render_template(
        "create_recipe.html", header="What Sweets you got in Mind?", recipes=recipe)


@app.route("/edit_recipe/<edit_id>", methods=["GET", "POST"])
def edit_recipe(edit_id):
    recipes = mongo.db.recipes.find_one({"_id": ObjectId(edit_id)})
    recipes = mongo.db.recipes.find().sort("title", 1)
    return render_template("edit_recipe.html", recipes=recipes)

if __name__ == "__main__":
    app.run(
            host=os.environ.get("IP", "0.0.0.0"),
            port=int(os.environ.get("PORT", "5000")),
            debug=True)