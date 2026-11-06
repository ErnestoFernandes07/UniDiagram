"""Superfícies e controles compartilhados da área de desenho."""
import tkinter as tk

PAPEL = "#f8faf8"
TINTA = "#243c38"
VERDE = "#126a54"


def arredondado(c,x,y,u,v,r,cor,contorno="",tags=()):
    return c.create_polygon(x+r,y,u-r,y,u,y,u,y+r,u,v-r,u,v,u-r,v,x+r,v,x,v,x,v-r,
                            x,y+r,x,y,x+r,y,smooth=True,splinesteps=12,fill=cor,outline=contorno,tags=tags)


class Cartao(tk.Canvas):
    """Painel flutuante que acompanha o tamanho dos widgets de conteúdo."""
    def __init__(self,pai,padding=10):
        super().__init__(pai,bg=PAPEL,highlightthickness=0,width=2*padding+1,height=2*padding+1)
        self.conteudo = tk.Frame(self,bg="white")
        self.create_window(padding,padding,window=self.conteudo,anchor="nw")
        self.conteudo.bind("<Configure>",lambda e:self.redimensionar(e.width,e.height,padding))

    def redimensionar(self,w,h,padding):
        w,h = w+padding*2,h+padding*2
        self.configure(width=w+4,height=h+5)
        self.delete("superficie")
        arredondado(self,3,5,w+3,h+4,14,"#e3e9e5",tags="superficie")
        arredondado(self,1,2,w+1,h+2,14,"#dce4df",tags="superficie")
        arredondado(self,0,0,w,h,14,"white","#d4ded8",tags="superficie")
        self.tag_lower("superficie")

    def levantar(self):
        self.tk.call("raise",self)


class BotaoMenu(tk.Canvas):
    def __init__(self,pai,texto,acao,largura=112,fundo="#e7f0e9",cor=TINTA):
        super().__init__(pai,width=largura,height=30,bg=pai.cget("bg"),highlightthickness=0,
                         cursor="hand2",takefocus=True)
        def pintar(ativo=False):
            self.delete("all")
            arredondado(self,1,1,largura-1,29,8,fundo,VERDE if ativo else "")
            self.create_text(12,15,anchor="w",text=texto,font=("Segoe UI",9,"bold"),fill=cor)
            self.create_line(largura-17,13,largura-13,17,largura-9,13,fill=cor,width=1.5)
        pintar()
        self.bind("<Enter>",lambda e:pintar(True))
        self.bind("<Leave>",lambda e:pintar(False))
        self.bind("<FocusIn>",lambda e:pintar(True))
        self.bind("<FocusOut>",lambda e:pintar(False))
        for evento in ("<ButtonRelease-1>","<Return>","<space>"):
            self.bind(evento,lambda e:acao())


class Faixa(tk.Canvas):
    """Opções compactas, com o estado selecionado e navegação pelo teclado."""
    def __init__(self,pai,opcoes,acao,largura=210,cores=False):
        super().__init__(pai,width=largura,height=28,bg="white",highlightthickness=0,
                         cursor="hand2",takefocus=True)
        self.opcoes,self.acao,self.cores = opcoes,acao,cores
        self.valor = None
        self.bind("<Button-1>",self.escolher)
        self.bind("<Left>",lambda e:self.avancar(-1))
        self.bind("<Right>",lambda e:self.avancar(1))
        self.bind("<Configure>",lambda e:self.pintar())
        self.bind("<FocusIn>",lambda e:self.pintar())
        self.bind("<FocusOut>",lambda e:self.pintar())

    def avancar(self,delta):
        chaves = [v for v,_ in self.opcoes]
        i = chaves.index(self.valor) if self.valor in chaves else 0
        self.acao(chaves[(i+delta)%len(chaves)])
        self.focus_set()
        return "break"

    def escolher(self,e):
        i = min(len(self.opcoes)-1,max(0,int(e.x*len(self.opcoes)/self.winfo_width())))
        self.acao(self.opcoes[i][0])

    def set(self,valor):
        if self.valor!=valor:
            self.valor = valor
            self.pintar()

    def pintar(self):
        self.delete("all")
        largura = max(self.winfo_width(),int(self.cget("width")))/len(self.opcoes)
        for i,(valor,rotulo) in enumerate(self.opcoes):
            x,u = i*largura+1,(i+1)*largura-2
            ativo = self.valor==valor
            if self.cores:
                if ativo:
                    arredondado(self,x,0,u,27,6,"white",VERDE)
                arredondado(self,x+2,2,u-2,25,5,valor)
                if ativo:
                    self.create_text((x+u)/2,14,text="✓",font=("Segoe UI",10,"bold"),fill="white")
            else:
                arredondado(self,x,2,u,26,6,"#daf0e4" if ativo else "#f1f4f2",
                            VERDE if ativo and self.focus_get()==self else "")
                if isinstance(rotulo,tuple):
                    texto,font = rotulo
                else:
                    texto,font = rotulo,("Segoe UI",9)
                self.create_text((x+u)/2,14,text=texto,font=font,fill=VERDE if ativo else TINTA)


class Opacidade(tk.Canvas):
    def __init__(self,pai,alterar):
        super().__init__(pai,width=210,height=20,highlightthickness=0,bg="white",cursor="hand2",takefocus=True)
        self.alterar = alterar
        self.valor = 100
        self.bind("<Button-1>",lambda e:self.mudar(e,True))
        self.bind("<B1-Motion>",lambda e:self.mudar(e,False))
        self.bind("<Left>",lambda e:self.tecla(-5))
        self.bind("<Right>",lambda e:self.tecla(5))
        self.bind("<Configure>",lambda e:self.pintar())

    def tecla(self,delta):
        self.alterar(max(0,min(100,self.valor+delta)),True)
        self.focus_set()
        return "break"

    def mudar(self,e,inicio):
        valor = max(0,min(100,round((e.x-7)*100/max(1,self.winfo_width()-14))))
        self.alterar(valor,inicio)

    def set(self,valor):
        self.valor = valor
        self.pintar()

    def pintar(self):
        self.delete("all")
        u = max(14,self.winfo_width()-7)
        x = 7+(u-7)*self.valor/100
        self.create_line(7,10,u,10,fill="#e1e8e3",width=4,capstyle="round")
        self.create_line(7,10,x,10,fill="#88c7a8",width=4,capstyle="round")
        self.create_oval(x-6,4,x+6,16,fill=VERDE,outline="white")
