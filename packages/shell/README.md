# Abbrev shell 0.1.0

Comando standalone, **modo universal apenas**. Nao exige Node.js, Python,
Go, Java, pip ou npm para executar. Nao oferece mapas nem limites configuraveis.
O nome da funcao principal em shell e PowerShell e `abbrev`; em batch,
o processamento usa a subrotina `:abbrev`.

## Plataformas e requisitos

| Arquivo | Plataformas | Requisitos presentes no sistema |
| --- | --- | --- |
| `abbrev.sh` | Linux, macOS, BSD, WSL | `/bin/sh` e `awk` POSIX |
| `abbrev.bat` | Windows 10/11, Windows Server | `cmd.exe`, sem PowerShell |
| `abbrev.ps1` | Windows; Linux/macOS com PowerShell | Windows PowerShell 5.1+ ou PowerShell 7 |

Um unico argumento contem o texto; a saida vai para stdout com nova linha.
`--help` no shell/batch e `-Help` no PowerShell exibem ajuda. Saida vazia
tambem tem uma nova linha. Entrada incorreta gera erro em stderr e codigo
nao zero. `""` e uma entrada valida. Em PowerShell, informar `-Text ""`.
Para texto com hifen inicial, preferir `-Text` no PowerShell.

```sh
sh abbrev.sh "codigo-do-cliente-ativo-no-estoque"
# cdg-clnt-atv-estq
sh abbrev.sh "active-customer-code-in-the-stock"
# actv-cstm-cd-the-stck
```

```bat
abbrev.bat "codigo-do-cliente-ativo-no-estoque"
REM cdg-clnt-atv-estq
```

```powershell
.\abbrev.ps1 -Text "codigo-do-cliente-ativo-no-estoque"
# cdg-clnt-atv-estq
```

As regras ASCII seguem o algoritmo universal: minusculas, separacao por
hifen/underscore/espacos, descarte de termos menores que 3, preservacao dos
de 3, remocao de vogais depois da inicial, colapso de letras repetidas e
corte em 4. Nao traduz nem garante unicidade ou idempotencia.

## Unicode e limites intencionais

Unicode e aceito, mas **nao ha promessa de paridade com as bibliotecas ou
entre os scripts**:

- POSIX: caixa, `[[:alpha:]]`, espacos, comprimento e corte dependem do `awk`
  e da localidade. Somente vogais ASCII sao removidas. Nao ha normalizacao
  NFC/NFD. Um awk orientado a bytes pode cortar uma sequencia UTF-8 no meio.
  Use ASCII quando precisar de saida portavel e UTF-8 valida garantida.
- PowerShell: normaliza NFC e remove vogais latinas decompostas e suas marcas.
  Usa minusculas invariantes do .NET. Comprimentos e cortes usam unidades
  UTF-16; caracteres suplementares podem ser cortados no meio. Preferir
  letras do plano basico Unicode. Espacos seguem a regex do .NET.
- Batch: conversao de caixa, remocao de vogais e colapso de letras cobrem
  somente ASCII. Demais caracteres sao preservados conforme a pagina de
  codigo ativa do CMD; contagem/corte seguem o CMD. So hifen, underscore,
  espaco e tab sao separadores. Nao ha normalizacao de acentos.

O batch recebe argumentos sujeitos a expansao do CMD: `%`, `!`, aspas,
metacaracteres e multiplas linhas exigem cuidado. Use apenas slugs simples
sem esses caracteres no `.bat`; para texto arbitrario prefira `.ps1` ou
`.sh`, com o quoting apropriado do shell. NUL nao pode ser transportado
como argumento. Limite de entrada do batch: 4000 caracteres, abaixo do
limite de linha do CMD (8191). Nao usar estes scripts para dados hostis
interpolados em comandos. Eles nao sao parsers de linhas de comando.

## Download HTTP

Os arquivos gerados sao `abbrev-shell-0.1.0.tar.gz`,
`abbrev-shell-0.1.0.zip` e `SHA256SUMS`, versionados em `packages/shell/dist/`.
O download usa o proprio repositorio GitHub, sem Releases ou servidor adicional:

`https://raw.githubusercontent.com/alansferreira/abbrev/main/packages/shell/dist`

Os links ficam disponiveis depois do commit e push dos arquivos para `main`.
Para downloads imutaveis e reproduziveis, substitua `main` pelo SHA de um commit
ou por uma tag publicada. A branch `main` acompanha as alteracoes do projeto.

