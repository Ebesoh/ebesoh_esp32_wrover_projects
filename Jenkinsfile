/*
===============================================================================
ESP32-WROVER HARDWARE CI PIPELINE — ARCHITECTURE OVERVIEW by Ebesoh Ebesoh 
===============================================================================

PURPOSE
-------
This Jenkins pipeline provides a deterministic, hardware-in-the-loop CI system
for ESP32-WROVER boards running MicroPython. It flashes firmware, deploys test
code, executes hardware validation suites, and produces a single authoritative
CI verdict.

The pipeline is designed to fail fast on critical issues, isolate test domains,
and remain stable when executed repeatedly on the same physical device.

-------------------------------------------------------------------------------

HIGH-LEVEL FLOW
---------------
1. Host Preparation
   - Initialize mutable CI state variables
   - Auto-clean workspace if disk space is low
   - Install required host-side tooling (Python, esptool, mpremote)

2. Hardware Bring-Up
   - Preflight connectivity check to ensure ESP32 is reachable
   - Full flash erase + MicroPython firmware installation
   - Wait until MicroPython REPL is responsive

3. Test Deployment
   - Upload all test modules to the ESP32 filesystem via mpremote

4. Test Execution (Ordered, Isolated)
   - System Self-Test (HARD GATE)
   - DS18B20 temperature sensor validation
   - Soft reset to clear Wi-Fi/network state
   - Wi-Fi functional test suite
   - Bluetooth (BLE) functional test suite

5. Final CI Verdict
   - Aggregate all results
   - Produce a single pass/fail decision
   - Archive logs for traceability

-------------------------------------------------------------------------------

DESIGN PRINCIPLES
-----------------
• HARD GATES
  The system self-test is a non-negotiable gate. Failure immediately stops
  the pipeline to avoid meaningless downstream results.

• STATE ISOLATION
  A soft reset is performed before Wi-Fi testing to avoid cross-contamination
  from previous tests or driver state.

• SINGLE SOURCE OF TRUTH
  Each test suite emits a clear "CI_RESULT: PASS|FAIL" marker.
  Jenkins evaluates results only by parsing this marker.

• DETERMINISTIC ORDER
  Tests run in a fixed, documented order. No parallelism is used to protect
  shared hardware and ensure repeatability.

• HARDWARE SAFETY
  Concurrent pipeline executions are disabled to prevent multiple jobs from
  accessing the same ESP32 simultaneously.

-------------------------------------------------------------------------------

RESULT HANDLING
---------------
- All test output is redirected to text files (*.txt)
- Jenkins scans logs using `findstr` to detect failures
- Artifacts are always archived for post-mortem analysis
- Final verdict is explicit and authoritative

-------------------------------------------------------------------------------

INTENDED USE
------------
- Local Jenkins agents with direct USB access to ESP32 hardware
- Continuous validation of firmware + hardware integration
- Regression testing after firmware, driver, or test changes

This pipeline is intentionally verbose, explicit, and conservative.
Clarity, traceability, and hardware safety are prioritized over speed.

===============================================================================
*/

pipeline {
    agent any

    /* ---------------------------------------------------------
       Global environment variables used across all stages
       --------------------------------------------------------- */
    environment {
        ESP_PORT = 'COM5'   // Serial port where ESP32 is connected
        FIRMWARE = 'firmware/ESP32_GENERIC-SPIRAM-20251209-v1.27.0.bin' // MicroPython firmware
        PYTHONUNBUFFERED = '1' // Ensure real-time Python output in logs
    }

    /* ---------------------------------------------------------
       Pipeline-wide options
       --------------------------------------------------------- */
    options {
        timestamps() // Prefix all logs with timestamps
        disableConcurrentBuilds(abortPrevious: true) // Prevent parallel runs on same hardware
    }

    stages {

        /* =========================================================
           Initialize mutable CI state variables
           These are updated as tests execute
           ========================================================= */
        stage('Init Variables') {
            steps {
                script {
                    env.SELF_TEST_PASSED = 'false'   // Hard gate default
                    env.WIFI_TEST_PASSED = 'unknown' // Set after Wi-Fi tests
                    env.TEMP_TEST_PASSED = 'unknown' // Set after DS18B20 tests
                    env.BT_TEST_PASSED   = 'unknown' // Set after Bluetooth tests
                    env.FAILED_TESTS = ''            // Human-readable failure list
                    echo 'CI variables initialized'
                }
            }
        }

        /* =========================================================
           Automatically clean workspace if disk space is low
           Prevents Jenkins failures due to disk exhaustion
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
           Install required host-side tools
           - Python
           - esptool (flashing)
           - mpremote (MicroPython control)
           ========================================================= */
        stage('Install Tools') {
            steps {
                checkout scm // Fetch repository contents

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
           Preflight check to confirm ESP32 is reachable
           Fails early if hardware is missing or busy
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
           Flash MicroPython firmware onto ESP32
           Includes erase + fresh firmware write
           ========================================================= */
        stage('Flash ESP32 Firmware') {
            steps {
                bat '''
                python -m esptool --chip esp32 --port %ESP_PORT% erase-flash
                python -m esptool --chip esp32 --port %ESP_PORT% write-flash -z 0x1000 %FIRMWARE%
                '''
                powershell 'Start-Sleep -Seconds 15' // Allow reboot + flash settle
            }
        }

        /* =========================================================
           Wait until MicroPython REPL responds
           Retries a few times before failing
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
           Upload all test scripts to ESP32 filesystem
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
           SYSTEM SELF-TEST (HARD GATE)
           Pipeline stops immediately on failure
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
           DS18B20 TEMPERATURE SENSOR VALIDATION
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
           Soft reset before Wi-Fi tests
           Clears driver state and network stack
           ========================================================= */
        stage('Reset before Wi-Fi') {
            steps {
                bat '''
                 python -m mpremote connect %ESP_PORT% reset >nul 2>&1 || exit /b 0
                 powershell -command "Start-Sleep -Seconds 5"
                '''
            }
        }

        /* =========================================================
           WI-FI TEST SUITE
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
           BLUETOOTH (BLE) TEST SUITE
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
           FINAL CI VERDICT
           Single authoritative pass/fail decision
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

    /* ---------------------------------------------------------
       Post-run actions (always executed)
       --------------------------------------------------------- */
    post {
        always {
            archiveArtifacts artifacts: '*.txt', allowEmptyArchive: true // Preserve logs
        }
        success {
            echo 'Pipeline completed successfully'
        }
        failure {
            echo 'Pipeline FAILED'
        }
    }
}
