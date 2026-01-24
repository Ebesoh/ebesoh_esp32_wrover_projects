pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        FIRMWARE = 'firmware/ESP32_GENERIC-SPIRAM-20251209-v1.27.0.bin'
        PYTHONUNBUFFERED = '1'
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        /* =========================================================
           INITIALIZE VARIABLES
        ========================================================= */
        stage('Initialize') {
            steps {
                script {
                    // Set global variables here
                    env.SYSTEM_TEST_PASSED = 'false'
                    env.HARDWARE_TEST_PASSED = 'true'
                    env.FAILED_TESTS = ''
                }
            }
        }

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
           SYSTEM SELF TEST (HARD GATE)
        ========================================================= */
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
                        env.SYSTEM_TEST_PASSED = 'false'
                        error('System Self-Test failed')
                    }

                    env.SYSTEM_TEST_PASSED = 'true'
                }
            }
        }

        /* =========================================================
           HARDWARE TESTS - TEMPERATURE
        ========================================================= */
        stage('Temperature Test (DS18B20)') {
            options {
                timeout(time: 2, unit: 'MINUTES')
            }
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
                        if (!env.FAILED_TESTS) {
                            env.FAILED_TESTS = 'DS18B20'
                        } else {
                            env.FAILED_TESTS = env.FAILED_TESTS + ', DS18B20'
                        }
                        env.HARDWARE_TEST_PASSED = 'false'
                        currentBuild.result = 'FAILURE'  // Mark stage as failed
                    }
                }
            }
        }

        /* =========================================================
           HARDWARE TESTS - WI-FI
        ========================================================= */
        stage('Wi-Fi Test') {
            options {
                timeout(time: 5, unit: 'MINUTES')
            }
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
                        if (!env.FAILED_TESTS) {
                            env.FAILED_TESTS = 'Wi-Fi'
                        } else {
                            env.FAILED_TESTS = env.FAILED_TESTS + ', Wi-Fi'
                        }
                        env.HARDWARE_TEST_PASSED = 'false'
                        currentBuild.result = 'FAILURE'  // Mark stage as failed
                    }
                }
            }
        }

        /* =========================================================
           HARDWARE TESTS - BLUETOOTH
        ========================================================= */
        stage('Bluetooth Test') {
            options {
                timeout(time: 3, unit: 'MINUTES')
            }
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
                        if (!env.FAILED_TESTS) {
                            env.FAILED_TESTS = 'Bluetooth'
                        } else {
                            env.FAILED_TESTS = env.FAILED_TESTS + ', Bluetooth'
                        }
                        env.HARDWARE_TEST_PASSED = 'false'
                        currentBuild.result = 'FAILURE'  // Mark stage as failed
                    }
                }
            }
        }

        /* =========================================================
           FINAL VERDICT (EXPLICIT AUTHORITY)
        ========================================================= */
        stage('Final CI Verdict') {
            steps {
                script {
                    echo "SYSTEM_TEST_PASSED   = ${env.SYSTEM_TEST_PASSED}"
                    echo "HARDWARE_TEST_PASSED = ${env.HARDWARE_TEST_PASSED}"

                    if (env.SYSTEM_TEST_PASSED != 'true') {
                        error('Final verdict: System Self-Test failed')
                    }

                    if (env.HARDWARE_TEST_PASSED != 'true') {
                        echo "FAILED HARDWARE TESTS: ${env.FAILED_TESTS}"
                        error('Final verdict: One or more hardware tests failed')
                    }

                    echo 'FINAL VERDICT: ALL TESTS PASSED'
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