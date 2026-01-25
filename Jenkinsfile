pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        PYTHONUNBUFFERED = '1'

        SYSTEM_TEST_PASSED   = 'false'
        HARDWARE_TEST_PASSED = 'true'   // assume pass, mark false on failure
        FAILED_TESTS = ''
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
           HARDWARE TESTS
        ========================================================= */
        stage('Hardware Tests (Temperature, Wi-Fi, Bluetooth)') {
            steps {
                script {
                    def failures = []

                    if (bat(returnStatus: true, script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_ds18b20; test_runner_ds18b20.main()" > temp.txt
                    ''')) {
                        failures << 'DS18B20'
                    }

                    if (bat(returnStatus: true, script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" > wifi.txt
                    ''')) {
                        failures << 'Wi-Fi'
                    }

                    if (bat(returnStatus: true, script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_bt; test_runner_bt.run_all_tests()" > bt.txt
                    ''')) {
                        failures << 'Bluetooth'
                    }

                    if (failures) {
                        env.HARDWARE_TEST_PASSED = 'false'
                        env.FAILED_TESTS = failures.join(', ')
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
