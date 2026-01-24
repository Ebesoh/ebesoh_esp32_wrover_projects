@echo off
python -m mpremote connect %ESP_PORT% exec "import test_runner_bt; test_runner_bt.run_all_tests()" > bt.txt
type bt.txt
findstr /C:"CI_RESULT: FAIL" bt.txt >nul && exit /b 1
