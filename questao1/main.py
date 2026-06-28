#!/usr/bin/env python3
"""
KBS-Shell — Ponto de entrada principal.
Uso:
    python main.py                      # shell vazia
    python main.py <arquivo_kb.json>    # carrega KB automaticamente
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.knowledge_base import KnowledgeBase
from ui.cli import CLIShell


def main():
    kb = None
    if len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            kb = KnowledgeBase.load(path)
            print(f"Base '{kb.domain}' carregada de '{path}'.")
        except Exception as e:
            print(f"Aviso: não foi possível carregar '{path}': {e}")
    shell = CLIShell(kb)
    shell.run()


if __name__ == "__main__":
    main()
