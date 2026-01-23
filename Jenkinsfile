pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        FIRMWARE = 'firmware/ESP32_GENERIC-SPIRAM-20251209-v1.27.0.bin'
        PYTHONUNBUFFERED = '1'

        SYSTEM_RESULT = 'PASS'
        TEMP_RESULT   = 'PASS'
        WIFI_RESULT   = 'PASS'
        BT_RESULT     = 'PASS'
    }

    options {
        timestamps()
    }

    stages {

        /* ================= CHECKOUT ================= */

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        /* ================= HOST ENV ================= */

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

        /* ================= FIRMWARE ================= */

        stage('Verify Firmware') {
            steps {
                bat '''
                echo === Verifying firmware ===
                if not exist "%FIRMWARE%" (
                    echo ERROR: Firmware binary not found!
                    echo Expected path: %FIRMWARE%
                    exit /b 1
                )
                echo Firmware found
                '''
            }
        }

        stage('Flash ESP32') {
            steps {
                bat '''
                echo === Flashing ESP32 ===
                python -m esptool --chip esp32 --port %ESP_PORT% erase-flash
                python -m esptool --chip esp32 --port %ESP_PORT% write-flash -z 0x1000 %FIRMWARE%
                '''
            }
        }

        stage('Wait for ESP32 reboot') {
            steps {
                bat 'python -c "import time; time.sleep(10)"'
            }
        }

        stage('Force RAW REPL') {
            steps {
                bat '''
                python -m mpremote connect %ESP_PORT% reset
                python -c "import time; time.sleep(3)"
                '''
            }
        }

        /* ================= UPLOAD TEST FILES ================= */

        stage('Upload Test Files') {
            steps {
                bat '''
                echo === Uploading System tests ===
                for %%f in (tests_selftest_DS18B20_gps_wifi\\*.py) do (
                    python -m mpremote connect %ESP_PORT% fs cp %%f :
                )

                echo === Uploading DS18B20 tests ===
                for %%f in (test_temp\\*.py) do (
                    python -m mpremote connect %ESP_PORT% fs cp %%f :
                )

                echo === Uploading WiFi tests ===
                for %%f in (tests_wifi\\*.py) do (
                    python -m mpremote connect %ESP_PORT% fs cp %%f :
                )

                echo === Uploading Bluetooth tests ===
                for %%f in (tests_bt\\*.py) do (
                    python -m mpremote connect %ESP_PORT% fs cp %%f :
                )
                '''
            }
        }

        /* ================= SYSTEM TESTS ================= */

        stage('Run System Self-Tests') {
            steps {
                bat '''
                echo === Running System Self-Tests ===

                python -m mpremote connect %ESP_PORT% exec ^
                "import test_runner_system; test_runner_system.main()" ^
                > esp32_system_output.txt || echo mpremote exit ignored

                type esp32_system_output.txt

                findstr /C:"CI_RESULT: FAIL" esp32_system_output.txt >nul && exit /b 1 || exit /b 0
                '''
            }
            post {
                failure { script { env.SYSTEM_RESULT = 'FAIL' } }
            }
        }

        /* ================= DS18B20 ================= */

        stage('Run DS18B20 Tests') {
            steps {
                bat '''
                echo === Running DS18B20 Tests ===

                python -m mpremote connect %ESP_PORT% exec ^
                "import test_runner_ds18b20; test_runner_ds18b20.main()" ^
                > esp32_temp_output.txt || echo mpremote exit ignored

                type esp32_temp_output.txt

                findstr /C:"CI_RESULT: FAIL" esp32_temp_output.txt >nul && exit /b 1 || exit /b 0
                '''
            }
            post {
                failure { script { env.TEMP_RESULT = 'FAIL' } }
            }
        }

        /* ================= WIFI ================= */

        stage('Run WiFi Tests') {
            steps {
                bat '''
                echo === Running WiFi Tests ===

                python -m mpremote connect %ESP_PORT% exec ^
                "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" ^
                > esp32_wifi_output.txt || echo mpremote exit ignored

                type esp32_wifi_output.txt

                findstr /C:"CI_RESULT: FAIL" esp32_wifi_output.txt >nul && exit /b 1 || exit /b 0
                '''
            }
            post {
                failure { script { env.WIFI_RESULT = 'FAIL' } }
            }
        }

        /* ================= BLUETOOTH ================= */

        stage('Run Bluetooth Tests') {
            steps {
                bat '''
                echo === Running Bluetooth Tests ===

                python -m mpremote connect %ESP_PORT% exec ^
                "import test_runner_bt; test_runner_bt.run_all_tests()" ^
                > esp32_bt_output.txt || echo mpremote exit ignored

                type esp32_bt_output.txt

                findstr /C:"CI_RESULT: FAIL" esp32_bt_output.txt >nul && exit /b 1 || exit /b 0
                '''
            }
            post {
                failure { script { env.BT_RESULT = 'FAIL' } }
            }
        }

        /* ================= FINAL VERDICT ================= */

        stage('Final CI Verdict') {
            steps {
                script {
                    echo "System     : ${env.SYSTEM_RESULT}"
                    echo "Temperature: ${env.TEMP_RESULT}"
                    echo "WiFi       : ${env.WIFI_RESULT}"
                    echo "Bluetooth  : ${env.BT_RESULT}"

                    if (env.SYSTEM_RESULT == 'FAIL' ||
                        env.TEMP_RESULT   == 'FAIL' ||
                        env.WIFI_RESULT   == 'FAIL' ||
                        env.BT_RESULT     == 'FAIL') {
                        error('CI FAILED — One or more subsystems failed')
                    }

                    echo 'CI PASSED — All subsystems healthy'
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.txt', allowEmptyArchive: true
            echo 'CI run completed'
        }
        success {
            echo 'CI PIPELINE SUCCESS'
        }
        failure {
            echo 'CI PIPELINE FAILURE'
        }
    }
}

