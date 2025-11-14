# BatePonto - Sistema de Apontamento de Horas

Sistema de controle de horas trabalhadas em projetos com interface TUI (Terminal User Interface) usando Python e Curses.

## Características

- 🕐 **Relógio em tempo real** com timer de projeto ativo
- 📊 **Múltiplos projetos** (até 5 projetos ativos simultaneamente)
- ⌨️ **Múltiplas formas de interação**: mouse, teclas numéricas (1-5), ou navegação por setas
- 💾 **Persistência automática** de dados em JSON
- 😴 **Detecção de inatividade** com pausas automáticas
- 📈 **Relatórios detalhados** com períodos customizáveis
- 📤 **Exportação para CSV** para análise externa
- 🎨 **Interface colorida** com suporte a temas
- ✏️ **CRUD completo de projetos** direto na interface (sem editar JSON)
- 📐 **Interface compacta** que ocupa mínimo espaço no desktop

## Instalação

### Requisitos

- Python 3.8 ou superior
- macOS, Linux ou Windows com suporte a curses

### Instalar dependências

```bash
pip install -r requirements.txt
```

## Uso

### Executar diretamente

```bash
python main.py
```

### Compilar para executável (macOS)

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements.txt

# Executar build
./build_macos.sh

# O app estará em: dist/BatePonto.app
```

Após compilar, você pode:
- Arrastar `BatePonto.app` para a pasta Applications
- Criar atalho no Desktop
- Executar com duplo clique

## Controles

### Tela Principal

- **1-5**: Iniciar/parar projeto correspondente
- **↑↓**: Navegar entre projetos
- **Enter/Space**: Toggle projeto selecionado
- **Mouse**: Clicar nos painéis de projeto
- **R**: Abrir relatórios
- **C**: Configurações
- **P**: Pausar projeto atual
- **Q**: Sair

### Tela de Relatórios

- **←→**: Mudar período (Hoje, Semana, Mês, etc.)
- **E**: Exportar relatório para CSV
- **ESC/Q**: Voltar à tela principal

### Tela de Configurações

- **↑↓**: Navegar entre projetos
- **A**: Adicionar novo projeto
- **E**: Editar projeto selecionado
- **D**: Deletar projeto selecionado
- **T**: Toggle status ativo/inativo do projeto
- **Tab**: Navegar entre campos (ao editar)
- **Enter**: Salvar (ao editar)
- **ESC/Q**: Voltar/Cancelar

## Estrutura de Arquivos

### Código-fonte
```
bateponto/
├── main.py                 # Ponto de entrada
├── core/                   # Lógica de negócio
│   ├── storage.py         # Persistência JSON
│   ├── project_manager.py # Gerenciamento de projetos
│   └── time_tracker.py    # Rastreamento de tempo
├── ui/                     # Interface do usuário
│   ├── main_screen.py     # Tela principal
│   ├── report_screen.py   # Relatórios
│   └── config_screen.py   # Configurações
└── utils/                  # Utilitários
    ├── idle_detector.py   # Detecção de inatividade
    └── export.py          # Exportação de relatórios
```

### Dados do usuário (criado automaticamente em ~/.bateponto/)
```
~/.bateponto/
├── projects.json          # Lista de projetos
├── time_entries.json      # Registros de tempo
└── exports/               # Relatórios exportados
```

## Configuração de Projetos

### Via Interface (Recomendado)

1. Pressione **C** na tela principal
2. Use os comandos:
   - **A**: Adicionar novo projeto
   - **E**: Editar projeto existente
   - **D**: Deletar projeto
   - **T**: Ativar/desativar projeto

3. Ao adicionar/editar:
   - Digite o nome do projeto
   - Use ←→ para escolher a cor
   - Use espaço para ativar/desativar
   - **Enter** para salvar

### Via Arquivo JSON (Alternativo)

Edite `~/.bateponto/projects.json` manualmente se preferir:

```json
{
  "projects": [
    {
      "id": "p1",
      "name": "Projeto A",
      "color": "green",
      "active": true
    }
  ]
}
```

**Localização dos dados**: Todos os dados são salvos em `~/.bateponto/` no seu diretório home.

### Cores disponíveis

- `green`, `blue`, `yellow`, `red`, `magenta`, `cyan`, `white`

## Formato dos Dados

### Registros de Tempo (`~/.bateponto/time_entries.json`)

```json
{
  "entries": [
    {
      "project_id": "p1",
      "event": "start",
      "timestamp": "2025-01-14T10:30:00",
      "auto_pause": false
    },
    {
      "project_id": "p1",
      "event": "stop",
      "timestamp": "2025-01-14T12:00:00",
      "auto_pause": false
    }
  ]
}
```

### Tipos de Eventos

- `start`: Início de trabalho em um projeto
- `stop`: Parada manual
- `auto_pause`: Pausa automática por inatividade

## Detecção de Inatividade

O sistema monitora atividade de teclado e mouse. Após 5 minutos de inatividade, o projeto ativo é pausado automaticamente.

Configure o tempo em `utils/idle_detector.py` alterando o parâmetro `idle_timeout_minutes`.

## Exportação de Relatórios

Os relatórios exportados são salvos em `~/.bateponto/exports/` no formato CSV com:

- Nome do projeto
- Horas totais (formato HH:MM)
- Horas decimais
- Período do relatório

## Solução de Problemas

### Problema: Mouse não funciona

Alguns terminais não suportam eventos de mouse com curses. Use as teclas como alternativa.

### Problema: Cores não aparecem

Verifique se seu terminal suporta cores. Recomendamos:
- macOS: Terminal.app ou iTerm2
- Linux: gnome-terminal, konsole
- Windows: Windows Terminal

### Problema: Erro ao importar pynput

Instale as dependências:

```bash
pip install -r requirements.txt
```

No macOS, pode ser necessário conceder permissões de acessibilidade em:
System Preferences → Security & Privacy → Privacy → Accessibility

## Licença

MIT License

## Autor

Desenvolvido com Claude Code
