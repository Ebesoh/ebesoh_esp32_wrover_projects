pipeline {
    agent any

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

        stage('Preflight: ESP32 connectivity') {
            steps {
                bat '''
                @echo off
                echo Preflight: checking ESP32 on %ESP_PORT%...

                python -m mpremote connect %ESP_PORT% repl --exit

                if %ERRORLEVEL% NEQ 0 (
                    echo Preflight failed: ESP32 not reachable on %ESP_PORT%
                    exit /b %ERRORLEVEL%
                )

                echo Preflight OK: ESP32 is reachable
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
                    if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
                )
                '''
            }
        }

        stage('Run Loopback Tests') {
            steps {
                bat '''
                @echo off
                echo Running GPIO loopback tests on ESP32...

                python -m mpremote connect %ESP_PORT% exec ^
                "import gpio_loopback_runner; gpio_loopback_runner.run_all_tests()"

                if %ERRORLEVEL% NEQ 0 (
                    echo GPIO loopback tests failed
                    exit /b %ERRORLEVEL%
                )

                echo GPIO loopback tests passed
                '''
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
