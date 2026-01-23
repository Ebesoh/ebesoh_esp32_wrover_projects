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
                echo === Installing ESP32 host tools ===
                python -m pip install --upgrade pip
                python -m pip install esptool mpremote
                '''
            }
        }

        stage('Flash ESP32 (optional)') {
            steps {
                bat '''
                echo === Flashing ESP32-WROVER (optional) ===
                python -m esptool --chip esp32 --port %ESP_PORT% erase-flash || echo Skipping erase
                python -m esptool --chip esp32 --port %ESP_PORT% write-flash -z 0x1000 %FIRMWARE% || echo Skipping flash
                '''
            }
        }

        stage('Wait for ESP32 reboot') {
            steps {
                bat '''
                echo === Waiting for ESP32 reboot ===
                python -c "import time; time.sleep(10)"
                '''
            }
        }

        stage('Force RAW REPL') {
            steps {
                bat '''
                echo === Forcing RAW REPL ===
                python -m mpremote connect %ESP_PORT% reset
                python -c "import time; time.sleep(3)"
                '''
            }
        }

        stage('Upload WiFi + Bluetooth Test Files') {
            steps {
                bat '''
                echo === Uploading WiFi test files ===
                for %%f in (tests_wifi\\*.py) do (
                    echo Uploading %%f
                    python -m mpremote connect %ESP_PORT% fs cp %%f :
                )

                echo === Uploading Bluetooth test files ===
                for %%f in (tests_bt\\*.py) do (
                    echo Uploading %%f
                    python -m mpremote connect %ESP_PORT% fs cp %%f :
                )
                '''
            }
        }

        stage('Run WiFi Tests on ESP32') {
            steps {
                bat '''
                echo === Running WiFi tests ===

                python -m mpremote connect %ESP_PORT% exec ^
                "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" ^
                > esp32_wifi_output.txt

                echo === WIFI TEST OUTPUT ===
                type esp32_wifi_output.txt

                findstr /C:"CI_RESULT: FAIL" esp32_wifi_output.txt && (
                    echo WIFI TESTS FAILED
                    exit /b 1
                )

                echo WIFI TESTS PASSED
                '''
            }
        }

        stage('Run Bluetooth Tests on ESP32') {
            steps {
                bat '''
                echo === Running Bluetooth tests ===

                python -m mpremote connect %ESP_PORT% exec ^
                "import test_runner_bt; test_runner_bt.run_all_tests()" ^
                > esp32_bt_output.txt

                echo === BLUETOOTH TEST OUTPUT ===
                type esp32_bt_output.txt

                findstr /C:"CI_RESULT: FAIL" esp32_bt_output.txt && (
                    echo BLUETOOTH TESTS FAILED
                    exit /b 1
                )

                echo BLUETOOTH TESTS PASSED
                '''
            }
        }
    }

    post {
        success {
            echo '✅ CI PIPELINE SUCCESS — WiFi and Bluetooth tests passed'
        }
        failure {
            echo '❌ CI PIPELINE FAILURE — WiFi and/or Bluetooth tests failed'
        }
        always {
            echo 'ℹ️ CI run completed'
            archiveArtifacts artifacts: '*.txt', allowEmptyArchive: true
        }
    }
}

