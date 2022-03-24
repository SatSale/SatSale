from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit
import time
import os
import csv

PASSWORD = os.getenv("APP_PASSWORD")
if PASSWORD == "" or PASSWORD is None:
    with open("SatSale_API_key", "r") as f:
            PASSWORD = f.read().strip()

def load_items(file="static/store.csv"):
    items = []
    with open(file) as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            items.append(row)
    return items

def save_items(items, file="static/store.csv"):
    with open(file, 'w') as csvfile:
        spamwriter = csv.writer(csvfile)
        for item in items:
            try:
                spamwriter.writerow(item)
            except Exception as e:
                print(e)
                continue
    return

def password_prompt(message):
    return render_template("auth.html", message=message)

def add_decorators(app, file="static/store.csv"):
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

    if not os.path.exists(file):
        # app.items = [["Roosters", 5, "https://img.jakpost.net/c/2020/08/18/2020_08_18_102621_1597723826._large.jpg"], ['Apples', 2, None], ['Pizza', 5, None]]
        app.items = []
        save_items(app.items, file)
    else:
        app.items = load_items(file)

    @app.route("/store")
    def store():
        # Render store page
        return render_template("store.html", params=app.items)

    @app.route('/admin', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'GET':
            return password_prompt("Admin password:")
        elif request.method == 'POST':
            if request.form['password'] != PASSWORD:
                return password_prompt("Invalid password, try again. Admin password:")
            else:
                return render_template("admin.html", params=app.items)

    @app.route("/additem", methods = ['POST'])
    def add_item():
        params = dict(request.form)
        if request.method == 'POST':
            if params['pass'] != PASSWORD:
                return "Incorrect password."
            else:
                print(params)
                app.items.append([params['itemName'], params['itemPrice'], params['itemURL']])
                save_items(app.items)
                return redirect("/store")


    @app.route('/uploader', methods = ['POST'])
    def upload_file(file="static/store.csv"):
        params = dict(request.form)
        if params['pass'] != PASSWORD:
            return "Incorrect password."
        if request.method == 'POST':
            f = request.files['file']
            f.save(file)
            app.items = load_items()
            return redirect("/store")


    return app
