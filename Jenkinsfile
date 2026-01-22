pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        ESP_PORT = 'COM5'          // 🔧 CHANGE if needed
        PYTHONUNBUFFERED = '1'
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
                pip --version
                '''
            }
        }

        stage('Install CI Tools') {
            steps {
                bat '''
                echo === Installing CI tools ===
                python -m pip install --upgrade pip
                python -m pip install esptool mpremote pyserial
                '''
            }
        }

        stage('Flash MicroPython Firmware') {
            steps {
                bat '''
                echo === Flashing ESP32-WROVER ===
                python -m esptool --chip esp32 --port %ESP_PORT% erase_flash
                python -m esptool --chip esp32 --port %ESP_PORT% write_flash -z 0x1000 firmware\\esp32-micropython.bin
                '''
            }
        }

        stage('Upload WiFi Test Suite') {
            steps {
                bat '''
                echo === Uploading WiFi test files ===
                python -m mpremote connect %ESP_PORT% fs cp tests\\*.py :
                '''
            }
        }

        stage('Run ESP32 WiFi Tests') {
            steps {
                bat '''
                echo === Running ESP32 WiFi Test Runner ===
                python ci\\run_wifi_tests.py
                '''
            }
        }
    }

    post {
        success {
            echo '✅ WIFI CI SUCCESS: ESP32 WiFi tests passed'
        }
        failure {
            echo '❌ WIFI CI FAILURE: One or more WiFi tests failed'
        }
        always {
            echo 'ESP32 WiFi CI pipeline completed'
        }
    }
}
