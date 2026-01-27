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
                for %%f in (gpio_test\\*.py) do python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                '''
            }
        }

        stage('Run Loopback Tests') {
            steps {
                script {
                    def code = bat(
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import gpio_loopback_runner; gpio_loopback_runner.run_all_tests()"
                        ''',
                        returnStatus:true 
                    )

                    echo "ESP32 exit code: ${code}"

                    if (code == 1) {
                        error("Loopback test failed: GPIO 14 -> 19")
                    } else if (code == 2) {
                        error("Loopback test failed: GPIO 12 -> 18")
                    } else if (code != 0) {
                        error("Unknown failure code: ${code}")
                    }
                }
            }
        }
    }
}
