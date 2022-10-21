import logging

from pathlib import Path
from copy import copy

from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt6.QtCore import Qt

from assets.ui_janela_principal import Ui_JanelaPrincipal
from old_trabalhos import Tipo, busca_arquivos
from job import Job


COLS_PQ = 60
COL_CLIENTE = 150
COL_NOME = 420

ENTRADA = Path(
    r"C:\Users\Everton Souza\OneDrive\dev\python\analise_midia\v2\busca_trabalhos\Entrada"
)
SAIDA = Path(
    r"C:\Users\Everton Souza\OneDrive\dev\python\analise_midia\v2\busca_trabalhos\Saida"
)


class JanelaPrincipal(QMainWindow, Ui_JanelaPrincipal):
    def __init__(self, lista_jobs: list[list]):
        super().__init__()
        self.setupUi(self)
        self.lista_jobs = copy(lista_jobs)

        self.at_buscar_arquivos.triggered.connect(self.busca_arquivos_trabalhos)

        # Carrega os trabalhos na tabela:
        self.carrega_tabela(self.lista_jobs)
        self.tabela_trabalhos.sortByColumn(7, Qt.SortOrder.AscendingOrder)


    def carrega_tabela(self, lista_jobs):
        self.tabela_trabalhos.clearContents()
        self.tabela_trabalhos.setRowCount(len(lista_jobs))
        for row, job in enumerate(lista_jobs):
            for col, data in enumerate(job):
                self.tabela_trabalhos.setItem(row, col, QTableWidgetItem(str(data)))


    def busca_arquivos_trabalhos(self):
        # jobs_atualizados = []
        for linha in self.lista_jobs:
            if linha[3] and linha[10] is not None:
                arquivos_encontrados = busca_arquivos(Job(*linha), ENTRADA, SAIDA, Tipo.LAYOUT)
                if len(arquivos_encontrados) > 0:
                    linha[10] = arquivos_encontrados
                    linha[3] = "OK"
                else:
                    linha[3] = "NOTOK"
            # jobs_atualizados.append(linha)
        self.carrega_tabela(self.lista_jobs)
