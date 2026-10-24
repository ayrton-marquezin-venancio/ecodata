# Base fictícia para a correção R2

Esta base testa somente `detalhar_ausentes()` e `validar_valores()`. O script lê as definições dessas funções diretamente do notebook, sem executar as células ou usar `EcoData_Organizado` e `dados_recebidos` reais.

| Arquivo | Finalidade |
|---|---|
| `Chuvas/01_chuva_valida.csv` | CSV legível com precipitação ausente. |
| `Chuvas/02_chuva_corrompida.csv` | Bytes `0xFF` inválidos em UTF-8; reproduz `UnicodeDecodeError`. Nunca contém dados reais. |
| `Chuvas/03_chuva_valida_posterior.csv` | CSV legível após o corrompido, com `id_registro` e precipitação negativa. |
| `Chuvas/04_chuva_vazia.csv` | Arquivo vazio; reproduz `EmptyDataError`. |
| `Chuvas/05_chuva_malformada.csv` | Campo com aspas não fechadas; reproduz `ParserError`. |
| `Temperatura/01_temperatura_valida.csv` | CSV legível de outra categoria, com temperatura e umidade fictícias. |

Todos os arquivos são sintéticos. Os CSVs legíveis usam UTF-8-SIG. A pasta `dados_teste` é isolada dos dados de produção. O teste de `OSError` usa uma falha de leitura simulada em memória.

Execute na raiz do projeto:

```powershell
python testes_r2/executar_teste_r2.py
```

O script apresenta o resultado de T1–T8 e dos casos extras, verifica os hashes SHA-256 antes e depois de duas execuções e retorna código diferente de zero se alguma verificação falhar. Ele não corrige, move ou substitui documentos.

Se um CSV real falhar, confira primeiro o formato e a codificação do original. Descubra a codificação correta, prepare uma **cópia** em UTF-8-SIG e confira estrutura e registros. Reprocesse a cópia pelo fluxo seguro de ingestão R1; confirme a categoria e examine eventuais conflitos antes de decidir sobre o destino existente. Não realoque um arquivo somente por causa do erro de leitura.
