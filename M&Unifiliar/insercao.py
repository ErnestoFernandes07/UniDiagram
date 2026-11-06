"""Prévia e inserção de componentes pelo terminal de apoio do pacote."""
from nucleo.geometria import transformar
from nucleo.pacotes import referencia
from nucleo.simbolos import desenhar

UNIDADE = 10


class Insercao:
    def componente_no_cursor(self,pos,snap):
        x,y = pos
        if snap:
            x,y = (round(v/UNIDADE)*UNIDADE for v in pos)
        item = dict(tipo=self.modo,nome=self.modo,x=0,y=0,pacote=referencia(self.pacote),
                    rotacao=self.rotacao_insercao,espelho=self.espelho_insercao)
        definicao = self.pacote.componentes[self.modo]
        porta = definicao["terminais"][definicao.get("apoio",0)]
        dx,dy = transformar(item,*porta)
        item.update(x=x-dx,y=y-dy)
        return item

    def atualizar_insercao(self,e):
        self.cursor_insercao = (e.x,e.y)
        self.shift_insercao = bool(e.state&1)
        self.previa_componente()

    def alternar_snap(self,ativo):
        if self.modo in self.pacote.componentes:
            self.shift_insercao = ativo
            self.previa_componente()

    def sair_insercao(self,e=None):
        self.cursor_insercao = None
        self.c.delete("previa_componente")

    def previa_componente(self):
        c = self.c
        c.delete("previa_componente")
        if self.modo not in self.pacote.componentes or self.cursor_insercao is None:
            return
        px,py = self.cursor_insercao
        pos = (c.canvasx(px)/self.zoom,c.canvasy(py)/self.zoom)
        item = self.componente_no_cursor(pos,self.shift_insercao)
        definicao = self.pacote.componentes[self.modo]
        apoio = definicao.get("apoio",0)
        ax,ay = transformar(item,*definicao["terminais"][apoio])
        if self.shift_insercao:
            # Local fine grid exposes the fixed logical lattice, even with no background.
            portas = [transformar(item,*p) for p in definicao["terminais"]]
            xs,ys = zip(*portas)
            for x in range(int(max(min(xs)-20,ax-80)//10)*10,int(min(max(xs)+20,ax+80)//10)*10+1,10):
                for y in range(int(max(min(ys)-20,ay-80)//10)*10,int(min(max(ys)+20,ay+80)//10)*10+1,10):
                    c.create_oval(x*self.zoom-1,y*self.zoom-1,x*self.zoom+1,y*self.zoom+1,
                                  fill="#94b9a5",outline="",tags="previa_componente")
            c.create_oval(ax*self.zoom-6,ay*self.zoom-6,ax*self.zoom+6,ay*self.zoom+6,
                          outline="#16835f",width=2,tags="previa_componente")
        desenhar(c,"rascunho",item,self.pacote,False,["rascunho",apoio])
        for obj in c.find_withtag("item:rascunho"):
            c.itemconfigure(obj,tags="previa_componente")
            c.scale(obj,0,0,self.zoom,self.zoom)
            if c.type(obj)=="text":
                familia,tamanho,*estilo = c.tk.splitlist(c.itemcget(obj,"font"))
                c.itemconfigure(obj,font=(familia,round(int(tamanho)*self.zoom),*estilo))
            else:
                c.itemconfigure(obj,width=max(1,float(c.itemcget(obj,"width"))*self.zoom))
