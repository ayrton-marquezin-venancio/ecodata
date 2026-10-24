"""Testes isolados de R3 e regressão de R2; não executa células do notebook."""

import ast
from contextlib import redirect_stdout
import hashlib
from io import StringIO
import json
from pathlib import Path
import subprocess
import tempfile
import shutil

import pandas as pd


RAIZ = Path(__file__).resolve().parent
DADOS = RAIZ / "dados_teste"
NOTEBOOK = RAIZ.parent / "Automação_Ecodata.ipynb"
COMMIT_ANTERIOR_R3 = "49eff6de76e8412895fea50417bc05b216777f39"


def assinaturas():
    return {
        str(arquivo.relative_to(DADOS)): hashlib.sha256(arquivo.read_bytes()).hexdigest()
        for arquivo in sorted(DADOS.rglob("*.csv"))
    }


def carregar_validacao(conteudo_notebook):
    notebook = json.loads(conteudo_notebook)
    arvore = ast.parse("".join(notebook["cells"][18]["source"]))
    funcao = next(
        nodo for nodo in arvore.body
        if isinstance(nodo, ast.FunctionDef) and nodo.name == "validar_valores"
    )
    espaco = {"Path": Path, "pd": pd}
    codigo = compile(
        ast.Module(body=[funcao], type_ignores=[]),
        str(NOTEBOOK),
        "exec",
    )
    exec(codigo, espaco)
    return espaco["validar_valores"]


def executar(funcao, pasta=DADOS):
    saida = StringIO()
    with redirect_stdout(saida):
        funcao(pasta)
    return saida.getvalue()


def verificar(codigo, objetivo, evidencia, passou):
    estado = "PASSOU" if passou else "FALHOU"
    print(f"{codigo} | {estado} | esperado: {objetivo} | observado: {evidencia}")
    if not passou:
        raise AssertionError(f"{codigo}: {evidencia}")


def main():
    antes = assinaturas()
    atual = carregar_validacao(NOTEBOOK.read_text(encoding="utf-8"))
    notebook_anterior = subprocess.check_output(
        ["git", "show", f"{COMMIT_ANTERIOR_R3}:Automação_Ecodata.ipynb"]
    )
    anterior = carregar_validacao(notebook_anterior.decode("utf-8"))

    # Com id_registro presente e preenchido, a saída anterior deve ser idêntica.
    with tempfile.TemporaryDirectory(prefix="ecodata_r3_baseline_") as temporario:
        pasta = Path(temporario) / "Chuvas"
        pasta.mkdir(parents=True)
        shutil.copy2(DADOS / "Chuvas/01_chuva_com_id.csv", pasta)
        saida_anterior = executar(anterior, Path(temporario))
        saida_atual_com_id = executar(atual, Path(temporario))
    verificar(
        "T1", "id e medição exibidos como antes; mesma contagem",
        "CH-02 e -3; relatório anterior e atual idênticos",
        saida_anterior == saida_atual_com_id
        and "CH-02" in saida_atual_com_id
        and "Valores problemáticos: 1" in saida_atual_com_id,
    )

    saida = executar(atual)
    resumo = "Arquivos lidos com sucesso: 6\nArquivos com erro de leitura: 1"

    trecho_sem_id = saida.split("Arquivo: 02_chuva_sem_id.csv", 1)[1].split(
        "Arquivo: 03_chuva_id_vazio.csv", 1
    )[0]
    verificar(
        "T2", "sem id: índice e valores inválidos sem KeyError",
        "Índice do DataFrame localiza -5 e -2.5; sem KeyError",
        "[AVISO] COLUNA IDENTIFICADORA AUSENTE" in trecho_sem_id
        and "Índice do DataFrame" in trecho_sem_id
        and "1" in trecho_sem_id and "-5" in trecho_sem_id
        and "2" in trecho_sem_id and "-2.5" in trecho_sem_id,
    )
    trecho_id_vazio = saida.split("Arquivo: 03_chuva_id_vazio.csv", 1)[1].split(
        "Arquivo: 04_chuva_sem_id_valida.csv", 1
    )[0]
    verificar(
        "T3", "id vazio sinalizado e ocorrência localizável por índice",
        "1 id indisponível; índices 0 e 1 exibidos com os valores",
        "[AVISO] IDENTIFICADOR INDISPONÍVEL" in trecho_id_vazio
        and "Identificadores indisponíveis: 1" in trecho_id_vazio
        and "Índice do DataFrame" in trecho_id_vazio
        and "0" in trecho_id_vazio and "-3" in trecho_id_vazio
        and "1" in trecho_id_vazio and "-4" in trecho_id_vazio,
    )
    verificar(
        "T4", "arquivo sem id e sem violações processado sem falso alerta",
        "arquivo incluído nas 6 leituras; nenhum bloco de violação para ele",
        resumo in saida and "Arquivo: 04_chuva_sem_id_valida.csv" not in saida,
    )
    verificar(
        "T5", "todas as medições problemáticas apresentadas",
        "3 ocorrências no CSV sem id: -5, -2.5 e indisponivel",
        "Valores problemáticos: 3" in trecho_sem_id
        and "indisponivel" in trecho_sem_id,
    )
    verificar(
        "T6", "texto não numérico continua sinalizado sem id",
        "indisponivel aparece no mesmo relatório sem id",
        "indisponivel" in trecho_sem_id and "Índice do DataFrame" in trecho_sem_id,
    )
    verificar(
        "T7", "NaN não é contado como violação de limite",
        "precipitação ausente em 04 não gera bloco de problemas",
        "Arquivo: 04_chuva_sem_id_valida.csv" not in saida,
    )
    verificar(
        "T8", "validação continua pelos arquivos seguintes e outras categorias",
        "registros de 03, Temperatura e Qualidade_do_Ar aparecem após 02",
        saida.index("Arquivo: 02_chuva_sem_id.csv")
        < saida.index("Arquivo: 03_chuva_id_vazio.csv")
        < saida.index("Arquivo: 01_umidade_invalida_sem_id.csv")
        < saida.index("Arquivo: 01_poluicao_invalida_sem_id.csv"),
    )
    verificar(
        "T9", "R2 continua capturando erro de decodificação e prosseguindo",
        "00 corrompido reportado; resumo 6 lidos/1 falha e medições posteriores impressas",
        "[ERRO DE DECODIFICAÇÃO]" in saida
        and "00_chuva_corrompida_r2.csv" in saida
        and resumo in saida and "CH-02" in saida,
    )

    depois = assinaturas()
    saida_repetida = executar(atual)
    depois_repetido = assinaturas()
    verificar(
        "T10", "nenhum arquivo de teste alterado",
        f"{len(antes)} hashes iguais após duas execuções",
        antes == depois == depois_repetido and saida == saida_repetida,
    )
    print("\nEvidência observada para T2:")
    print("Arquivo: 02_chuva_sem_id.csv")
    print(trecho_sem_id.rstrip())


if __name__ == "__main__":
    main()
