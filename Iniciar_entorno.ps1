$ErrorActionPreference = 'Stop'
$podmanCommand = Get-Command podman -ErrorAction SilentlyContinue
if ($podmanCommand) { $podmanExe = $podmanCommand.Source } else { $podmanExe = Join-Path $env:LOCALAPPDATA 'Programs\Podman\podman.exe' }
if (-not (Test-Path -LiteralPath $podmanExe)) { throw 'No se encuentra Podman. Abre Podman Desktop.' }
& $podmanExe start pymes-sunat pymes-n8n
if ($LASTEXITCODE -ne 0) { throw 'Primero inicia la maquina desde Podman Desktop y vuelve a ejecutar este archivo.' }
Write-Host 'Abre http://127.0.0.1:5680/form/pymes-consulta-padron-sunat'
Write-Host 'Editor: http://127.0.0.1:5680/workflow/pymesSunatRuc02'

