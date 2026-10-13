# 📘 ShopEase DevOps Handbook: Complete Operations & Command Guide

A practical, step-by-step handbook covering how to start **Docker**, run **Jenkins**, launch the **ShopEase** web application, execute **tests**, and demonstrate the full DevOps workflow on Windows.

---

## 📌 Table of Contents

1. [System Prerequisites & PATH Setup](#1-system-prerequisites--path-setup)
2. [How to Start Docker Desktop](#2-how-to-start-docker-desktop)
3. [How to Start & Access Jenkins](#3-how-to-start--access-jenkins)
4. [How to Run the Application Locally (No Docker)](#4-how-to-run-the-application-locally-no-docker)
5. [How to Run with Docker & Docker Compose](#5-how-to-run-with-docker--docker-compose)
6. [How to Run Automated Tests & Code Quality Checks](#6-how-to-run-automated-tests--code-quality-checks)
7. [How to Configure & Run the Jenkins CI/CD Pipeline](#7-how-to-configure--run-the-jenkins-cicd-pipeline)
8. [Administrator Credentials & Management](#8-administrator-credentials--management)
9. [Demonstration Checklist for Evaluators](#9-demonstration-checklist-for-evaluators)
10. [Troubleshooting & Quick Fixes](#10-troubleshooting--quick-fixes)

---

## 1. System Prerequisites & PATH Setup

Open **PowerShell** (Run as Administrator or standard user). If any tool commands report `'not recognized'`, execute this in your terminal session to make all project tools available:

```powershell
# Add Python, Git, and Docker to the current session PATH:
$env:Path += ";C:\Program Files\Git\cmd;C:\Users\ajaya\AppData\Local\Programs\DockerDesktop\resources\bin;C:\Users\ajaya\AppData\Local\Python\pythoncore-3.15-64;C:\Windows\System32"
```

### Verify Tool Availability:
```powershell
git --version          # Should show git version 2.x
python --version       # Should show Python 3.13+ or 3.15+
docker --version       # Should show Docker version 29.x
java -version          # Should show OpenJDK / Java 17+ or 21+
```

---

## 2. How to Start Docker Desktop

Docker Desktop must be running before container builds or Jenkins Docker stages can execute.

### Step 1: Launch the Docker Desktop Application
- Click the Windows **Start Menu**, search for **Docker Desktop**, and open it.
- Alternatively, launch it via PowerShell:
  ```powershell
  Start-Process "C:\Users\ajaya\AppData\Local\Programs\DockerDesktop\frontend\Docker Desktop.exe"
  ```

### Step 2: Verify Docker Daemon is Running
Wait 10–20 seconds until the whale icon in the Windows taskbar stays solid (not animating). Then test in PowerShell:

```powershell
docker info
```
If this prints system details without any `error during connect` message, Docker is ready.

### Useful Docker Status Commands:
```powershell
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View Docker images
docker images

# View Docker named volumes
docker volume ls
```

---

## 3. How to Start & Access Jenkins

Jenkins manages the CI/CD pipeline automation.

### Step 1: Start Jenkins from Terminal
Open a dedicated PowerShell terminal and run:

```powershell
# Navigate to the folder containing jenkins.war (usually Downloads or C:\Tools)
# If your jenkins.war is in Downloads:
cd $HOME\Downloads

# Start Jenkins on port 8080:
java -jar jenkins.war --httpPort=8080
```
> 💡 **Keep this terminal window open** while you want Jenkins running. When you see:
> `Jenkins is fully up and running`
> Jenkins is ready.

### Step 2: Open Jenkins in Browser
Open your browser and navigate to:
**[http://localhost:8080](http://localhost:8080)**

- **Default User**: `Ajay` (or your configured Jenkins admin login).
- If prompted for an initial administrator password on first run, it is located at:
  ```powershell
  Get-Content "C:\Users\ajaya\.jenkins\secrets\initialAdminPassword"
  ```

---

## 4. How to Run the Application Locally (No Docker)

Use this mode for rapid development and testing without containers.

```powershell
# 1. Navigate to the project root
cd "d:\DevOps Project\shop-ease"

# 2. Activate Python Virtual Environment
# If running scripts is blocked by PowerShell policy, use the direct binary path:
.\.venv\Scripts\Activate.ps1
# (Or bypass policy for current session: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)

# 3. Install/verify Python packages
.\.venv\Scripts\pip.exe install -r requirements.txt

# 4. Initialise SQLite Database and Seed 10 Products
.\.venv\Scripts\python.exe init_db.py

# 5. Create the Initial Admin User
.\.venv\Scripts\python.exe init_db.py --create-admin --username admin --password adminpass123

# 6. Run the Flask Server in Debug Mode
.\.venv\Scripts\python.exe -m flask run --debug --port 5000
```

### Accessing the Local App:
- **Homepage**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **Health Check**: [http://127.0.0.1:5000/health](http://127.0.0.1:5000/health)
- **Admin Login**: [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)

To stop the server: Press <kbd>Ctrl</kbd> + <kbd>C</kbd> in PowerShell.

---

## 5. How to Run with Docker & Docker Compose

Use this mode for production-like deployment with Gunicorn and persistent named volumes.

```powershell
cd "d:\DevOps Project\shop-ease"

# 1. Build the Docker Image
docker compose build

# 2. Start the Container in Background
docker compose up -d

# 3. Check Container Health Status
docker compose ps
# Output will display: Up (healthy) on 0.0.0.0:5000->5000/tcp

# 4. View Container Logs (live streaming)
docker compose logs -f web

# 5. Stop the Application
docker compose down

# 6. Restart Container (preserving database data)
docker compose up -d
```

### Direct Docker CLI Commands (Alternative):
```powershell
# Build image
docker build -t shopease:latest .

# Run container with named volume and port mapping
docker run -d --name shopease-web -p 5000:5000 -v shopease-data:/data -e SECRET_KEY=demo-key shopease:latest

# Stop and remove container
docker stop shopease-web
docker rm shopease-web

# Backup SQLite database from Docker to Windows host:
docker cp shopease-web:/data/shop.db ./backup_shop.db

# Inspect persistent volume:
docker volume inspect shopease-data
```

---

## 6. How to Run Automated Tests & Code Quality Checks

Automated testing runs using **pytest** with an isolated temporary SQLite database so real production data is never touched.

```powershell
cd "d:\DevOps Project\shop-ease"

# 1. Run All 33 Automated Tests with Verbose Output & JUnit XML generation
.\.venv\Scripts\pytest.exe

# 2. Run Only a Specific Test Suite:
.\.venv\Scripts\pytest.exe tests/test_products.py
.\.venv\Scripts\pytest.exe tests/test_cart.py
.\.venv\Scripts\pytest.exe tests/test_checkout.py
.\.venv\Scripts\pytest.exe tests/test_admin.py
.\.venv\Scripts\pytest.exe tests/test_health.py

# 3. Run Flake8 Code Style & Linting Checks
.\.venv\Scripts\flake8.exe app.py db.py init_db.py --max-line-length=120 --count --show-source --statistics
```

Expected result: `33 passed` and `0` lint errors.

---

## 7. How to Configure & Run the Jenkins CI/CD Pipeline

The declarative pipeline automates: **Checkout ➔ Setup ➔ Lint ➔ Test ➔ Build Docker ➔ Deploy ➔ Verify**.

### Step 1: Create or Open the Pipeline Job in Jenkins
1. Open **[http://localhost:8080](http://localhost:8080)**.
2. Select your job **ShopEase-Pipeline** (or click **New Item** ➔ **Pipeline** ➔ name it `ShopEase-Pipeline`).
3. Click **Configure** on the left menu.
4. Scroll to **Pipeline**:
   - **Definition**: `Pipeline script from SCM`
   - **SCM**: `Git`
   - **Repository URL**: `https://github.com/003Ajay/DevOps-Laboratory.git`
   - **Branch Specifier**: `*/main` *(Must be `*/main`, not `*/master`)*
   - **Script Path**: `Jenkinsfile`
5. Click **Save**.

### Step 2: Trigger a Build
Click **Build Now** on the left menu:
1. Watch the **Stage View** table update in real time.
2. All 7 stage boxes will turn green (SUCCESS):
   - `Checkout` (fetches latest Git commit)
   - `Setup` (virtual environment & dependency resolution)
   - `Lint` (flake8 check)
   - `Test` (33 pytest tests + records JUnit XML)
   - `Build Docker Image` (builds `shopease:<build_number>` and `shopease:latest`)
   - `Deploy` (starts container `shopease-web` on port 5000 with volume `shopease-data`)
   - `Verify` (curl checks `http://localhost:5000/health`)
3. Click on the build number (e.g., **#2**) ➔ **Test Result** to see the 33 passed test cases.

### Step 3: Enable Auto-Build on Git Push (Poll SCM)
To make Jenkins build automatically whenever you run `git push`:
1. In the job configuration, check **Poll SCM** under **Build Triggers**.
2. Enter schedule: `* * * * *` (polls GitHub every minute).
3. Click **Save**.

---

## 8. Administrator Credentials & Management

### Default Administrator Login:
- **Login URL**: [http://localhost:5000/admin/login](http://localhost:5000/admin/login)
- **Username**: `admin`
- **Password**: `adminpass123`

### Create a New Administrator Account:

#### Option A: Inside Running Docker Container
```powershell
docker exec -it shopease-web python init_db.py --create-admin --username myadmin --password mypassword123
```

#### Option B: In Local Development
```powershell
cd "d:\DevOps Project\shop-ease"
.\.venv\Scripts\python.exe init_db.py --create-admin --username myadmin --password mypassword123
```

#### Option C: Interactive (prompts for password securely without displaying it on screen):
```powershell
.\.venv\Scripts\python.exe init_db.py --create-admin
```

---

## 9. Demonstration Checklist for Evaluators

Follow this exact sequence when presenting the project:

| Step | Action | Command / URL | What to Point Out |
| :--- | :--- | :--- | :--- |
| **1. CI/CD** | Show Jenkins UI | `http://localhost:8080/job/ShopEase-Pipeline/` | All 7 stages green in Stage View; show the JUnit test report (33 passed). |
| **2. Container** | Show running Docker container | `docker ps` | Image `shopease:latest`, port `5000:5000`, status `Up (healthy)`. |
| **3. Catalog** | Browse products | `http://localhost:5000` | 10 sample products, 4 categories, prices in ₹, search filter works. |
| **4. Cart** | Add to cart & modify | Add 2 items, update quantity, remove item | Cart badge updates; totals calculate server-side; stock validation. |
| **5. Checkout** | Complete an order | Fill name, phone, address ➔ submit | Validation on inputs; order confirmation page displays Order ID (`#1`). |
| **6. Admin** | Log in as admin | `http://localhost:5000/admin/login` (`admin`/`adminpass123`) | Analytics cards (Total Orders, Revenue); order list; update order to "Shipped". |
| **7. Security** | Test route protection | Log out ➔ visit `http://localhost:5000/admin` | Access denied; automatically redirected to `/admin/login`. |
| **8. Persistence** | Restart container | `docker restart shopease-web` | Refresh admin page: Order `#1` is still there! SQLite volume preserved it. |
| **9. Tests** | Run automated tests | `pytest` | 33 unit & integration tests execute in < 2 seconds with 100% pass rate. |

---

## 10. Troubleshooting & Quick Fixes

### 🔴 Problem: `'git'`, `'docker'`, or `'python'` is not recognized
**Fix**: Add the tool locations to PowerShell for the current session:
```powershell
$env:Path += ";C:\Program Files\Git\cmd;C:\Users\ajaya\AppData\Local\Programs\DockerDesktop\resources\bin;C:\Users\ajaya\AppData\Local\Python\pythoncore-3.15-64"
```

### 🔴 Problem: `Activate.ps1 cannot be loaded because running scripts is disabled`
**Fix**: Bypass execution policy for current PowerShell session:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```
Or execute Python tools directly via `.\.venv\Scripts\python.exe` and `.\.venv\Scripts\pytest.exe`.

### 🔴 Problem: Port 5000 is already in use
**Fix**: Find what is listening on port 5000 and stop it:
```powershell
# Check which process is using port 5000:
netstat -ano | findstr :5000

# Stop any old Docker container using port 5000:
docker stop shopease-web
```

### 🔴 Problem: Jenkins build fails with `couldn't find remote ref refs/heads/master`
**Fix**:
1. Open Jenkins job configuration.
2. Under **Pipeline** ➔ **Branches to build**, change `*/master` to `*/main`.
3. Save and re-run **Build Now**.

### 🔴 Problem: Docker commands fail with `error during connect`
**Fix**: Docker Desktop is not running. Start Docker Desktop from the Windows Start menu and wait until the whale icon is stable.
