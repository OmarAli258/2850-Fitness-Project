# Physical Fitness & Training Web Application

This project is developed for the **COMP2850 Software Engineering** module at the **University of Leeds**.

FitTrack is a web application designed to help users plan, record, and monitor their physical fitness activities. The system supports both casual users who want to maintain a healthy lifestyle and more competitive users who may be training for events such as races or triathlons.

## Features

The application currently supports:

- User registration and login
- Secure password hashing for user accounts
- PostgreSQL database storage
- Logging physical activities such as running, cycling, swimming, walking, gym workouts, yoga, hiking, rowing, and other activities
- Viewing activity history
- Searching and filtering activity records
- Editing and deleting logged activities
- Dashboard statistics based on real user activity data
- Recent activity preview on the dashboard
- Dashboard charts and visualisations
- Exercise plans for structured training
- Community feed for public activity sharing
- GPX upload support for route-based activities
- Race tracker for upcoming and completed races
- Recording race results and personal bests

## Technologies

The project uses:

- Python
- Flask
- PostgreSQL
- HTML
- CSS
- JavaScript
- Chart.js
- Werkzeug Security for password hashing
- python-dotenv for environment variables
- psycopg2 for PostgreSQL connection
- gpxpy for GPX route file support
- GitHub for version control, issues, pull requests, and project management

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/OmarAli258/2850-Fitness-Project.git
cd 2850-Fitness-Project
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

If any packages are missing, install them manually:

```bash
pip install flask python-dotenv psycopg2-binary werkzeug gpxpy
```

### 3. Create a .env File

Create a file called `.env` in the root directory of the project:

```bash
touch .env
```

Inside the `.env` file, add the PostgreSQL database connection string:

```
DATABASE_URL="your_postgresql_database_url_here"
```

**Note:** Do not commit the `.env` file to GitHub because it contains private database credentials.

### 4. Run the Application

```bash
python app.py
```

The app should run on `http://localhost:8080`

## Test Login Details

The following test accounts can be used to explore the application if they are available in the shared database:

**Account 1:**
- Email: 
- Password: 

**Account 2:**
- Email: 
- Password: 

## Database

The system currently uses PostgreSQL to store application data persistently.

**Tables:**
- Users
- Activities
- Races

The project originally used SQLite during early development because it was simple for local testing. It later moved to PostgreSQL so that the team could connect to a shared database more easily.

Passwords are not stored as plain text. The system uses Werkzeug Security to hash passwords before saving them to the database.

## Project Management

The project is organised using GitHub tools:

- **Wiki** – Project documentation including requirements, personas, user stories, job stories, wireframes, system design, and testing plan
- **Project Board** – Kanban board used to manage development tasks
- **Issues** – Used to track individual tasks, bugs, and feature development
- **Branches and Pull Requests** – Used to manage individual contributions before merging into the main branch

## Team Members

- Omar
- Ben
- Justin
- Ibrahim
- Safyan

## Documentation

Detailed documentation for the project can be found in the GitHub Wiki.
