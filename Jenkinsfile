stage('Run Loopback Tests') {
    steps {
        script {
            def output = bat(
                script: '''
                python -m mpremote connect %ESP_PORT% exec ^
                "import gpio_loopback_runner; gpio_loopback_runner.run_all_tests()"
                ''',
                returnStdout: true
            ).trim()

            echo "ESP32 output:"
            echo output

            // Collect failures
            def failures = []

            if (output.contains("CI_RESULT: FAIL")) {

                if (output.contains("GPIO 14 -> 19")) {
                    failures << "GPIO 14 -> 19"
                }

                if (output.contains("GPIO 12 -> 18")) {
                    failures << "GPIO 12 -> 18"
                }

                if (failures.isEmpty()) {
                    failures << "Unknown failure"
                }
            }

            // Final decision
            if (!failures.isEmpty()) {
                echo "Detected failures:"
                failures.each { f ->
                    echo "- ${f}"
                }
                error("Loopback tests failed: ${failures.join(', ')}")
            }

            if (output.contains("CI_RESULT: PASS")) {
                echo "✓ All GPIO loopback tests passed"
            } else {
                error("Unexpected output from ESP32:\n${output}")
            }
        }
    }
}

