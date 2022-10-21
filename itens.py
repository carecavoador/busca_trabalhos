from pathlib import Path
from trabalhos import Trabalho

dir_ordens = r"C:\Users\Everton Souza\OneDrive\dev\python\analise_midia\busca_trabalhos\busca_trabalhos\testes\ordens"

trabalhos = [Trabalho(t) for t in Path(dir_ordens).iterdir()]
for trabalho in trabalhos:
    print(trabalho)