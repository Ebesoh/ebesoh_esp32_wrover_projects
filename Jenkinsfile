pipeline {
    agent any

    options {
        timestamps() // Lägger till tidsstämplar på alla rader i konsolutdata
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

        stage('Upload Loopback Tests') {
            steps {
                bat '''
                @echo off
                for %%f in (gpio_test\\*.py) do (
                    python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                )
                '''
            }
        }

        stage('Run Loopback Tests') {
            steps {
                script {

                    bat 'if not exist %REPORT_DIR% mkdir %REPORT_DIR%'

                    def output = bat(
                        script: '''
                        @echo off
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import gpio_loopback_runner; gpio_loopback_runner.run_all_tests()"
                        ''',
                        returnStdout: true
                    ).trim()

                    echo "=== ESP32 OUTPUT ==="
                    echo output

                    // Explicit test list (source of truth)
                    def tests = [
                        "GPIO 14 - 19",
                        "GPIO 12 - 18"
                    ]

                    def failedTests = []

                    tests.each { t ->
                        if (output.contains(t)) {
                            failedTests << t
                        }
                    }

                    // Generate HTML report
                    def html = new StringBuilder()
                    html << "<html><body>"
                    html << "<h1>GPIO Loopback Test Report</h1>"
                    html << "<p>Build: ${env.BUILD_NUMBER}</p>"
                    html << "<table border='1' cellpadding='6'>"
                    html << "<tr><th>Test Name</th><th>Status</th></tr>"

                    tests.each { t ->
                        if (failedTests.contains(t)) {
                            html << "<tr><td>${t}</td><td style='color:red'>FAIL</td></tr>"
                        } else {
                            html << "<tr><td>${t}</td><td style='color:green'>PASS</td></tr>"
                        }
                    }

                    html << "</table></body></html>"

                    writeFile file: "${REPORT_DIR}/${REPORT_FILE}", text: html.toString()

                    echo "HTML report generated at:"
                    echo "${pwd()}/${REPORT_DIR}/${REPORT_FILE}"

                    if (!failedTests.isEmpty()) {
                        error("GPIO loopback tests FAILED: ${failedTests.join(', ')}")
                    }

                    echo "All GPIO loopback tests PASSED"
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
        }
    }
}
