pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        FIRMWARE = 'firmware/ESP32_GENERIC-SPIRAM-20251209-v1.27.0.bin'
        PYTHONUNBUFFERED = '1'

        TEMP_RESULT = 'PASS'
        WIFI_RESULT = 'PASS'
        BT_RESULT   = 'PASS'
        FAILED_TESTS = ''
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {

        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Verify Python Environment') {
            steps {
                bat '''
                where python
                python --version
                python -m pip --version
                '''
            }
        }

        stage('Install Host Tools') {
            steps {
                bat '''
                python -m pip install --upgrade pip
                python -m pip install esptool mpremote
                '''
            }
        }

        stage('Flash ESP32 (optional)') {
            steps {
                bat '''
                python -m esptool --chip esp32 --port %ESP_PORT% erase-flash || echo Skipping erase
                python -m esptool --chip esp32 --port %ESP_PORT% write-flash -z 0x1000 %FIRMWARE% || echo Skipping flash
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

        stage('Upload Test Files') {
            steps {
                bat '''
                for %%f in (test_temp\\*.py) do python -m mpremote connect %ESP_PORT% fs cp %%f :
                for %%f in (tests_wifi\\*.py) do python -m mpremote connect %ESP_PORT% fs cp %%f :
                for %%f in (tests_bt\\*.py)   do python -m mpremote connect %ESP_PORT% fs cp %%f :
                for %%f in (tests_selftest_DS18B20_gps_wifi\\*.py) do python -m mpremote connect %ESP_PORT% fs cp %%f :
                '''
            }
        }

        /* ===== SYSTEM HARD GATE ===== */
        stage('System Self-Test (HARD GATE)') {
            steps {
                script {
                    def rc = bat(
                        returnStatus: true,
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_system; test_runner_system.main()" > system.txt
                        '''
                    )

                    if (rc != 0) {
                        error('SYSTEM SELF-TEST FAILED — PIPELINE STOPPED')
                    }
                }
            }
        }

        stage('DS18B20 Temperature Tests') {
            steps {
                script {
                    def rc = bat(
                        returnStatus: true,
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_ds18b20; test_runner_ds18b20.main()" > temp.txt
                        '''
                    )

                    if (rc != 0) {
                        env.TEMP_RESULT = 'FAIL'
                        env.FAILED_TESTS += env.FAILED_TESTS ? ', DS18B20' : 'DS18B20'
                    }
                }
            }
        }

        stage('Wi-Fi Tests') {
            steps {
                script {
                    def rc = bat(
                        returnStatus: true,
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" > wifi.txt
                        '''
                    )

                    if (rc != 0) {
                        env.WIFI_RESULT = 'FAIL'
                        env.FAILED_TESTS += env.FAILED_TESTS ? ', Wi-Fi' : 'Wi-Fi'
                    }
                }
            }
        }

        stage('Bluetooth Tests') {
            steps {
                script {
                    def rc = bat(
                        returnStatus: true,
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_bt; test_runner_bt.run_all_tests()" > bt.txt
                        '''
                    )

                    if (rc != 0) {
                        env.BT_RESULT = 'FAIL'
                        env.FAILED_TESTS += env.FAILED_TESTS ? ', Bluetooth' : 'Bluetooth'
                    }
                }
            }
        }

        stage('Final CI Verdict') {
            steps {
                script {
                    echo "Temperature : ${env.TEMP_RESULT}"
                    echo "Wi-Fi       : ${env.WIFI_RESULT}"
                    echo "Bluetooth   : ${env.BT_RESULT}"

                    if (env.FAILED_TESTS) {
                        echo "FAILED TESTS: ${env.FAILED_TESTS}"
                        error('FINAL VERDICT: One or more test suites failed')
                    }

                    echo 'ALL TEST SUITES PASSED'
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.txt', allowEmptyArchive: true
        }
        success {
            echo 'PIPELINE SUCCESS'
        }
        failure {
            echo 'PIPELINE FAILURE'
        }
    }
}
