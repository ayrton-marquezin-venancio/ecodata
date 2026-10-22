# Regras de trabalho do EcoData

## Antes de modificar
- Confirme o caminho absoluto da raiz do projeto e use esta pasta como raiz Git.
- Execute `git status --short --branch` e identifique o último commit com `git log -1 --oneline --decorate`.
- Registre o SHA-256 do notebook salvo em disco e verifique se existem alterações não registradas.
- Se houver alterações inesperadas ou uma divergência entre o arquivo em disco e a versão aberta no editor, interrompa e informe; não sobrescreva o trabalho existente.
- Registre no plano qual arquivo ou função recebeu autorização explícita para mudança.

## Durante a implementação
- Altere somente os componentes autorizados.
- Preserve as células Markdown, as funções não relacionadas, as saídas históricas e os metadados do notebook.
- Não modifique arquivos originais em `dados_recebidos` nem execute operações destrutivas sobre dados reais.
- Não use `git reset --hard`, limpeza destrutiva, restauração automática ou mudanças de configuração Git para contornar verificações.

## Depois da implementação
- Reabra e leia o notebook diretamente do disco; confirme que o código esperado foi persistido.
- Compare o notebook por célula, distinguindo código, Markdown, saídas, contadores de execução, IDs e metadados. Não normalize ou apague saídas automaticamente.
- Valide o JSON do Jupyter e a sintaxe Python sem executar indiscriminadamente o notebook.
- Execute os testes pertinentes em diretórios temporários com cópias isoladas dos dados; nunca rode operações destrutivas contra as pastas reais.
- Revise `git diff` e confirme que não há mudanças fora do escopo autorizado.
- Compare o SHA-256 antes e depois para detectar gravações inesperadas, inclusive de uma versão antiga pelo editor. Se o arquivo mudar inesperadamente, interrompa a publicação da correção e informe a divergência.

## Registro de versões
- Uma alteração lógica explicitamente autorizada e validada corresponde a um commit local descritivo.
- Adicione somente os arquivos relacionados à alteração; nunca use `git add .` ou `git add -A` sem autorização explícita.
- Inspecione os arquivos staged e o diff staged antes de cada commit.
- Não crie commits que afirmem aprovação quando testes falharem ou não tiverem sido executados.
- Depois do commit, registre o hash completo e confirme que o conteúdo no disco corresponde ao commit e informe o estado de `git status`.
- Não inclua outras mudanças apenas para limpar a árvore de trabalho.

## Recuperação
- O Git serve para comparar e localizar versões. Restaurar ou reverter arquivos exige autorização explícita; nunca restaure automaticamente um backup ou commit sobre trabalho atual.
- Para notebook, compare o conteúdo real das células, incluindo código e Markdown, em vez de confiar somente no diff bruto do JSON.
