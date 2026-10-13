/*  ShopEase – Declarative Jenkins Pipeline
 *  ==========================================
 *  Stages: Checkout → Setup → Lint → Test → Build Docker → Deploy → Verify
 *
 *  Required Jenkins plugins:
 *    - Pipeline                (workflow-aggregator)
 *    - Git                     (git)
 *    - JUnit                   (junit)
 *    - Pipeline: Stage View    (pipeline-stage-view)
 *
 *  Required tools on the Jenkins agent:
 *    - Python 3.13+   (in PATH)
 *    - pip             (bundled with Python)
 *    - Docker CLI      (docker.exe in PATH)
 *    - Docker Engine   (Docker Desktop running, or dockerd accessible)
 *
 *  Windows note:
 *    When Jenkins is run via `java -jar jenkins.war`, it inherits the
 *    current user's environment. Make sure Docker Desktop is running
 *    and that `docker info` works in the same terminal before starting
 *    Jenkins.
 */

pipeline {
    agent any

    environment {
        IMAGE_NAME  = 'shopease'
        IMAGE_TAG   = "${BUILD_NUMBER}"
        CONTAINER   = 'shopease-web'
    }

    stages {

        // ----------------------------------------------------------------
        // 1. Checkout
        // ----------------------------------------------------------------
        stage('Checkout') {
            steps {
                echo '📥 Checking out source code …'
                checkout scm
            }
        }

        // ----------------------------------------------------------------
        // 2. Setup Python
        // ----------------------------------------------------------------
        stage('Setup') {
            steps {
                echo '🐍 Setting up Python virtual environment …'
                bat '''
                    python -m venv .venv
                    call .venv\\Scripts\\activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        // ----------------------------------------------------------------
        // 3. Lint
        // ----------------------------------------------------------------
        stage('Lint') {
            steps {
                echo '🔍 Running flake8 linting …'
                bat '''
                    call .venv\\Scripts\\activate
                    flake8 app.py db.py init_db.py --max-line-length=120 --count --show-source --statistics || exit 0
                '''
            }
        }

        // ----------------------------------------------------------------
        // 4. Test
        // ----------------------------------------------------------------
        stage('Test') {
            steps {
                echo '🧪 Running pytest …'
                bat '''
                    call .venv\\Scripts\\activate
                    if not exist reports mkdir reports
                    pytest
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/test-results.xml'
                }
            }
        }

        // ----------------------------------------------------------------
        // 5. Build Docker Image
        // ----------------------------------------------------------------
        stage('Build Docker Image') {
            steps {
                echo "🐳 Building Docker image ${IMAGE_NAME}:${IMAGE_TAG} …"
                bat "docker build -t %IMAGE_NAME%:%IMAGE_TAG% -t %IMAGE_NAME%:latest ."
            }
        }

        // ----------------------------------------------------------------
        // 6. Deploy
        // ----------------------------------------------------------------
        stage('Deploy') {
            steps {
                echo "🚀 Deploying container ${CONTAINER} …"
                bat '''
                    docker stop %CONTAINER% 2>nul || echo Container was not running.
                    docker rm   %CONTAINER% 2>nul || echo No old container to remove.
                    docker run -d --name %CONTAINER% ^
                        -p 5000:5000 ^
                        -v shopease-data:/data ^
                        -e SECRET_KEY=jenkins-demo-key ^
                        -e DB_PATH=/data/shop.db ^
                        %IMAGE_NAME%:latest
                '''
            }
        }

        // ----------------------------------------------------------------
        // 7. Verify
        // ----------------------------------------------------------------
        stage('Verify') {
            steps {
                echo '✅ Verifying application health …'
                bat '''
                    timeout /t 10 /nobreak >nul
                    curl -sf http://localhost:5000/health || (echo Health check FAILED && exit 1)
                    echo Application is healthy!
                '''
            }
        }
    }

    post {
        success {
            echo '🎉 Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check the logs above.'
        }
        always {
            echo 'Pipeline execution complete.'
            script {
                try {
                    cleanWs(deleteDirs: true, patterns: [[pattern: '.venv/**', type: 'INCLUDE']])
                } catch (Exception e) {
                    echo 'Workspace cleanup step skipped (ws-cleanup plugin optional).'
                }
            }
        }
    }
}
