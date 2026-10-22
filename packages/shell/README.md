# curtail-str shell

Standalone identifier shortening in **universal mode**. No Node.js, Python,
Go, Java, pip, or npm is required to run the scripts. Replacement maps and
configurable length limits are not supported.

## Platforms and requirements

| Script | Platforms | System requirements |
| --- | --- | --- |
| `curtail-str.sh` | Linux, macOS, BSD, WSL | `/bin/sh` and POSIX `awk` |
| `curtail-str.bat` | Windows 10/11, Windows Server | `cmd.exe`; no PowerShell dependency |
| `curtail-str.ps1` | Windows; Linux/macOS with PowerShell | Windows PowerShell 5.1+ or PowerShell 7 |

Pass the text as one argument. Results are written to stdout with a trailing
newline, including empty results. Invalid arguments produce a nonzero exit
code and an error on stderr. Use `--help` in POSIX shell or CMD and `-Help` in
PowerShell. Empty input is valid; use `-Text ""` in PowerShell.

```sh
sh curtail-str.sh "active-customer-code-in-the-stock"
# actv-cstm-cd-the-stck
```

```bat
curtail-str.bat "active-customer-code-in-the-stock"
REM actv-cstm-cd-the-stck
```

```powershell
.\curtail-str.ps1 -Text "active-customer-code-in-the-stock"
# actv-cstm-cd-the-stck
```

The ASCII rules follow the universal algorithm: lowercase, split on hyphens,
underscores and whitespace, discard words shorter than 3 characters, preserve
words of length 3, remove vowels after the first character, collapse repeated
letters, and truncate compressed words to 4 characters.
Results are not translations and are not guaranteed to be unique or idempotent.

## Unicode and input limitations

Unicode input is accepted, but **results are not guaranteed to match between
scripts or with the library APIs**:

- **POSIX:** case conversion, `[[:alpha:]]`, whitespace, lengths, and truncation
  depend on `awk` and the locale. Only ASCII vowels are removed. No NFC/NFD
  normalization is performed. Byte-oriented awk implementations may truncate
  inside a UTF-8 sequence. Use ASCII for portable, guaranteed valid UTF-8 output.
- **PowerShell:** normalizes to NFC and removes decomposed Latin vowels and
  their marks. Uses .NET invariant lowercase conversion. Lengths and truncation
  use UTF-16 units, so supplementary characters may be split. Prefer Basic
  Multilingual Plane letters. Whitespace follows .NET regular expressions.
- **Batch:** case conversion, vowel removal, and duplicate-letter removal cover
  ASCII only. Other characters depend on the active CMD code page; counting and
  truncation follow CMD behavior. Only hyphens, underscores, spaces, and tabs
  are separators. Accents are not normalized.

CMD expands arguments before execution. Percent signs, exclamation marks,
quotes, metacharacters, and multiline text require special care. Use simple
slugs without these characters in the batch script. For arbitrary text, prefer
PowerShell or POSIX shell with appropriate quoting. NUL cannot be passed in
an argument. Batch input is limited to 4000 characters, below CMD's 8191-character
command-line limit. Do not interpolate untrusted input into shell commands.

## Download

Download the standalone scripts directly from the repository. No archives or
distribution directories are generated.

Replace `main` with a commit SHA or tag for an immutable revision.
Inspect downloaded scripts and compare checksums with a trusted source before
executing them. MD5 checksums can detect accidental corruption, but are not
suitable for security or authenticity verification. Avoid `curl | sh` and
`Invoke-Expression` on downloaded content.

### Unix

```sh
base='https://raw.githubusercontent.com/alansferreira/curtail-str/main/packages/shell'
curl -fL "$base/curtail-str.sh" -o curtail-str.sh
md5sum curtail-str.sh
# macOS: md5 curtail-str.sh
# Inspect the script and compare the hash with a trusted value before running:
sh curtail-str.sh "active-customer-code-in-the-stock"
```

With wget, replace `curl -fL URL -o FILE` with `wget -O FILE URL`.
To install the command for your user, copy `curtail-str.sh` to
`~/.local/bin/curtail-str`, run `chmod +x ~/.local/bin/curtail-str`, and ensure
that directory is on your PATH. No sudo is needed.

### Windows PowerShell

```powershell
$base = 'https://raw.githubusercontent.com/alansferreira/curtail-str/main/packages/shell'
Invoke-WebRequest -UseBasicParsing "$base/curtail-str.ps1" -OutFile curtail-str.ps1
Get-FileHash curtail-str.ps1 -Algorithm MD5
# Inspect the script and compare the hash with a trusted value before running:
.\curtail-str.ps1 -Text "active-customer-code-in-the-stock"
```

Follow your organization's execution policy for `.ps1` scripts. The batch
script does not require changing PowerShell execution policy.

### Windows CMD

On systems with `curl.exe`:

```bat
curl.exe -fL https://raw.githubusercontent.com/alansferreira/curtail-str/main/packages/shell/curtail-str.bat -o curtail-str.bat
certutil -hashfile curtail-str.bat MD5
REM Inspect the script and compare the hash with a trusted value before running:
curtail-str.bat "active-customer-code-in-the-stock"
```

### Download individual scripts

Each script can run independently:

```sh
curl -fL https://raw.githubusercontent.com/alansferreira/curtail-str/main/packages/shell/curtail-str.sh -o curtail-str.sh
# Alternatively:
# wget -O curtail-str.sh https://raw.githubusercontent.com/alansferreira/curtail-str/main/packages/shell/curtail-str.sh
sh curtail-str.sh "active-customer-code-in-the-stock"
```

```powershell
Invoke-WebRequest -UseBasicParsing https://raw.githubusercontent.com/alansferreira/curtail-str/main/packages/shell/curtail-str.ps1 -OutFile curtail-str.ps1
.\curtail-str.ps1 -Text "active-customer-code-in-the-stock"
```

```bat
curl.exe -fL https://raw.githubusercontent.com/alansferreira/curtail-str/main/packages/shell/curtail-str.bat -o curtail-str.bat
curtail-str.bat "active-customer-code-in-the-stock"
```

## Development

Run from the repository root:

```sh
python3 scripts/package_shell.py
python3 -m unittest discover -s packages/shell/tests -v
```

The checksum command uses only the Python standard library and prints one
`<md5>  <filename>` line for each of `curtail-str.sh`, `curtail-str.bat`, and
`curtail-str.ps1`. It hashes the existing bytes without normalizing line endings
and creates no files or directories. Consumers do not need Python.

Tests cover shared ASCII behavior and platform-specific cases. CMD tests
require native Windows; PowerShell tests require an installed PowerShell.
The CI workflow covers Linux, macOS, and Windows.
