param(
    [string]$BlenderExe = 'D:\blender-5.1.2-windows-x64\blender.exe'
)

$ErrorActionPreference = 'Stop'
$SourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Resolve-Path (Join-Path $SourceDir '..\..')).Path

if (-not (Test-Path -LiteralPath $BlenderExe -PathType Leaf)) {
    throw "Blender executable not found: $BlenderExe"
}

Push-Location $RepoRoot
try {
    python 'lkivivube_delivery\source\build_models.py'
    if ($LASTEXITCODE -ne 0) {
        throw "Model generation failed with exit code $LASTEXITCODE"
    }

    python 'lkivivube_delivery\source\make_presentation_handoff.py'
    if ($LASTEXITCODE -ne 0) {
        throw "Presentation handoff generation failed with exit code $LASTEXITCODE"
    }

    & $BlenderExe --background --factory-startup --python 'lkivivube_delivery\source\blender_review.py'
    if ($LASTEXITCODE -ne 0) {
        throw "Blender review failed with exit code $LASTEXITCODE"
    }

    python 'lkivivube_delivery\source\validate_models.py'
    if ($LASTEXITCODE -ne 0) {
        throw "GLB validation failed with exit code $LASTEXITCODE"
    }

    python 'lkivivube_delivery\source\make_contact_sheet.py'
    if ($LASTEXITCODE -ne 0) {
        throw "Contact sheet generation failed with exit code $LASTEXITCODE"
    }

    python 'lkivivube_delivery\source\make_reference_detail_sheets.py'
    if ($LASTEXITCODE -ne 0) {
        throw "Private reference-detail-sheet generation failed with exit code $LASTEXITCODE"
    }

    python 'lkivivube_delivery\source\prepare_all_kivicube_packages.py'
    if ($LASTEXITCODE -ne 0) {
        throw "Static-ground Kivicube package generation failed with exit code $LASTEXITCODE"
    }

    python 'lkivivube_delivery\source\make_trigger_reference_review.py'
    if ($LASTEXITCODE -ne 0) {
        throw "Kivicube asset review-sheet generation failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
