# MedSyncPro - Hospital Management System V2

MedSyncPro is a web-based hospital management system designed to facilitate operations between administrators, doctors, and patients. The system implements Role-Based Access Control (RBAC) and utilizes asynchronous processing for background tasks.

## Features

### Roles and Permissions
-   **Admin**: Full access to system data and user management.
-   **Doctor**: Access to assigned appointments, patient history, and personal schedule.
-   **Patient**: Access to booking, personal medical history, and profile management.
-   **RBAC Implementation**: Custom `authorization` decorators enforce role boundaries.

### Administrators
-   **Dashboard**: View total counts for doctors, patients, and pending appointments.
-   **Doctor Management**: Add, update, delete, and search doctors.
-   **Department Management**: Add and list hospital departments.
-   **Patient Management**: View and block patients; search by name/ID.
-   **System Oversight**: View all appointments across the system.

### Doctors
-   **Schedule Management**: View daily appointments.
-   **Availability**: Set and update consultation hours (e.g., MON,TUE|09:00-17:00).
-   **Consultations**:
    -   Mark appointments as completed.
    -   Add diagnosis, prescription, and notes.
-   **Patient History**: View medical records of assigned patients.
-   **Reporting**: Receive automated monthly performance reports via email.

### Patients
-   **Registration**: Self-registration with email validation.
-   **Doctor Search**: Filter doctors by department or name.
-   **Booking System**:
    -   View available time slots based on doctor's schedule.
    -   Conflict detection prevents double-booking.
    -   Book appointments for future dates (up to 7 days).
-   **Appointment Management**: Reschedule or cancel pending appointments.
-   **Medical Records**: View past treatments and prescriptions.
-   **Data Export**: Request CSV export of treatment history (sent via email).

## Technology Stack

### Backend
-   **Language**: Python 3.8+
-   **Framework**: Flask
-   **Database**: SQLite (SQLAlchemy ORM)
-   **Authentication**: JWT (JSON Web Tokens)
-   **Asynchronous Tasks**: Celery
-   **Message Broker**: Redis
-   **Caching**: Redis (Flask-Caching)
-   **Email**: Flask-Mail (SMTP)

### Frontend
-   **Language**: JavaScript (ES6+)
-   **Framework**: Vue.js 3 (Composition API)
-   **State Management**: Pinia
-   **Routing**: Vue Router 4
-   **HTTP Client**: Axios
-   **Styling**: Bootstrap 5

## System Architecture

-   **Client-Server**: Frontend SPA communicates with Backend REST API.
-   **Database**: Relational data model with Users, Doctors, Patients, Appointments, Treatments, and Departments.
-   **Background Processing**:
    -   **Celery Worker**: Executes long-running tasks (Email, Exports) asynchronously.
    -   **Celery Beat**: Schedules periodic tasks (Reminders, Reports).
-   **Caching**: Redis caches frequently accessed data (e.g., Doctor/Department lists) to reduce DB load.

## Final Submission Structure

```
MAD-2-Project/
├── .gitignore                    # Git ignore rules
├── README.md                     # Project documentation
│
├── backend/
│   ├── app.py                    # Flask application entry point
│   ├── models.py                 # Database models (User, Doctor, Patient, etc.)
│   ├── extensions.py             # Flask extensions (SQLAlchemy, JWT, etc.)
│   ├── celery_worker.py          # Celery configuration
│   ├── tasks.py                  # Background tasks (emails, reports)
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Example environment variables
│   │
│   ├── routes/
│   │   ├── auth.py               # Authentication endpoints
│   │   ├── admin_routes.py       # Admin-specific endpoints
│   │   ├── doctor_routes.py      # Doctor-specific endpoints
│   │   └── patient_routes.py     # Patient-specific endpoints
│   │
│   └── templates/
│       └── report.html           # Email template for reports
│
└── frontend/
    ├── package.json              # Node dependencies
    ├── babel.config.js           # Babel configuration
    ├── vue.config.js             # Vue CLI configuration
    ├── jsconfig.json             # JavaScript/Vue configuration
    │
    ├── public/
    │   ├── index.html            # HTML entry point
    │   └── favicon.ico           # App icon
    │
    └── src/
        ├── main.js               # Vue app entry point
        ├── App.vue               # Root component
        │
        ├── router/
        │   └── index.js          # Route definitions
        │
        ├── store/
        │   └── index.js          # Pinia store (state management)
        │
        ├── components/
        │   ├── Navbar.vue        # Navigation bar
        │   └── NotificationHost.vue  # Toast notifications
        │
        ├── utils/
        │   └── availability.js   # Doctor availability helper
        │
        ├── ui/
        │   └── notify.js         # Notification service
        │
        └── views/
            ├── Login.vue         # Login page
            ├── Signup.vue        # Patient registration
            │
            ├── Admin/
            │   ├── AdminDashboard.vue
            │   ├── AddDoctor.vue
            │   ├── UpdateDoctor.vue
            │   ├── ViewDoctors.vue
            │   ├── SearchDoctors.vue
            │   ├── SearchPatients.vue
            │   ├── ManageDepartments.vue
            │   └── ViewAppointments.vue
            │
            ├── Doctor/
            │   ├── DoctorDashboard.vue
            │   ├── AddTreatment.vue
            │   ├── PatientHistory.vue
            │   └── UpdateAvailability.vue
            │
            └── Patient/
                ├── PatientDashboard.vue
                ├── BookAppointment.vue
                ├── MyAppointments.vue
                └── UpdateProfile.vue
```

