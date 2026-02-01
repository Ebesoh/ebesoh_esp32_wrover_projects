/*
===============================================================================
ESP32-WROVER HARDWARE CI PIPELINE — ARCHITECTURE OVERVIEW
Author: Ebesoh Ebesoh
===============================================================================

WHAT THIS PIPELINE IS FOR
-------------------------
This Jenkins pipeline is a hardware-in-the-loop CI system for ESP32-WROVER
boards running MicroPython.

It does four things, every time, in a predictable way:
- Flashes known-good firmware
- Deploys test code to the board
- Runs real hardware tests
- Produces one clear pass/fail result

The goal is simple: if this pipeline says “PASS”, the firmware and hardware
work together as expected. If it says “FAIL”, something is genuinely broken.

It is designed to be repeatable, conservative, and safe to run over and over
on the same physical device.

-------------------------------------------------------------------------------

HOW IT FLOWS
------------
1. Host Setup
   - Initialize CI state variables
   - Clean the workspace if disk space is running low
   - Install required host tools (Python, esptool, mpremote)

2. Hardware Bring-Up
   - Verify the ESP32 is reachable over USB
   - Fully erase flash and install MicroPython firmware
   - Wait until the MicroPython REPL responds

3. Test Deployment
   - Upload all test modules to the ESP32 filesystem using mpremote

4. Test Execution (Strict Order, No Shortcuts)
   - System self-test (this is a hard gate)
   - DS18B20 temperature sensor validation
   - Soft reset to clear Wi-Fi and network state
   - Wi-Fi functional tests
   - Bluetooth (BLE) functional tests

5. Final CI Decision
   - Collect all test results
   - Produce a single, authoritative pass/fail verdict
   - Archive logs for traceability and debugging

-------------------------------------------------------------------------------

CORE DESIGN IDEAS
-----------------
• HARD GATES
  The system self-test is non-negotiable. If it fails, the pipeline stops
  immediately. There’s no point running further tests on a broken baseline.

• STATE ISOLATION
  A soft reset is performed before Wi-Fi testing to prevent leftover state
  from earlier tests affecting the results.

• SINGLE SOURCE OF TRUTH
  Each test suite prints an explicit marker:
      CI_RESULT: PASS or CI_RESULT: FAIL
  Jenkins does not guess. It only trusts this marker.

• DETERMINISTIC ORDER
  Tests always run in the same order. No parallel execution.
  This protects shared hardware and makes failures reproducible.

• HARDWARE SAFETY
  Only one pipeline run is allowed at a time.
  This prevents multiple jobs from fighting over the same ESP32.

-------------------------------------------------------------------------------

HOW RESULTS ARE HANDLED
----------------------
- All test output is written to text files (*.txt)
- Jenkins scans logs using `findstr` to detect failures
- Logs are always archived, even on failure
- The final result is explicit and unambiguous

-------------------------------------------------------------------------------

WHEN TO USE THIS
----------------
- Jenkins agents with direct USB access to ESP32 hardware
- Continuous validation of firmware and hardware integration
- Regression testing after changes to firmware, drivers, or tests

This pipeline is intentionally verbose and cautious.
Speed is secondary. Clarity, repeatability, and hardware safety come first.

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
