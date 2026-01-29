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
                    def status = failedGpios.isEmpty() && output.contains("CI_RESULT: PASS") ? "PASS" : "FAIL"

                    // -------- HTML REPORT (Groovy, not BAT) --------
                    def failedListHtml = failedGpios.isEmpty()
                        ? "<li>None</li>"
                        : failedGpios.collect { "<li>${it}</li>" }.join("\n")

                    def reportHtml = """
<html>
<body>
<h1>GPIO Loopback Test Report</h1>
<p>Result: <b>${status}</b></p>

<h2>Failed GPIOs</h2>
<ul>
${failedListHtml}
</ul>

<h2>Raw ESP32 Output</h2>
<pre>
${output}
</pre>
</body>
</html>
"""

                    bat "if not exist ${REPORT_DIR} mkdir ${REPORT_DIR}"
                    writeFile file: "${REPORT_DIR}/${REPORT_FILE}", text: reportHtml

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
    }
}