"""main.py"""
import sys
import re
import shutil
import datetime as dt

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, BadZipFile

from configuracoes import console, carrega_config
from trabalhos import Trabalho
from itens_expedir import ItensExpedir


# Padrão para capturar o número de OS e a Versão em strings usando RE.
RE_NUM_OS = r"(?P<os>\d{4,}).+[vV](?P<versao>\d+)"

# Timestamp
ts = dt.datetime.now()
# Data: DIA_MES_ANO
HOJE = f"{ts:%d-%m-%Y}"
# Hota: HORA_MIN_SEG
AGORA = f"{ts:%H_%M_%S}"


def descompacta(_arquivo: Path) -> list[tuple[str, BytesIO]]:
    """Extrai o conteúdo de um arquivo .zip e retorna uma lista de tuples
    contendo (nome do arquivo: str, bytes do arquivo: BytesIO)."""
    conteudo = []
    try:
        with ZipFile(_arquivo, mode="r") as arquivo_zip:
            _lista_arquivos = arquivo_zip.infolist()
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
                conteudo.append((item.filename, BytesIO(arquivo_zip.read(item))))
    except BadZipFile as exc:
        raise BadZipFile from exc
    return conteudo


def adivinha_num_os(nome_arquivo: str) -> tuple[int, int]:
    padrao = re.compile(RE_NUM_OS)
    resultado = re.findall(padrao, nome_arquivo)
    if resultado:
        try:
            num_os, versao = int(resultado[0][0]), int(resultado[0][1])
            return (num_os, versao)
        except ValueError:
            return (0, 0)


def busca_arquivos(
    trabalho: Trabalho,
    dir_entrada: Path,
    dir_saida: Path,
    tipo_arquivo: ItensExpedir,
    sufixo: str = "",
) -> ItensExpedir:
    """Tenta localizar arquivos relativos ao Trabalho no local especificado,
    depois tenta copiar os respectivos arquivos para o diretório de saida.
    Retorna ItensExpedir caso não seja possível localizar arquivos."""
    # Se o diretório de entrada não existir, retorna tipo de arquivo não encontrado
    if not dir_entrada.exists():
        return tipo_arquivo
    # Lista com os arquivos presentes no diretório de entrada com o mesmo
    # número de OS e Versão do Trabalho.
    arquivos_encontrados = [
        arquivo
        for arquivo in dir_entrada.iterdir()
        if adivinha_num_os(arquivo.name) == (trabalho.num_os, trabalho.versao)
    ]

    # Se não houver nenhum arquivo encontrado, retorna tipo de arquivo não encontrado.
    if not arquivos_encontrados:
        return tipo_arquivo

    # Verifica se os diretórios de Saida e Baixados já existem ou cria os
    # diretórios caso não existam.
    dir_saida = dir_saida.joinpath(tipo_arquivo.value)
    dir_saida.mkdir(exist_ok=True)
    dir_baixados = dir_entrada.joinpath("Baixados")
    dir_baixados.mkdir(exist_ok=True)

    # Processa a lista de arquivos encontrados no diretório de entrada.
    for idx, arquivo in enumerate(arquivos_encontrados):
        # Adiciona _ (underline) à frente do sufixo.
        if sufixo:
            sufixo = "_" + sufixo

        # Caso seja arquivo .zip
        if arquivo.suffix.lower() == ".zip":
            try:
                conteudo_zip = descompacta(arquivo)
                for idx, item in enumerate(conteudo_zip):
                    nome_arquivo, bytes_arquivo = item
                    extensao = "." + nome_arquivo.split(".")[-1]
                    arquivo_saida = (
                        f"{trabalho.num_os}_p"
                        f"{trabalho.pedido}_v"
                        f"{trabalho.versao}_"
                        f"{tipo_arquivo.value}"
                        f"{sufixo}"
                        f"{'_'+ str(idx) if idx >= 1 else ''}"
                        f"{extensao}"
                    )
                    if dir_saida.joinpath(arquivo_saida).exists():
                        # Acrescenta AGORA depois do sufixo caso
                        # o arquivo de saída já exista.
                        arquivo_saida = (
                            f"{trabalho.num_os}_p"
                            f"{trabalho.pedido}_v"
                            f"{trabalho.versao}_"
                            f"{tipo_arquivo.value}"
                            f"{sufixo}"
                            f"{'_'+ str(idx) if idx >= 1 else ''}"
                            f"_{AGORA}"
                            f"{extensao}"
                        )
                    with open(
                        dir_saida.joinpath(arquivo_saida), mode="wb"
                    ) as arquivo_descompactado:
                        arquivo_descompactado.write(bytes_arquivo.read())
            except BadZipFile:
                return tipo_arquivo
        # Caso não seja arquivo .zip
        else:
            # Copia para o diretório de saida.
            arquivo_saida = (
                f"{trabalho.num_os}_p"
                f"{trabalho.pedido}_v"
                f"{trabalho.versao}_"
                f"{tipo_arquivo.value}"
                f"{sufixo}"
                f"{'_'+ str(idx) if idx >= 1 else ''}"
                f"{arquivo.suffix}"
            )
            if dir_saida.joinpath(arquivo_saida).exists():
                # Acrescenta AGORA depois do sufixo caso
                # o arquivo de saída já exista.
                arquivo_saida = (
                    f"{trabalho.num_os}_p"
                    f"{trabalho.pedido}_v"
                    f"{trabalho.versao}_"
                    f"{tipo_arquivo.value}"
                    f"{sufixo}"
                    f"{'_'+ str(idx) if idx >= 1 else ''}"
                    f"_{AGORA}"
                    f"{arquivo.suffix}"
                )
            shutil.copy(arquivo, dir_saida.joinpath(arquivo_saida))

        # Copia o arquivo original para o diretório de baixados.
        if dir_baixados.joinpath(arquivo.name).exists():
            shutil.copy(
                arquivo,
                dir_baixados.joinpath(f"{arquivo.stem}_{AGORA}{arquivo.suffix}"),
            )
        shutil.copy(arquivo, dir_baixados.joinpath(arquivo.name))

        # Apaga o arquivo original.
        arquivo.unlink()


