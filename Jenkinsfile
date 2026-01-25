pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        PYTHONUNBUFFERED = '1'
    }

    options {
        timestamps()
        disableConcurrentBuilds(abortPrevious: true)
    }

    stages {

        /* =========================================================
           INITIALIZE STATE
        ========================================================= */
        stage('Initialize State') {
            steps {
                script {
                    SYSTEM_TEST_PASSED   = false
                    HARDWARE_TEST_PASSED = true
                    FAILED_TESTS = []
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
           UPLOAD TEST FILES
        ========================================================= */
        stage('Upload Test Files') {
            steps {
                bat '''
                for %%f in (test_temp\\*.py) do python -m mpremote connect %ESP_PORT% fs cp "%%f" :
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
                    bat '''
                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_runner_system; test_runner_system.main()" > system.txt
                    '''

                    def failed = bat(
                        returnStatus: true,
                        script: 'findstr /C:"CI_EXIT_CODE=1" system.txt >nul'
                    )

                    if (failed == 0) {
                        SYSTEM_TEST_PASSED = false
                        error('System Self-Test failed')
                    }

                    SYSTEM_TEST_PASSED = true
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
                        script: 'findstr /C:"CI_RESULT=1" temp.txt >nul'
                    )

                    if (failed == 0) {
                        HARDWARE_TEST_PASSED = false
                        FAILED_TESTS << 'DS18B20'
                    } else {
                        echo 'DS18B20 test PASSED'
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
                    env.SYSTEM_TEST_PASSED   = SYSTEM_TEST_PASSED.toString()
                    env.HARDWARE_TEST_PASSED = HARDWARE_TEST_PASSED.toString()
                    env.FAILED_TESTS         = FAILED_TESTS.join(', ')

                    echo "SYSTEM_TEST_PASSED   = ${env.SYSTEM_TEST_PASSED}"
                    echo "HARDWARE_TEST_PASSED = ${env.HARDWARE_TEST_PASSED}"
                    echo "FAILED_TESTS         = ${env.FAILED_TESTS ?: 'None'}"

                    if (!SYSTEM_TEST_PASSED) {
                        error('Final verdict: System Self-Test failed')
                    }

                    if (!HARDWARE_TEST_PASSED) {
                        error("Final verdict: Hardware tests failed: ${FAILED_TESTS.join(', ')}")
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