Unix, com curl:

```sh
base='https://raw.githubusercontent.com/alansferreira/abbrev/main/packages/shell/dist'
curl -fL "$base/abbrev-shell-0.1.0.tar.gz" -o abbrev-shell-0.1.0.tar.gz
curl -fL "$base/SHA256SUMS" -o SHA256SUMS
# Compare o hash com uma fonte confiavel antes de extrair/executar:
sha256sum abbrev-shell-0.1.0.tar.gz
# macOS: shasum -a 256 abbrev-shell-0.1.0.tar.gz
tar -xzf abbrev-shell-0.1.0.tar.gz
sh abbrev-shell-0.1.0/abbrev.sh "codigo-do-cliente"
```

Com wget, substituir cada `curl -fL URL -o ARQUIVO` por
`wget -O ARQUIVO URL`. Pode-se instalar manualmente `abbrev.sh` como
`~/.local/bin/abbrev`, dar permissao com `chmod +x` e adicionar esse
diretorio ao PATH. Nao precisa de sudo.

Windows PowerShell:

```powershell
$base = 'https://raw.githubusercontent.com/alansferreira/abbrev/main/packages/shell/dist'
Invoke-WebRequest -UseBasicParsing "$base/abbrev-shell-0.1.0.zip" -OutFile abbrev-shell-0.1.0.zip
Invoke-WebRequest -UseBasicParsing "$base/SHA256SUMS" -OutFile SHA256SUMS
Get-FileHash abbrev-shell-0.1.0.zip -Algorithm SHA256
# Compare com o hash confiavel antes de extrair:
Expand-Archive abbrev-shell-0.1.0.zip -DestinationPath .
.\abbrev-shell-0.1.0\abbrev.bat "codigo-do-cliente"
```

No CMD do Windows 10/11 com `curl.exe` e `tar.exe` disponiveis:

```bat
curl.exe -fL https://raw.githubusercontent.com/alansferreira/abbrev/main/packages/shell/dist/abbrev-shell-0.1.0.zip -o abbrev-shell-0.1.0.zip
certutil -hashfile abbrev-shell-0.1.0.zip SHA256
REM Compare com o hash confiavel antes de extrair:
tar.exe -xf abbrev-shell-0.1.0.zip
abbrev-shell-0.1.0\abbrev.bat "codigo-do-cliente"
```

Checksum baixado do mesmo servidor detecta corrupcao, nao autentica um host
comprometido. Nao use `curl | sh` ou `Invoke-Expression` com scripts baixados.
Inspecione os arquivos. Para `.ps1`, respeite a politica de execucao da
organizacao; nao e necessario desabilita-la para usar o `.bat`.

### Download direto de um script

Cada script e independente e pode ser baixado sem o pacote:

```sh
curl -fL https://raw.githubusercontent.com/alansferreira/abbrev/main/packages/shell/abbrev.sh -o abbrev.sh
# Alternativa:
# wget -O abbrev.sh https://raw.githubusercontent.com/alansferreira/abbrev/main/packages/shell/abbrev.sh
sh abbrev.sh "codigo-do-cliente"
```

```powershell
Invoke-WebRequest -UseBasicParsing https://raw.githubusercontent.com/alansferreira/abbrev/main/packages/shell/abbrev.ps1 -OutFile abbrev.ps1
.\abbrev.ps1 -Text "codigo-do-cliente"
```

```bat
curl.exe -fL https://raw.githubusercontent.com/alansferreira/abbrev/main/packages/shell/abbrev.bat -o abbrev.bat
abbrev.bat "codigo-do-cliente"
```

## Geracao e testes (somente desenvolvimento)

Na raiz do repositorio:

```sh
python3 scripts/package_shell.py
python3 -m unittest discover -s packages/shell/tests -v
```

O empacotamento exige apenas a biblioteca padrao Python no ambiente de build,
nao nas maquinas consumidoras. O ZIP inclui CRLF nos scripts Windows.
Depois de alterar os scripts ou este guia, gere novamente os arquivos e inclua
os dois pacotes e `SHA256SUMS` no mesmo commit. Nao e necessario executar o build
para baixar os arquivos ja versionados.
Os testes verificam ASCII compartilhado e casos especificos de cada
plataforma. Testes Windows exigem Windows; a CI cobre CMD e PowerShell.
