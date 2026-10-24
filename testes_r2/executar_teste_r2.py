"""Verifica R2 sem executar o notebook completo nem alterar os CSVs de teste."""

import ast
from contextlib import redirect_stdout
import hashlib
from io import StringIO
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pandas as pd


RAIZ = Path(__file__).resolve().parent
DADOS = RAIZ / "dados_teste"
NOTEBOOK = RAIZ.parent / "Automação_Ecodata.ipynb"


def assinaturas():
    return {
        str(arquivo.relative_to(DADOS)): hashlib.sha256(arquivo.read_bytes()).hexdigest()
        for arquivo in sorted(DADOS.rglob("*.csv"))
    }


def carregar_funcoes():
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    espaco = {"Path": Path, "pd": pd}
    for indice, nome in ((16, "detalhar_ausentes"), (18, "validar_valores")):
        arvore = ast.parse("".join(notebook["cells"][indice]["source"]))
        funcao = next(
            nodo for nodo in arvore.body
            if isinstance(nodo, ast.FunctionDef) and nodo.name == nome
        )
        codigo = compile(ast.Module(body=[funcao], type_ignores=[]), str(NOTEBOOK), "exec")
        exec(codigo, espaco)
    return espaco


def executar(funcao, pasta=DADOS):
    saida = StringIO()
    with redirect_stdout(saida):
        funcao(pasta)
    return saida.getvalue()


def verificar(codigo, esperado, observado, passou):
    estado = "PASSOU" if passou else "FALHOU"
    print(f"{codigo} | {estado} | esperado: {esperado} | observado: {observado}")
    if not passou:
        raise AssertionError(f"{codigo}: {observado}")


def main():
    antes = assinaturas()
    verificar("Inventário", "6 CSVs fictícios", f"{len(antes)} CSVs", len(antes) == 6)
    funcoes = carregar_funcoes()

    ausentes = executar(funcoes["detalhar_ausentes"])
    valores = executar(funcoes["validar_valores"])
    resumo = "Arquivos lidos com sucesso: 3\nArquivos com erro de leitura: 3"
    verificar(
        "T1", "CSV válido processado nas duas rotinas",
        "3 leituras e ausência em 01_chuva_valida.csv",
        resumo in ausentes and resumo in valores
        and "Arquivo: 01_chuva_valida.csv" in ausentes,
    )
    verificar(
        "T2", "erro UTF-8 visível, identificado e com orientação",
        "UnicodeDecodeError em 02_chuva_corrompida.csv nas duas rotinas",
        all(
            "[ERRO DE DECODIFICAÇÃO]" in saida
            and "Arquivo: 02_chuva_corrompida.csv" in saida
            and "Categoria: Chuvas" in saida
            and str((DADOS / "Chuvas/02_chuva_corrompida.csv").resolve()) in saida
            and "ORIENTAÇÃO:" in saida
            and "Arquivos não analisados:" in saida
            for saida in (ausentes, valores)
        ),
    )
    verificar(
        "T3", "validação prossegue após o CSV ilegível",
        "03_chuva_valida_posterior.csv consta após o erro e tem -2 sinalizado",
        valores.index("Arquivo: 02_chuva_corrompida.csv")
        < valores.index("Arquivo: 03_chuva_valida_posterior.csv")
        and "-2" in valores,
    )
    verificar(
        "T4", "precipitação ausente identificada",
        "01_chuva_valida.csv: precipitacao_mm e registro C1",
        "Arquivo: 01_chuva_valida.csv" in ausentes
        and "precipitacao_mm" in ausentes
        and "C1" in ausentes,
    )
    verificar(
        "T5", "precipitação negativa sinalizada",
        "03_chuva_valida_posterior.csv: id C3 e valor -2",
        "Arquivo: 03_chuva_valida_posterior.csv" in valores
        and "C3" in valores and "-2" in valores,
    )
    with TemporaryDirectory(prefix="ecodata_r2_temperatura_") as temporario:
        pasta_temp = Path(temporario) / "base"
        destino = pasta_temp / "Temperatura"
        destino.mkdir(parents=True)
        shutil.copy2(DADOS / "Temperatura/01_temperatura_valida.csv", destino)
        saida_temp = executar(funcoes["validar_valores"], pasta_temp)
    verificar(
        "T6", "outra categoria continua legível",
        "Temperatura: 1 leitura e 0 falhas em execução isolada",
        "Arquivos lidos com sucesso: 1" in saida_temp
        and "Arquivos com erro de leitura: 0" in saida_temp
        and resumo in valores,
    )
    verificar(
        "Extra vazio", "EmptyDataError informado e continuidade",
        "04_chuva_vazia.csv na lista de não analisados",
        all(
            "Tipo: EmptyDataError" in saida
            and "04_chuva_vazia.csv" in saida
            for saida in (ausentes, valores)
        ),
    )
    verificar(
        "Extra malformado", "ParserError informado e continuidade",
        "05_chuva_malformada.csv na lista de não analisados",
        all(
            "Tipo: ParserError" in saida
            and "05_chuva_malformada.csv" in saida
            for saida in (ausentes, valores)
        ),
    )

    leitura_original = pd.read_csv

    def falha_de_acesso(arquivo, *args, **kwargs):
        if Path(arquivo).name == "02_chuva_corrompida.csv":
            raise OSError("falha de acesso simulada")
        return leitura_original(arquivo, *args, **kwargs)

    with patch.object(pd, "read_csv", side_effect=falha_de_acesso):
        saida_acesso = executar(funcoes["detalhar_ausentes"])
        saida_acesso_validacao = executar(funcoes["validar_valores"])
    verificar(
        "Extra acesso", "OSError informado e continuidade",
        "falha simulada em 02 nas duas rotinas; demais arquivos lidos",
        all(
            "Tipo: OSError" in saida
            and "falha de acesso simulada" in saida
            and resumo in saida
            for saida in (saida_acesso, saida_acesso_validacao)
        ),
    )

    depois = assinaturas()
    verificar(
        "T7", "hashes SHA-256 dos 6 CSVs inalterados",
        f"{sum(antes[nome] == depois.get(nome) for nome in antes)} de {len(antes)} iguais",
        antes == depois,
    )
    ausentes_2 = executar(funcoes["detalhar_ausentes"])
    valores_2 = executar(funcoes["validar_valores"])
    depois_2 = assinaturas()
    verificar(
        "T8", "segunda execução com resultados e hashes iguais",
        "relatórios idênticos; 6 hashes estáveis",
        ausentes_2 == ausentes and valores_2 == valores and depois_2 == antes,
    )
    print("Resumo observado: 3 CSVs legíveis e 3 erros de leitura por função.")


if __name__ == "__main__":
    main()
