pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        FIRMWARE = 'firmware/ESP32_GENERIC-SPIRAM-20251209-v1.27.0.bin'
        PYTHONUNBUFFERED = '1'

        WIFI_RESULT = 'PASS'
        BT_RESULT   = 'PASS'
    }

    options { timestamps() }

    stages {

        /* ================= CHECKOUT + SETUP ================= */

        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Install Host Tools') {
            steps {
                bat '''
                python -m pip install --upgrade pip
                python -m pip install esptool mpremote
                '''
            }
        }

        /* ================= SYSTEM SELF TEST (HARD GATE) ================= */

        stage('System Self-Test (HARD GATE)') {
            steps {
                script {
                    def rc = bat(
                        returnStatus: true,
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_system; test_runner_system.main()" ^
                        > system.txt

                        type system.txt
                        findstr /C:"CI_RESULT: FAIL" system.txt >nul
                        '''
                    )

                    if (rc != 0) {
                        error('❌ SYSTEM SELF-TEST FAILED — PIPELINE STOPPED')
                    }

                    echo '✅ SYSTEM SELF-TEST PASSED'
                }
            }
        }

        /* ================= WIFI ================= */

        stage('Wi-Fi Tests') {
            steps {
                script {
                    try {
                        bat '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" ^
                        > wifi.txt

                        type wifi.txt
                        findstr /C:"CI_RESULT: FAIL" wifi.txt >nul
                        if not errorlevel 1 exit /b 1
                        '''
                        env.WIFI_RESULT = 'PASS'
                    } catch (Exception e) {
                        env.WIFI_RESULT = 'FAIL'
                        unstable('Wi-Fi tests failed')
                    }
                }
            }
        }

        /* ================= BLUETOOTH ================= */

        stage('Bluetooth Tests') {
            steps {
                script {
                    try {
                        bat '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_bt; test_runner_bt.run_all_tests()" ^
                        > bt.txt

                        type bt.txt
                        findstr /C:"CI_RESULT: FAIL" bt.txt >nul
                        if not errorlevel 1 exit /b 1
                        '''
                        env.BT_RESULT = 'PASS'
                    } catch (Exception e) {
                        env.BT_RESULT = 'FAIL'
                        unstable('Bluetooth tests failed')
                    }
                }
            }
        }

        /* ================= FINAL DECISION ================= */

        stage('Final Decision') {
            steps {
                script {
                    echo "Wi-Fi     : ${env.WIFI_RESULT}"
                    echo "Bluetooth : ${env.BT_RESULT}"

                    if (env.WIFI_RESULT == 'FAIL' ||
                        env.BT_RESULT   == 'FAIL') {
                        error('❌ One or more test suites failed')
                    }

                    echo '✅ ALL TEST SUITES PASSED'
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.txt', allowEmptyArchive: true
        }
        success {
            echo '✅ PIPELINE SUCCESS'
        }
        failure {
            echo '❌ PIPELINE FAILURE'
        }
    }
}
