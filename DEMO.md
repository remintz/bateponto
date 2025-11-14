# Demonstração Visual - BatePonto

## Tela Principal

```
┌────────────────────────────────────────────────────────────────────────┐
│           BatePonto - Apontamento de Horas                             │
│                                                                         │
│                     14/11/2025  10:30:45                               │
│                  Projeto ativo: Projeto A                              │
│                   Tempo atual: 01:15:23                                │
│                                                                         │
│     ┌──────────────────────────┐    ┌──────────────────────────┐     │
│     │ [1] Projeto A            │    │ [4] Projeto D            │     │
│     │                          │    │                          │     │
│     │ ● ATIVO                  │    │ ○ Parado                 │     │
│     │ Hoje: 01:15              │    │ Hoje: 00:00              │     │
│     └──────────────────────────┘    └──────────────────────────┘     │
│                                                                         │
│     ┌──────────────────────────┐    ┌──────────────────────────┐     │
│     │ [2] Projeto B            │    │ [5] Projeto E            │     │
│     │                          │    │                          │     │
│     │ ○ Parado                 │    │ ○ Parado                 │     │
│     │ Hoje: 02:30              │    │ Hoje: 00:45              │     │
│     └──────────────────────────┘    └──────────────────────────┘     │
│                                                                         │
│     ┌──────────────────────────┐                                      │
│     │ [3] Projeto C            │                                      │
│     │                          │                                      │
│     │ ○ Parado                 │                                      │
│     │ Hoje: 01:00              │                                      │
│     └──────────────────────────┘                                      │
│                                                                         │
│  1-5: Projeto  |  ↑↓: Navegar  |  Enter/Space: Toggle  |              │
│  R: Relatórios  |  C: Config  |  Q: Sair                              │
└────────────────────────────────────────────────────────────────────────┘
```

## Comportamento: Apenas Um Projeto Ativo

### Cenário 1: Nenhum projeto ativo

```
Todos os projetos mostram: ○ Parado
```

### Cenário 2: Usuário pressiona "1" (ou clica em Projeto A)

```
Projeto A: ● ATIVO  ← Timer inicia
Projeto B: ○ Parado
Projeto C: ○ Parado
```

### Cenário 3: Usuário pressiona "2" enquanto Projeto A está ativo

```
Evento automático:
  1. Projeto A é PARADO (tempo registrado)
  2. Projeto B é INICIADO (novo timer)

Resultado:
Projeto A: ○ Parado  ← Tempo foi salvo
Projeto B: ● ATIVO   ← Agora este está ativo
Projeto C: ○ Parado
```

### Cenário 4: Usuário pressiona "2" novamente (mesmo projeto ativo)

```
Projeto B é PARADO (tempo registrado)

Resultado:
Projeto A: ○ Parado
Projeto B: ○ Parado  ← Timer parou
Projeto C: ○ Parado
```

## Tela de Relatórios

```
┌────────────────────────────────────────────────────────────────────────┐
│                     Relatórios de Horas                                │
│                                                                         │
│ Período:  [Hoje]  Esta Semana  Este Mês  Últimos 7  Últimos 30        │
│                                                                         │
│     ┌────────────────────────────────────┬────────────────┐           │
│     │ Projeto                            │ Horas Totais   │           │
│     ├────────────────────────────────────┼────────────────┤           │
│     │ Projeto B                          │ 02:30          │           │
│     │ Projeto A                          │ 01:15          │           │
│     │ Projeto C                          │ 01:00          │           │
│     │ Projeto E                          │ 00:45          │           │
│     │ Projeto D                          │ 00:00          │           │
│     ├────────────────────────────────────┼────────────────┤           │
│     │ TOTAL                              │ 05:30          │           │
│     └────────────────────────────────────┴────────────────┘           │
│                                                                         │
│     Distribuição de Horas:                                            │
│                                                                         │
│     Projeto B            ████████████████████ 2.5h                    │
│     Projeto A            ██████████ 1.3h                              │
│     Projeto C            ████████ 1.0h                                │
│     Projeto E            ██████ 0.8h                                  │
│                                                                         │
│  ←→: Mudar período  |  E: Exportar CSV  |  ESC/Q: Voltar              │
└────────────────────────────────────────────────────────────────────────┘
```

## Fluxo de Dados

```
┌─────────────────┐
│  Usuário clica  │
│  em Projeto A   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  TimeTracker.start_project()    │
│  1. Para projeto atual (se any) │  ← IMPORTANTE: Auto-stop
│  2. Inicia Projeto A            │
│  3. Salva evento "start"        │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Storage.add_entry()            │
│  Salva em time_entries.json:    │
│  {                              │
│    "project_id": "p1",          │
│    "event": "start",            │
│    "timestamp": "...",          │
│    "auto_pause": false          │
│  }                              │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  UI atualiza (a cada 100ms)     │
│  - Timer incrementa             │
│  - Projeto A mostra "● ATIVO"   │
│  - Outros mostram "○ Parado"    │
└─────────────────────────────────┘
```

## Detecção de Inatividade

```
┌──────────────────┐
│ Usuário ativo    │
│ (teclas/mouse)   │
└────────┬─────────┘
         │
         │ 5 minutos sem atividade
         ▼
┌──────────────────────────────┐
│ IdleDetector detecta         │
│ inatividade                  │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ TimeTracker.pause_project()  │
│ Salva evento "auto_pause"    │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Projeto parado               │
│ Tempo até pausa foi salvo    │
└──────────────────────────────┘
```

## Formato dos Arquivos JSON

### projects.json

```json
{
  "projects": [
    {
      "id": "p1",
      "name": "Projeto A",
      "color": "green",
      "active": true
    },
    {
      "id": "p2",
      "name": "Projeto B",
      "color": "blue",
      "active": true
    }
  ]
}
```

### time_entries.json (exemplo de sessão)

```json
{
  "entries": [
    {
      "project_id": "p1",
      "event": "start",
      "timestamp": "2025-11-14T10:00:00",
      "auto_pause": false
    },
    {
      "project_id": "p1",
      "event": "stop",
      "timestamp": "2025-11-14T11:30:00",
      "auto_pause": false
    },
    {
      "project_id": "p2",
      "event": "start",
      "timestamp": "2025-11-14T11:30:00",
      "auto_pause": false
    },
    {
      "project_id": "p2",
      "event": "auto_pause",
      "timestamp": "2025-11-14T12:35:00",
      "auto_pause": true
    }
  ]
}
```

**Interpretação:**
- 10:00-11:30: Trabalhou 1h30 no Projeto A
- 11:30-12:35: Trabalhou 1h05 no Projeto B
- 12:35: Sistema detectou inatividade e pausou automaticamente

## Exportação CSV

Arquivo exportado: `exports/bateponto_report_20251114_103045.csv`

```csv
BatePonto - Relatório de Horas
Período: 14/11/2025 - 14/11/2025

Projeto,Horas Totais,Horas Decimais
Projeto B,02:30,2.50
Projeto A,01:15,1.25
Projeto C,01:00,1.00
Projeto E,00:45,0.75
Projeto D,00:00,0.00

TOTAL,05:30,5.50
```

## Compilação para .app (macOS)

```bash
./build_macos.sh
```

Resultado:
```
dist/
└── BatePonto.app/
    ├── Contents/
    │   ├── MacOS/
    │   │   └── bateponto      ← Executável
    │   ├── Resources/
    │   │   └── icon.icns      ← Ícone
    │   └── Info.plist         ← Metadados
```

Duplo clique no ícone → Terminal abre → App inicia!
