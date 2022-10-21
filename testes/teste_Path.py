from pathlib import Path

dir_raiz = Path(__file__).parent
dir_teste = dir_raiz.joinpath("testes/novo/")
dir_teste.mkdir(parents=True, exist_ok=True)

# Remove um arquivo
Path.unlink()

# Remove um diretório (precisa estar vazio)
Path.rmdir()
