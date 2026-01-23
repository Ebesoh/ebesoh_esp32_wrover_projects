pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        FIRMWARE = 'firmware/ESP32_GENERIC-SPIRAM-20251209-v1.27.0.bin'
        PYTHONUNBUFFERED = '1'

        WIFI_RESULT   = 'PASS'
        BT_RESULT     = 'PASS'
        SYSTEM_RESULT = 'PASS'
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

        /* ================= HOST SETUP ================= */

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

        /* ================= FLASH ================= */

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

        /* ================= UPLOAD TESTS ================= */

        stage('Upload Test Files') {
            steps {
                bat '''
                for %%f in (tests_wifi\\*.py) do python -m mpremote connect %ESP_PORT% fs cp %%f :
                for %%f in (tests_bt\\*.py) do python -m mpremote connect %ESP_PORT% fs cp %%f :
                for %%f in (tests_system\\*.py) do python -m mpremote connect %ESP_PORT% fs cp %%f :
                '''
            }
        }

        /* ================= WIFI ================= */

        stage('Wi-Fi Tests') {
            steps {
                catchError(stageResult: 'FAILURE', buildResult: 'SUCCESS') {
                    bat '''
                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" ^
                    > wifi.txt

                    type wifi.txt
                    findstr /C:"CI_RESULT: FAIL" wifi.txt && exit /b 1
                    '''
                }
            }
            post {
                failure {
                    script { env.WIFI_RESULT = 'FAIL' }
                }
            }
        }

        /* ================= BLUETOOTH ================= */

        stage('Bluetooth Tests') {
            steps {
                catchError(stageResult: 'FAILURE', buildResult: 'SUCCESS') {
                    bat '''
                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_runner_bt; test_runner_bt.run_all_tests()" ^
                    > bt.txt

                    type bt.txt
                    findstr /C:"CI_RESULT: FAIL" bt.txt && exit /b 1
                    '''
                }
            }
            post {
                failure {
                    script { env.BT_RESULT = 'FAIL' }
                }
            }
        }

        /* ================= SYSTEM (HARD GATE) ================= */

        stage('System Self-Test (Gate)') {
            steps {
                bat '''
                python -m mpremote connect %ESP_PORT% exec ^
                "import test_runner_system; test_runner_system.main()" ^
                > system.txt

                type system.txt
                findstr /C:"CI_RESULT: FAIL" system.txt && exit /b 1
                '''
            }
            post {
                failure {
                    script {
                        env.SYSTEM_RESULT = 'FAIL'
                        error('❌ SYSTEM SELF-TEST FAILED — PIPELINE HALTED')
                    }
                }
            }
        }

        /* ================= FINAL VERDICT ================= */

        stage('Final CI Verdict') {
            steps {
                script {
                    echo "Wi-Fi Result: ${env.WIFI_RESULT}"
                    echo "Bluetooth Result: ${env.BT_RESULT}"
                    echo "System Result: ${env.SYSTEM_RESULT}"

                    if (env.SYSTEM_RESULT == 'FAIL') {
                        error('Pipeline failed due to system self-test')
                    }

                    if (env.WIFI_RESULT == 'FAIL' || env.BT_RESULT == 'FAIL') {
                        error('One or more functional test suites failed')
                    }

                    echo '✅ ALL TESTS PASSED'
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
            echo '✅ PIPELINE SUCCESS'
        }
        failure {
            echo '❌ PIPELINE FAILURE'
        }
    }
}


