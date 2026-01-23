pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        ESP_PORT = 'COM5'
        PYTHONUNBUFFERED = '1'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Verify Python & Tools') {
            steps {
                bat '''
                echo === Python Detection ===
                where python
                python --version

                echo === Pip Detection ===
                python -m pip --version
                '''
            }
        }

        stage('Install Host Dependencies') {
            steps {
                bat '''
                echo === Installing host-side tools ===
                python -m pip install --upgrade pip
                python -m pip install esptool mpremote
                '''
            }
        }

        stage('Flash ESP32 (Optional)') {
            steps {
                bat '''
                echo === Flashing ESP32-WROVER (if firmware exists) ===

                if not exist firmware\\esp32-micropython.bin (
                    echo Firmware not found - skipping flash
                    exit /b 0
                )

                python -m esptool --chip esp32 --port %ESP_PORT% erase-flash
                python -m esptool --chip esp32 --port %ESP_PORT% write-flash -z 0x1000 firmware\\ESP32_GENERIC-SPIRAM-20251209-v1.27.0.bin
                '''
            }
        }

        stage('Wait for ESP32 Boot') {
            steps {
                bat '''
                echo === Waiting for ESP32 reboot ===
                ping 127.0.0.1 -n 6 > nul
                '''
            }
        }

        stage('Upload WiFi Test Files') {
            steps {
                bat '''
                echo === Uploading WiFi test files ===
                python -m mpremote connect %ESP_PORT% fs cp tests\\*.py :
                '''
            }
        }

        stage('Run WiFi Tests on ESP32') {
            steps {
                bat '''
                echo === Running WiFi tests on ESP32 ===

                python -m mpremote connect %ESP_PORT% exec "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()"
                '''
            }
        }
    }

    post {
        success {
            echo 'CI SUCCESS: ESP32 WiFi tests passed'
        }
        failure {
            echo 'CI FAILURE: ESP32 WiFi tests failed'
        }
        always {
            echo 'CI run completed'
        }
    }
}

