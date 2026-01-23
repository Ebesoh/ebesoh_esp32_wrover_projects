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
                echo === Python detection ===
                where python
                python --version
                '''
            }
        }

        stage('Install Tooling') {
            steps {
                bat '''
                echo === Installing tools ===
                python -m pip install --upgrade pip
                python -m pip install esptool mpremote pytest
                '''
            }
        }

        stage('Flash ESP32-WROVER') {
            steps {
                bat '''
                echo === Flashing ESP32-WROVER ===

                python -m esptool --chip esp32 --port %ESP_PORT% erase-flash

                ping 127.0.0.1 -n 6 > nul

                python -m esptool --chip esp32 --port %ESP_PORT% write-flash -z 0x1000 %FIRMWARE%
                '''
            }
        }

        stage('Wait for Device Reboot') {
            steps {
                bat '''
                echo === Waiting for ESP32 reboot ===
                ping 127.0.0.1 -n 11 > nul
                '''
            }
        }

        stage('Reset ESP32 (mpremote)') {
            steps {
                bat '''
                echo === Resetting ESP32 via mpremote ===
                python -m mpremote connect %ESP_PORT% reset
                ping 127.0.0.1 -n 6 > nul
                '''
            }
        }

        stage('Upload WiFi Test Files') {
            steps {
                bat '''
                echo === Uploading WiFi test files ===
                python -m mpremote connect %ESP_PORT% fs cp tests\\*.py :
                ping 127.0.0.1 -n 4 > nul
                '''
            }
        }

        stage('Run WiFi Test Suite on ESP32') {
            steps {
                bat '''
                echo === Running WiFi tests on ESP32 ===

                python -m mpremote connect %ESP_PORT% exec "
import test_wifi_runner
test_wifi_runner.run_all_wifi_tests()
"
                '''
            }
        }
    }

    post {
        success {
            echo 'CI PIPELINE SUCCESS: ESP32 WiFi tests passed'
        }
        failure {
            echo 'CI PIPELINE FAILURE: ESP32 WiFi tests failed'
        }
        always {
            echo 'CI run completed'
        }
    }
}

