import re
import os
import shutil
import datetime
import zipfile
import logging

from enum import Enum
from pathlib import Path

from PyPDF2 import PdfReader

from job import Job


# log
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


ts = datetime.datetime.now()
AGORA = f"{ts.day:02d}-{ts.month:02d}-{ts.year} {ts.hour:02d}_{ts.minute:02d}_{ts.second:02d}"

# Itens a expedir
SEM_PERFIL = "Sem"
FIM_PERFIL = "Fechamento:"
INICIO_LISTA = 'Itens para Expedir:'
FIM_LISTA = 'Observações:'
ITEM_LAYOUT = "Print Layout"
ITEM_DIGITAL = "Prova Digital"
ITEM_SUB_EPSON = "Prova Substrato - EPSON"
ITEM_SUB_ROLAND = "Prova Substrato - ROLAND"
ITEM_HEAFORD = "Prova de Máquina"
ITEM_AMOSTRA = "Amostra"

# Número de OS
RE_OS_PEDIDO_VERSAO = r"(?P<os>\d{4,}).+[vV](?P<versao>\d+)"


class Tipo(Enum):
    LAYOUT = "Print Layout"
    DIGITAL = "Print Digital"


def carrega_trabalhos(local: Path) -> list[Job]:
    """
    Lê o diretório especificado em busca de arquivos .PDF e tenta
    extrair as informações do trabalho a partir do arquivo.
    Retorna uma lista de Jobs.
    """
    for arquivo in local.iterdir():
        if arquivo.suffix.lower() == ".pdf":
            pdf = PdfReader(arquivo)
            pg = pdf.pages[0]
            linhas = pg.extract_text().splitlines()

            # Os, Pedido, Versão, Cliente
            num_os, pedido, versao, cliente = (
                int(linhas[10].split()[0]),
                int(linhas[10].split()[2]),
                int(linhas[10].split()[1]),
                " ".join(linhas[10].split()[3:])
            )

            # Nome
            nome = linhas[11]

            # Perfil
            perfil = None
            if not linhas[13].startswith(SEM_PERFIL):
                perfil = linhas[13].strip(FIM_PERFIL)

            # Materiais para expedir
            layout = False
            digital = False
            substrato = False
            amostra = False
            try:
                idx_a = linhas.index(INICIO_LISTA) + 2
                try:
                    idx_b = linhas.index(FIM_LISTA)
                except ValueError:
                    idx_b = -1
            except ValueError:
                continue
            itens_expedicao = linhas[idx_a:idx_b]
            for item in itens_expedicao:
                if item.startswith(ITEM_LAYOUT):
                    layout = True
                elif item.startswith(ITEM_DIGITAL):
                    digital = True
                elif item.startswith(ITEM_SUB_EPSON):
                    substrato = True
                elif item.startswith(ITEM_SUB_ROLAND):
                    substrato = True
                elif item.startswith(ITEM_HEAFORD):
                    substrato = True
                elif item.startswith(ITEM_AMOSTRA):
                    amostra = True

            yield Job(
                num_os=num_os,
                versao=versao,
                pedido=pedido,
                cliente=cliente,
                nome=nome,
                perfil=perfil,
                layout=layout,
                digital=digital,
                substrato=substrato,
                amostra=amostra
            )


def carrega_trabalhos_lista(local: Path) -> list[list]:
    """
    Lê o diretório especificado em busca de arquivos .PDF e tenta
    extrair as informações do trabalho a partir do arquivo.
    Retorna uma lista de Jobs.
    """
    trabalhos = []
    for arquivo in local.iterdir():
        if arquivo.suffix.lower() == ".pdf":
            pdf = PdfReader(arquivo)
            pg = pdf.pages[0]
            linhas = pg.extract_text().splitlines()

            # Os, Pedido, Versão, Cliente
            num_os, pedido, versao, cliente = (
                int(linhas[10].split()[0]),
                int(linhas[10].split()[2]),
                int(linhas[10].split()[1]),
                " ".join(linhas[10].split()[3:])
            )

            # Nome
            nome = linhas[11]

            # Perfil
            perfil = None
            if not linhas[13].startswith(SEM_PERFIL):
                perfil = linhas[13].strip(FIM_PERFIL)

            # Materiais para expedir
            layout = False
            digital = False
            substrato = False
            amostra = False
            try:
                idx_a = linhas.index(INICIO_LISTA) + 2
                try:
                    idx_b = linhas.index(FIM_LISTA)
                except ValueError:
                    idx_b = -1
            except ValueError:
                continue
            itens_expedicao = linhas[idx_a:idx_b]
            for item in itens_expedicao:
                if item.startswith(ITEM_LAYOUT):
                    layout = True
                elif item.startswith(ITEM_DIGITAL):
                    digital = True
                elif item.startswith(ITEM_SUB_EPSON):
                    substrato = True
                elif item.startswith(ITEM_SUB_ROLAND):
                    substrato = True
                elif item.startswith(ITEM_HEAFORD):
                    substrato = True
                elif item.startswith(ITEM_AMOSTRA):
                    amostra = True

            trabalhos.append([num_os, pedido, versao, layout, digital, amostra, substrato, cliente, nome, perfil,  [],  []])
    return trabalhos

