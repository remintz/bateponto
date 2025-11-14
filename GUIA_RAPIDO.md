# Guia Rápido - BatePonto

## Início Rápido

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Executar o programa

```bash
python3 main.py
```

## Como Usar

### Registrar Horas

1. Na tela principal, você verá até 5 projetos
2. Para **iniciar** um projeto, você pode:
   - Pressionar a tecla **1-5** correspondente ao projeto
   - Clicar no painel do projeto com o mouse
   - Usar as setas ↑↓ para navegar e pressionar Enter

3. **Importante**: Apenas **um projeto** pode estar ativo por vez
   - Ao iniciar um novo projeto, o anterior é automaticamente parado
   - O projeto ativo aparece destacado em verde com "● ATIVO"

4. Para **parar** o projeto atual:
   - Clique novamente no projeto ativo, ou
   - Pressione a tecla correspondente (1-5), ou
   - Pressione **P** para pausar

### Ajustar Horas

1. Pressione **A** na tela principal para abrir a tela de ajustes
2. Use **↑↓** para selecionar o projeto
3. Pressione **M** para inserir os minutos (positivo ou negativo):
   - Valores positivos: horas extras, tempo adicional
   - Valores negativos: descontos, correções
4. Pressione **D** para adicionar descrição (opcional)
5. Pressione **S** para salvar o ajuste
6. Pressione **ESC** para voltar

**Exemplos:**
- Adicionar 30 minutos de horas extras: `+30`
- Descontar 15 minutos de pausa: `-15`

### Visualizar Relatórios

1. Pressione **R** na tela principal
2. Use **←→** para mudar o período:
   - Hoje
   - Esta Semana
   - Este Mês
   - Últimos 7 dias
   - Últimos 30 dias
3. Pressione **E** para exportar para CSV
4. Pressione **ESC** ou **Q** para voltar

### Configurar Projetos

1. Pressione **C** na tela principal
2. Use as teclas para gerenciar projetos:
   - **A**: Adicionar novo projeto
   - **E**: Editar projeto selecionado
   - **D**: Deletar projeto
   - **T**: Ativar/desativar projeto

3. Ao adicionar/editar:
   - Digite o nome
   - Use **←→** ou **espaço** para mudar a cor
   - Use **espaço** para ativar/desativar
   - **Tab** para próximo campo
   - **Enter** para salvar

## Compilar para macOS

### Criar executável .app

```bash
./build_macos.sh
```

O arquivo `BatePonto.app` será criado em `dist/`

### Instalar

```bash
# Copiar para Applications
cp -r dist/BatePonto.app /Applications/

# Ou criar atalho no Desktop
ln -s $(pwd)/dist/BatePonto.app ~/Desktop/BatePonto.app
```

## Recursos Principais

- ✅ **Apenas um projeto ativo por vez** - automático
- ✅ **Timer em tempo real** - atualizado a cada segundo
- ✅ **Pausas automáticas inteligentes** - após 5 minutos de inatividade
  - Pausa registrada automaticamente
  - Retomada automática ao voltar à atividade
  - Tempo de pausa descontado do total
- ✅ **Ajustes de tempo** - adicione horas extras ou descontos manualmente
- ✅ **Persistência automática** - todos os eventos são salvos instantaneamente
- ✅ **Múltiplas formas de interação** - mouse, teclado, atalhos
- ✅ **CRUD completo** - adicione, edite e delete projetos pela interface
- ✅ **Interface compacta** - ocupa mínimo espaço vertical no desktop
- ✅ **Exportação CSV** - para análise externa
- ✅ **Interface colorida** - projetos com cores customizáveis

## Atalhos de Teclado

### Tela Principal
- **1-5**: Toggle projeto (iniciar/parar)
- **↑↓**: Navegar entre projetos
- **Enter/Space**: Toggle projeto selecionado
- **P**: Pausar projeto atual
- **R**: Abrir relatórios
- **A**: Ajustes de tempo
- **C**: Configurações
- **Q**: Sair

### Tela de Relatórios
- **←→**: Mudar período
- **E**: Exportar CSV
- **ESC/Q**: Voltar

### Tela de Ajustes
- **↑↓**: Selecionar projeto
- **M**: Inserir minutos
- **D**: Adicionar descrição
- **S**: Salvar ajuste
- **ESC**: Voltar

### Tela de Configurações
- **↑↓**: Navegar
- **A**: Adicionar projeto
- **E**: Editar projeto
- **D**: Deletar projeto
- **T**: Toggle ativo/inativo
- **Tab**: Próximo campo (ao editar)
- **Enter**: Salvar
- **ESC/Q**: Voltar/Cancelar

## Onde os Dados São Salvos

- **Projetos**: `~/.bateponto/projects.json`
- **Registros de tempo**: `~/.bateponto/time_entries.json`
- **Relatórios exportados**: `~/.bateponto/exports/`

Todos os dados ficam no seu diretório home (pasta oculta `.bateponto`).

## Solução de Problemas

### Problema: Mouse não funciona
- Use as teclas numéricas (1-5) ou navegação por setas

### Problema: Erro ao importar pynput
```bash
pip install pynput
```

No macOS, conceda permissões em:
**System Preferences → Security & Privacy → Privacy → Accessibility**

### Problema: Terminal muito pequeno
- Redimensione o terminal para pelo menos 80x24 caracteres

## Dicas

1. **Deixe o programa aberto** durante o trabalho para tracking automático
2. **Pausas automáticas inteligentes**:
   - Após 5 minutos de inatividade, o projeto é pausado automaticamente
   - Ao voltar à atividade (mover mouse, digitar), o projeto retoma automaticamente
   - O tempo de pausa é registrado e descontado do total
3. **Backup**: Os arquivos em `~/.bateponto/` contêm todo seu histórico
4. **Cores**: Escolha cores distintas para cada projeto para identificação rápida
