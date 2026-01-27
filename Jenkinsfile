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
                python -m pip install --upgrade pip
                python -m pip install mpremote
                '''
            }
        }

        stage('Upload Loopback Tests') {
            steps {
                bat '''
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

                    echo "ESP32 output:"
                    echo output

                    if (output.contains("CI_RESULT: PASS")) {
                        echo "✓ All GPIO loopback tests passed"
                    }
                    else if (output.contains("CI_RESULT: FAIL")) {

                        if (output.contains("GPIO 14 -> 19")) {
                            error("Loopback test failed: GPIO 14 -> 19")
                        }

                        if (output.contains("GPIO 12 -> 18")) {
                            error("Loopback test failed: GPIO 12 -> 18")
                        }

                        error("Loopback test failed (unknown reason)")
                    }
                    else {
                        error("Unexpected output from ESP32:\n${output}")
                    }
                }
            }
        }
    }
}

