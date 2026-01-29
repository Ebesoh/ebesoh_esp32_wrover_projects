pipeline {
    agent any

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

                    writeFile file: 'test_output.txt', text: output

                    def failedGpios = []

                    // Explicit known failures
                    if (output.contains("GPIO 14 - 19")) {
                        failedGpios << "GPIO 14 -> GPIO 19"
                    }
                    if (output.contains("GPIO 12 - 18")) {
                        failedGpios << "GPIO 12 -> GPIO 18"
                    }

                    // Generic failure lines: "- GPIO X -> GPIO Y"
                    output.split('\n').each { line ->
                        def clean = line.trim()
                        if (clean.startsWith("- ")) {
                            failedGpios << clean.substring(2)
                        }
                    }

                    failedGpios = failedGpios.unique()

                    def passed = failedGpios.isEmpty() && output.contains("CI_RESULT: PASS")
                    def status = passed ? "PASS" : "FAIL"

                    def failedHtml = failedGpios.isEmpty()
                        ? "<li>None</li>"
                        : failedGpios.collect { "<li>${it}</li>" }.join("\n")

                    // Generate HTML report
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
                        echo ^</style^>
                        echo ^</head^>
                        echo ^<body^>
                        echo ^<h1^>GPIO Loopback Test Report^</h1^>
                        echo ^<p^>Result: ^<span class="${status.toLowerCase()}"^>${status}^</span^>^</p^>
                        echo ^<h2^>Failed GPIOs^</h2^>
                        echo ^<ul^>
                        echo ${failedHtml}
                        echo ^</ul^>
                        echo ^</body^>
                        echo ^</html^>
                    ) > %REPORT_DIR%\\%REPORT_FILE%
                    """

                    // Echo ONLY failures
                    if (!failedGpios.isEmpty()) {
                        echo "Failed GPIOs:"
                        failedGpios.each { gpio ->
                            echo " - ${gpio}"
                        }
                        error("GPIO loopback tests FAILED (${failedGpios.size()} failure(s))")
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
