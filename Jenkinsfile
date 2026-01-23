pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        FIRMWARE = 'firmware/ESP32_GENERIC-SPIRAM-20251209-v1.27.0.bin'
        PYTHONUNBUFFERED = '1'
        WIFI_RESULT = 'PASS'
        BT_RESULT   = 'PASS'
    }

    options {
        timestamps()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

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

        stage('Flash ESP32 (optional)') {
            steps {
                bat '''
                echo === Flashing ESP32-WROVER (optional) ===
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

        stage('Upload WiFi + Bluetooth Test Files') {
            steps {
                bat '''
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

        /* ---------------- WIFI TESTS ---------------- */

        stage('Run WiFi Tests') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    bat '''
                    echo === Running WiFi tests ===

                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" ^
                    > esp32_wifi_output.txt

                    type esp32_wifi_output.txt

                    findstr /C:"CI_RESULT: FAIL" esp32_wifi_output.txt && (
                        echo WIFI FAILED
                        exit /b 1
                    )
                    '''
                }
            }
            post {
                failure {
                    script {
                        env.WIFI_RESULT = 'FAIL'
                    }
                }
            }
        }

        /* ---------------- BLUETOOTH TESTS ---------------- */

        stage('Run Bluetooth Tests') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    bat '''
                    echo === Running Bluetooth tests ===

                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_runner_bt; test_runner_bt.run_all_tests()" ^
                    > esp32_bt_output.txt

                    type esp32_bt_output.txt

                    findstr /C:"CI_RESULT: FAIL" esp32_bt_output.txt && (
                        echo BLUETOOTH FAILED
                        exit /b 1
                    )
                    '''
                }
            }
            post {
                failure {
                    script {
                        env.BT_RESULT = 'FAIL'
                    }
                }
            }
        }

        /* ---------------- FINAL VERDICT ---------------- */

        stage('Final CI Verdict') {
            steps {
                script {
                    echo "WiFi result: ${env.WIFI_RESULT}"
                    echo "Bluetooth result: ${env.BT_RESULT}"

                    if (env.WIFI_RESULT == 'FAIL' || env.BT_RESULT == 'FAIL') {
                        error('❌ One or more test suites failed')
                    }

                    echo '✅ All test suites passed'
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.txt', allowEmptyArchive: true
            echo 'ℹ️ CI run completed'
        }
        success {
            echo '✅ CI PIPELINE SUCCESS — WiFi and Bluetooth OK'
        }
        failure {
            echo '❌ CI PIPELINE FAILURE — Check test results'
        }
    }
}