def adivinha_numero_os(nome_arquivo: str) -> tuple[int, int]:
    """Tenta encontrar o número da OS, pedido e versão no nome do arquivo."""
    padrao = re.compile(RE_OS_PEDIDO_VERSAO)
    resultado = re.findall(padrao, nome_arquivo)
    if resultado:
        num_os, versao = int(resultado[0][0]), int(resultado[0][1])
        return num_os, versao


def descompacta(_arquivo: Path, _novo_arquivo: Path) -> None:
    try:
        with zipfile.ZipFile(_arquivo, mode="r") as arquivo_zip:
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
    except zipfile.BadZipFile as erro:
        print(f"Não foi possível abrir o arquivo {_arquivo.name}.")
        print(erro)


def busca_arquivos(
        job: Job,
        entrada: Path,
        saida: Path,
        tipo: Tipo,
        sufixo: str = ""
    ) -> list:
    """Tenta localizar arquivos relativos ao Job no local especificado, depois
    tenta baixar os respectivos arquivos do FTP."""
    onde_buscar = entrada.joinpath(tipo.value)
    lista_arquivos_baixados = []
    lista_arquivos_a_baixar = [
        arquivo for arquivo in onde_buscar.iterdir() if
        (job.num_os, job.versao) == adivinha_numero_os(arquivo.name)
    ]

    if lista_arquivos_a_baixar:
        dir_saida_arquivos = saida / tipo.value
        if not dir_saida_arquivos.exists():
            os.mkdir(dir_saida_arquivos)

        dir_baixados = entrada / "Baixados"
        if not dir_baixados.exists():
            os.mkdir(dir_baixados)

        for arquivo in lista_arquivos_a_baixar:

            novo_arquivo = dir_saida_arquivos / arquivo.name
            lista_arquivos_baixados.append(novo_arquivo)

            if not arquivo.suffix.lower() == ".zip":
                shutil.copy(arquivo, novo_arquivo)
            else:
                descompacta(arquivo, novo_arquivo)

            arquivo_baixado = dir_baixados / arquivo.name

            if not arquivo_baixado.exists():
                shutil.copy(arquivo, arquivo_baixado)
                # os.remove(arquivo)
            else:
                _novo_arquivo_baixado = dir_baixados / str(arquivo.stem + "_" + AGORA + arquivo.suffix)
                shutil.copy(arquivo, _novo_arquivo_baixado)
                # os.remove(arquivo)
    return lista_arquivos_baixados


if __name__ == "__main__":
    ENTRADA = Path(r"C:\Users\Everton Souza\OneDrive\dev\python\analise_midia\v2\busca_trabalhos\Entrada")
    SAIDA = Path(r"C:\Users\Everton Souza\OneDrive\dev\python\analise_midia\v2\busca_trabalhos\Saida")
    job_t = Job(
        num_os=755129,
        pedido=5,
        versao=3,
        cliente="Teste",
        nome="Trabalho teste",
        perfil="ISO",
        layout=True,
        digital=True,
        substrato=False,
        amostra=False
    )
    # print((job_t.num_os, job_t.versao) == adivinha_numero_os(Path(r"C:\Users\Everton Souza\OneDrive\dev\python\analise_midia\v2\busca_trabalhos\Entrada\Print Layout\OS_755129_5_V3.pdf").name))
    arquivos = busca_arquivos(job=job_t, entrada=ENTRADA, saida=SAIDA, tipo=Tipo.LAYOUT)
    print(arquivos)
