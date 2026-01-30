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
                if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

                echo Preflight OK
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
                '''
            }
        }

        stage('Run Loopback Tests') {
            steps {
                bat '''
                @echo off
                echo Running GPIO loopback tests...

                if not exist %REPORT_DIR% mkdir %REPORT_DIR%

                REM Default FAIL report
                (
                    echo ^<html^>
                    echo ^<body^>
                    echo ^<h1^>GPIO Loopback Tests^</h1^>
                    echo ^<p^>Build: %BUILD_NUMBER%^</p^>
                    echo ^<p^>Result: FAIL^</p^>
                    echo ^</body^>
                    echo ^</html^>
                ) > %REPORT_DIR%\\%REPORT_FILE%

                python -m mpremote connect %ESP_PORT% exec ^
                "import gpio_loopback_runner; gpio_loopback_runner.run_all_tests()"

                if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

                REM PASS report
                (
                    echo ^<html^>
                    echo ^<body^>
                    echo ^<h1^>GPIO Loopback Tests^</h1^>
                    echo ^<p^>Build: %BUILD_NUMBER%^</p^>
                    echo ^<p^>Result: PASS^</p^>
                    echo ^</body^>
                    echo ^</html^>
                ) > %REPORT_DIR%\\%REPORT_FILE%

                echo.
                echo Current working directory (Jenkins workspace):
                echo %CD%

                echo.
                echo Full HTML report path:
                echo %CD%\\%REPORT_DIR%\\%REPORT_FILE%

                echo.
                echo Report directory contents:
                dir %REPORT_DIR%
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
            echo "PIPELINE SUCCESS"
        }

        failure {
            echo "PIPELINE FAILURE"
            // GPIO failures are printed by gpio_loopback_runner
        }
    }
}