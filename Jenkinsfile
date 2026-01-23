pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        FIRMWARE = 'firmware/ESP32_GENERIC-SPIRAM-20251209-v1.27.0.bin'
        PYTHONUNBUFFERED = '1'

        TEMP_RESULT = 'PASS'
        WIFI_RESULT = 'PASS'
        BT_RESULT   = 'PASS'
    }

    options { timestamps() }

    stages {

        /* ================= CHECKOUT + SETUP ================= */

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

        /* ================= FLASH + RESET ================= */

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

        /* ================= UPLOAD TEST FILES ================= */

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
                        if %errorlevel%==0 (
                            exit /b 1
                        ) else (
                            exit /b 0
                        )
                        '''
                    )

                    if (rc != 0) {
                        error('❌ SYSTEM SELF-TEST FAILED — PIPELINE STOPPED')
                    }

                    echo '✅ SYSTEM SELF-TEST PASSED'
                }
            }
        }

        /* ================= DS18B20 TEMPERATURE ================= */

        stage('DS18B20 Temperature Tests') {
            steps {
                script {
                    def rc = bat(returnStatus: true, script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_ds18b20; test_runner_ds18b20.main()" ^
                        > temp.txt

                        type temp.txt

                        REM: Use PowerShell for cleaner logic
                        powershell '''
                            $content = Get-Content temp.txt
                            if ($content -match "CI_RESULT: FAIL") {
                                exit 1
                            } else {
                                exit 0
                            }
                        '''
                    ''')

                    env.TEMP_RESULT = (rc == 0) ? 'PASS' : 'FAIL'
                    
                    // ADD THIS - fail the stage immediately if test failed
                    if (rc != 0) {
                        error("❌ DS18B20 Tests FAILED - see temp.txt")
                    }
                }
            }
        }

        /* ================= WIFI ================= */

        stage('Wi-Fi Tests') {
            steps {
                script {
                    def rc = bat(returnStatus: true, script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" ^
                        > wifi.txt

                        type wifi.txt

                        REM: Use PowerShell for cleaner logic
                        powershell '''
                            $content = Get-Content wifi.txt
                            if ($content -match "CI_RESULT: FAIL") {
                                exit 1
                            } else {
                                exit 0
                            }
                        '''
                    ''')

                    env.WIFI_RESULT = (rc == 0) ? 'PASS' : 'FAIL'
                    
                    // ADD THIS - fail the stage immediately if test failed
                    if (rc != 0) {
                        error("❌ Wi-Fi Tests FAILED - see wifi.txt")
                    }
                }
            }
        }

        /* ================= BLUETOOTH ================= */

        stage('Bluetooth Tests') {
            steps {
                script {
                    def rc = bat(returnStatus: true, script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_bt; test_runner_bt.run_all_tests()" ^
                        > bt.txt

                        type bt.txt

                        REM: Use PowerShell for cleaner logic
                        powershell '''
                            $content = Get-Content bt.txt
                            if ($content -match "CI_RESULT: FAIL") {
                                exit 1
                            } else {
                                exit 0
                            }
                        '''
                    ''')

                    env.BT_RESULT = (rc == 0) ? 'PASS' : 'FAIL'
                    
                    // ADD THIS - fail the stage immediately if test failed
                    if (rc != 0) {
                        error("❌ Bluetooth Tests FAILED - see bt.txt")
                    }
                }
            }
        }

        /* ================= FINAL VERDICT ================= */

        stage('Final CI Verdict') {
            when {
                // Only run this stage if all previous stages passed
                expression { 
                    env.TEMP_RESULT == 'PASS' && 
                    env.WIFI_RESULT == 'PASS' && 
                    env.BT_RESULT == 'PASS' 
                }
            }
            steps {
                script {
                    echo "Temperature : ${env.TEMP_RESULT}"
                    echo "Wi-Fi       : ${env.WIFI_RESULT}"
                    echo "Bluetooth   : ${env.BT_RESULT}"
                    echo '✅ ALL TEST SUITES PASSED'
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.txt', allowEmptyArchive: true
            script {
                echo "=== FINAL RESULTS ==="
                echo "Temperature: ${env.TEMP_RESULT}"
                echo "Wi-Fi: ${env.WIFI_RESULT}"
                echo "Bluetooth: ${env.BT_RESULT}"
            }
        }
        success { 
            echo '✅ PIPELINE SUCCESS' 
        }
        failure { 
            echo '❌ PIPELINE FAILURE' 
        }
    }
}
