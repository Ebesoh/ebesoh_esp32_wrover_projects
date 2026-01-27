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

                    // Collect all faults printed by the ESP32
                    def faults = []

                    output.eachLine { line ->
                        if (line.startsWith("- ")) {
                            faults << line.substring(2)
                        }
                    }

                    // Print all detected faults
                    if (!faults.isEmpty()) {
                        echo "Detected GPIO loopback faults:"
                            echo " - ${faults}"
                        }
                        error("GPIO loopback tests FAILED (${faults.size()} fault(s))")
                    }

                    // Final sanity check
                    if (output.contains("CI_RESULT: PASS")) {
                        echo "✓ All GPIO loopback tests PASSED"
                    } else if (output.contains("CI_RESULT: FAIL")) {
                        error("GPIO loopback tests FAILED (see faults above)")
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
