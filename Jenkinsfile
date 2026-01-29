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
                echo Installing tools...
                python -m pip install --upgrade pip
                python -m pip install mpremote
                '''
            }
        }

        stage('Preflight: ESP32 connectivity') {
            steps {
                bat '''
                @echo off
                echo Preflight: checking ESP32 on %ESP_PORT%...

                python -m mpremote connect %ESP_PORT% exec "pass"

                if %ERRORLEVEL% NEQ 0 (
                    echo Preflight failed: ESP32 not reachable on %ESP_PORT%
                    exit /b %ERRORLEVEL%
                )

                echo Preflight OK: ESP32 is reachable
                '''
            }
        }

        stage('Upload Loopback Tests') {
            steps {
                bat '''
                @echo off
                echo Uploading loopback test files...

                for %%f in (gpio_test\\*.py) do (
                    python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                    if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
                )

                echo Upload complete
                '''
            }
        }

        stage('Run Loopback Tests') {
            steps {
                bat '''
                @echo off
                echo Running GPIO loopback tests...

                if not exist %REPORT_DIR% mkdir %REPORT_DIR%

                REM Create default FAIL report
                (
                    echo ^<html^>
                    echo ^<head^>^<title^>GPIO Loopback Report^</title^>^</head^>
                    echo ^<body^>
                    echo ^<h1^>GPIO Loopback Tests^</h1^>
                    echo ^<p^>Build: %BUILD_NUMBER%^</p^>
                    echo ^<p^>Result: ^<b style="color:red"^>FAIL^</b^>^</p^>
                    echo ^<p^>Timestamp: %DATE% %TIME%^</p^>
                    echo ^</body^>
                    echo ^</html^>
                ) > %REPORT_DIR%\\%REPORT_FILE%

                python -m mpremote connect %ESP_PORT% exec ^
                "import gpio_loopback_runner; gpio_loopback_runner.run_all_tests()"

                if %ERRORLEVEL% NEQ 0 (
                    echo GPIO loopback tests failed
                    exit /b %ERRORLEVEL%
                )

                REM Overwrite with PASS report
                (
                    echo ^<html^>
                    echo ^<head^>^<title^>GPIO Loopback Report^</title^>^</head^>
                    echo ^<body^>
                    echo ^<h1^>GPIO Loopback Tests^</h1^>
                    echo ^<p^>Build: %BUILD_NUMBER%^</p^>
                    echo ^<p^>Result: ^<b style="color:green"^>PASS^</b^>^</p^>
                    echo ^<p^>Timestamp: %DATE% %TIME%^</p^>
                    echo ^</body^>
                    echo ^</html^>
                ) > %REPORT_DIR%\\%REPORT_FILE%

                echo GPIO loopback tests passed

                echo.
                echo HTML report location:
                echo %WORKSPACE%\\%REPORT_DIR%\\%REPORT_FILE%
                '''
            }
        }
    }

    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: "${REPORT_DIR}",
                reportFiles: "${REPORT_FILE}",
                reportName: "ESP32 GPIO Loopback Report"
            ])

            archiveArtifacts artifacts: "${REPORT_DIR}/${REPORT_FILE}",
                             fingerprint: true,
                             allowEmptyArchive: false
        }

        success {
            echo "PIPELINE SUCCESS: GPIO loopback tests passed"
        }

        failure {
            echo "PIPELINE FAILURE: GPIO loopback tests failed"
            echo "Check wiring:"
            echo " - GPIO 14 -> GPIO 19"
            echo " - GPIO 12 -> GPIO 18"
        }
    }
}
