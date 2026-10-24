# Base fictícia para a correção R3

Esta base verifica `validar_valores()` sem executar o notebook completo. O script extrai somente a definição da função atual e a executa contra `dados_teste/`; não aponta para `EcoData_Organizado`, `dados_recebidos` nem para arquivos ambientais reais.

| Arquivo | Finalidade |
|---|---|
| `Chuvas/00_chuva_corrompida_r2.csv` | Bytes inválidos em UTF-8 para confirmar que o tratamento R2 continua e a análise prossegue. |
| `Chuvas/01_chuva_com_id.csv` | Precipitação negativa com `id_registro`; compara a saída com a versão anterior a R3. |
| `Chuvas/02_chuva_sem_id.csv` | Duas precipitações negativas e um texto não numérico sem identificador. |
| `Chuvas/03_chuva_id_vazio.csv` | Medições negativas; o primeiro registro tem `id_registro` vazio. |
| `Chuvas/04_chuva_sem_id_valida.csv` | Sem `id_registro`, sem valores fora dos limites e com uma precipitação ausente. |
| `Temperatura/01_umidade_invalida_sem_id.csv` | Umidade abaixo de zero e acima de 100%, sem `id_registro`. |
| `Qualidade_do_Ar/01_poluicao_invalida_sem_id.csv` | Valores negativos em PM2,5 e PM10, sem `id_registro`. |

Todos os dados são fictícios; os arquivos legíveis usam UTF-8-SIG. O arquivo de R2 foi construído com um byte `0xFF` inválido em UTF-8. Não corrija nem regrave os arquivos de teste para executar o script.

Na raiz do projeto, execute:

```powershell
python testes_r3/executar_teste_r3.py
```

O script usa a revisão R2 atualmente registrada no Git para comparar a saída do caso com ID presente. Depois verifica os dez cenários, executa a validação duas vezes e compara os hashes SHA-256 dos arquivos de teste antes e depois. Código de saída diferente de zero indica falha.
