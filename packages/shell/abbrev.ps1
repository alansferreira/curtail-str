param(
    [Parameter(Position = 0)]
    [AllowEmptyString()]
    [string] $Text,
    [switch] $Help
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

function abbrev {
    param([AllowEmptyString()][string] $Value)

    $output = New-Object 'System.Collections.Generic.List[string]'
    $normalized = $Value.ToLowerInvariant().Normalize([Text.NormalizationForm]::FormC)
    foreach ($word in [regex]::Split($normalized, '[-_\s\u0085]+')) {
        if ($word.Length -lt 3) { continue }
        if ($word.Length -eq 3) {
            $output.Add($word)
            continue
        }
        $first = $word.Substring(0, 1)
        $tail = $word.Substring(1).Normalize([Text.NormalizationForm]::FormD)
        $tail = [regex]::Replace($tail, '[aeiou]\p{M}*', '')
        $compressed = $first + $tail.Normalize([Text.NormalizationForm]::FormC)
        $compressed = [regex]::Replace($compressed, '(\p{L})\1+', '$1')
        if ($compressed.Length -gt 4) {
            $compressed = $compressed.Substring(0, 4)
        }
        $output.Add($compressed)
    }
    return [string]::Join('-', $output.ToArray())
}

try {
    if ($Help) {
        Write-Output 'Usage: .\abbrev.ps1 -Text "text"'
        Write-Output 'Universal mode. Windows PowerShell 5.1+ or PowerShell 7.'
        exit 0
    }
    if (-not $PSBoundParameters.ContainsKey('Text')) {
        [Console]::Error.WriteLine('Usage: .\abbrev.ps1 -Text "text"')
        exit 2
    }
    Write-Output (abbrev $Text)
    exit 0
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
