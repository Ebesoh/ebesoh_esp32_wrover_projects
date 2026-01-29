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

                    def faults = []

                    if (output.contains("GPIO 14 - 19")) {
                        faults << "GPIO 14 -> GPIO 19"
                    }

                    if (output.contains("GPIO 12 - 18")) {
                        faults << "GPIO 12 -> GPIO 18"
                    }

                    output.split('\n').each { line ->
                        def clean = line.trim()
                        if (clean.startsWith("- ")) {
                            faults << clean.substring(2)
                        }
                    }

                    faults = faults.unique()

                    if (!faults.isEmpty()) {
                        echo "Failed GPIOs:"
                        faults.each { fault ->
                            echo " - ${fault}"
                        }
                        error("GPIO loopback tests FAILED (${faults.size()} failure(s))")
                    }

                    if (!output.contains("CI_RESULT: PASS")) {
                        error("Unexpected output from ESP32")
                    }

                    echo "All GPIO loopback tests PASSED"
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
