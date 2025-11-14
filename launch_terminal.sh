#!/bin/bash
# Script para abrir BatePonto no Terminal

# Obtém o diretório do script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Abre uma nova janela do Terminal e executa o programa
osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$DIR' && ./dist/bateponto && exit"
end tell
EOF
