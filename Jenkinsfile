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
        skipDefaultCheckout()   // Prevent checkout before auto-clean
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
                    def decision = powershell(
                        script: '''
                        $drive = Get-PSDrive -Name C
                        $freeGb = [math]::Round($drive.Free / 1GB, 2)

                        Write-Host "Free disk space on C: $freeGb GB"

                        if ($freeGb -lt 10) {
                            Write-Output "CLEAN"
                        } else {
                            Write-Output "OK"
                        }
                        ''',
                        returnStdout: true
                    ).trim()

                    if (decision == "CLEAN") {
                        echo "⚠ Low disk space detected (<10 GB). Cleaning workspace contents..."

                        powershell '''
                        Write-Host "Cleaning workspace contents (Windows-safe)..."
                        if (Test-Path "$env:WORKSPACE") {
                            Get-ChildItem -Path "$env:WORKSPACE" -Force |
                            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
                        }
                        '''
                    } else {
                        echo "Disk space OK. No cleanup needed."
                    }
                }
            }
        }

        stage('Checkout SCM') {
            steps {
                checkout scm
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
