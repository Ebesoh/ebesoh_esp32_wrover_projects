pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds(abortPrevious: true)
    }

    environment {
        ESP_PORT = 'COM5'
        PYTHONUNBUFFERED = '1'
        FAILED_GPIOS = ''
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
                    // Run tests but always allow Jenkins to continue
                    def output = bat(
                        returnStdout: true,
                        script: '''
                        @echo off
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import gpio_loopback_runner; gpio_loopback_runner.run_all_tests()"
                        exit /b 0
                        '''
                    ).trim()

                    echo "=== ESP32 OUTPUT ==="
                    echo output

                    // Collect GPIO loopback failures
                    def faults = []

                    // Match GPIO pairs like "GPIO 12 - 18"
                    def gpioPattern = ~/GPIO\s+(\d+)\s*-\s*(\d+)/

                    def matcher = (output =~ gpioPattern)
                    while (matcher.find()) {
                        def gpioA = matcher.group(1)
                        def gpioB = matcher.group(2)
                        faults << "GPIO ${gpioA} -> GPIO ${gpioB}"
                    }

                    faults = faults.unique()
                    env.FAILED_GPIOS = faults.join(',')

                    // Fail on detected GPIO faults
                    if (!faults.isEmpty()) {
                        echo "Detected GPIO faults:"
                        faults.each { echo " - ${it}" }
                        error("GPIO loopback tests FAILED (${faults.size()} fault(s))")
                    }

                    // Otherwise require PASS indicator
                    if (output.toLowerCase().contains("loopback tests passed") ||
                        output.contains("CI_RESULT: PASS")) {
                        echo "All GPIO loopback tests PASSED"
                    } else {
                        error("GPIO loopback tests failed with unexpected output")
                    }
                }
            }
        }
    }

    post {
        success {
            echo "PIPELINE SUCCESS: GPIO loopback tests passed"
        }

        failure {
            script {
                echo "PIPELINE FAILURE: GPIO loopback tests failed"

                if (env.FAILED_GPIOS?.trim()) {
                    echo "Failed GPIO loopback(s):"
                    env.FAILED_GPIOS.split(',').each {
                        echo " - ${it}"
                    }
                } else {
                    echo "No specific GPIO fault reported (check ESP32 output)."
                }
            }
        }
    }
}
