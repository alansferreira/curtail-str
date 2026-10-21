@echo off
setlocal DisableDelayedExpansion
if "%~1"=="--help" goto help
if [%1]==[] goto usage
if not [%2]==[] goto usage
set "input=%~1"
setlocal EnableDelayedExpansion
if not "!input:~4000,1!"=="" (
    >&2 echo Input exceeds the 4000-character batch limit.
    exit /b 2
)
rem CMD uses the active code page; only ASCII case and vowels are normalized.
for %%P in (A=a B=b C=c D=d E=e F=f G=g H=h I=i J=j K=k L=l M=m N=n O=o P=p Q=q R=r S=s T=t U=u V=v W=w X=x Y=y Z=z) do (
    for /f "tokens=1,2 delims==" %%U in ("%%P") do set "input=!input:%%U=%%V!"
)
set "output="
set "word="
set /a "position=0"
:scan
set "char=!input:~%position%,1!"
if not defined char goto finish
set /a "position+=1"
set "boundary="
if "!char!"=="-" set "boundary=1"
if "!char!"=="_" set "boundary=1"
if "!char!"==" " set "boundary=1"
if "!char!"=="	" set "boundary=1"
if defined boundary (
    call :abbreviate
    set "word="
) else (
    set "word=!word!!char!"
)
goto scan
:finish
call :abbreviate
echo(!output!
exit /b 0

:abbreviate
if "!word:~2,1!"=="" exit /b 0
if "!word:~3,1!"=="" (
    set "result=!word!"
    goto append
)
set "result=!word:~0,1!"
set "previous=!word:~0,1!"
set /a "offset=1"
:compress
set "letter=!word:~%offset%,1!"
if not defined letter goto append
set /a "offset+=1"
set "vowel="
for %%V in (a e i o u) do if "!letter!"=="%%V" set "vowel=1"
if defined vowel goto compress
set "duplicate="
if "!letter!"=="!previous!" (
    for %%L in (a b c d e f g h i j k l m n o p q r s t u v w x y z) do (
        if "!letter!"=="%%L" set "duplicate=1"
    )
)
if not defined duplicate set "result=!result!!letter!"
set "previous=!letter!"
goto compress
:append
if defined output set "output=!output!-"
set "output=!output!!result:~0,4!"
exit /b 0

:help
echo Usage: abbreviate.bat "text"
echo Universal mode. Pure CMD; Unicode depends on the active code page.
exit /b 0
:usage
>&2 echo Usage: abbreviate.bat "text"
exit /b 2
