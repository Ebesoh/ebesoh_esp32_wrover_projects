pipeline {
    agent any

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

        stage('Run Loopback Testss') {
            steps {
                script {
                    def output = bat(
                        script: '''
                        @echo off
                        echo Running GPIO loopback tests...

                        REM Ensure clean REPL state (suppress noise)
                        python -m mpremote connect %ESP_PORT% reset repl < nul > nul 2>&1

                        REM Execute tests, capture all output
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
