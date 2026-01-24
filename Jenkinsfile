pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        FIRMWARE = 'firmware/ESP32_GENERIC-SPIRAM-20251209-v1.27.0.bin'
        PYTHONUNBUFFERED = '1'
        FAILED_TESTS = ''
        FAILURE_COUNT = '0'
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {

        /* =========================================================
           PREFLIGHT
        ========================================================= */

        stage('Preflight') {
            steps {
                checkout scm

                bat '''
                where python
                python --version
                '''

                bat '''
                python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
                '''

                bat '''
                python -m pip install --upgrade pip
                python -m pip install esptool mpremote
                '''
            }
        }

        /* =========================================================
           FLASH FIRMWARE
        ========================================================= */

        stage('Flash ESP32 Firmware') {
            steps {
                script {
                    bat '''
                    python -m esptool --chip esp32 --port %ESP_PORT% erase-flash
                    python -m esptool --chip esp32 --port %ESP_PORT% write-flash -z 0x1000 %FIRMWARE%
                    '''
                }

                powershell 'Start-Sleep -Seconds 15'
            }
        }

        /* =========================================================
           UPLOAD TEST FILES
        ========================================================= */

        stage('Upload Test Files') {
            steps {
                bat '''
                for %%f in (test_temp\\*.py) do python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                for %%f in (tests_wifi\\*.py) do python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                for %%f in (tests_bt\\*.py) do python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                for %%f in (tests_selftest_DS18B20_gps_wifi\\*.py) do python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                '''
            }
        }

        /* =========================================================
           SYSTEM SELF TEST (HARD GATE)
        ========================================================= */

        stage('System Self-Test (HARD GATE)') {
            steps {
                script {
                    def rc = bat(
                        returnStatus: true,
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_system; test_runner_system.main()" > system.txt

                        type system.txt
                        findstr /C:"CI_RESULT: PASS" system.txt >nul
                        if %errorlevel% neq 0 exit /b 1
                        '''
                    )

                    if (rc != 0) {
                        error('System self-test failed – stopping pipeline')
                    }
                }
            }
        }

        /* =========================================================
           HARDWARE TESTS
        ========================================================= */

        stage('Hardware Tests (Temperature, Wi-Fi, Bluetooth)') {
            steps {
                script {

                    /* ---- DS18B20 ---- */
                    def tempRc = bat(
                        returnStatus: true,
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_ds18b20; test_runner_ds18b20.main()" > temp.txt
                        '''
                    )

                    if (tempRc != 0) {
                        env.FAILED_TESTS += 'DS18B20, '
                        env.FAILURE_COUNT = ((env.FAILURE_COUNT as int) + 1).toString()
                    }

                    /* ---- Wi-Fi ---- */
                    def wifiRc = bat(
                        returnStatus: true,
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" > wifi.txt
                        '''
                    )

                    if (wifiRc != 0) {
                        env.FAILED_TESTS += 'Wi-Fi, '
                        env.FAILURE_COUNT = ((env.FAILURE_COUNT as int) + 1).toString()
                    }

                    /* ---- Bluetooth ---- */
                    def btRc = bat(
                        returnStatus: true,
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_bt; test_runner_bt.run_all_tests()" > bt.txt
                        '''
                    )

                    if (btRc != 0) {
                        env.FAILED_TESTS += 'Bluetooth, '
                        env.FAILURE_COUNT = ((env.FAILURE_COUNT as int) + 1).toString()
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
                    echo "Failures: ${env.FAILURE_COUNT}"

                    if (env.FAILED_TESTS?.trim()) {
                        def failed = env.FAILED_TESTS[0..-3]
                        echo "FAILED TESTS: ${failed}"
                        currentBuild.result = 'FAILURE'
                    } else {
                        echo 'ALL TEST SUITES PASSED'
                        currentBuild.result = 'SUCCESS'
                    }
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
            echo 'Pipeline failed'
        }
    }
}
