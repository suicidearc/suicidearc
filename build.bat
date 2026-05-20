@echo off
title Build Suicide Selfbot
echo.
echo  =======================================
echo   Buildando o selfbot em .exe ...
echo  =======================================
echo.

:: Verifica se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Instale o Python primeiro.
    pause
    exit /b 1
)

:: Instala dependencias + PyInstaller
echo [1/4] Instalando dependencias...
pip install -r requirements.txt pyinstaller pillow --quiet
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

:: Gera o icone se nao existir
echo.
echo [2/4] Gerando icone...
set "GENERATED_ICON=0"
if not exist "icon.ico" (
    python -c "from PIL import Image,ImageDraw,ImageFont;img=Image.new('RGBA',(64,64),(15,15,15,255));d=ImageDraw.Draw(img);f=ImageFont.truetype('arial.ttf',48);b=d.textbbox((0,0),'S',font=f);d.text(((64-(b[2]-b[0]))//2-b[0],(64-(b[3]-b[1]))//2-b[1]),'S',fill=(180,0,0,255),font=f);img.save('icon.ico',format='ICO',sizes=[(16,16),(32,32),(64,64)]);print('  icon.ico gerado')"
    set "GENERATED_ICON=1"
) else (
    echo   icon.ico ja existe, usando o existente.
)

echo.
echo [3/4] Compilando selfbot.py em .exe ...
if exist "icon.ico" (
    pyinstaller --onefile --console --clean --name "suicide" --icon=icon.ico selfbot.py
) else (
    pyinstaller --onefile --console --clean --name "suicide" selfbot.py
)
if %errorlevel% neq 0 (
    echo [ERRO] Falha no build.
    pause
    exit /b 1
)

echo.
echo [4/4] Pronto!

:: Remove icon.ico se foi gerado pelo script (nao pelo usuario)
if "%GENERATED_ICON%"=="1" (
    if exist "icon.ico" (
        del "icon.ico"
        echo   icon.ico gerado removido.
    )
)

:: Remove arquivos temporarios do PyInstaller
if exist "build" (
    rmdir /s /q "build"
    echo   pasta build removida.
)
if exist "__pycache__" (
    rmdir /s /q "__pycache__"
    echo   pasta __pycache__ removida.
)
if exist "suicide.spec" (
    del "suicide.spec"
    echo   suicide.spec removido.
)

echo.
echo  =======================================
echo   Build concluido!
echo   O .exe esta em: dist\suicide.exe
echo.
echo   Basta enviar o suicide.exe para
echo   quem quiser. Ao rodar, ele cria
echo   automaticamente a pasta 'cl' com
echo   os arquivos de configuracao.
echo.
echo   Estrutura ao rodar:
echo     suicide.exe
echo     cl\
echo       config.json
echo       settings.json
echo  =======================================
echo.
