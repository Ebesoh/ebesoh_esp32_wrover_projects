pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds(abortPrevious: true)
    }

    environment {
        ESP_PORT = 'COM5'
        PYTHONUNBUFFERED = '1'
        REPORT_DIR = 'reports'
        REPORT_FILE = 'gpio_loopback_report.html'
    }

    stages {

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
                        echo "⚠ Low disk space detected (<10 GB). Cleaning workspace contents..."

                        powershell '''
                          if (Test-Path "$env:WORKSPACE") {
                              Get-ChildItem -Path "$env:WORKSPACE" -Force |
                              Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
                          }
                        '''
                    } else {
                        echo "Disk space OK. No cleanup needed."
                    }
                }
            }
        }

        stage('Install Tools') {
            steps {
                bat '''
                @echo off
                echo Installing tools...
                python -m pip install --upgrade pip
                python -m pip install mpremote
                '''
            }
        }

        stage('Preflight: ESP32 connectivity') {
            steps {
                bat '''
                @echo off
                echo Preflight: checking ESP32 on %ESP_PORT%...

                python -m mpremote connect %ESP_PORT% exec "pass"
                if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

                echo Preflight OK
                '''
            }
        }

        stage('Upload Tests') {
            steps {
                bat '''
                @echo off
                for %%f in (gpio_test\\*.py) do (
                    python -m mpremote connect %ESP_PORT% fs cp "%%f" :
                    if errorlevel 1 exit /b 1
                )
                '''
            }
        }

        stage('Run Tests') {
            steps {

                dir(REPORT_DIR) {
                    echo "Report directory ready"
                }

                writeFile file: "${REPORT_DIR}/${REPORT_FILE}", text: """
                <html><body>
                <h1>GPIO Loopback Tests</h1>
                <p>Build: ${env.BUILD_NUMBER}</p>
                <p>Result: FAIL</p>
                </body></html>
                """

                script {
                    def output = bat(
                        returnStdout: true,
                        script: '''
                        @echo off
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import gpio_loopback_runner; print(gpio_loopback_runner.run_all_tests())"
                        '''
                    ).trim()

                    int result
                    try {
                        result = output.toInteger()
                    } catch (Exception e) {
                        error("Non-integer test output: '${output}'")
                    }

                    echo "Test result code (int): ${result}"

                    switch (result) {
                        case 1:
                            writeFile file: "${REPORT_DIR}/${REPORT_FILE}", text: """
                            <html><body>
                            <h1>GPIO Loopback Tests</h1>
                            <p>Build: ${env.BUILD_NUMBER}</p>
                            <p>Result: PASS</p>
                            </body></html>
                            """
                            break
                        case 0:
                            error('GPIO test failure')
                        case -1:
                            error('Test setup error')
                        case -2:
                            error('ESP32 device error')
                        default:
                            error("Unknown test result code: ${result}")
                    }
                }
            }
        }
    }

    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: REPORT_DIR,
                reportFiles: REPORT_FILE,
                reportName: 'ESP32 GPIO Loopback Report'
            ])

            archiveArtifacts artifacts: "${REPORT_DIR}/${REPORT_FILE}"
        }

        success {
            echo 'PIPELINE SUCCESS'
        }

        failure {
            echo 'PIPELINE FAILURE'
        }
    }
}

