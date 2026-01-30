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

        stage('Run Loopback Tests') {
            steps {
                script {
                    def output = bat(
                        script: '''
                        @echo off
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import gpio_loopback_runner; gpio_loopback_runner.run_all_tests()"
                        ''',
                        returnStdout: true
                    ).trim()

                    echo "=== ESP32 OUTPUT ==="
                    echo output

                    def faults = []

                    if (output.contains("GPIO 14 - 19")) {
                        faults << "GPIO 14 - 19"
                    }

                    if (output.contains("GPIO 12 - 18")) {
                        faults << "GPIO 12 - 18"
                    }

                    def lines = output.split('\\n')
                    for (String line : lines) {
                        def clean = line.trim()
                        if (clean.startsWith("-")) {
                            faults << clean.substring(1).trim()
                        }
                    }

                    faults = faults.unique()

                    if (!faults.isEmpty()) {
                        echo "Detected GPIO faults:"
                        faults.each { fault ->
                            echo " - ${fault}"
                        }
                        error("GPIO loopback tests FAILED (${faults.size()} fault(s))")
                    }

                    if (output.contains("CI_RESULT: PASS")) {
                        echo "All GPIO loopback tests PASSED"
                    } 
                        error("Unexpected output from ESP32:\n${output}")
                    
                }
            }
        }
    }

    post {
        success {
            echo "PIPELINE SUCCESS: GPIO loopback tests passed"
        }

        failure {
            echo "PIPELINE FAILURE: GPIO loopback tests failed"
            echo "Check wiring:"
            echo " - GPIO 14 -> GPIO 19"
            echo " - GPIO 12 -> GPIO 18"
        }
    }
}
