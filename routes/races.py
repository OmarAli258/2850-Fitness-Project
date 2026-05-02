from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
import os

races = Blueprint('races', __name__)

#DataBase Establishing connection 
def getDB():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'fittrack.db') #we use this to find the db file
    conn = sqlite3.connect(db_path) #this begins the connection
    conn.row_factory = sqlite3.Row # this makes it so you can access the database by names not numbers
    return conn 

@races.route('/racetracker')
def racetracker():

    upcoming = [] #temp lists till database is made
    past = []

    return render_template('racetracker.html', upcoming=upcoming, past=past) #now we can pass upcoming here into upcoming html
    
@races.route('/addrace')
def addrace():
    return render_template('addrace.html')

@races.route('/addrace', methods=['POST']) #first post request aka what happens when somethin if filled in 
def addrace_post():

    sport        = request.form.get('sport', '').strip() #request.form is how you get whatwas typed into the form
    length   = request.form.get('length', '').strip()
    location    = request.form.get('location', '').strip()
    date        = request.form.get('date', '').strip()
    finish_time = request.form.get('finish_time', '').strip()
    is_pb       = 1 if request.form.get('is_pb') else 0

    if not sport or not length or not date: #validation check if entered wrong value
            flash('Please fill in all required fields.', 'error') #error message
            return redirect(url_for('races.addrace')) # go back to form
    
    from datetime import date as datetoday #automatically finds out if upcoming or past race
    status = 'upcoming' if date >= str(datetoday.today()) else 'past'

    # --- temp ---
    # conn = get_db()
    # conn.execute(
    #     'INSERT INTO races (sport, length, location, date, finish_time, is_pb, status)'
    #     ' VALUES (?, ?, ?, ?, ?, ?, ?)', #we use ?instead of the variables directly to avoid sql injection
    #     (sport, length, location, date, finish_time, is_pb, status)
    # )
    # conn.commit()
    # conn.close()
    # -------------------
        #this basically all it does it put new data in database
    flash('Race added! (Database not connected yet)', 'success')
    return redirect(url_for('races.racetracker'))
@races.route('/races/delete/<int:race_id>', methods=['POST'])
def delete_race(race_id):

    # --- PLACEHOLDER ---
    # conn = getDB()
    # conn.execute('DELETE FROM races WHERE id = ?', (race_id,))
    # conn.commit()
    # conn.close()
    # -------------------

    flash('Race deleted! (Database not connected yet)', 'success')
    return redirect(url_for('races.racetracker'))
#same concept when delete is pressed the number row is taken then its delted from the database 