pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        FIRMWARE = 'firmware/ESP32_GENERIC-SPIRAM-20251209-v1.27.0.bin'
        PYTHONUNBUFFERED = '1'

        SELF_TEST_PASSED = 'false'
        TEMP_TEST_PASSED = 'true'
        WIFI_TEST_PASSED = 'true'
        BT_TEST_PASSED   = 'true'
        FAILED_TESTS     = ''
    }

    options {
        timestamps()
        disableConcurrentBuilds(abortPrevious: true)
    }

    stages {

        /* =========================================================
           PREFLIGHT
        ========================================================= */
        stage('Preflight') {
            steps {
                checkout scm

                bat '''
                where python
                python --version
                '''

                bat '''
                python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
                '''

                bat '''
                python -m pip install --upgrade pip
                python -m pip install esptool mpremote
                '''
            }
        }

        /* =========================================================
           FLASH FIRMWARE
        ========================================================= */
        stage('Flash ESP32 Firmware') {
            steps {
                bat '''
                python -m esptool --chip esp32 --port %ESP_PORT% erase-flash
                python -m esptool --chip esp32 --port %ESP_PORT% write-flash -z 0x1000 %FIRMWARE%
                '''
                powershell 'Start-Sleep -Seconds 15'
            }
        }

        /* =========================================================
           UPLOAD TEST FILES
        ========================================================= */
        stage('Upload Test Files') {
            steps {
                bat '''
                for %%f in (test_temp\\*.py) do python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                for %%f in (tests_wifi\\*.py) do python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                for %%f in (tests_bt\\*.py) do python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                for %%f in (tests_selftest_DS18B20_gps_wifi\\*.py) do python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                '''
            }
        }

        /* =========================================================
           SELF TEST (HARD GATE)
        ========================================================= */
        stage('Self-Test (HARD GATE)') {
            steps {
                script {
                    bat '''
                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_runner_system; test_runner_system.main()" > system.txt
                    '''

                    def failed = bat(
                        returnStatus: true,
                        script: 'findstr /C:"CI_RESULT=1" system.txt > null'
                    )

                    if (failed == 0) {
                        env.SELF_TEST_PASSED = 'false'
                        error('System Self-Test FAILED (hard gate)')
                    }

                    env.SELF_TEST_PASSED = 'true'
                    echo 'System Self-Test PASSED'
                }
            }
        }

        /* =========================================================
           DS18B20 TEMPERATURE TEST
        ========================================================= */
        stage('DS18B20 Temperature Test') {
            steps {
                script {
                    bat '''
                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_runner_ds18b20; test_runner_ds18b20.main()" > temp.txt
                    '''

                    def failed = bat(
                        returnStatus: true,
                        script: 'findstr /C:"CI_RESULT=1" temp.txt > null'
                    )

                    if (failed == 0) {
                        env.TEMP_TEST_PASSED = 'false'
                        env.FAILED_TESTS += env.FAILED_TESTS ? ', DS18B20' : 'DS18B20'
                        echo 'Temperature test FAILED'
                    } else {
                        echo 'Temperature test PASSED'
                    }
                }
            }
        }

        /* =========================================================
           WI-FI TEST
        ========================================================= */
        stage('Wi-Fi Test') {
            steps {
                script {
                    bat '''
                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" > wifi.txt
                    '''

                    def failed = bat(
                        returnStatus: true,
                        script: 'findstr /C:"CI_RESULT=1" wifi.txt >null'
                    )

                    if (failed == 0) {
                        env.WIFI_TEST_PASSED = 'false'
                        env.FAILED_TESTS += env.FAILED_TESTS ? ', Wi-Fi' : 'Wi-Fi'
                        echo 'Wi-Fi test FAILED'
                    } else {
                        echo 'Wi-Fi test PASSED'
                    }
                }
            }
        }

        /* =========================================================
           BLUETOOTH TEST
        ========================================================= */
        stage('Bluetooth Test') {
            steps {
                script {
                    bat '''
                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_runner_bt; test_runner_bt.run_all_tests()" > bt.txt
                    '''

                    def result = bat(
                        //returnStatus:,
                        script: 'findstr /C:"CI_RESULT=1" bt.txt >null'
                    )
                    echo 'result' = ${result}

                    if (result == 0) {
                        env.BT_TEST_PASSED = 'false'
                        env.FAILED_TESTS += env.FAILED_TESTS ? ', Bluetooth' : 'Bluetooth'
                        echo 'Bluetooth test FAILED'
                    } else {
                        echo 'Bluetooth test PASSED'
                    }
                }
            }
        }

        /* =========================================================
           FINAL VERDICT
        ========================================================= */
        stage('Final CI Verdict') {
            steps {
                script {
                    echo "SELF_TEST_PASSED = ${env.SELF_TEST_PASSED}"
                    echo "TEMP_TEST_PASSED = ${env.TEMP_TEST_PASSED}"
                    echo "WIFI_TEST_PASSED = ${env.WIFI_TEST_PASSED}"
                    echo "BT_TEST_PASSED   = ${env.BT_TEST_PASSED}"
                    echo "FAILED_TESTS     = ${env.FAILED_TESTS ?: 'None'}"

                    if (env.SELF_TEST_PASSED != 'true') {
                        error('Final verdict: System Self-Test failed')
                    }

                    if (env.TEMP_TEST_PASSED != 'true'
                        || env.WIFI_TEST_PASSED != 'true'
                        || env.BT_TEST_PASSED   != 'true') {

                        error("Final verdict: Test failures detected: ${env.FAILED_TESTS}")
                    }

                    echo 'FINAL VERDICT: ALL TESTS PASSED'
                    echo 'Congratulations for successful run!!'
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.txt', allowEmptyArchive: true
        }
        success {
            echo 'Pipeline completed successfully'
        }
        failure {
            echo 'Pipeline FAILED'
        }
    }
}