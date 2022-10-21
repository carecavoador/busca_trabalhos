import json
import os
from datetime import datetime
from pathlib import Path

HOJE = datetime.today().strftime("%d-%m-%Y")

DIR_CONFIG = Path().home().joinpath(".juggler")
ARQUIVO_CONFIG = Path(DIR_CONFIG).joinpath("config.json")
MODELO_CONFIG = """
// {
//  "diretorios": {
//      "layouts": "caminho",
//      "provas": "caminho",
//      "saida": "caminho"
//  }
// }"""


def carrega_config(config_file=ARQUIVO_CONFIG) -> None:
    """Verifica se o arquivo de configuração existe e retorna as
    configurações como um dicionário. Se não existir, cria o arquivo."""
    if not DIR_CONFIG.exists():
        os.mkdir(DIR_CONFIG)

    if not config_file.exists():
        with open(config_file, "w", encoding="utf-8") as arquivo:
            arquivo.write(MODELO_CONFIG)
            print(f"Arquivo de configuração criado em:\n{MODELO_CONFIG}")
    try:
        return json.load(open(config_file, "r", encoding="utf-8"))
    except json.decoder.JSONDecodeError:
        return None


if __name__ == "__main__":
    cfg = carrega_config()
    print(cfg)
