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

        stage('Upload Tests') {
            steps {
                bat '''
                for %%f in (gpio_test\\*.py) do (
                    python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                )
                '''
            }
        }

        stage('Run GPIO Loopback Tests') {
            steps {
                script {
                    def code = bat(
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import sys, gpio_loopback_runner; sys.exit(gpio_loopback_runner.run_all_tests())"
                        ''',
                        returnStatus: true
                    )

                    echo "ESP32 exit code: ${code}"

                    if (code == 1) {
                        error("GPIO loopback FAILED: GPIO 14 → 19")
                    }

                    if (code == 2) {
                        error("GPIO loopback FAILED: GPIO 12 → 18")
                    }

                    if (code != 0) {
                        error("GPIO loopback FAILED with unknown code: ${code}")
                    }

                    echo "✓ All GPIO loopback tests passed"
                }
            }
        }
    }

    post {
        success {
            echo "✅ GPIO LOOPBACK TESTS PASSED"
        }
        failure {
            echo "❌ GPIO LOOPBACK TESTS FAILED"
            echo "Check wiring:"
            echo " - GPIO 14 → GPIO 19"
            echo " - GPIO 12 → GPIO 18"
        }
    }
}
