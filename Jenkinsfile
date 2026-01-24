pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        PYTHONUNBUFFERED = '1'
        HARDWARE_TEST_PASSED = 'false'
        FAILED_TESTS = 'false'
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        /* =========================================================
           SIMPLIFIED PREFLIGHT
        ========================================================= */
        stage('Preflight') {
            steps {
                checkout scm
                bat 'python --version'
                bat 'python -m pip install mpremote'
            }
        }

        /* =========================================================
           TEMPERATURE TEST
        ========================================================= */
        stage('Temperature Test (DS18B20)') {
            options {
                timeout(time: 2, unit: 'MINUTES')
            }
            steps {
                script {
                    echo "=== STARTING DS18B20 TEMPERATURE TEST ==="
                    
                    def rc = bat(
                        returnStatus: true,
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_ds18b20; test_runner_ds18b20.main()" > temp.txt
                        '''
                    )
                    
                    if (rc != 0) {
                        echo "❌ TEMPERATURE TEST FAILED (rc=${rc})"
                        if (!env.FAILED_TESTS) {
                            env.FAILED_TESTS = 'DS18B20'
                        } else {
                            env.FAILED_TESTS = env.FAILED_TESTS + ', DS18B20'
                        }
                        env.HARDWARE_TEST_PASSED = 'false'
                        currentBuild.result = 'FAILURE'
                    } else {
                        echo "✅ TEMPERATURE TEST PASSED"
                    }
                    
                    // Show first few lines of log for debugging
                    bat '''
                        echo "=== TEMPERATURE TEST LOG (first 20 lines) ==="
                        if exist temp.txt (
                            head -n 20 temp.txt || type temp.txt 2>nul | findstr /n "." | select -first 20
                        ) else (
                            echo "temp.txt not found"
                        )
                    '''
                }
            }
        }

        /* =========================================================
           WI-FI TEST
        ========================================================= */
        stage('Wi-Fi Test') {
            options {
                timeout(time: 5, unit: 'MINUTES')
            }
            steps {
                script {
                    echo "=== STARTING WI-FI TEST ==="
                    
                    def rc = bat(
                        returnStatus: true,
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" > wifi.txt
                        '''
                    )
                    
                    if (rc != 0) {
                        echo "❌ WI-FI TEST FAILED (rc=${rc})"
                        if (!env.FAILED_TESTS) {
                            env.FAILED_TESTS = 'Wi-Fi'
                        } else {
                            env.FAILED_TESTS = env.FAILED_TESTS + ', Wi-Fi'
                        }
                        env.HARDWARE_TEST_PASSED = 'false'
                        currentBuild.result = 'FAILURE'
                    } else {
                        echo "✅ WI-FI TEST PASSED"
                    }
                    
                    // Show first few lines of log for debugging
                    bat '''
                        echo "=== WI-FI TEST LOG (first 20 lines) ==="
                        if exist wifi.txt (
                            head -n 20 wifi.txt || type wifi.txt 2>nul | findstr /n "." | select -first 20
                        ) else (
                            echo "wifi.txt not found"
                        )
                    '''
                }
            }
        }

        /* =========================================================
           DEBUG OUTPUT
        ========================================================= */
        stage('Debug Output') {
            steps {
                script {
                    echo "=== DEBUG INFORMATION ==="
                    echo "COM Port: ${env.ESP_PORT}"
                    echo "Failed Tests: ${env.FAILED_TESTS ?: 'None'}"
                    echo "Hardware Test Passed: ${env.HARDWARE_TEST_PASSED}"
                    
                    // Check if log files exist and their size
                    bat '''
                        echo "=== LOG FILE STATUS ==="
                        for %%f in (temp.txt wifi.txt) do (
                            if exist %%f (
                                echo "%%f exists, size:"
                                for /f "tokens=3" %%s in ('dir "%%f" ^| find "%%f"') do echo %%s
                            ) else (
                                echo "%%f does NOT exist"
                            )
                        )
                    '''
                }
            }
        }

        /* =========================================================
           FINAL VERDICT
        ========================================================= */
        stage('Final Verdict') {
            steps {
                script {
                    echo "=== FINAL VERDICT ==="
                    
                    if (env.HARDWARE_TEST_PASSED != 'true') {
                        echo "FAILED TESTS: ${env.FAILED_TESTS}"
                        error("❌ FINAL VERDICT: Hardware tests failed")
                    } else {
                        echo "🎉 FINAL VERDICT: ALL TESTS PASSED"
                    }
                }
            }
        }
    }

    post {
        always {
            echo "=== ARCHIVING LOGS ==="
            archiveArtifacts artifacts: '*.txt', allowEmptyArchive: true
            echo "Archived logs: temp.txt, wifi.txt"
        }
        failure {
            echo '❌ PIPELINE FAILED'
            echo 'Check individual test stages above'
        }
        success {
            echo '✅ PIPELINE SUCCESS'
        }
    }
}