def encerrar() -> None:
    """Encerra o programa."""
    console.print("[bold green]Programa encerrado com sucesso!")
    sys.exit()


def main() -> None:
    """Início do programa."""
    console.print(
        "Desenvolvido por [bold]Everton Souza[/bold] para a Clicheria Blumenau\n"
        "Contato: e.rodrigo@outlook.com\n"
        "https://github.com/carecavoador/busca_trabalhos"
    )
    console.rule()
    # Carrega arquivo de configurações.
    config = carrega_config()

    # Diretórios do programa.
    dir_saida = Path(config["diretorios"]["dir_saida"])
    dir_layouts = Path(config["diretorios"]["dir_pt_layout"]).joinpath(HOJE)
    dir_digitais = Path(config["diretorios"]["dir_pt_digital"]).joinpath(HOJE)
    dir_ordens = Path().home().joinpath("Downloads")

    # Cria a lista de trabalhos a serem feitos.
    # Verifica se foi passado algum PDF de ordem via argumentos.
    if len(sys.argv) > 1:
        lista_trabalhos = [
            Trabalho(Path(pdf)) for pdf in sys.argv if pdf.lower().endswith(".pdf")
        ]
    # Caso não, tenta carregar as ordens na pasta Downloads.
    else:
        lista_trabalhos = [
            Trabalho(pdf) for pdf in dir_ordens.iterdir() if pdf.suffix == ".pdf"
        ]

    # Se não houver trabalhos, encerra.
    if not lista_trabalhos:
        print("Sem trabalhos no momento.")
        encerrar()

    # Caso haja trabalhos, inicia o procedimento.
    arquivos_nao_encontrados = []
    for trabalho in lista_trabalhos:
        erros = []
        print(trabalho.resumo)
        print(trabalho.lista_materiais())
        for item in trabalho.itens_expedir:
            if item == ItensExpedir.LAYOUT:
                with console.status(
                    f"Buscando arquivo de {ItensExpedir.LAYOUT.value}..."
                ):
                    falta_layouts = busca_arquivos(
                        trabalho, dir_layouts, dir_saida, ItensExpedir.LAYOUT
                    )
                    if falta_layouts:
                        erros.append(falta_layouts)
                        console.print(
                            f"[bold red]Arquivo de {ItensExpedir.LAYOUT.value} não encontrado!"
                        )
                    else:
                        console.print(
                            f"[bold green]Arquivo de {ItensExpedir.LAYOUT.value} OK!"
                        )
            if item == ItensExpedir.DIGITAL:
                with console.status(
                    f"Buscando arquivo de {ItensExpedir.DIGITAL.value}..."
                ):
                    falta_digitais = busca_arquivos(
                        trabalho,
                        dir_digitais,
                        dir_saida,
                        ItensExpedir.DIGITAL,
                        sufixo=trabalho.perfil,
                    )
                    if falta_digitais:
                        erros.append(falta_digitais)
                        console.print(
                            f"[bold red]Arquivo de {ItensExpedir.DIGITAL.value} não encontrado!"
                        )
                    else:
                        console.print(
                            f"[bold green]Arquivo de {ItensExpedir.DIGITAL.value} OK!"
                        )
        if erros:
            arquivos_nao_encontrados.extend([{trabalho.resumo: erros}])
        console.rule()

    # Exibe a relação de arquivos não encontrados, caso exista.
    if arquivos_nao_encontrados:
        console.print("[bold red]ARQUIVOS NÃO ENCONTRADOS:")
        for nao_encontrado in arquivos_nao_encontrados:
            for trabalho, itens in nao_encontrado.items():
                for material in itens:
                    console.print(f"[bold red]{trabalho} -> {material.value}")
        console.rule()
        input("Pressione 'enter' para fechar. ")
        encerrar()

    # Fim do programa.
    encerrar()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("[bold red]Programa cancelado pelo usuário.")
        sys.exit()
