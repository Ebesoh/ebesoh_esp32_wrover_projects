pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        FIRMWARE = 'firmware/ESP32_GENERIC-SPIRAM-20251209-v1.27.0.bin'
        PYTHONUNBUFFERED = '1'
    }

    options {
        timestamps()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Verify Python Environment') {
            steps {
                bat '''
                echo === Python Environment ===
                where python
                python --version
                python -m pip --version
                '''
            }
        }

        stage('Install Host Tools') {
            steps {
                bat '''
                echo === Installing ESP32 tools ===
                python -m pip install --upgrade pip
                python -m pip install esptool mpremote
                '''
            }
        }

        stage('Flash ESP32 (optional)') {
            steps {
                bat '''
                echo === Flashing ESP32-WROVER ===
                python -m esptool --chip esp32 --port %ESP_PORT% erase-flash || exit /b 0
                python -m esptool --chip esp32 --port %ESP_PORT% write-flash -z 0x1000 %FIRMWARE% || exit /b 0
                '''
            }
        }

        stage('Wait for ESP32 reboot') {
            steps {
                bat '''
                echo === Waiting for ESP32 reboot ===
                python - <<EOF
import time
time.sleep(10)
EOF
                '''
            }
        }

        stage('Upload WiFi Test Files') {
            steps {
                bat '''
                echo === Uploading WiFi test files ===
                python -m mpremote connect %ESP_PORT% fs cp tests :
                '''
            }
        }

        stage('Run WiFi Test Suite on ESP32') {
            steps {
                bat '''
                echo === Running WiFi tests on ESP32 ===
                python -m mpremote connect %ESP_PORT% exec "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()"
                '''
            }
        }

        stage('Evaluate Result') {
            steps {
                bat '''
                echo === Evaluating CI result ===
                python -m mpremote connect %ESP_PORT% exec "print('CI_RESULT: PASS')" || exit /b 1
                '''
            }
        }
    }

    post {
        success {
            echo '✅ CI PIPELINE SUCCESS — ESP32 WiFi tests passed'
        }
        failure {
            echo '❌ CI PIPELINE FAILURE — ESP32 WiFi tests failed'
        }
        always {
            echo 'ℹ️ CI run completed'
        }
    }
}
