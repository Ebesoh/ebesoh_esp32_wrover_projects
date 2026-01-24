pipeline {
    agent any

    environment {
        ESP_PORT = 'COM5'
        PYTHONUNBUFFERED = '1'
    }

    options { timestamps() }

    stages {

        stage('Checkout') {
            steps { checkout scm }
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
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    bat '''
                    echo Uploading test files...
                    
                    REM Upload temperature test files only
                    for %%f in (test_temp\\*.py) do python -m mpremote connect %ESP_PORT% fs cp %%f :
                    
                    echo ✅ Test files uploaded successfully
                    '''
                }
            }
        }

        /* ===== SYSTEM HARD GATE ===== */

        stage('System Self-Test (HARD GATE)') {
            steps {
                script {
                    def rc = bat(returnStatus: true, script: '''
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import test_runner_system; test_runner_system.main()" ^
                        > system.txt

                        type system.txt
                        findstr /C:"CI_RESULT: FAIL" system.txt >nul
                        if %errorlevel%==0 (
                            exit /b 1
                        ) else (
                            exit /b 0
                        )
                    ''')

                    if (rc != 0) {
                        error('❌ SYSTEM SELF-TEST FAILED — PIPELINE STOPPED')
                    }
                }
            }
        }

        /* ===== TEMPERATURE TEST ===== */

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

                    // REMOVED: env.TEMP_RESULT = (rc == 0) ? 'PASS' : 'FAIL'
                    // REMOVED: if (rc != 0) { env.ANY_TEST_FAILED = 'true' }
                    
                    // ADDED: Fail the stage immediately if test fails
                    if (rc != 0) {
                        error('❌ DS18B20 TEMPERATURE TEST FAILED')
                    }
                }
            }
        }

        /* ===== FINAL VERDICT ===== */
        // This stage only runs if all previous stages passed

        stage('Final CI Verdict') {
            steps {
                script {
                    echo "=== FINAL RESULT ==="
                    echo '✅ ALL TESTS PASSED'
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.txt', allowEmptyArchive: true
            script {
                echo "=== PIPELINE COMPLETED ==="
                echo "Final build result: ${currentBuild.result ?: 'SUCCESS'}"
            }
        }
        success { 
            echo '✅ PIPELINE COMPLETED SUCCESSFULLY' 
        }
        failure { 
            echo '❌ PIPELINE FAILURE - Test(s) failed' 
        }
    }
}