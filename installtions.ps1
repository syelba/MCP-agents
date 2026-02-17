$ErrorActionPreference = "Stop"

$python = "C:\Users\user\Desktop\MCP\ovms\ovms\python\python.exe"
$hf_cli = "C:\Users\user\Desktop\MCP\ovms\ovms\python\Scripts\huggingface-cli.exe"

$proxy = "http://"

$modelDir = "C:\Users\user\Desktop\MCP\ov_model"

Write-Host "Setting proxy..."
$env:HTTP_PROXY = $proxy
$env:HTTPS_PROXY = $proxy

Write-Host "Installing huggingface CLI if needed..."
& $python -m pip install "huggingface_hub[cli]" --proxy $proxy

Write-Host "Downloading ready OpenVINO model..."

& $hf_cli download OpenVINO/Phi-3-mini-4k-instruct-int4-ov `
  --local-dir $modelDir `
  --local-dir-use-symlinks False

Write-Host "Checking files..."

if (Test-Path "$modelDir\openvino_model.xml") {
    Write-Host "SUCCESS - Model ready."
} else {
    Write-Host "ERROR - Model not found."
    exit 1
}

Write-Host "DONE."
