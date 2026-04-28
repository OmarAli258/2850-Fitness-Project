from flask import Blueprint, render_template

races = Blueprint('races', __name__)

@races.route('/racetracker')
def racetracker():
    return render_template('racetracker.html')

@races.route('/addrace')
def addrace():
    return render_template('addrace.html')
