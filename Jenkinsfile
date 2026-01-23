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

    options {
        timestamps()
    }

    stages {

        /* =========================================================
           CHECKOUT + HOST SETUP
           ========================================================= */

        stage('Checkout') {
            steps {
                checkout scm
            }
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

        /* =========================================================
           FLASH + RESET
           ========================================================= */

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

        /* =========================================================
           UPLOAD TEST FILES
           ========================================================= */

        stage('Upload Test Files') {
            steps {
                bat '''
                echo === Uploading test files ===

                for %%f in (test_temp\\*.py) do python -m mpremote connect %ESP_PORT% fs cp %%f :
                for %%f in (tests_wifi\\*.py) do python -m mpremote connect %ESP_PORT% fs cp %%f :
                for %%f in (tests_bt\\*.py)   do python -m mpremote connect %ESP_PORT% fs cp %%f :
                for %%f in (tests_selftest_DS18B20_gps_wifi\\*.py) do python -m mpremote connect %ESP_PORT% fs cp %%f :

//                echo === Uploading DS18B20 runner explicitly ===
//                python -m mpremote connect %ESP_PORT% fs cp test_runner_ds18b20.py :
                '''
            }
        }

        /* =========================================================
           SYSTEM SELF TEST — HARD GATE
           ========================================================= */

        stage('System Self-Test (HARD GATE)') {
            steps {
                bat '''
                python -m mpremote connect %ESP_PORT% exec ^
                "import test_runner_system; test_runner_system.main()" ^
                > system.txt

                type system.txt

                findstr /C:"CI_RESULT: FAIL" system.txt >nul
                if %errorlevel%==0 (
                    echo ❌ SYSTEM SELF-TEST FAILED
                    exit /b 1
                )

                echo ✅ SYSTEM SELF-TEST PASSED
                exit /b 0
                '''
            }
            post {
                failure {
                    error('❌ SYSTEM SELF-TEST FAILED — PIPELINE STOPPED')
                }
            }
        }

        /* =========================================================
           DS18B20 EXTENDED TEMPERATURE TESTS
           ========================================================= */

        stage('DS18B20 Temperature Tests') {
            steps {
                catchError(stageResult: 'FAILURE', buildResult: 'SUCCESS') {
                    bat '''
                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_runner_ds18b20; test_runner_ds18b20.main()" ^
                    > temp.txt

                    type temp.txt

                    findstr /C:"CI_RESULT: FAIL" temp.txt >nul
                    if %errorlevel%==0 exit /b 1
                    exit /b 0
                    '''
                }
            }
            post {
                failure {
                    script { env.TEMP_RESULT = 'FAIL' }
                }
            }
        }

        /* =========================================================
           WIFI TESTS
           ========================================================= */

        stage('Wi-Fi Tests') {
            steps {
                catchError(stageResult: 'FAILURE', buildResult: 'SUCCESS') {
                    bat '''
                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" ^
                    > wifi.txt

                    type wifi.txt

                    findstr /C:"CI_RESULT: FAIL" wifi.txt >nul
                    if %errorlevel%==0 exit /b 1
                    exit /b 0
                    '''
                }
            }
            post {
                failure {
                    script { env.WIFI_RESULT = 'FAIL' }
                }
            }
        }

        /* =========================================================
           BLUETOOTH TESTS
           ========================================================= */

        stage('Bluetooth Tests') {
            steps {
                catchError(stageResult: 'FAILURE', buildResult: 'SUCCESS') {
                    bat '''
                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_runner_bt; test_runner_bt.run_all_tests()" ^
                    > bt.txt

                    type bt.txt

                    findstr /C:"CI_RESULT: FAIL" bt.txt >nul
                    if %errorlevel%==0 exit /b 1
                    exit /b 0
                    '''
                }
            }
            post {
                failure {
                    script { env.BT_RESULT = 'FAIL' }
                }
            }
        }

        /* =========================================================
           FINAL CI VERDICT
           ========================================================= */

        stage('Final CI Verdict') {
            steps {
                script {
                    echo "Temperature : ${env.TEMP_RESULT}"
                    echo "Wi-Fi       : ${env.WIFI_RESULT}"
                    echo "Bluetooth   : ${env.BT_RESULT}"

                    if (env.TEMP_RESULT == 'FAIL' ||
                        env.WIFI_RESULT == 'FAIL' ||
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
