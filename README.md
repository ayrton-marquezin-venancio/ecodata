# EcoData — organização e qualidade de dados ambientais

Projeto em Python e Pandas que recebe arquivos ambientais CSV/XLSX, converte para CSV, organiza por tema e produz relatórios de duplicidade e qualidade. O fluxo é procedural e está documentado célula a célula no [notebook principal](Automacao_Ecodata_RV01_RV02_validado_20261024_96ae10bd047d.ipynb).

## Fluxo

```text
dados_recebidos/  →  conversão e classificação  →  EcoData_Organizado/
                                                     ├── Chuvas/
                                                     ├── Temperatura/
                                                     ├── Qualidade_do_Ar/
                                                     └── Pendencias/
                                      ↓
                         duplicatas e qualidade dos dados
                                      ↓
               EcoData_Duplicados_Arquivados/ (somente por ação explícita)
```

A classificação usa palavras no nome do arquivo. Nomes sem categoria reconhecida ou com pistas ambíguas seguem para `Pendencias`. A organização preserva os originais, detecta conflitos de nome e conteúdo e publica saídas com nomes alternativos sem sobrescrever arquivos existentes. Uma execução repetida reconhece conteúdos já processados e duplicatas anteriormente arquivadas quando há uma cópia ativa válida.

O notebook também identifica arquivos exatamente iguais por SHA-256, investiga valores ausentes e valida limites ambientais para precipitação, umidade relativa, PM2,5 e PM10. Essas análises informam inconsistências; não corrigem medições automaticamente.

## Como executar

Requisitos: Python 3, `pandas` e `openpyxl`. Para abrir o notebook, use JupyterLab ou o suporte a notebooks do VS Code.

```powershell
python -m pip install pandas openpyxl jupyterlab
mkdir dados_recebidos
jupyter lab "Automacao_Ecodata_RV01_RV02_validado_20261024_96ae10bd047d.ipynb"
```

Execute os comandos na raiz do repositório. Coloque os arquivos `.csv` ou `.xlsx` em `dados_recebidos/` e execute as células do notebook na ordem. O diretório de entrada precisa existir; as pastas de saída são criadas pela organização.

A chamada de tratamento de duplicatas no notebook usa `executar=False`: ela **simula** o arquivamento. Para mover cópias redundantes para `EcoData_Duplicados_Arquivados/`, é preciso chamar explicitamente `remover_arquivos_duplicados(pasta_destino, executar=True)` após conferir o relatório. Os arquivos recebidos permanecem na origem.

### Organização automática enquanto o monitor está ativo

O [monitor de ingestão](monitorar_ingestao.py) observa `dados_recebidos/` e executa apenas a organização quando os arquivos se estabilizam. Ele carrega as definições do notebook principal, sem executar suas células de análise.

```powershell
python -u monitorar_ingestao.py
```

Mantenha o processo aberto enquanto quiser detectar novas entradas; encerre com `Ctrl+C`. O monitor **não arquiva duplicatas automaticamente**. Para transferências grandes, conclua a cópia com extensão `.tmp` e depois renomeie para `.csv` ou `.xlsx`.

## Estrutura publicada

| Arquivo | Papel |
|---|---|
| `Automacao_Ecodata_RV01_RV02_validado_20261024_96ae10bd047d.ipynb` | Fluxo completo, explicações e relatórios históricos de execução. |
| `monitorar_ingestao.py` | Organização automática enquanto o processo estiver ativo. |
| `.gitignore` | Exclui dados recebidos, saídas, arquivos arquivados e cópias locais. |
| `AGENTS.md` | Regras de preservação e versionamento usadas no desenvolvimento. |

Os diretórios de dados não são publicados no GitHub. Depois de clonar, crie `dados_recebidos/` e forneça seus próprios arquivos. As revisões do notebook podem ser consultadas pelo histórico Git; a pasta local `Versões Git/` contém cópias de consulta e não integra a versão publicada.

## Resultado observado e limites

No inventário local de **24/10/2026**, havia **48 arquivos recebidos**, **38 CSVs ativos** e **10 cópias arquivadas**. A última verificação salva no notebook encontrou **0 duplicatas exatas entre os 38 ativos**. Essas contagens representam aquele estado dos dados e podem mudar após novas entradas ou arquivamentos.

A classificação depende do nome do arquivo; `Pendencias` exige revisão humana. A conversão XLSX usa a primeira planilha. CSVs devem ser legíveis em UTF-8-SIG. O monitor funciona somente enquanto seu processo está em execução. Os relatórios de qualidade e as saídas salvas no notebook registram observações, não uma garantia de que todos os dados estejam corretos.
