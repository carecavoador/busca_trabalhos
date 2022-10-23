"""
trabalhos.py
Classe Trabalhos
"""
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field

from PyPDF2 import PdfReader


SEM_PERFIL = "Sem"
FIM_PERFIL = "Fechamento:"
INICIO_LISTA = "Itens para Expedir:"
FIM_LISTA = "Observações:"


class ItensExpedir(Enum):
    CLICHES = "Clichês"
    LAYOUT = "Print Layout"
    DIGITAL = "Prova Digital"
    AMOSTRA = "Amostra"
    EPSON = "Prova Substrato - EPSON"
    ROLAND = "Prova Substrato - ROLAND"
    HEAFORD = "Prova de Máquina"


@dataclass
class Trabalho:
    pdf_os: Path
    num_os: int = field(init=False)
    pedido: int = field(init=False)
    versao: int = field(init=False)
    cliente: str = field(init=False)
    nome: str = field(init=False)
    perfil: str = field(init=False)
    itens_expedir: set = field(init=False, default_factory=set[ItensExpedir])
    arquivos_layout: list = field(init=False, default_factory=list)
    arquivos_digital: list = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self.carrega_info_do_pdf()

    def __str__(self) -> str:
        return f"{self.resumo} {self.nome}'\n'{self.lista_materiais()}"

    @property
    def resumo(self) -> str:
        return f"[OS {self.num_os}/{self.pedido} v{self.versao} - {self.cliente}]"

    def lista_materiais(self) -> str:
        if self.itens_expedir:
            lista = ["Materiais a expedir:"]
            lista.extend([item.value for item in self.itens_expedir])
            return "\n- ".join(lista)
        else:
            return "- SEM ITENS A EXPEDIR"

    def carrega_info_do_pdf(self) -> None:
        """Carrega as informações do trabalho a partir do PDF da OS."""
        with open(self.pdf_os, "rb") as arquivo_pdf:
            reader = PdfReader(arquivo_pdf)
            pagina = reader.pages[0]
            texto = pagina.extract_text().splitlines()

            # Os, Pedido, Versão, Cliente
            self.num_os, self.pedido, self.versao, self.cliente = (
                int(texto[10].split()[0]),
                int(texto[10].split()[2]),
                int(texto[10].split()[1]),
                " ".join(texto[10].split()[3:]),
            )

            # Nome do trabalho
            self.nome = texto[11]

            # Perfil de cores
            if not texto[13].startswith(SEM_PERFIL):
                self.perfil = texto[13].strip(FIM_PERFIL)
            else:
                self.perfil = "Sem Perfil"

            # Materiais para expedir
            try:
                idx_a = texto.index(INICIO_LISTA) + 2
                try:
                    idx_b = texto.index(FIM_LISTA)
                except ValueError:
                    idx_b = -1
            except ValueError:
                pass
            itens_expedicao = texto[idx_a:idx_b]
            for item in itens_expedicao:
                if item.startswith(ItensExpedir.CLICHES.value):
                    self.itens_expedir.add(ItensExpedir.CLICHES)
                elif item.startswith(ItensExpedir.LAYOUT.value):
                    self.itens_expedir.add(ItensExpedir.LAYOUT)
                elif item.startswith(ItensExpedir.DIGITAL.value):
                    self.itens_expedir.add(ItensExpedir.DIGITAL)
                elif item.startswith(ItensExpedir.EPSON.value):
                    self.itens_expedir.add(ItensExpedir.EPSON)
                elif item.startswith(ItensExpedir.ROLAND.value):
                    self.itens_expedir.add(ItensExpedir.ROLAND)
                elif item.startswith(ItensExpedir.HEAFORD.value):
                    self.itens_expedir.add(ItensExpedir.HEAFORD)
                elif item.startswith(ItensExpedir.AMOSTRA.value):
                    self.itens_expedir.add(ItensExpedir.AMOSTRA)
