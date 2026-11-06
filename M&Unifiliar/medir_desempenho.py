"""Benchmark local com janela Tk visível; não modifica o arquivo do projeto."""
import argparse
import math
import statistics
import time
import tkinter as tk
from pathlib import Path
from types import SimpleNamespace
from app import Editor
from nucleo.documento import carregar


def medir(editor,root,nome,acao):
    tempos=[]
    for i in range(60):
        inicio=time.perf_counter()
        acao(i)
        root.update_idletasks()
        tempos.append((time.perf_counter()-inicio)*1000)
    print(f"{nome}: mediana={statistics.median(tempos):.2f} ms; p95={sorted(tempos)[56]:.2f} ms")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("projeto",nargs="?",default=str(Path(__file__).parent/"exemplos/quadro-geral/quadro-geral-multifilar.json"))
    args=parser.parse_args()
    root=tk.Tk()
    try:
        editor=Editor(root)
        editor.substituir(carregar(args.projeto),None)
        root.update()
        medir(editor,root,"Redesenho",lambda i:editor.render())
        editor.c.scan_mark(400,300)
        medir(editor,root,"Pan",lambda i:editor.arrastar_tela(SimpleNamespace(x=400+i*2,y=300+i)))
        if editor.folha["componentes"]:
            chave=next(iter(editor.folha["componentes"]))
            item=editor.folha["componentes"][chave]
            x,y=item["x"],item["y"]
            editor.escolher_componente(chave,0,(x,y))
            medir(editor,root,"Arraste circular",lambda i:editor.deslocar_grupo((x+80*math.cos(i/8),y+80*math.sin(i/8))))
    finally:
        root.destroy()

if __name__=="__main__":main()
