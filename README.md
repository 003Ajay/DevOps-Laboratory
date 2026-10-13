# 🛍️ ShopEase – Simple E-Commerce with DevOps CI/CD

A minimal, modern e-commerce web application built with **Flask**, **SQLite**, **Docker**, and **Jenkins** for academic demonstration.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-green)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Table of Contents

1. [Features](#-features)
2. [Project Structure](#-project-structure)
3. [Prerequisites](#-prerequisites)
4. [Quick Start (Local)](#-quick-start-local)
5. [Running Tests](#-running-tests)
6. [Docker Deployment](#-docker-deployment)
7. [Persistent Storage](#-persistent-storage)
8. [Jenkins CI/CD](#-jenkins-cicd)
9. [Git & GitHub Setup](#-git--github-setup)
10. [Demo Checklist](#-demo-checklist)

---

## ✨ Features

| Area       | Details                                                         |
| ---------- | --------------------------------------------------------------- |
| Products   | 10 sample products across 4 categories, search & filter         |
| Cart       | Add / update / remove items, session-based, stock validation    |
| Checkout   | Server-side validation, order creation, stock deduction         |
| Admin      | Secure login, order list, status updates, revenue statistics    |
| Database   | SQLite with foreign keys, parameterised queries, paise storage  |
| Docker     | Gunicorn, non-root user, health check, named volume             |
| CI/CD      | Jenkins declarative pipeline, pytest, flake8, JUnit reports     |

---

## 📁 Project Structure

```
shop-ease/
├── app.py                  # Flask application
├── db.py                   # Database helpers
├── schema.sql              # Table definitions
├── init_db.py              # DB init & admin creation script
├── requirements.txt        # Python dependencies
├── pytest.ini              # Pytest configuration
├── Dockerfile              # Container image
├── compose.yaml            # Docker Compose
├── Jenkinsfile             # CI/CD pipeline
├── .dockerignore
├── .gitignore
├── README.md
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── products.html
│   ├── product_details.html
│   ├── cart.html
│   ├── checkout.html
│   ├── order_confirmation.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   └── order_details.html
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   └── images/
└── tests/
    ├── conftest.py
    ├── test_products.py
    ├── test_cart.py
    ├── test_checkout.py
    ├── test_admin.py
    └── test_health.py
```

---

## ⚙️ Prerequisites

| Tool              | Version  | Purpose                |
| ----------------- | -------- | ---------------------- |
| Python            | 3.13+    | Backend                |
| pip               | latest   | Package management     |
| Docker Desktop    | latest   | Containerisation       |
| Jenkins (war)     | LTS      | CI/CD                  |
| Git               | latest   | Version control        |
| curl              | any      | Health check (Jenkins) |

---

## 🚀 Quick Start (Local)

Open a terminal in the `shop-ease` directory:

```powershell
# 1. Create a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialise database and seed products
python init_db.py

# 4. (Optional) Create an admin account
python init_db.py --create-admin

# 5. Run the development server
flask run --debug
```

Open **http://127.0.0.1:5000** in your browser.

---

## 🧪 Running Tests

```powershell
# Activate virtualenv if not already active
.\.venv\Scripts\Activate.ps1

# Create reports directory
mkdir reports -ErrorAction SilentlyContinue

# Run all tests
pytest
```

Test results are saved to `reports/test-results.xml` (JUnit format for Jenkins).

---

## 🐳 Docker Deployment

### Build and run

```powershell
# Build the image
docker compose build

# Start in background
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f web
```

The application is available at **http://localhost:5000**.

### Stop and restart

```powershell
# Stop
docker compose down

# Restart (data is preserved in the named volume)
docker compose up -d
```

### Create admin inside container

```powershell
docker exec -it shopease-web python init_db.py --create-admin
```

---

## 💾 Persistent Storage

SQLite data is stored in the Docker named volume `shopease-data`.

```powershell
# Inspect the volume
docker volume inspect shopease-data

# Verify data survives restart
docker compose down
docker compose up -d
# → Existing orders are still available at http://localhost:5000/admin

# Back up the database
docker cp shopease-web:/data/shop.db ./backup_shop.db

# ⚠️ Never delete the volume during normal deployments:
#    docker volume rm shopease-data   ← This deletes ALL order data!
```

---

## 🔧 Jenkins CI/CD

### Required Jenkins Plugins

| Plugin               | ID                    |
| -------------------- | --------------------- |
| Pipeline             | workflow-aggregator   |
| Git                  | git                   |
| JUnit                | junit                 |
| Pipeline: Stage View | pipeline-stage-view   |

Install via **Manage Jenkins → Plugins → Available plugins**.

### Starting Jenkins on Windows

```powershell
# Download jenkins.war (LTS) from https://www.jenkins.io/download/
java -jar jenkins.war --httpPort=8080
```

Open **http://localhost:8080** and complete the initial setup wizard.

### Creating the Pipeline Job

1. **New Item** → Enter name `ShopEase` → select **Pipeline** → OK.
2. Under **Pipeline**:
   - **Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: `https://github.com/<your-username>/shop-ease.git`
   - **Branch**: `*/main`
   - **Script Path**: `Jenkinsfile`
3. Click **Save**, then **Build Now**.

### Docker Access from Jenkins (Windows)

When Jenkins runs via `jenkins.war`, it uses the current user's session:

1. **Start Docker Desktop** before running Jenkins.
2. Open a terminal and verify: `docker info` (should succeed).
3. Start Jenkins from **the same terminal** so it inherits the Docker socket.
4. Verify inside a Jenkins pipeline: the `docker build` and `docker run` commands will work because Jenkins runs as your user.

> **Note**: If `docker` is not found, add Docker Desktop's path
> (`C:\Program Files\Docker\Docker\resources\bin`) to your system PATH.

### Optional: GitHub Webhook

1. In your GitHub repo: **Settings → Webhooks → Add webhook**.
2. **Payload URL**: `http://<your-ip>:8080/github-webhook/`
3. **Content type**: `application/json`
4. **Events**: Just the push event.
5. In Jenkins job config: check **GitHub hook trigger for GITScm polling**.

> Webhooks require Jenkins to be reachable from the internet (use ngrok for local testing).

---

## 📦 Git & GitHub Setup

```powershell
cd shop-ease

# Initialise repository
git init
git add .
git commit -m "Initial commit: ShopEase e-commerce application"

# Create repo on GitHub, then:
git remote add origin https://github.com/<your-username>/shop-ease.git
git branch -M main
git push -u origin main
```

---

## ✅ Demo Checklist

Use this checklist when demonstrating the project to an evaluator:

### Website Features
- [ ] Homepage loads with 10 products and categories
- [ ] Search bar filters products by name/description
- [ ] Category pills filter by category
- [ ] Product detail page shows full information
- [ ] Add products to cart – badge updates
- [ ] Cart page shows items, quantities, totals
- [ ] Increase/decrease quantity in cart
- [ ] Remove item from cart
- [ ] Checkout validates name, phone, and address
- [ ] Successful order shows confirmation with order ID
- [ ] Stock decreases after ordering

### Admin Dashboard
- [ ] Admin login with hashed password
- [ ] Dashboard shows order statistics
- [ ] View individual order details
- [ ] Update order status (pending → shipped → delivered)
- [ ] Logout works and prevents re-access

### Database
- [ ] SQLite database created automatically
- [ ] 10 products seeded without duplicates
- [ ] Foreign keys enforced
- [ ] Prices stored as integer paise

### Docker
- [ ] `docker compose build` succeeds
- [ ] `docker compose up -d` starts the container
- [ ] App accessible at http://localhost:5000
- [ ] `/health` returns `{"status": "healthy"}`
- [ ] Data persists after `docker compose down` and `up`
- [ ] Container runs as non-root user

### Jenkins CI/CD
- [ ] Pipeline job configured with Git SCM
- [ ] All 7 stages visible in Stage View
- [ ] Tests run and JUnit report published
- [ ] Docker image built successfully
- [ ] Container deployed and health-checked
- [ ] Pipeline stops if tests fail

### Tests
- [ ] `pytest` passes all tests
- [ ] JUnit XML generated in `reports/`
- [ ] Tests use temporary database

---

## 📄 License

This project is for academic/educational purposes.
