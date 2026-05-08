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

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database (local or hosted)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/OmarAli258/2850-Fitness-Project.git
cd 2850-Fitness-Project
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If any packages are missing, install them manually:

```bash
pip install flask python-dotenv psycopg2-binary werkzeug gpxpy chart.js
```

### 4. Create a .env File

Create a file called `.env` in the root directory of the project:

**Windows:**
```powershell
type nul > .env
```

**macOS/Linux:**
```bash
touch .env
```

Inside the `.env` file, add the PostgreSQL database connection string:

```
DATABASE_URL="postgresql://username:password@host:port/database_name"
```

Example for local PostgreSQL:
```
DATABASE_URL="postgresql://postgres:password@localhost:5432/fittrack"
```

**Important:** Do not commit the `.env` file to GitHub because it contains private database credentials. The file is already in `.gitignore`.

### 5. Set Up the Database

Ensure your PostgreSQL database is running and accessible. The application will create the necessary tables automatically on first run.

### 6. Run the Application

```bash
python app.py
```

The app should run on `http://localhost:8080`

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Module not found" error | Run `pip install -r requirements.txt` again |
| Database connection error | Check `.env` file has correct `DATABASE_URL` |
| Port already in use | Change port in `app.py` or stop other application |
| Import errors | Ensure all dependencies from requirements.txt are installed |

---

## Project Structure

```
2850-Fitness-Project/
├── app.py                 # Main application entry point
├── requirements.txt      # Python dependencies
├── .env                   # Environment variables (create this)
├── .gitignore             # Files to ignore in version control
├── static/
│   ├── css/
│   │   └── style.css     # Application styles
│   └── js/
│       └── script.js     # Client-side scripts
└── templates/
    ├── base.html         # Base template
    ├── home.html        # Landing page
    ├── login.html       # Login page
    ├── register.html    # Registration page
    ├── dashboard.html   # User dashboard
    ├── activities.html  # Activity logging and history
    ├── plans.html       # Exercise plans
    ├── races.html       # Race tracker
    └── community.html   # Community feed
```

---

## Development Workflow

1. Create a new branch for your feature: `git checkout -b feature/your-feature`
2. Make changes and commit them with clear messages
3. Push to GitHub and create a Pull Request
4. After review, merge into the main branch

See [Git Workflow](https://github.com/OmarAli258/2850-Fitness-Project/wiki/Git-Workflow) in the Wiki for detailed guidelines.

## Test Login Details

The following test accounts can be used to explore the application if they are available in the shared database. Each account represents one of the project personas.

**Account 1: Justin**  
- Email: `justin123@gmail.com`  
- Password: `Justin123`

**Account 2: Sofia**  
- Email: `sofia.persona@gmail.com`  
- Password: `Sofia123`

**Account 3: Noah**  
- Email: `noah.persona@gmail.com`  
- Password: `Noah123`

**Account 4: Keith**  
- Email: `keith.persona@gmail.com`  
- Password: `Keith123`

**Account 5: Layla**  
- Email: `layla.persona@gmail.com`  
- Password: `Layla123`

If these accounts are not available, a new account can be created through the **Sign Up** page.

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
