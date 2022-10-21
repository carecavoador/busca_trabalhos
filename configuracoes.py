import sys
import tomli, tomli_w
from pathlib import Path


dir_raiz = Path().home().joinpath("busca-trabalhos")
dir_config = dir_raiz.joinpath("config")
arquivo_config = dir_config / "config.toml"


def _cria_nova_config():
    print("[NOVA CONFIGURAÇÃO]")

    def tenta_tres_vezes(diretorio: str) -> Path:
        for _ in range(3):
            dir = input(f"> Diretório de {diretorio}: ")
            if dir:
                dir = Path(dir)
                if dir.exists():
                    return dir
            print("> Diretório inválido.")
            continue
        print("[ERRO] Não foi possível criar o arquivo de configuração.")
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
        tomli_w.dump(config, arquivo_config.open(mode="wb"))


def carrega_config(arquivo_config: Path = arquivo_config):
    """Tenta carregar um arquivo de configurações existente. Cria um novo caso não exista."""
    if not dir_config.exists():
        dir_config.mkdir(parents=True)
    if not arquivo_config.exists():
        _cria_nova_config()
    return tomli.load(arquivo_config.open(mode="rb"))
