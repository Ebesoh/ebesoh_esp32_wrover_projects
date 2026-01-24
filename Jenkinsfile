pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        PYTHONUNBUFFERED = '1'
        HARDWARE_TEST_PASSED = 'true'
        FAILED_TESTS = ''
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {

        /* =========================================================
           PREFLIGHT
        ========================================================= */
        stage('Preflight') {
            steps {
                checkout scm
                bat 'python --version'
                bat 'python -m pip install --upgrade pip mpremote'
            }
        }

        /* =========================================================
           TEMPERATURE TEST
        ========================================================= */
        stage('Temperature Test (DS18B20)') {
            options {
                timeout(time: 2, unit: 'MINUTES')
            }
            steps {
                script {
                    echo 'STARTING DS18B20 TEMPERATURE TEST'

                    def rc = bat(
                        returnStatus: true,
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_ds18b20; test_runner_ds18b20.main()" > temp.txt
                        '''
                    )

                    if (rc != 0) {
                        echo "DS18B20 TEST FAILED (rc=${rc})"
                        env.FAILED_TESTS += env.FAILED_TESTS ? ', DS18B20' : 'DS18B20'
                        env.HARDWARE_TEST_PASSED = 'false'
                    } else {
                        echo 'DS18B20 TEST PASSED'
                    }

                    bat '''
                        echo === DS18B20 LOG (first 20 lines) ===
                        if exist temp.txt (
                            for /f "delims=" %%l in ('findstr /n "^" temp.txt ^| findstr "^[1-2][0-9]:"') do echo %%l
                        ) else (
                            echo temp.txt not found
                        )
                    '''
                }
            }
        }

        /* =========================================================
           WI-FI TEST
        ========================================================= */
        stage('Wi-Fi Test') {
            options {
                timeout(time: 5, unit: 'MINUTES')
            }
            steps {
                script {
                    echo 'STARTING WI-FI TEST'

                    def rc = bat(
                        returnStatus: true,
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" > wifi.txt
                        '''
                    )

                    if (rc != 0) {
                        echo "WI-FI TEST FAILED (rc=${rc})"
                        env.FAILED_TESTS += env.FAILED_TESTS ? ', Wi-Fi' : 'Wi-Fi'
                        env.HARDWARE_TEST_PASSED = 'false'
                    } else {
                        echo 'WI-FI TEST PASSED'
                    }

                    bat '''
                        echo === WI-FI LOG (first 20 lines) ===
                        if exist wifi.txt (
                            for /f "delims=" %%l in ('findstr /n "^" wifi.txt ^| findstr "^[1-2][0-9]:"') do echo %%l
                        ) else (
                            echo wifi.txt not found
                        )
                    '''
                }
            }
        }

        /* =========================================================
           FINAL VERDICT
        ========================================================= */
        stage('Final Verdict') {
            steps {
                script {
                    echo 'FINAL VERDICT'
                    echo "Failed Tests: ${env.FAILED_TESTS ?: 'None'}"
                    echo "Hardware Test Passed: ${env.HARDWARE_TEST_PASSED}"

                    if (env.HARDWARE_TEST_PASSED != 'true') {
                        error("FINAL VERDICT: Hardware tests failed")
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
        failure {
            echo 'PIPELINE FAILED'
        }
        success {
            echo 'PIPELINE SUCCESS'
        }
    }
}
