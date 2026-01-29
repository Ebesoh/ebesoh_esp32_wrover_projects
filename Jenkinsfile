pipeline {
    agent {
        label 'esp32'
    }

    triggers {
        githubPush()
    }

    options {
        timestamps()
        disableConcurrentBuilds(abortPrevious: true)
    }

    environment {
        ESP_PORT = 'COM5'
        PYTHONUNBUFFERED = '1'
    }

    stages {

        stage('Build') {
            steps {
                echo "Running on ESP32 node"
            }
        }

        stage('Auto-clean (low disk space)') {
            steps {
                script {
                    def freeGb = powershell(
                        script: '''
                        $drive = Get-PSDrive -Name C
                        [math]::Round($drive.Free / 1GB, 2)
                        ''',
                        returnStdout: true
                    ).trim()

                    echo "Free disk space on C: ${freeGb} GB"

                    // Jenkins sandbox-safe numeric comparison
                    if (Double.parseDouble(freeGb) < 10) {
                        echo "⚠ Low disk space detected (<10 GB). Cleaning workspace..."
                        cleanWs()
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

        stage('Upload Loopback Tests') {
            steps {
                bat '''
                @echo off
                echo Uploading test files to ESP32...
                for %%f in (gpio_test\\*.py) do (
                    python -m mpremote connect %ESP_PORT% fs cp "%%f" :
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
                        echo Running GPIO loopback tests...

                        REM Ensure clean REPL state
                        python -m mpremote connect %ESP_PORT% reset repl < nul > nul 2>&1

                        REM Execute tests and capture output
                        python -m mpremote connect %ESP_PORT% exec ^
                        "import gpio_loopback_runner; gpio_loopback_runner.run_all_tests()" > result.txt 2>&1

                        REM Extract last line only (expected 0 or 1)
                        for /f "usebackq delims=" %%l in (`type result.txt`) do set LAST=%%l
                        echo %LAST%

                        exit /b 0
                        ''',
                        returnStdout: true
                    ).trim()

                    echo "ESP32 returned value: ${output}"

                    if (output == "1") {
                        error("GPIO loopback tests FAILED (output = 1)")
                    } else if (output == "0") {
                        echo "✓ GPIO loopback tests PASSED (output = 0)"
                    } else {
                        error("Unexpected output from ESP32: '${output}'")
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ PIPELINE SUCCESS"
        }
        failure {
            echo "❌ PIPELINE FAILURE"
            echo "Check ESP32 output above"
        }
    }
}
