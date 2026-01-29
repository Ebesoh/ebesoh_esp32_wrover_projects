
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
                        