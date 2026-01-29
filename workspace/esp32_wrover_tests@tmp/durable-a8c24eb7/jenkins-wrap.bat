@echo off 
cmd /c call "C:\ESP32_Wrover\ebesoh_esp32_wrover_projects\workspace\esp32_wrover_tests@tmp\durable-a8c24eb7\jenkins-main.bat" > "C:\ESP32_Wrover\ebesoh_esp32_wrover_projects\workspace\esp32_wrover_tests@tmp\durable-a8c24eb7\output.txt" 2> "C:\ESP32_Wrover\ebesoh_esp32_wrover_projects\workspace\esp32_wrover_tests@tmp\durable-a8c24eb7\jenkins-log.txt"
echo %ERRORLEVEL% > "C:\ESP32_Wrover\ebesoh_esp32_wrover_projects\workspace\esp32_wrover_tests@tmp\durable-a8c24eb7\jenkins-result.txt"
