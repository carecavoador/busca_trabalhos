from pathlib import Path
from dataclasses import dataclass, field

# [num_os, pedido, versao, layout, digital, amostra, substrato, cliente, nome, perfil,  [],  []]

@dataclass
class Job:
    num_os: int
    pedido: int
    versao: int
    layout: bool
    digital: bool
    amostra: bool
    substrato: bool
    cliente: str
    nome: str
    perfil: str
    arquivos_layout: list[Path] = field(default_factory=(list))
    arquivos_digital: list[Path] = field(default_factory=(list))


if __name__ == "__main__":
    job = Job(
        num_os=224466,
        versao=1,
        pedido=1,
        cliente="Teste",
        nome="Trabalhinho bom",
        perfil="Sem perfil",
        layout=True,
        digital=True,
        substrato=False,
        amostra=True
    )
    print(job)
    print(job.arquivos_digital is True)
