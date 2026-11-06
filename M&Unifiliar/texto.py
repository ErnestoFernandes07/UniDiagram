import copy
from math import cos, radians, sin
import tkinter as tk
from tkinter import font as tkfont
from uuid import uuid4

from formas import desenhar_forma


class TextoNaFolha:
    def iniciar_texto(self,pos,existente=None):
        self.ferramenta("Selecionar")
        self.selecao = existente or uuid4().hex
        self.texto_rascunho = (copy.deepcopy(self.folha["formas"][existente]) if existente else
                              dict(tipo="Texto",texto="",pontos=[list(pos)],cor=self.cor_forma.get()))
        caixa = self.entrada_texto
        caixa.delete("1.0","end")
        caixa.insert("1.0",self.texto_rascunho["texto"])
        caixa.mark_set("insert","end-1c")
        caixa.edit_reset()
        caixa.edit_modified(False)
        caixa.focus_set()
        self.status.set("Digite na folha. Enter conclui, Shift + Enter quebra a linha e Esc cancela.")
        self.render()

    def preparar_entrada_texto(self):
        # O controle nativo cuida do teclado e da área de transferência. A folha
        # desenha os caracteres na posição, fonte e rotação reais do objeto.
        caixa = tk.Text(self.area,undo=True,wrap="none",width=1,height=1)
        caixa.place(x=-8,y=-8,width=1,height=1)
        caixa.bindtags((str(caixa),"Text","all"))
        self.entrada_texto = caixa
        caixa.bind("<<Modified>>",self.atualizar_digitacao)
        caixa.bind("<KeyRelease>",lambda e:self.render() if self.texto_rascunho is not None else None)
        caixa.bind("<Return>",lambda e:self.concluir_digitacao())
        caixa.bind("<Shift-Return>",self.quebrar_linha)
        caixa.bind("<Escape>",lambda e:self.concluir_digitacao(cancelar=True))
        caixa.bind("<Control-s>",lambda e:(self.salvar(),"break")[1])

    def quebrar_linha(self,e):
        self.entrada_texto.insert("insert","\n")
        return "break"

    def atualizar_digitacao(self,e=None):
        if self.entrada_texto.edit_modified():
            self.entrada_texto.edit_modified(False)
            if self.texto_rascunho is not None:
                self.texto_rascunho["texto"] = self.entrada_texto.get("1.0","end-1c")
                self.render()

    def concluir_digitacao(self,cancelar=False):
        rascunho = self.texto_rascunho
        if rascunho is None:
            return
        self.texto_rascunho = None
        rascunho["texto"] = self.entrada_texto.get("1.0","end-1c")
        anterior = self.folha.get("formas",{}).get(self.selecao)
        if not cancelar and anterior!=rascunho:
            if rascunho["texto"].strip():
                self.lembrar()
                self.folha.setdefault("formas",{})[self.selecao] = rascunho
            elif anterior is not None:
                self.lembrar()
                del self.folha["formas"][self.selecao]
        if self.selecao not in self.folha.get("formas",{}):
            self.selecao = None
        self.c.focus_set()
        self.status.set("Clique duas vezes no texto para voltar a escrever.")
        self.render()
        return "break"

    def geometria_texto(self):
        obj = self.texto_rascunho
        fonte = tkfont.Font(root=self.root,family=obj.get("fonte","Segoe UI"),size=-obj.get("tamanho",18))
        linhas = obj["texto"].split("\n")
        largura = max(map(fonte.measure,linhas))
        altura = fonte.metrics("linespace")
        angulo = radians(obj.get("angulo",0))
        return fonte,linhas,largura,altura,cos(angulo),sin(angulo)

    def desenhar_digitacao(self,c):
        obj = self.texto_rascunho
        obj["texto"] = self.entrada_texto.get("1.0","end-1c")
        desenhar_forma(c,self.selecao,obj)
        fonte,linhas,largura,h,co,si = self.geometria_texto()
        cx,cy = obj["pontos"][0]
        def ponto(x,y):
            return cx+x*co+y*si,cy-x*si+y*co
        linha,coluna = map(int,self.entrada_texto.index("insert").split("."))
        x = -largura/2+fonte.measure(linhas[linha-1][:coluna])
        y = (linha-1-len(linhas)/2)*h
        if self.entrada_texto.tag_ranges("sel"):
            de,ate = [tuple(map(int,str(i).split("."))) for i in self.entrada_texto.tag_ranges("sel")]
            for n in range(de[0],min(ate[0],len(linhas))+1):
                texto = linhas[n-1]
                a = -largura/2+fonte.measure(texto[:de[1]]) if n==de[0] else -largura/2
                b = -largura/2+fonte.measure(texto[:ate[1]]) if n==ate[0] else -largura/2+fonte.measure(texto)
                base = (n-len(linhas)/2)*h
                c.create_line(ponto(a,base),ponto(b,base),fill="#16876f",width=2)
        c.create_line(ponto(x,y),ponto(x,y+h),fill="#14806b",width=1.5)

    def posicionar_cursor(self,pos):
        fonte,linhas,largura,h,co,si = self.geometria_texto()
        cx,cy = self.texto_rascunho["pontos"][0]
        dx,dy = pos[0]-cx,pos[1]-cy
        x = dx*co-dy*si+largura/2
        y = dx*si+dy*co+len(linhas)*h/2
        linha = min(len(linhas)-1,max(0,int(y//h)))
        texto = linhas[linha]
        coluna = min(range(len(texto)+1),key=lambda i:abs(fonte.measure(texto[:i])-x))
        self.entrada_texto.tag_remove("sel","1.0","end")
        self.entrada_texto.mark_set("insert",f"{linha+1}.{coluna}")
        self.entrada_texto.focus_set()
        self.render()
