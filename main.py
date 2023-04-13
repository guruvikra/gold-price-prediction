from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from pymongo import MongoClient
import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime
import math

# MongoDB setup
client = MongoClient(
  "mongodb+srv://guruvikram:Vikram326@cluster0.jpxgdhu.mongodb.net/?retryWrites=true&w=majority"
)
db = client["gold_price"]
gold_prices = db["price"]
print(gold_prices)
users = db["users"]


# Prediction model
def predict_gold_price(data, user_input):
  df = pd.DataFrame(data)
  df["Date"] = pd.to_datetime(df["Date"])
  df["Date"] = df["Date"].map(lambda x: x.timestamp())
  X = df['Date']
  y = df['High']
  print(X, y)
  X = X.values.reshape(-1, 1)
  model = LinearRegression()
  model.fit(X, y)
  user_input = datetime.strptime(user_input, '%Y-%m-%d').timestamp()
  prediction = model.predict([[user_input]])
  return prediction[0]


# Flask app
main = Flask(__name__)
main.secret_key = os.environ.get("SECRET_KEY", "secret")


# Home page
@main.route("/")
def index():
  if "user" in session:
    return render_template("index.html", username=session["user"]["username"])
  return render_template("index.html")


# Signup
@main.route("/signup", methods=["GET", "POST"])
def signup():
  if request.method == "POST":
    # Get form data
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    # Insert data into MongoDB
    users.insert_one({
      "username": username,
      "email": email,
      "password": password
    })
    # Redirect to login page
    return redirect(url_for("login"))
  return render_template("signup.html")


# Login
@main.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    # Get form data
    email = request.form["email"]
    password = request.form["password"]
    # Get user data from MongoDB
    user = users.find_one({"email": email, "password": password})
    if user:
# Login successful
      session["user"] = {"username": user["username"], "email": user["email"]}
      return redirect(url_for("index"))
  return render_template("login.html")


# Logout
@main.route("/logout")
def logout():
  session.clear()
  return redirect(url_for("index"))


@main.route("/predict", methods=["GET", "POST"])
def predict():
  if request.method == "POST":
    user_input = request.form["date"]
    data = list(gold_prices.find())
    prediction = predict_gold_price(data, user_input)
    prediction=math.floor((prediction//28)*82.51)
    if(prediction):
        return render_template("predict.html",prediction= prediction)
  else:
    return render_template("predict.html")


if __name__ == "__main__":
  main.run(debug=True)
