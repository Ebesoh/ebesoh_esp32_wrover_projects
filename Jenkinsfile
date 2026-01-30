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

        stage('Preflight') {
            steps {
                bat '''
                @echo off
                echo Preflight: checking ESP32 on %ESP_PORT%...

                python -m mpremote connect port=%ESP_PORT% exec "pass"
                if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

                echo Preflight OK
                '''
            }
        }

        stage('Upload Tests') {
            steps {
                bat '''
                @echo off
                for %%f in (gpio_test\\*.py) do (
                    python -m mpremote connect port=%ESP_PORT% fs cp "%%f" :
                    if errorlevel 1 exit /b 1
                )
                '''
            }
        }

        stage('Run Tests') {
            steps {

                /* ---------- Prepare Report ---------- */
                script {
                    if (!fileExists(REPORT_DIR)) {
                        new File(REPORT_DIR).mkdirs()
                    }
                }

                writeFile file: "${REPORT_DIR}/${REPORT_FILE}", text: """
                <html><body>
                <h1>GPIO Loopback Tests</h1>
                <p>Build: ${env.BUILD_NUMBER}</p>
                <p>Result: FAIL</p>
                </body></html>
                """

                script {
                    /* ---------- Run Tests ---------- */
                    def output = bat(
                        returnStdout: true,
                        script: '''
                        @echo off
                        python -m mpremote connect port=%ESP_PORT% exec ^
                        "import gpio_loopback_runner; print(gpio_loopback_runner.run_all_tests())"
                        '''
                    ).trim()

                    echo "Test result code: ${output}"

                    switch (output) {
                        case '1':
                            writeFile file: "${REPORT_DIR}/${REPORT_FILE}", text: """
                            <html><body>
                            <h1>GPIO Loopback Tests</h1>
                            <p>Build: ${env.BUILD_NUMBER}</p>
                            <p>Result: PASS</p>
                            </body></html>
                            """
                            break

                        case '0':
                            error('GPIO test failure')
                        case '-1':
                            error('Test setup error')
                        case '-2':
                            error('ESP32 device error')
                        default:
                            error("Unknown test result code: ${output}")
                    }
                }
            }
        }
    }

    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: REPORT_DIR,
                reportFiles: REPORT_FILE,
                reportName: 'ESP32 GPIO Loopback Report'
            ])

            archiveArtifacts artifacts: "${REPORT_DIR}/${REPORT_FILE}"
        }

        success {
            echo 'PIPELINE SUCCESS'
        }

        failure {
            echo 'PIPELINE FAILURE'
        }
    }
}
