from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fittrack.db'
app.config['SECRET_KEY'] = 'mysecretkey'
db = SQLAlchemy(app)
@app.route('/')
def home():
    return render_template('home.html')

#Guys you can add routes here 

if __name__ == '__main__':
    app.run(debug=True)
    