pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
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
                echo === Python Detection ===
                where python
                python --version
                python -m pip --version
                '''
            }
        }

        stage('Install Host Tools') {
            steps {
                bat '''
                echo === Installing host-side tools ===
                python -m pip install --upgrade pip
                python -m pip install esptool mpremote
                '''
            }
        }

        stage('Flash MicroPython Firmware') {
            steps {
                bat '''
                echo === Flashing ESP32-WROVER ===

                echo Erasing flash...
                python -m esptool --chip esp32 --port %ESP_PORT% erase-flash

                echo Writing MicroPython firmware...
                python -m esptool --chip esp32 --port %ESP_PORT% write-flash -z 0x1000 firmware\\esp32-micropython.bin
                '''
            }
        }

        stage('Wait for Device Reboot') {
            steps {
                bat '''
                echo === Waiting for ESP32 reboot ===
                timeout /t 6 /nobreak > nul
                '''
            }
        }

        stage('Reset MicroPython & Prepare REPL') {
            steps {
                bat '''
                echo === Resetting MicroPython ===
                python -m mpremote connect %ESP_PORT% reset

                echo === Waiting for MicroPython boot ===
                timeout /t 5 /nobreak > nul
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

        stage('Run WiFi Test Suite on ESP32') {
            steps {
                bat '''
                echo === Running WiFi test suite on device ===
                python -m mpremote connect %ESP_PORT% run test_wifi_runner.py
                '''
            }
        }
    }

    post {
        success {
            echo '✅ CI SUCCESS: ESP32 WiFi tests passed'
        }
        failure {
            echo '❌ CI FAILURE: ESP32 WiFi tests failed'
        }
        always {
            echo 'CI run completed'
        }
    }
}
