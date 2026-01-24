pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        FIRMWARE = 'firmware/ESP32_GENERIC-SPIRAM-20251209-v1.27.0.bin'
        PYTHONUNBUFFERED = '1'

        TEMP_RESULT = 'PASS'
        WIFI_RESULT = 'PASS'
        BT_RESULT   = 'PASS'
        ANY_TEST_FAILED = 'false'
    }

    options { timestamps() }

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
            steps { bat 'python -c "import time; time.sleep(10)"' }
        }

        stage('Force RAW REPL') {
            steps {
                bat '''
                python -m mpremote connect %ESP_PORT% reset
                python -c "import time; time.sleep(3)"
                '''
            }
        }

        /* ===== UPLOAD TEST FILES ===== */
        
        stage('Upload Test Files') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    bat '''
                    echo Uploading test files (will overwrite existing)...
                    
                    for %%f in (test_temp\\*.py) do python -m mpremote connect %ESP_PORT% fs cp %%f :
                    for %%f in (tests_wifi\\*.py) do python -m mpremote connect %ESP_PORT% fs cp %%f :
                    for %%f in (tests_bt\\*.py)   do python -m mpremote connect %ESP_PORT% fs cp %%f :
                    for %%f in (tests_selftest_DS18B20_gps_wifi\\*.py) do python -m mpremote connect %ESP_PORT% fs cp %%f :
                    
                    echo ✅ Test files uploaded successfully
                    '''
                }
            }
        }

        /* ===== SYSTEM HARD GATE ===== */
        // Keep as hard stop - if hardware is broken, no point continuing

        stage('System Self-Test (HARD GATE)') {
            steps {
                script {
                    def rc = bat(returnStatus: true, script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_system; test_runner_system.main()" ^
                        > system.txt

                        type system.txt
                        findstr /C:"CI_RESULT: FAIL" system.txt >nul
                        if %errorlevel%==0 (
                            exit /b 1
                        ) else (
                            exit /b 0
                        )
                    ''')

                    if (rc != 0) {
                        error('❌ SYSTEM SELF-TEST FAILED — PIPELINE STOPPED')
                    }
                }
            }
        }

        /* ===== TEST STAGES ===== */

        stage('DS18B20 Temperature Tests') {
            steps {
                script {
                    def rc = bat(returnStatus: true, script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_ds18b20; test_runner_ds18b20.main()" ^
                        > temp.txt

                        type temp.txt
                        findstr /C:"CI_RESULT: FAIL" temp.txt >nul
                        if %errorlevel%==0 (
                            echo ❌ DS18B20 TEST FAILED
                            exit /b 1
                        ) else (
                            echo ✅ DS18B20 TEST PASSED
                            exit /b 0
                        )
                    ''')

                    env.TEMP_RESULT = (rc == 0) ? 'PASS' : 'FAIL'
                    
                    if (rc != 0) {
                        echo "DS18B20 test failed"
                        env.ANY_TEST_FAILED = 'true'
                    }
                }
            }
        }

        stage('Wi-Fi Tests') {
            steps {
                script {
                    def rc = bat(returnStatus: true, script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" ^
                        > wifi.txt

                        type wifi.txt
                        findstr /C:"CI_RESULT: FAIL" wifi.txt >nul
                        if %errorlevel%==0 (
                            echo ❌ WIFI TEST FAILED
                            exit /b 1
                        ) else (
                            echo ✅ WIFI TEST PASSED
                            exit /b 0
                        )
                    ''')

                    env.WIFI_RESULT = (rc == 0) ? 'PASS' : 'FAIL'
                    
                    if (rc != 0) {
                        echo "Wi-Fi test failed"
                        env.ANY_TEST_FAILED = 'true'
                    }
                }
            }
        }

        stage('Bluetooth Tests') {
            steps {
                script {
                    def rc = bat(returnStatus: true, script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_bt; test_runner_bt.run_all_tests()" ^
                        > bt.txt

                        type bt.txt
                        findstr /C:"CI_RESULT: FAIL" bt.txt >nul
                        if %errorlevel%==0 (
                            echo ❌ BLUETOOTH TEST FAILED
                            exit /b 1
                        ) else (
                            echo ✅ BLUETOOTH TEST PASSED
                            exit /b 0
                        )
                    ''')

                    env.BT_RESULT = (rc == 0) ? 'PASS' : 'FAIL'
                    
                    if (rc != 0) {
                        echo "Bluetooth test failed"
                        env.ANY_TEST_FAILED = 'true'
                    }
                }
            }
        }

        /* ===== FINAL VERDICT ===== */

        stage('Final CI Verdict') {
            steps {
                script {
                    echo "=== TEST RESULTS ==="
                    echo "Temperature : ${env.TEMP_RESULT}"
                    echo "Wi-Fi       : ${env.WIFI_RESULT}"
                    echo "Bluetooth   : ${env.BT_RESULT}"
                    
                    if (env.ANY_TEST_FAILED == 'true') {
                        // This makes the ENTIRE PIPELINE RED
                        error("❌ ONE OR MORE TESTS FAILED")
                    } else {
                        echo '✅ ALL TEST SUITES PASSED'
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.txt', allowEmptyArchive: true
            script {
                echo "=== PIPELINE COMPLETED ==="
                echo "Final build result: ${currentBuild.result ?: 'SUCCESS'}"
            }
        }
        success { 
            echo '✅ PIPELINE COMPLETED SUCCESSFULLY' 
        }
        failure { 
            echo '❌ PIPELINE FAILURE - Tests failed' 
        }
    }
}