#!/bin/bash

# BatePonto - macOS Build Script
# Este script compila o BatePonto em um aplicativo .app para macOS

set -e  # Exit on error

echo "========================================="
echo "BatePonto - Build Script para macOS"
echo "========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar Python
echo -e "${BLUE}[1/6]${NC} Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Erro: Python 3 não encontrado!${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python $(python3 --version) encontrado"
echo ""

# Criar ambiente virtual (opcional mas recomendado)
if [ ! -d "venv" ]; then
    echo -e "${BLUE}[2/6]${NC} Criando ambiente virtual..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Ambiente virtual criado"
else
    echo -e "${BLUE}[2/6]${NC} Usando ambiente virtual existente"
fi
echo ""

# Ativar ambiente virtual
echo -e "${BLUE}[3/6]${NC} Ativando ambiente virtual..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Ambiente virtual ativado"
echo ""

# Instalar dependências
echo -e "${BLUE}[4/6]${NC} Instalando dependências..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓${NC} Dependências instaladas"
echo ""

# Criar ícone .icns
echo -e "${BLUE}[5/6]${NC} Gerando ícone do aplicativo..."

if [ ! -f "assets/icon.icns" ]; then
    echo "  Criando ícone a partir do SVG..."

    # Verificar se temos sips (nativo do macOS)
    if command -v sips &> /dev/null; then
        # Tentar converter SVG para PNG usando sips ou outras ferramentas
        if command -v rsvg-convert &> /dev/null; then
            # Se tiver rsvg-convert (brew install librsvg)
            rsvg-convert -w 1024 -h 1024 assets/icon.svg -o assets/icon.png
        elif command -v inkscape &> /dev/null; then
            # Se tiver inkscape (brew install inkscape)
            inkscape assets/icon.svg -o assets/icon.png -w 1024 -h 1024
        elif command -v convert &> /dev/null; then
            # Se tiver ImageMagick (brew install imagemagick)
            convert -background none -size 1024x1024 assets/icon.svg assets/icon.png
        else
            echo -e "${RED}  Aviso: Nenhuma ferramenta de conversão SVG encontrada${NC}"
            echo "  Instale uma das seguintes ferramentas:"
            echo "    - brew install librsvg"
            echo "    - brew install inkscape"
            echo "    - brew install imagemagick"
            echo ""
            echo "  Continuando sem ícone customizado..."
        fi

        # Se conseguimos criar o PNG, criar o .icns
        if [ -f "assets/icon.png" ]; then
            echo "  Criando iconset..."
            mkdir -p assets/icon.iconset

            # Gerar todos os tamanhos necessários
            sips -z 16 16 assets/icon.png --out assets/icon.iconset/icon_16x16.png > /dev/null 2>&1
            sips -z 32 32 assets/icon.png --out assets/icon.iconset/icon_16x16@2x.png > /dev/null 2>&1
            sips -z 32 32 assets/icon.png --out assets/icon.iconset/icon_32x32.png > /dev/null 2>&1
            sips -z 64 64 assets/icon.png --out assets/icon.iconset/icon_32x32@2x.png > /dev/null 2>&1
            sips -z 128 128 assets/icon.png --out assets/icon.iconset/icon_128x128.png > /dev/null 2>&1
            sips -z 256 256 assets/icon.png --out assets/icon.iconset/icon_128x128@2x.png > /dev/null 2>&1
            sips -z 256 256 assets/icon.png --out assets/icon.iconset/icon_256x256.png > /dev/null 2>&1
            sips -z 512 512 assets/icon.png --out assets/icon.iconset/icon_256x256@2x.png > /dev/null 2>&1
            sips -z 512 512 assets/icon.png --out assets/icon.iconset/icon_512x512.png > /dev/null 2>&1
            cp assets/icon.png assets/icon.iconset/icon_512x512@2x.png

            # Criar .icns
            iconutil -c icns assets/icon.iconset -o assets/icon.icns

            # Limpar
            rm -rf assets/icon.iconset
            # rm assets/icon.png  # Manter o PNG pode ser útil

            echo -e "${GREEN}✓${NC} Ícone .icns criado"
        fi
    else
        echo -e "${RED}  Erro: sips não encontrado (necessário para criar ícone)${NC}"
    fi
else
    echo -e "${GREEN}✓${NC} Ícone já existe"
fi
echo ""

# Compilar com PyInstaller
echo -e "${BLUE}[6/7]${NC} Compilando aplicação com PyInstaller..."
pyinstaller --clean --noconfirm bateponto.spec

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Compilação concluída com sucesso!"
else
    echo -e "${RED}✗${NC} Erro na compilação"
    exit 1
fi
echo ""

# Criar .app wrapper que abre no Terminal
echo -e "${BLUE}[7/7]${NC} Criando .app wrapper..."

# Criar estrutura do .app
mkdir -p "dist/BatePonto.app/Contents/MacOS"
mkdir -p "dist/BatePonto.app/Contents/Resources"

# Criar Info.plist
cat > "dist/BatePonto.app/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIconFile</key>
    <string>icon</string>
    <key>CFBundleIdentifier</key>
    <string>com.bateponto.app</string>
    <key>CFBundleName</key>
    <string>BatePonto</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
PLIST

# Criar script launcher
cat > "dist/BatePonto.app/Contents/MacOS/launcher" <<'LAUNCHER'
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EXEC_PATH="$DIR/../Resources/bateponto"

osascript <<EOF
tell application "Terminal"
    activate
    do script "clear && '$EXEC_PATH' ; exit"
end tell
EOF
LAUNCHER

chmod +x "dist/BatePonto.app/Contents/MacOS/launcher"

# Mover executável para Resources
mv dist/bateponto "dist/BatePonto.app/Contents/Resources/"

# Copiar ícone
if [ -f "assets/icon.icns" ]; then
    cp assets/icon.icns "dist/BatePonto.app/Contents/Resources/icon.icns"
fi

echo -e "${GREEN}✓${NC} Wrapper criado"
echo ""

# Verificar resultado
if [ -d "dist/BatePonto.app" ]; then
    echo "========================================="
    echo -e "${GREEN}BUILD CONCLUÍDO COM SUCESSO!${NC}"
    echo "========================================="
    echo ""
    echo "Aplicativo criado em: dist/BatePonto.app"
    echo ""
    echo "Próximos passos:"
    echo "  1. Testar: open dist/BatePonto.app"
    echo "  2. Instalar: cp -r dist/BatePonto.app /Applications/"
    echo "  3. Ou criar atalho no Desktop:"
    echo "     ln -s $(pwd)/dist/BatePonto.app ~/Desktop/BatePonto.app"
    echo ""
    echo "Nota: Na primeira execução, pode ser necessário permitir"
    echo "      o app nas preferências de segurança do macOS."
    echo ""
else
    echo -e "${RED}Erro: dist/BatePonto.app não foi criado!${NC}"
    exit 1
fi