### Files NOT Included in Submission

These are auto-generated or contain sensitive data and should be in `.gitignore`:

```
# Virtual Environments
.venv/
backend/venv/
node_modules/

# Database & Instance Data
backend/instance/
*.db
*.sqlite3

# Environment Variables (Secrets)
backend/.env

# Python Cache
__pycache__/
*.pyc

# Celery Generated Files
celerybeat-schedule.*

# Build Output
frontend/dist/

# Exports & Logs
backend/exports/
*.log

# IDE Settings
.vscode/
.idea/

# OS Files
Thumbs.db
.DS_Store
```

## Building and Running the Application

## Configuration (.env)

Create a `.env` file in the `backend` directory:

```properties
JWT_SECRET_KEY=your_secret_key
REDIS_URL=redis://127.0.0.1:6379/0
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USERNAME=null
MAIL_PASSWORD=null
CORS_ALLOWED_ORIGINS=http://localhost:8080
```

There are two primary methods to launch the MedSyncPro application running all associated dependencies (Redis, MailHog, Flask APIs, Vue).

### Option 1: Automated Start (Recommended)
If you are on Windows using Git Bash, or are on a Unix system, you can use the unified control script. It will automatically detect, launch, and manage Python, Node, Redis, and MailHog within a single terminal instance.

1. Open Git Bash in the project root directory.
2. Run the script:
   ```bash
   ./start_all.sh
   ```
3. To safely shutdown all 5 running services concurrently, simply press `Ctrl+C` in that terminal. 
*Note: Depending on your execution policy, you may need to run `chmod +x start_all.sh` beforehand.*

---

### Option 2: Step-by-Step (Manual via Git Bash)

If you need to debug specific console output or prefer granular control, spin up each microservice manually in its own dedicated terminal.

#### Prerequisites
-   Python 3.8+
-   Node.js and npm
-   Redis Server (running on port 6379)
-   SMTP Server (e.g., MailHog running on port 1025)

#### 1. Backend Setup
Open Git Bash in the project root:
```bash
cd backend
python -m venv env
source env/Scripts/activate
pip install -r requirements.txt
python app.py
```

#### 2. Frontend Setup
Open a new Git Bash terminal:
```bash
cd frontend
npm install
npm install bootstrap bootstrap-icons
npm run serve
```

#### 3. Background Workers
Open two separate Git Bash terminals in the `backend` directory:

**Worker**:
```bash
cd backend
source env/Scripts/activate
celery -A celery_worker.celery_app worker --pool=solo --loglevel=info
```

**Scheduler**:
```bash
cd backend
source env/Scripts/activate
celery -A celery_worker.celery_app beat --loglevel=info
```


## API Endpoints

### Auth
-   `POST /api/auth/login`: Authenticate user.
-   `POST /api/auth/signup`: Register patient.

### Admin
-   `GET /api/admin/get-dashboard-stats`: System metrics.
-   `POST /api/admin/add-doctor`: Create doctor account.
-   `DELETE /api/admin/delete-doctor/<id>`: Block doctor.

### Doctor
-   `GET /api/doctor/get_my_appointments/`: View schedule.
-   `POST /api/doctor/add_treatment/<id>`: Complete appointment.
-   `PUT /api/doctor/update-availability`: Update hours.

### Patient
-   `POST /api/patient/search-doctors`: Find doctors.
-   `POST /api/patient/book-appointment/`: Book slot.
-   `POST /api/patient/export-treatments`: Request CSV export.

## Background Jobs

-   **Welcome Email**: Triggered on registration.
-   **Daily Reminder**: Runs daily at 13:42. Check pending appointments for today and email patients.
-   **Monthly Report**: Runs monthly on the 1st at 02:00. Compiles doctor activity and emails report.
-   **CSV Export**: Triggered by user request. Generates CSV of patient history and emails it.
