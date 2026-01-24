@echo off
python -m mpremote connect %ESP_PORT% exec "import test_wifi_runner; test_wifi_runner.run_all_wifi_tests()" > wifi.txt
type wifi.txt
findstr /C:"CI_RESULT: FAIL" wifi.txt >nul && exit /b 1
