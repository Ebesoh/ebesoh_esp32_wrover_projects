pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        FIRMWARE = 'firmware/ESP32_GENERIC-SPIRAM-20251209-v1.27.0.bin'
        PYTHONUNBUFFERED = '1'
    }

    options {
        timestamps()
        disableConcurrentBuilds(abortPrevious: true)
    }

    stages {

        /* =========================================================
           Init Variables (mutable CI state)
           ========================================================= */
        stage('Init Variables') {
            steps {
                script {
                    env.SELF_TEST_PASSED = 'false'
                    env.WIFI_TEST_PASSED = 'unknown'
                    env.TEMP_TEST_PASSED = 'unknown'
                    env.BT_TEST_PASSED   = 'unknown'
                    env.FAILED_TESTS = ''
                    echo 'CI variables initialized'
                }
            }
        }

        /* =========================================================
           Auto-clean (Low disk space)
           ========================================================= */
        stage('Auto-clean (low disk space)') {
            steps {
                script {
                    def decision = powershell(
                        script: '''
                        $drive = Get-PSDrive -Name C
                        $freeGb = [math]::Round($drive.Free / 1GB, 2)

                        Write-Host "Free disk space on C: $freeGb GB"
                        if ($freeGb -lt 10) { "CLEAN" } else { "OK" }
                        ''',
                        returnStdout: true
                    ).trim()

                    if (decision == "CLEAN") {
                        echo "Low disk space detected (<10 GB). Cleaning workspace..."
                        powershell '''
                        if (Test-Path "$env:WORKSPACE") {
                            Get-ChildItem -Path "$env:WORKSPACE" -Force |
                            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
                        }
                        '''
                    }
                }
            }
        }

        /* =========================================================
           Install Tools
           ========================================================= */
        stage('Install Tools') {
            steps {
                checkout scm

                bat '''
                where python
                python --version
                python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
                '''

                bat '''
                python -m pip install --upgrade pip
                python -m pip install esptool mpremote
                '''
            }
        }

        /* =========================================================
           Preflight: ESP32 connectivity
           ========================================================= */
        stage('Preflight: ESP32 connectivity') {
            steps {
                bat '''
                @echo off
                echo Preflight: checking ESP32 on %ESP_PORT%...
                python -m mpremote connect %ESP_PORT% exec "print('ESP detected')"
                if errorlevel 1 exit /b 1
                echo Preflight OK
                '''
            }
        }

        /* =========================================================
           FLASH FIRMWARE
           ========================================================= */
        stage('Flash ESP32 Firmware') {
            steps {
                bat '''
                python -m esptool --chip esp32 --port %ESP_PORT% erase-flash
                python -m esptool --chip esp32 --port %ESP_PORT% write-flash -z 0x1000 %FIRMWARE%
                '''
                powershell 'Start-Sleep -Seconds 15'
            }
        }

        /* =========================================================
           WAIT FOR MICROPYTHON REPL (UPDATED)
           ========================================================= */
        stage('Wait for REPL') {
            steps {
                bat '''
                @echo off
                set READY=0

                for /L %%i in (1,1,5) do (
                    python -m mpremote connect %ESP_PORT% exec "print('READY')" >nul 2>&1 && (
                        echo MicroPython READY
                        set READY=1
                        goto done
                    )
                    timeout /t 3 >nul
                )

                :done
                if "%READY%"=="0" exit /b 1
                '''
            }
        }

        /* =========================================================
           Upload Test Files
           ========================================================= */
        stage('Upload Test Files') {
            steps {
                bat '''
                for %%f in (test_temp\\*.py) do (
                    python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                )

                for %%f in (tests_wifi\\*.py) do (
                    python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                )

                for %%f in (tests_bt\\*.py) do (
                    python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                )

                for %%f in (tests_selftest_DS18B20_gps_wifi\\*.py) do (
                    python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                )
                '''
            }
        }

        /* =========================================================
           SELF TEST (HARD GATE)
           ========================================================= */
        stage('Self-Test (HARD GATE)') {
            steps {
                script {
                    bat '''
                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_runner_system; test_runner_system.main()" ^
                    > selftest.txt
                    '''

                    def exitcode_st = bat(
                        returnStatus: true,
                        script: 'findstr /C:"CI_RESULT: FAIL" selftest.txt > nul'
                    )

                    echo "exitcode_st = ${exitcode_st}"

                    if (exitcode_st == 0) {
                        env.FAILED_TESTS = 'System Self-Test'
                        error 'System Self-Test FAILED (hard gate)'
                    } else if (exitcode_st == 1) {
                        env.SELF_TEST_PASSED = 'true'
                        echo 'System Self-Test: PASSED'
                    } else {
                        error 'System Self-Test infrastructure error'
                    }
                }
            }
        }

        /* =========================================================
           DS18B20 TEMPERATURE SENSOR TEST
           ========================================================= */
        stage('DS18B20 Temp-Sensor Test') {
            steps {
                script {
                    bat '''
                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_runner_ds18b20; test_runner_ds18b20.main()" ^
                    > temp.txt
                    '''

                    def exitcode_temp = bat(
                        returnStatus: true,
                        script: 'findstr /C:"CI_RESULT: FAIL" temp.txt > nul'
                    )

                    echo "exitcode_temp = ${exitcode_temp}"

                    if (exitcode_temp == 0) {
                        env.TEMP_TEST_PASSED = 'false'
                        env.FAILED_TESTS = 'DS18B20 Temp-Sensor Test'
                        error 'DS18B20 Temp-Sensor Test FAILED'
                    } else if (exitcode_temp == 1) {
                        env.TEMP_TEST_PASSED = 'true'
                        echo 'DS18B20 Temp-Sensor Test: PASSED'
                    } else {
                        error 'DS18B20 Test infrastructure error'
                    }
                }
            }
        }

        /* =========================================================
           WI-FI TEST
           ========================================================= */
        stage('WI-FI TEST') {
            steps {
                script {
                    bat '''
                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" ^
                    > wifi.txt
                    '''

                    def exitcode_wifi = bat(
                        returnStatus: true,
                        script: 'findstr /C:"CI_RESULT: FAIL" wifi.txt > nul'
                    )

                    echo "exitcode_wifi = ${exitcode_wifi}"

                    if (exitcode_wifi == 0) {
                        env.WIFI_TEST_PASSED = 'false'
                        env.FAILED_TESTS = 'Wi-fi Test'
                        error 'Wi-fi Test FAILED'
                    } else if (exitcode_wifi == 1) {
                        env.WIFI_TEST_PASSED = 'true'
                        echo 'Wi-fi Test: PASSED'
                    } else {
                        error 'Wi-fi Test infrastructure error'
                    }
                }
            }
        }

        /* =========================================================
           BLUETOOTH TEST
           ========================================================= */
        stage('Bluetooth Test') {
            steps {
                script {
                    bat '''
                    python -m mpremote connect %ESP_PORT% exec ^
                    "import test_runner_bt; test_runner_bt.run_all_tests()" ^
                    > bt.txt
                    '''

                    def exitcode_bt = bat(
                        returnStatus: true,
                        script: 'findstr /C:"CI_RESULT: FAIL" bt.txt > nul'
                    )

                    echo "exitcode_BT = ${exitcode_bt}"

                    if (exitcode_bt == 0) {
                        env.BT_TEST_PASSED = 'false'
                        env.FAILED_TESTS = 'BT Test'
                        error 'BT Test FAILED'
                    } else if (exitcode_bt == 1) {
                        env.BT_TEST_PASSED = 'true'
                        echo 'BT Test: PASSED'
                    } else {
                        error 'BT Test infrastructure error'
                    }
                }
            }
        }

        /* =========================================================
           FINAL VERDICT
           ========================================================= */
        stage('Final CI Verdict') {
            steps {
                script {
                    echo "SELF_TEST_PASSED = ${env.SELF_TEST_PASSED}"
                    echo "TEMP_TEST_PASSED = ${env.TEMP_TEST_PASSED}"
                    echo "WIFI_TEST_PASSED = ${env.WIFI_TEST_PASSED}"
                    echo "BT_TEST_PASSED   = ${env.BT_TEST_PASSED}"
                    echo "FAILED_TESTS     = ${env.FAILED_TESTS ?: 'None'}"

                    if (env.SELF_TEST_PASSED != 'true') {
                        error 'Final verdict: System Self-Test failed'
                    }

                    if (
                        env.TEMP_TEST_PASSED != 'true' ||
                        env.WIFI_TEST_PASSED != 'true' ||
                        env.BT_TEST_PASSED   != 'true'
                    ) {
                        error "Final verdict: Test failures detected: ${env.FAILED_TESTS}"
                    }

                    echo 'FINAL VERDICT: ALL TESTS PASSED'
                }
            }
        }
    }

    post {
