@echo off
echo ========================================
echo  CallAndroid - Instalacao Completa
echo ========================================
echo.

REM Verifica se esta rodando como Administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Execute este arquivo como Administrador.
    echo Clique com o botao direito e selecione "Executar como administrador".
    pause
    exit /b 1
)

REM Vai para o diretorio do script
cd /d "%~dp0"

REM Remove registros antigos do protocolo callandroid://
reg delete "HKEY_CLASSES_ROOT\callandroid" /f >nul 2>&1

REM 1. Verifica Python
echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado. Instale o Python 3.9+.
    pause
    exit /b 1
)
echo OK
echo.

REM 2. Instala PyInstaller se necessario
echo [2/6] Verificando PyInstaller...
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)
echo OK
echo.

REM 3. Build do executavel
echo [3/6] Gerando CallAndroid.exe...
taskkill /F /IM CallAndroid.exe >nul 2>&1
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
python -m PyInstaller --onefile --windowed --name=CallAndroid --paths src --distpath=dist --workpath=build --specpath=build --clean src\main.py
if %errorlevel% neq 0 (
    echo ERRO: Falha ao gerar o executavel.
    pause
    exit /b 1
)
echo OK
echo.

REM 4. Registra auto-start no Windows
echo [4/6] Configurando inicio automatico...
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "EXE_PATH=%~dp0dist\CallAndroid.exe"
python src\vbs_helper.py run "%STARTUP%\CallAndroid.vbs" "%EXE_PATH%"
echo OK
echo.

REM 5. Cria atalho no Desktop
echo [5/6] Criando atalho no Desktop...
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\CallAndroid.lnk"
python src\vbs_helper.py shortcut "%TEMP%\create_shortcut.vbs" "%EXE_PATH%" "%~dp0dist" "%SHORTCUT%"
cscript //nologo "%TEMP%\create_shortcut.vbs"
del "%TEMP%\create_shortcut.vbs"
echo OK
echo.

REM 6. Inicia o servidor agora (100% invisivel via VBS)
echo [6/6] Iniciando CallAndroid...
if exist "%EXE_PATH%" (
    python src\vbs_helper.py run "%TEMP%\start_callandroid.vbs" "%EXE_PATH%"
    cscript //nologo "%TEMP%\start_callandroid.vbs"
    del "%TEMP%\start_callandroid.vbs"
    echo OK
) else (
    echo ERRO: dist\CallAndroid.exe nao encontrado.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Pronto! CallAndroid esta rodando!
echo ========================================
echo.
echo Use links no Notion como:
echo   http://localhost:39527/call/5511999999999
echo.
echo Atalho criado no Desktop: CallAndroid
echo O CallAndroid inicia automaticamente com o Windows.
echo.
pause
