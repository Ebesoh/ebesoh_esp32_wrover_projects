pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        PYTHONUNBUFFERED = '1'
    }

    stages {

        stage('Install Tools') {
            steps {
                bat '''
                echo Installing tools...
                python -m pip install --upgrade pip
                python -m pip install mpremote
                '''
            }
        }

        stage('Upload Loopback Tests') {
            steps {
                bat '''
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
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import gpio_loopback_runner; gpio_loopback_runner.run_all_tests()"
                        ''',
                        returnStdout: true
                    ).trim()

                    echo "=== ESP32 OUTPUT ==="
                    echo output
                    echo "===================="

                    // Collect all detected failures
                    def failures = []

                    if (output.contains("CI_RESULT: FAIL")) {

                        if (output.contains("GPIO 14 -> 19")) {
                            failures << "GPIO 14 -> 19"
                        }

                        if (output.contains("GPIO 12 -> 18")) {
                            failures << "GPIO 12 -> 18"
                        }

                        if (failures.isEmpty()) {
                            failures << "Unknown failure"
                        }
                    }

                    // Final decision (single authority)
                    if (!failures.isEmpty()) {
                        echo "Detected loopback failures:"
                        failures.each { f ->
                            echo "- ${f}"
                        }
                        error("GPIO loopback tests FAILED: ${failures.join(', ')}")
                    }

                    if (output.contains("CI_RESULT: PASS")) {
                        echo "✓ All GPIO loopback tests PASSED"
                    } else {
                        error("Unexpected output from ESP32:\n${output}")
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ PIPELINE SUCCESS: GPIO loopback tests passed"
        }

        failure {
            echo "❌ PIPELINE FAILURE: GPIO loopback tests failed"
            echo "Check wiring:"
            echo " - GPIO 14 → GPIO 19"
            echo " - GPIO 12 → GPIO 18"
        }
    }
}

