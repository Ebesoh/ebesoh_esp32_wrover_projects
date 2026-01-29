pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds(abortPrevious: true)
    }

    environment {
        ESP_PORT = 'COM5'
        REPORT_DIR = 'reports'
        REPORT_FILE = 'gpio_loopback_report.html'
    }

    stages {

        stage('Install Tools') {
            steps {
                bat 'python -m pip install --upgrade pip mpremote'
            }
        }

        stage('Preflight') {
            steps {
                bat 'python -m mpremote connect port=%ESP_PORT% exec "pass"'
            }
        }

        stage('Upload Tests') {
            steps {
                bat '''
                @echo off
                for %%f in (gpio_test\\*.py) do (
                    python -m mpremote connect port=%ESP_PORT% fs cp "%%f" :
                    if ERRORLEVEL 1 exit /b 1
                )
                '''
            }
        }

        stage('Run Tests') {
            steps {
                script {

                    writeFile file: "${REPORT_DIR}/${REPORT_FILE}", text: """
                    <html><body>
                    <h1>GPIO Loopback Tests</h1>
                    <p>Build: ${env.BUILD_NUMBER}</p>
                    <p>Result: FAIL</p>
                    </body></html>
                    """

                    def output = bat(
                        returnStdout: true,
                        script: '''
                        @echo off
                        python -m mpremote connect port=%ESP_PORT% exec ^
                        "import gpio_loopback_runner; print(gpio_loopback_runner.run_all_tests())"
                        '''
                    ).trim()

                    echo "Test result code: ${output}"

                    if (output != '1') {
                        error('GPIO loopback tests failed')
                    }

                    writeFile file: "${REPORT_DIR}/${REPORT_FILE}", text: """
                    <html><body>
                    <h1>GPIO Loopback Tests</h1>
                    <p>Build: ${env.BUILD_NUMBER}</p>
                    <p>Result: PASS</p>
                    </body></html>
                    """
                }
            }
        }
    }

    post {
        always {
            publishHTML([
                reportDir: REPORT_DIR,
                reportFiles: REPORT_FILE,
                reportName: 'ESP32 GPIO Loopback Report'
            ])
            archiveArtifacts artifacts: "${REPORT_DIR}/${REPORT_FILE}"
        }
    }
}
