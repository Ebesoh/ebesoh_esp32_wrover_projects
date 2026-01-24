pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        PYTHONUNBUFFERED = '1'
        FAILED_TESTS = ''
        HARDWARE_TEST_PASSED = 'false'  // This creates env.HARDWARE_TEST_PASSED
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Preflight') {
            steps {
                checkout scm
                bat 'python --version'
                bat 'python -m pip install mpremote'
            }
        }

        stage('Temperature Test (DS18B20)') {
            options { timeout(time: 2, unit: 'MINUTES') }
            steps {
                script {
                    echo "=== Starting DS18B20 Test ==="
                    catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                        def rc = bat(returnStatus: true, script: '''
                            python -m mpremote connect %ESP_PORT% exec ^
                            "import test_runner_ds18b20; test_runner_ds18b20.main()" > temp.txt
                        ''')
                        
                        if (rc != 0) {
                            echo "❌ DS18B20 Test FAILED"
                            env.FAILED_TESTS += (env.FAILED_TESTS ? ', DS18B20' : 'DS18B20')
                            env.HARDWARE_TEST_PASSED = 'false'  // ✅ Use env. prefix
                            error('DS18B20 test failed')
                        } else {
                            echo "✅ DS18B20 Test PASSED"
                        }
                    }
                }
            }
        }

        stage('Wi-Fi Test') {
            options { timeout(time: 5, unit: 'MINUTES') }
            steps {
                script {
                    echo "=== Starting Wi-Fi Test ==="
                    catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                        def rc = bat(returnStatus: true, script: '''
                            python -m mpremote connect %ESP_PORT% exec ^
                            "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" > wifi.txt
                        ''')
                        
                        if (rc != 0) {
                            echo "❌ Wi-Fi Test FAILED"
                            env.FAILED_TESTS += (env.FAILED_TESTS ? ', Wi-Fi' : 'Wi-Fi')
                            env.HARDWARE_TEST_PASSED = 'false'  // ✅ Use env. prefix
                            error('Wi-Fi test failed')
                        } else {
                            echo "✅ Wi-Fi Test PASSED"
                        }
                    }
                }
            }
        }

        stage('Bluetooth Test') {
            options { timeout(time: 3, unit: 'MINUTES') }
            steps {
                script {
                    echo "=== Starting Bluetooth Test ==="
                    catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                        def rc = bat(returnStatus: true, script: '''
                            python -m mpremote connect %ESP_PORT% exec ^
                            "import test_runner_bt; test_runner_bt.run_all_tests()" > bt.txt
                        ''')
                        
                        if (rc != 0) {
                            echo "❌ Bluetooth Test FAILED"
                            env.FAILED_TESTS += (env.FAILED_TESTS ? ', Bluetooth' : 'Bluetooth')
                            env.HARDWARE_TEST_PASSED = 'false'  // ✅ Use env. prefix
                            error('Bluetooth test failed')
                        } else {
                            echo "✅ Bluetooth Test PASSED"
                        }
                    }
                }
            }
        }

        stage('Final Verdict') {
            steps {
                script {
                    echo "=== FINAL RESULTS ==="
                    echo "Failed Tests: ${env.FAILED_TESTS ?: 'None'}"
                    echo "Hardware Test Passed: ${env.HARDWARE_TEST_PASSED}"  // ✅ Use env. prefix
                    
                    if (env.HARDWARE_TEST_PASSED == 'false') {  // ✅ Use env. prefix
                        error("❌ FINAL VERDICT: Tests failed: ${env.FAILED_TESTS}")
                    } else {
                        echo "🎉 FINAL VERDICT: ALL TESTS PASSED"
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
            echo '✅ Pipeline SUCCESS'
        }
        failure {
            echo '❌ Pipeline FAILED'
        }
    }
}