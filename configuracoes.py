import sys
from typing import Any
import tomli, tomli_w
from pathlib import Path

from rich.console import Console

console = Console()


DIR_CONFIG = Path().home().joinpath(".config", "busca-trabalhos")
ARQUIVO_CONFIG = DIR_CONFIG.joinpath("config.toml")


def _cria_nova_config() -> None:
    """
    Cria um novo arquivo de configuração no diretório %HOME%
    """
    console.print("[bold cyan][NOVA CONFIGURAÇÃO]")

    def tenta_tres_vezes(diretorio: str) -> Path:
        """
        Tenta três vezes retornar um objeto Path válido com o caminho
        informado pelo usuário.
        """
        for _ in range(3):
            dir = input(f"> Diretório de {diretorio}: ")
            if dir:
                dir = Path(dir)
                if dir.exists():
                    return dir
            console.print(
                "[bold red][ERRO]Diretório inválido. Por favor, tente novamente."
            )
            continue
        console.print(
            "[bold red][ERRO]Não foi possível criar o arquivo de configuração."
        )
        sys.exit()

    dir_layouts = tenta_tres_vezes("Prints Layout")
    dir_digitais = tenta_tres_vezes("Provas Digitais")
    dir_saida = tenta_tres_vezes("Saída")

    if dir_layouts is not None and dir_digitais is not None and dir_saida is not None:
        config = {
            "diretorios": {
                "dir_pt_layout": dir_layouts.as_posix(),
                "dir_pt_digital": dir_digitais.as_posix(),
                "dir_saida": dir_saida.as_posix(),
            }
        }
        tomli_w.dump(config, ARQUIVO_CONFIG.open(mode="wb"))


def carrega_config(arquivo_config: Path = ARQUIVO_CONFIG) -> dict[str, Any]:
    """Tenta carregar um arquivo de configurações existente. Cria um novo caso não exista."""
    if not DIR_CONFIG.exists():
        DIR_CONFIG.mkdir(parents=True)
    if not arquivo_config.exists():
        _cria_nova_config()
    return tomli.load(arquivo_config.open(mode="rb"))
