# Demo Task App

A Flask-based project tracking and approval application designed for different user roles: Writers, Techpub Leads, and Development Leads. The application helps manage content/books through review stages and tracks progress across project workflows.

## Overview

This project simulates a business workflow where:

- Writers add and manage books for projects
- Techpub Leads create projects and manage internal review approval
- Development Leads handle external review approval
- The system keeps a history of movement across stages

## Features

- Role-based login and dashboard redirection
- Project creation for Techpub Leads
- Book creation and assignment to writers
- Stage-based progress tracking
- Internal and external review flows
- Approval walkthrough for each reviewer group
- Seeded demo users for quick testing

## Tech Stack

- Python
- Flask
- Flask-Login
- Flask-SQLAlchemy
- PyMySQL
- WTForms
- Jinja2

## Project Structure

```text
.
├── app/
│   ├── authentication/
│   ├── development_leads/
│   ├── models/
│   ├── techpub_leads/
│   ├── writers/
│   └── __init__.py
├── tests/
├── .env
├── config.py
├── run.py
├── seed.py
├── requirements.txt (if present)
└── README.md
```

## Setup

1. Open a terminal in the project root.
2. Activate the virtual environment if needed:

```bash
./demo_task_app/Scripts/activate
```

On Windows PowerShell, use:

```powershell
.\demo_task_app\Scripts\Activate.ps1
```

3. Install project dependencies if not already installed.

```bash
pip install -r requirements.txt
```

If there is no requirements file, install the essentials:

```bash
pip install flask flask-login flask-sqlalchemy flask-wtf pymysql python-dotenv
```

4. Ensure the database configuration in `.env` matches your local MySQL setup.

Example:

```env
DB_USER = 'your_db_user'
DB_PASSWORD = 'your_db_password'
DB_HOST = 'localhost'
DB_NAME = 'project_tracking_app_demo'
SECRET_KEY = 'your_secret_key'
```

## Database Initialization

Create the database tables:

```bash
python run.py
```

The application automatically creates tables when `run.py` is executed in the app context.

To populate demo data:

```bash
python seed.py
```

This will add:

- sample writers
- a techpub lead
- a development lead
- standard review stages

## Demo Accounts

After seeding the database, these accounts can be used to log in:

| Role | Email | Password |
| --- | --- | --- |
| Writer | aj@gmail.com | password123 |
| Writer | mc@gmail.com | password123 |
| Techpub Lead | gb@gmail.com | password123 |
| Development Lead | dm@gmail.com | password123 |

## Running the App

Start the server:

```bash
python run.py
```

Then open:

```text
http://127.0.0.1:5000/
```

## User Experience Workflow

### 1) Start with Techpub Lead login

Log in as the Techpub Lead using:

- Email: `gb@gmail.com`
- Password: `password123`

After login, the app redirects you to the Techpub Lead dashboard automatically.

From there, begin the workflow by creating a project:

1. Click on Create Work / Project Details
2. Enter the project details such as Network ID, Project Name, Product Line, Development Manager, and Techpub Manager
3. Save the project
4. After saving, you will be redirected to the Add Books page
5. Add book details such as Book Number, Revision, and Writer
6. Save the book to create the project-book record

This is the starting point of the process that the writer and reviewers will follow later.

### 2) Log in as a user

The app accepts logins by email and password. Demo accounts from the seed file include:

- Writer: `aj@gmail.com` / `password123`
- Writer: `mc@gmail.com` / `password123`
- Techpub Lead: `gb@gmail.com` / `password123`
- Development Lead: `dm@gmail.com` / `password123`

After login, the app redirects to the correct dashboard automatically.

---

### 3) Experience the Writer flow

Log in as the writer, for example `aj@gmail.com`.

On the writer dashboard you can:

- View your project list
- Add new books to a project
- Check current stage/status of each book
- Transfer a book to a different writer if needed
- Move a book to the next approval stage

A normal writer flow looks like this:

1. Choose or create a project context
2. Add a book with a number, revision, and project name
3. Save the book
4. Submit the book for review by moving it to a stage such as Internal Review
5. Add comments if needed
6. Return to the dashboard and observe its updated status

---

### 4) Experience the Techpub Lead flow

Log out and sign in as `gb@gmail.com`.

The Techpub Lead dashboard is used to:

- Create a project
- Add books to the project
- Review books that are in Internal Review
- Approve or move those books forward

Typical Techpub process:

1. Create a project with network ID, project name, product line, dev manager, and techpub manager
2. Add books for the project
3. Review queued books under Internal Review
4. Approve the review and move the work to the next stage
5. Continue monitoring the project queue

---

### 5) Experience the Development Lead flow

Log out again and sign in as `dm@gmail.com`.

The Development Lead dashboard focuses on:

- Viewing books in External Review
- Reviewing them before release
- Approving and moving them to the next stage

Typical flow:

1. Open the External Review queue
2. Select a book
3. Review details and comments
4. Approve the book
5. Advance it through the next stage until it reaches release/closure

---

### 6) End-to-end lifecycle

In simple terms, the overall workflow is:

1. Techpub Lead creates a project
2. Writer adds books to the project
3. Writer moves a book from draft status into review
4. Techpub Lead reviews and approves Internal Review
5. Development Lead reviews and approves External Review
6. The item moves toward Release and final closure

## Notes

- The app is a demo/prototype workflow system.
- Validation and role checks are enforced using Flask routes and login state.
- It is designed to demonstrate project lifecycle handling rather than a production-grade enterprise system.

## License

This project is provided for educational and demo purposes.
