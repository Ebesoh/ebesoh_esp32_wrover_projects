pipeline {
    agent any

    triggers {
        githubPush()
    }

    options {
        timestamps()
        disableConcurrentBuilds(abortPrevious: true)
    }

    environment {
        ESP_PORT = 'COM5'
        PYTHONUNBUFFERED = '1'
        REPORT_DIR = 'html-report'
        REPORT_FILE = 'gpio-loopback-report.html'
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

        stage('Upload Loopback Tests') {
            steps {
                bat '''
                @echo off
                echo Uploading test files to ESP32...
                for %%f in (gpio_test\\*.py) do (
                    python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                )
                '''
            }
        }

        stage('Run Loopback Tests') {
            steps {
                script {
                    def output = bat(
                        script: '''
                        @echo off
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import gpio_loopback_runner; gpio_loopback_runner.run_all_tests()"
                        ''',
                        returnStdout: true
                    ).trim()

                    writeFile file: 'esp_output.txt', text: output

                    def failedGpios = []

                    if (output.contains("GPIO 14 - 19")) {
                        failedGpios << "GPIO 14 -> GPIO 19"
                    }
                    if (output.contains("GPIO 12 - 18")) {
                        failedGpios << "GPIO 12 -> GPIO 18"
                    }

                    output.split('\n').each { line ->
                        def clean = line.trim()
                        if (clean.startsWith("- ")) {
                            failedGpios << clean.substring(2)
                        }
                    }

                    failedGpios = failedGpios.unique()
                    def passed = failedGpios.isEmpty() && output.contains("CI_RESULT: PASS")
                    def status = passed ? "PASS" : "FAIL"

                    // --- HTML HEADER ---
                    bat """
                    @echo off
                    if not exist %REPORT_DIR% mkdir %REPORT_DIR%
                    (
                      echo ^<!DOCTYPE html^>
                      echo ^<html^>
                      echo ^<head^>
                      echo ^<title^>GPIO Loopback Test Report^</title^>
                      echo ^<style^>
                      echo body { font-family: Arial; padding: 20px; }
                      echo .pass { color: green; font-weight: bold; }
                      echo .fail { color: red; font-weight: bold; }
                      echo pre { background: #f4f4f4; padding: 10px; }
                      echo ^</style^>
                      echo ^</head^>
                      echo ^<body^>
                      echo ^<h1^>GPIO Loopback Test Report^</h1^>
                      echo ^<p^>Result: ^<span class="${status.toLowerCase()}"^>${status}^</span^>^</p^>
                      echo ^<h2^>Failed GPIOs^</h2^>
                      echo ^<ul^>
                    ) > %REPORT_DIR%\\%REPORT_FILE%
                    """

                    // --- FAILED GPIO LIST ---
                    if (failedGpios.isEmpty()) {
                        bat "echo <li>None</li> >> %REPORT_DIR%\\%REPORT_FILE%"
                    } else {
                        failedGpios.each { g ->
                            bat "echo <li>${g}</li> >> %REPORT_DIR%\\%REPORT_FILE%"
                        }
                    }

                    // --- RAW OUTPUT ---
                    bat """
                    (
                      echo ^</ul^>
                      echo ^<h2^>Raw ESP32 Output^</h2^>
                      echo ^<pre^>
                    ) >> %REPORT_DIR%\\%REPORT_FILE%
                    """

                    bat "type esp_output.txt >> %REPORT_DIR%\\%REPORT_FILE%"

                    // --- HTML FOOTER ---
                    bat """
                    (
                      echo ^</pre^>
                      echo ^</body^>
                      echo ^</html^>
                    ) >> %REPORT_DIR%\\%REPORT_FILE%
                    """

                    // --- FAIL BUILD IF NEEDED ---
                    if (!failedGpios.isEmpty()) {
                        echo "Failed GPIOs:"
                        failedGpios.each { echo " - ${it}" }
                        error("GPIO loopback tests FAILED (${failedGpios.size()} failure(s))")
                    }

                    if (!output.contains("CI_RESULT: PASS")) {
                        error("Unexpected output from ESP32")
                    }

                    echo "All GPIO loopback tests PASSED"
                }
            }
        }
    }

    post {
        always {
            publishHTML([
                reportName: 'GPIO Loopback Test Report',
                reportDir: "${REPORT_DIR}",
                reportFiles: "${REPORT_FILE}",
                keepAll: true,
                alwaysLinkToLastBuild: true,
                allowMissing: false
            ])
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
