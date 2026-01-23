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
                    exit /b 1
                )
                echo Firmware OK
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

        /* ================= SYSTEM TEST (CI GATE) ================= */

        stage('Run System Self-Test (CI Gate)') {
            steps {
                bat '''
                echo === Running System Self-Test ===

                python -m mpremote connect %ESP_PORT% exec ^
                "import test_runner_system; test_runner_system.main()" ^
                > esp32_system_output.txt || echo mpremote exit ignored

                type esp32_system_output.txt

                findstr /C:"CI_RESULT: FAIL" esp32_system_output.txt >nul && exit /b 1 || exit /b 0
                '''
            }
            post {
                failure {
                    script { env.SYSTEM_RESULT = 'FAIL' }
                }
            }
        }

        /* ================= DS18B20 (NON-GATING) ================= */

        stage('Run DS18B20 Tests') {
            steps {
                bat '''
                echo === Running DS18B20 Tests ===

                python -m mpremote connect %ESP_PORT% exec ^
                "import test_runner_ds18b20; test_runner_ds18b20.main()" ^
                > esp32_temp_output.txt || echo mpremote exit ignored

                type esp32_temp_output.txt

                findstr /C:"CI_RESULT: FAIL" esp32_temp_output.txt >nul && (
                    echo DS18B20 TESTS FAILED
                    exit /b 0
                )
                '''
            }
            post {
                always { script { env.TEMP_RESULT = 'CHECKED' } }
            }
        }

        /* ================= WIFI (NON-GATING) ================= */

        stage('Run WiFi Tests') {
            steps {
                bat '''
                echo === Running WiFi Tests ===

                python -m mpremote connect %ESP_PORT% exec ^
                "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" ^
                > esp32_wifi_output.txt || echo mpremote exit ignored

                type esp32_wifi_output.txt
                '''
            }
            post {
                always { script { env.WIFI_RESULT = 'CHECKED' } }
            }
        }

        /* ================= BLUETOOTH (NON-GATING) ================= */

        stage('Run Bluetooth Tests') {
            steps {
                bat '''
                echo === Running Bluetooth Tests ===

                python -m mpremote connect %ESP_PORT% exec ^
                "import test_runner_bt; test_runner_bt.run_all_tests()" ^
                > esp32_bt_output.txt || echo mpremote exit ignored

                type esp32_bt_output.txt
                '''
            }
            post {
                always { script { env.BT_RESULT = 'CHECKED' } }
            }
        }

        /* ================= FINAL VERDICT ================= */

        stage('Final CI Verdict') {
            steps {
                script {
                    echo "SYSTEM SELF-TEST : ${env.SYSTEM_RESULT}"
                    echo "DS18B20 TESTS    : ${env.TEMP_RESULT}"
                    echo "WIFI TESTS       : ${env.WIFI_RESULT}"
                    echo "BLUETOOTH TESTS  : ${env.BT_RESULT}"

                    if (env.SYSTEM_RESULT == 'FAIL') {
                        error('CI FAILED — System Self-Test failed')
                    }

                    echo 'CI PASSED — System Self-Test OK'
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

