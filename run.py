import os
import json
from flask import Flask, render_template, request, flash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")


@app.route("/")
def index():
    return render_template("index.html", header="Index Page")


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
        flash("Welcome back, {}!".format(
            request.form.get("name")))
    return render_template(
        "login.html", header="Log In Below",  subheader="We've Missed You!")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        flash("Welcome to the Family, {}!".format(
            request.form.get("name")))
    return render_template("signup.html", header="Create an Account!")


if __name__ == "__main__":
    app.run(
            host=os.environ.get("IP", "0.0.0.0"),
            port=int(os.environ.get("PORT", "5000")),
            debug=True)