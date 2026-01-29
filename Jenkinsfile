pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds(abortPrevious: true)
    }

    environment {
        ESP_PORT = 'COM5'
        PYTHONUNBUFFERED = '1'
        REPORT_DIR = 'reports'
        REPORT_FILE = 'gpio_loopback_report.html'
    }

    stages {

        stage('Install Tools') {
            steps {
                bat '''
                @echo off
                python -m pip install --upgrade pip
                python -m pip install mpremote
                '''
            }
        }

        stage('Preflight: ESP32 connectivity') {
            steps {
                bat '''
                @echo off
                python -m mpremote connect %ESP_PORT% exec "pass"
                if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
                '''
            }
        }

        stage('Upload Loopback Tests') {
            steps {
                bat '''
                @echo off
                for %%f in (gpio_test\\*.py) do (
                    python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                    if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
                )
                '''
            }
        }

        stage('Run Loopback Tests') {
            steps {
                bat '''
                @echo off
                mkdir %REPORT_DIR% 2>nul

                python -m mpremote connect %ESP_PORT% exec ^
                "import gpio_loopback_runner; gpio_loopback_runner.run_all_tests()"

                if %ERRORLEVEL% NEQ 0 (
                    echo Tests failed
                    exit /b %ERRORLEVEL%
                )
                '''
            }
        }
    }

    post {
        always {
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: "${REPORT_DIR}",
                reportFiles: "${REPORT_FILE}",
                reportName: "ESP32 GPIO Loopback Report"
            ])
        }

        success {
            echo "PIPELINE SUCCESS: GPIO loopback tests passed"
        }

        failure {
            echo "PIPELINE FAILURE: GPIO loopback tests failed"
        }
    }
}
