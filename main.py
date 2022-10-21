"""main.py"""
import sys
import os

from shutil import copy
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile, BadZipFile

from configuracoes import carrega_config
from trabalhos import Trabalho


HOJE = datetime.today().strftime("%d-%m-%Y")
AGORA = datetime.now().strftime("%H-%M-%S")

ARGUMENTOS = sys.argv[1:]

RE_NUM_OS = r"(\d{4,}).*[vV](\d+)"

def descompacta(_arquivo: Path, _novo_arquivo: Path) -> None:
    try:
        with ZipFile(_arquivo, mode="r") as arquivo_zip:
            _lista_arquivos = arquivo_zip.infolist()
            idx = 1
            for item in _lista_arquivos:
                # Ignora item se for diretório.
                if item.is_dir():
                    continue

                # Extrai apenas o nome de arquivo, ignorando subpastas.
                item.filename = item.filename.split("/")[-1]

                # Ignora itens na lista de ignorar.
                if item.filename in ["Thumbs.db"]:
                    continue

                # Ignora itens ocultos (que começam com ".").
                if item.filename.startswith("."):
                    continue

                if len(_lista_arquivos) > 1:
                    item.filename = (
                        _novo_arquivo.stem
                        + "_"
                        + str(idx)
                        + "."
                        + item.filename.split(".")[-1]
                    )
                    idx += 1
                else:
                    item.filename = (
                        _novo_arquivo.stem + "." + item.filename.split(".")[-1]
                    )

                arquivo_zip.extract(item, path=_novo_arquivo.parent)
    except BadZipFile as erro:
        print(f"Não foi possível abrir o arquivo {_arquivo.name}.")
        print(erro)


def busca_arquivos(
    job: Trabalho, entrada: Path, dir_saida: Path, tipo: str, sufixo: str = ""
) -> None:
    """Tenta localizar arquivos relativos ao Job no local especificado, depois
    tenta baixar os respectivos arquivos do FTP."""

    _arquivos = [
        Path(entrada, a)
        for a in os.listdir(entrada)
        if (adivinha_num_os(a) == (job.num_os, job.versao))
        and Path(entrada, a).is_file()
    ]
    if _arquivos:

        _saida_arquivos = dir_saida.joinpath(tipo)
        if not _saida_arquivos.exists():
            os.mkdir(_saida_arquivos)

        _baixados = entrada.joinpath("Baixados")
        if not _baixados.exists():
            os.mkdir(_baixados)

        for _arquivo in _arquivos:

            _novo_arquivo = _saida_arquivos.joinpath(
                "".join([str(job), "_", tipo, sufixo, _arquivo.suffix])
            )

            if not _arquivo.suffix.lower() == ".zip":
                copy(_arquivo, _novo_arquivo)
            else:
                descompacta(_arquivo, _novo_arquivo)

            _arquivo_baixado = _baixados.joinpath(_arquivo.name)

            if not _arquivo_baixado.exists():
                copy(_arquivo, _arquivo_baixado)
                os.remove(_arquivo)
            else:
                _novo_arquivo_baixado = _baixados.joinpath(
                    _arquivo.stem + "_" + AGORA + _arquivo.suffix
                )
                copy(_arquivo, _novo_arquivo_baixado)
                os.remove(_arquivo)

    else:
        print(f"Não foi possível localizar arquivos de {tipo} para {job}.")
        continua = input("Pressione qualquer tecla para continuar...\n> ")


def main() -> None:
    """Início do programa."""

    # Carrega arquivo de configurações.
    config = carrega_config()

    # Diretórios do programa.
    dir_saida = Path(config["diretorios"]["dir_saida"])
    dir_layouts = Path(config["diretorios"]["dir_pt_layout"]).joinpath(HOJE)
    dir_digitais = Path(config["diretorios"]["dir_pt_digital"]).joinpath(HOJE)

    # Cria a lista de trabalhos a serem feitos.
    jobs = [Trabalho(Path(pdf)) for pdf in ARGUMENTOS if Path(pdf).suffix == ".pdf"]

    if not jobs:
        input("Sem trabalhos no momento. Pressione 'Enter' para sair: ")
        sys.exit()

    for job in jobs:
        print(f"Processando {job}...")
        if job.precisa_layout:
            busca_arquivos(job, dir_layouts, dir_saida, "Layout")
        if job.precisa_digital:
            busca_arquivos(job, dir_digitais, dir_saida, "Prova Digital", sufixo=job.perfil)


if __name__ == "__main__":
    main()
