import re

from pathlib import Path
from dataclasses import dataclass, field

from PyPDF2 import PdfReader

from itens_expedir import ItensExpedir


SEM_PERFIL = "Sem"
FIM_PERFIL = "Fechamento:"
INICIO_LISTA = "Itens para Expedir:"
FIM_LISTA = "Observações:"


@dataclass
class Trabalho:
    """
    Esta classe serve para armazenar e manipular as informações contidas no
    arquivo .PDF da Ordem de Serviço. É preciso passar om objeto Path com o
    caminho absoluto para o arquivo .PDF no construtor do objeto. O método
    carrega_info_do_pdf extrai o texto do PDF e tenta carregar as informações
    pertinentes à partir do texto.
    """
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
        """Carrega as informações do trabalho a partir do PDF da OS."""
        with open(self.pdf_os, "rb") as arquivo_pdf:
            reader = PdfReader(arquivo_pdf)
            pagina = reader.pages[0]
            texto = pagina.extract_text().splitlines()

            # Número de OS, Pedido, Versão, Cliente
            self.num_os = int(texto[10].split()[0])
            self.pedido = int(texto[10].split()[1])
            self.versao = int(texto[10].split()[2])
            self.cliente = " ".join(texto[10].split()[3:])

            # Nome do trabalho
            self.nome = texto[11]

            # Perfil de cores
            if not texto[13].startswith(SEM_PERFIL):
                _perfil = texto[13].strip(FIM_PERFIL)
                # Substitui os caracteres '\', '/', '?', '*', ',', e '.' por '_'
                self.perfil = re.sub(r"[\/?*,.]", "_", _perfil)
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

    def __str__(self) -> str:
        return f"{self.resumo} {self.nome}'\n'{self.lista_materiais()}"

    @property
    def resumo(self) -> str:
        """[OS 000000/0 v0 - <nome do cliente>]"""
        return f"[OS {self.num_os}/{self.pedido} v{self.versao} - {self.cliente}]"

    def lista_materiais(self) -> str:
        """Retorna a lista de materiais no campo 'Itens para Expedir'"""
        if self.itens_expedir:
            lista = ["Itens para Expedir:"]
            lista.extend([item.value for item in self.itens_expedir])
            return "\n- ".join(lista)
        else:
            return "- SEM ITENS A EXPEDIR"
