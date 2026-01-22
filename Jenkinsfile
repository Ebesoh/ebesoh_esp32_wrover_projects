pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        ESP_PORT = 'COM5'        // CHANGE THIS
        PYTHONUNBUFFERED = '1'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Verify Tools') {
            steps {
                bat '''
                python --version
                pip --version
                where python
                '''
            }
        }

        stage('Install CI Tools') {
            steps {
                bat '''
                pip install --upgrade pip
                pip install pyserial esptool mpremote
                '''
            }
        }

        stage('Flash MicroPython') {
            steps {
                bat '''
                esptool.py --chip esp32 --port %ESP_PORT% erase_flash
                esptool.py --chip esp32 --port %ESP_PORT% write_flash -z 0x1000 firmware\\esp32-micropython.bin
                '''
            }
        }

        stage('Upload WiFi Test Suite') {
            steps {
                bat '''
                mpremote connect %ESP_PORT% fs mkdir tests || exit /b 0
                mpremote connect %ESP_PORT% fs cp tests/*.py :
                '''
            }
        }

        stage('Run ESP32 WiFi Tests') {
            steps {
                bat '''
                python ci\\run_wifi_tests.py
                '''
            }
        }
    }

    post {
        success {
            echo '✅ WIFI CI SUCCESS: ESP32 WiFi is healthy'
        }
        failure {
            echo '❌ WIFI CI FAILURE: WiFi tests failed'
        }
        always {
            echo 'ESP32 WiFi CI run completed'
        }
    }
}
