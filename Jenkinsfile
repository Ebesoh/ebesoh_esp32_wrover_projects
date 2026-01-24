pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        PYTHONUNBUFFERED = '1'
        FAILED_TESTS = ''
    }

    options { timestamps() }

    stages {
        // ... earlier stages remain the same ...

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

                    if (rc != 0) {
                        echo "DS18B20 test failed (will fail pipeline at end)"
                        env.FAILED_TESTS += 'DS18B20, '
                    }
                }
            }
        }

        /* ===== FINAL VERDICT ===== --------------*/

        stage('Final CI Verdict') {
            steps {
                script {
                    echo "=== FINAL RESULT ==="
                    
                    if (env.FAILED_TESTS) {
                        // Remove trailing comma and space
                        def failedList = env.FAILED_TESTS.substring(0, env.FAILED_TESTS.length() - 2)
                        error("❌ TESTS FAILED: ${failedList}")
                    } else {
                        echo '✅ ALL TESTS PASSED'
                    }
                }
            }
        }
    }

    // ... post section remains the same ...
}