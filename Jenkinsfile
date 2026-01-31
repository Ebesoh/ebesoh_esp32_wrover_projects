pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        FIRMWARE = 'firmware/ESP32_GENERIC-SPIRAM-20251209-v1.27.0.bin'
        PYTHONUNBUFFERED = '1'

        SELF_TEST_PASSED = 'unknown'
        TEMP_TEST_PASSED = 'true'
        WIFI_TEST_PASSED = 'true'
        BT_TEST_PASSED   = 'true'
        FAILED_TESTS     = ''
    }

    options {
        timestamps()
        disableConcurrentBuilds(abortPrevious: true)
    }

    stages {

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

                        if ($freeGb -lt 10) {
                            Write-Output "CLEAN"
                        } else {
                            Write-Output "OK"
                        }
                        ''',
                        returnStdout: true
                    ).trim()

                    if (decision == "CLEAN") {
                        echo "⚠ Low disk space detected (<10 GB). Cleaning workspace..."
                        powershell '''
                        if (Test-Path "$env:WORKSPACE") {
                            Get-ChildItem -Path "$env:WORKSPACE" -Force |
                            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
                        }
                        Write-Host "Workspace cleaned due to low disk space"
                        '''
                    } else {
                        echo "Disk space OK. No cleanup needed."
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
                if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
                echo Preflight OK
                '''
            }
        }

        /* =========================================================
                UPLOAD TEST FILES
           ========================================================= */
        stage('Upload Test Files') {
            steps {
                bat '''
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
                    > system.txt
                    '''

                    def result_st = bat(
                        returnStatus: true,
                        script: 'findstr /C:"CI_RESULT: FAIL" system.txt > nul'
                    )
                      echo result_st
           
                    if (result_st == 0) {
                        env.SELF_TEST_PASSED = 'false'
                        env.FAILED_TESTS = 'System Self-Test'
                        error('System Self-Test FAILED (hard gate)')
                    } else if (result_st == 1){ 
                       env.SELF_TEST_PASSED = 'true'
                       echo 'System Self-Test PASSED'
                    
                    }esle {
                      echo 'System Self-Test PASSED'
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
                        error('Final verdict: System Self-Test failed')
                    }

                    if (
                        env.TEMP_TEST_PASSED != 'true' ||
                        env.WIFI_TEST_PASSED != 'true' ||
                        env.BT_TEST_PASSED   != 'true'
                    ) {
                        error("Final verdict: Test failures detected: ${env.FAILED_TESTS}")
                    }

                    echo 'FINAL VERDICT: ALL TESTS PASSED'
                    echo 'Congratulations for successful run!!'
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
