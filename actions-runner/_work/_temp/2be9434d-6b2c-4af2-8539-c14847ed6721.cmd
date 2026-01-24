@echo off
python -m mpremote connect %ESP_PORT% exec "import test_runner_ds18b20; test_runner_ds18b20.main()" > temp.txt
type temp.txt
findstr /C:"CI_RESULT: FAIL" temp.txt >nul && exit /b 1
