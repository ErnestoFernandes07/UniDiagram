"""Reutiliza primitivas Tk entre quadros, preservando a ordem e os tags de hit-test."""
from copy import deepcopy

class CanvasRetido:
    def __init__(self,canvas):
        self.canvas=canvas
        self.itens={}
        self.ordem=[]
        self.estados={}
        self.grupos={}
        self.zoom=None

    def iniciar(self,zoom):
        self.mudou_zoom=self.zoom!=zoom
        self.zoom=zoom
        self.contagens={}
        self.nova_ordem=[]
        self.usados=set()

    def reutilizar(self,grupo,estado):
        if not self.mudou_zoom and grupo in self.grupos and self.estados.get(grupo)==estado:
            chaves=self.grupos[grupo]
            self.usados.update(chaves)
            self.nova_ordem.extend(self.itens[k][0] for k in chaves)
            return True
        self.estados[grupo]=deepcopy(estado)
        return False

    def criar(self,tipo,*args,**kw):
        tags=kw.get("tags",())
        grupo=tags if isinstance(tags,str) else (tags[0] if tags else "sem-tag")
        indice=self.contagens.get(grupo,0)
        self.contagens[grupo]=indice+1
        chave=(grupo,indice)
        def achatar(valores):
            for v in valores:
                if isinstance(v,(tuple,list)):
                    yield from achatar(v)
                else: yield v*self.zoom
        coords=tuple(achatar(args))
        if tipo=="text":
            font=kw.get("font")
            if font: kw["font"]=(font[0],round(font[1]*self.zoom) or -1,*font[2:])
        elif self.zoom!=1:
            kw["width"]=max(1,kw.get("width",1)*self.zoom)
        anterior=self.itens.get(chave)
        if anterior is None or anterior[1]!=tipo or set(anterior[3])!=set(kw):
            if anterior: self.canvas.delete(anterior[0])
            obj=getattr(self.canvas,"create_"+tipo)(*coords,**kw)
        else:
            obj=anterior[0]
            if anterior[2]!=coords:self.canvas.coords(obj,*coords)
            if anterior[3]!=kw:self.canvas.itemconfigure(obj,**kw)
        self.itens[chave]=(obj,tipo,coords,kw)
        self.usados.add(chave)
        self.nova_ordem.append(obj)
        return obj

    def finalizar(self):
        for chave in self.itens.keys()-self.usados:
            self.canvas.delete(self.itens.pop(chave)[0])
        if self.nova_ordem!=self.ordem:
            for obj in self.nova_ordem:self.canvas.tag_raise(obj)
        self.ordem=self.nova_ordem
        self.grupos={}
        for chave in self.itens:
            self.grupos.setdefault(chave[0],[]).append(chave)
        for chaves in self.grupos.values():chaves.sort(key=lambda k:k[1])
        self.estados={g:v for g,v in self.estados.items() if g in self.grupos}

    def bbox(self,*args):
        if len(args)==1 and isinstance(args[0],str):
            ids=[self.itens[k][0] for k in self.usados if k[0]==args[0]]
            caixa=self.canvas.bbox(*ids) if ids else None
        else:
            caixa=self.canvas.bbox(*args)
        return tuple(v/self.zoom for v in caixa) if caixa else None

    def __getattr__(self,nome):
        if nome.startswith("create_"):
            return lambda *a,**kw:self.criar(nome[7:],*a,**kw)
        return getattr(self.canvas,nome)
