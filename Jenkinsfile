pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        PYTHONUNBUFFERED = '1'
        FAILED_TESTS = ''
        FAILURE_COUNT = '0'
    }

    options {
        timestamps()
    }

    stages {

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

        /* ===== UPLOAD TEST FILES ===== */

        stage('Upload Test Files') {
            steps {
                script {
                    try {
                        bat '''
                        echo Uploading test files...
                        for %%f in (test_temp\\*.py) do (
                            python -m mpremote connect %ESP_PORT% fs cp %%f :
                        )
                        echo [PASS] Test files uploaded
                        '''
                    } catch (Exception e) {
                        echo "⚠️ Upload failed but continuing: ${e.message}"
                        env.FAILED_TESTS += 'File Upload, '
                        env.FAILURE_COUNT = ((env.FAILURE_COUNT as int) + 1).toString()
                    }
                }
            }
        }

        /* ===== SYSTEM HARD GATE ===== */

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
                            echo [FAIL] SYSTEM TEST FAILED
                            exit /b 1
                        ) else (
                            echo [PASS] SYSTEM TEST PASSED
                            exit /b 0
                        )
                        '''
                    )

                    if (rc != 0) {
                        error('System Self-Test failed – stopping pipeline')
                    }
                }
            }
        }

        /* ===== TEMPERATURE TEST (EXIT-CODE DRIVEN) ===== */

        stage('DS18B20 Temperature Tests') {
            steps {
                script {
                    def rc = bat(
                        returnStatus: true,
                        script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_ds18b20; test_runner_ds18b20.main()"
                        '''
                    )

                    if (rc != 0) {
                        echo '❌ Temperature test failed'
                        env.FAILED_TESTS += 'Temperature, '
                        env.FAILURE_COUNT = ((env.FAILURE_COUNT as int) + 1).toString()
                    } else {
                        echo '✅ Temperature test passed'
                    }
                }
            }
        }

        /* ===== FINAL VERDICT ===== */

        stage('Final CI Verdict') {
            steps {
                script {
                    echo '=== TEST EXECUTION COMPLETE ==='
                    echo "Total failures: ${env.FAILURE_COUNT}"

                    if (env.FAILED_TESTS?.trim()) {
                        def failedList = env.FAILED_TESTS.substring(0, env.FAILED_TESTS.length() - 2)
                        echo "❌ Failed tests: ${failedList}"
                        currentBuild.result = 'FAILURE'
                    } else {
                        echo '✅ ALL TESTS PASSED'
                        currentBuild.result = 'SUCCESS'
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.txt', allowEmptyArchive: true

            script {
                echo '=== FINAL STATUS ==='
                echo "Pipeline result: ${currentBuild.result}"
                echo "Failed tests: ${env.FAILED_TESTS ?: 'None'}"
                echo "Failure count: ${env.FAILURE_COUNT}"
            }
        }

        success {
            echo '✅ Pipeline completed successfully'
        }

        failure {
            echo '❌ Pipeline completed with test failures'
        }

        unstable {
            echo '⚠️ Pipeline completed with warnings'
        }
    }
}
