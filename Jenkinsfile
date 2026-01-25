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
           INITIALIZE VARIABLES
        ========================================================= */
        stage('Initialize Variables') {
            steps {
                script {
                    env.CI_RESULT_WiFi = 'true'
                    env.CI_RESULT_BT = 'true'
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
           UPLOAD TEST FILES
        ========================================================= */
        stage('Upload Test Files') {
            steps {
                bat '''
                for %%f in (tests_wifi\\*.py) do python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                for %%f in (tests_bt\\*.py) do python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                '''
            }
        }

        /* =========================================================
           FUNCTIONAL TESTS - WI-FI
        ========================================================= */
        stage('Wi-Fi Test') {
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
                        env.CI_RESULT_WiFi = 'false'
                        def current = env.FAILED_TESTS ?: ''
                        env.FAILED_TESTS = current ? "${current}, Wi-Fi" : "Wi-Fi"
                    }
                }
            }
        }

        /* =========================================================
           FUNCTIONAL TESTS - BLUETOOTH
        ========================================================= */
        stage('Bluetooth Test') {
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
                        env.CI_RESULT_BT = 'false'
                        env.FAILED_TESTS += env.FAILED_TESTS ? ', Bluetooth' : 'Bluetooth'
                    }
                }
            }
        }

        /* =========================================================
           FINAL CI VERDICT (EXPLICIT AUTHORITY)
        ========================================================= */
        stage('Final CI Verdict') {
            steps {
                script {
                    echo "WI-FI RESULT     = ${env.CI_RESULT_WiFi}"
                    echo "BLUETOOTH RESULT = ${env.CI_RESULT_BT}"
                    echo "FAILED_TESTS     = ${env.FAILED_TESTS ?: 'None'}"

                    if (env.CI_RESULT_WiFi != 'true' || env.CI_RESULT_BT != 'true') {
                        error("Final verdict: Hardware tests failed: ${env.FAILED_TESTS}")
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

