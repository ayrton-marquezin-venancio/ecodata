"""Organiza CSV/XLSX novos enquanto este processo estiver em execução.

Execute na raiz do projeto: python -u monitorar_ingestao.py
Interrompa com Ctrl+C. O monitor aguarda dois estados consecutivos iguais
da origem antes de organizar. Para transferências grandes, grave primeiro
com extensão .tmp e renomeie para .csv/.xlsx quando a cópia terminar.
As funções são lidas do notebook; nenhuma célula de execução é acionada.
"""

import ast
import hashlib
import json
from pathlib import Path
import time

import pandas as pd


def carregar_organizador(pasta_projeto):
    notebook = pasta_projeto / "Automacao_Ecodata_RV01_RV02_validado_20261024_96ae10bd047d.ipynb"
    conteudo = json.loads(notebook.read_text(encoding="utf-8"))
    nomes = {
        "listar_arquivos", "identificar_categoria",
        "converter_para_csv", "organizar_arquivos"
    }
    funcoes = []
    for celula in conteudo["cells"]:
        if celula["cell_type"] == "code":
            arvore = ast.parse("".join(celula["source"]))
            funcoes.extend(
                no for no in arvore.body
                if isinstance(no, ast.FunctionDef) and no.name in nomes
            )
    if len(funcoes) != len(nomes) or {no.name for no in funcoes} != nomes:
        raise ValueError("As quatro funções de ingestão devem existir uma única vez.")
    contexto = {"Path": Path, "pd": pd, "hashlib": hashlib}
    codigo = ast.Module(body=funcoes, type_ignores=[])
    exec(compile(codigo, str(notebook), "exec"), contexto)
    return contexto["organizar_arquivos"]


def estado_origem(pasta_origem):
    arquivos = []
    for arquivo in sorted(pasta_origem.iterdir()):
        if arquivo.is_file() and arquivo.suffix.lower() in (".csv", ".xlsx"):
            estado = arquivo.stat()
            arquivos.append((arquivo.name, estado.st_size, estado.st_mtime_ns))
    return tuple(arquivos)


def monitorar(pasta_projeto):
    origem = pasta_projeto / "dados_recebidos"
    destino = pasta_projeto / "EcoData_Organizado"
    if not origem.is_dir():
        raise FileNotFoundError(f"Pasta de origem não encontrada: {origem}")
    anterior = estado_origem(origem)
    processado = None
    print(f"MONITOR ATIVO: {origem}", flush=True)
    print("Verificação a cada segundo. Ctrl+C encerra o monitor.", flush=True)
    while True:
        time.sleep(1)
        try:
            atual = estado_origem(origem)
            if atual == anterior and atual != processado:
                organizar = carregar_organizador(pasta_projeto)
                print("\nALTERAÇÃO DETECTADA: iniciando organização.", flush=True)
                organizar(origem, destino)
                processado = atual
                print("MONITOR: aguardando novas alterações.", flush=True)
            anterior = atual
        except (OSError, ValueError, KeyError, SyntaxError) as erro:
            print(f"ERRO DO MONITOR: {type(erro).__name__}: {erro}", flush=True)


if __name__ == "__main__":
    try:
        monitorar(Path(__file__).resolve().parent)
    except KeyboardInterrupt:
        print("\nMonitor encerrado.", flush=True)
