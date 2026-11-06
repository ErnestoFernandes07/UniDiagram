import tkinter as tk
from tkinter import ttk

from formas import CORES, FORMAS
from nucleo.pacotes import REGISTRO, obter, referencia
from paineis import BotaoMenu, Cartao, Faixa, arredondado
from nucleo.simbolos import desenhar

PAPEL = "#f8faf8"
TINTA = "#243c38"
MENTA = "#b9f0d3"
VERDE = "#126a54"
FONTE = "Segoe UI"


def botao(pai,texto,acao,fundo="white",cor=TINTA,**opcoes):
    return tk.Button(pai,text=texto,command=acao,bg=fundo,fg=cor,bd=0,relief="flat",
                     activebackground="#d6e9df",activeforeground=TINTA,cursor="hand2",
                     highlightthickness=0,font=(FONTE,9,"bold"),padx=9,pady=5,**opcoes)


def icone(c,nome,x,y,cor):
    def linha(*pts):
        c.create_line(*[(x+a,y+b) for a,b in zip(pts[::2],pts[1::2])],
                      fill=cor,width=1.8,capstyle="round",joinstyle="round")
    if nome=="Selecionar":
        linha(-6,-9,-5,8,-1,3,4,9,7,7,2,1,8,0,-6,-9)
    elif nome=="Mover":
        linha(-9,0,-6,-2,-3,1,-3,-6,-1,-8,1,-7,1,-2,1,-8,4,-8,4,-2,4,-6,7,-5,7,-1,8,-3,10,-2,9,5,5,9,0,9,-9,0)
    elif nome=="Retângulo":
        c.create_rectangle(x-8,y-7,x+8,y+7,outline=cor,width=1.7)
    elif nome=="Losango":
        linha(0,-9,9,0,0,9,-9,0,0,-9)
    elif nome=="Elipse":
        c.create_oval(x-8,y-8,x+8,y+8,outline=cor,width=1.7)
    elif nome in ("Linha","Seta"):
        linha(-9,6,8,-6)
        if nome=="Seta":
            linha(1,-6,8,-6,7,1)
    elif nome=="Seta curva":
        c.create_line(x-10,y+8,x-10,y-5,x+9,y-5,fill=cor,width=2,smooth=True)
        c.create_line(x+4,y-10,x+9,y-5,x+4,y,fill=cor,width=2)
    elif nome=="Ligar":
        linha(-8,7,-8,0,7,0,7,-7)
        for a,b in [(-8,7),(7,-7)]:
            c.create_oval(x+a-2,y+b-2,x+a+2,y+b+2,fill="white",outline=cor)
    elif nome=="Derivar":
        linha(-9,5,9,5)
        linha(0,5,0,-6,7,-6)
        c.create_oval(x-2,y+3,x+2,y+7,fill=cor,outline=cor)
    elif nome=="Lápis":
        linha(-8,8,-6,2,4,-8,8,-4,-2,6,-8,8)
        linha(2,-6,6,-2)
    elif nome=="Texto":
        linha(-8,-7,8,-7)
        linha(0,-7,0,8)
        linha(-4,8,4,8)


class Interface:
    def montar_interface(self):
        root = self.root
        root.configure(bg=PAPEL)
        root.option_add("*Font",(FONTE,9))
        estilo = ttk.Style(root)
        estilo.theme_use("clam")
        estilo.configure("Treeview",background="white",fieldbackground="white",foreground=TINTA,
                         borderwidth=0,rowheight=26,font=(FONTE,9))
        estilo.map("Treeview",background=[("selected","#dbefe4")],foreground=[("selected",VERDE)])
        self.aba = tk.StringVar(value=self.dados["ativa"])
        self.ferramenta_ativa = tk.StringVar()
        self.indice_zoom = tk.StringVar(value="100%")
        self.cor_forma = tk.StringVar(value=CORES[0])
        topo = tk.Frame(root,bg="#182e2a",padx=16,pady=9)
        topo.pack(fill="x")
        logo = tk.Canvas(topo,width=32,height=32,bg="#182e2a",highlightthickness=0)
        logo.pack(side="left")
        arredondado(logo,1,1,31,31,7,MENTA)
        logo.create_line(9,22,9,16,16,16,16,10,24,10,fill="#154e3c",width=2)
        for x,y in [(9,22),(24,10)]:
            logo.create_oval(x-2,y-2,x+2,y+2,fill="#154e3c",outline="")
        tk.Label(topo,text="M&Unifiliar",bg="#182e2a",fg="white",font=(FONTE,15,"bold")).pack(side="left",padx=(8,18))
        self.titulo_projeto = tk.StringVar()
        tk.Label(topo,textvariable=self.titulo_projeto,bg="#182e2a",fg="#b8cec5",font=(FONTE,10)).pack(side="left")
        botao(topo,"Salvar JSON",self.salvar,MENTA,"#143e30").pack(side="right",padx=(8,0))
        arquivo = BotaoMenu(topo,"Arquivo",lambda:self.popup(arquivo,self.menu_arquivo),84,"#29443c","#eff9f4")
        arquivo.pack(side="right")
        self.menu_arquivo = tk.Menu(root,tearoff=False)
        for nome,acao in [("Novo projeto",self.novo),("Abrir JSON…",self.abrir),("Salvar como…",lambda:self.salvar(True)),
                          ("Exportar folha em PNG",self.exportar),("Atalhos",self.atalhos)]:
            self.menu_arquivo.add_command(label=nome,command=acao)
        menu_ia = tk.Menu(self.menu_arquivo,tearoff=False)
        menu_ia.add_command(label="Projeto atual",command=lambda:self.copiar_contexto_ia(True))
        menu_ia.add_command(label="Projeto novo (sem desenho atual)",command=lambda:self.copiar_contexto_ia(False))
        self.menu_arquivo.add_separator()
        self.menu_arquivo.add_cascade(label="Copiar contexto para IA",menu=menu_ia)
        self.menu_arquivo.add_command(label="Importar resposta da IA…",command=self.importar_resposta_ia)
        faixa = tk.Frame(root,bg="white",padx=16,pady=5)
        faixa.pack(fill="x")
        self.tabs = {}
        self.barra_abas = tk.Frame(faixa,bg="white")
        self.barra_abas.pack(side="left")
        BotaoMenu(faixa,"Bibliotecas",self.biblioteca).pack(side="right",padx=(8,0))
        botao(faixa,"↶",self.desfazer).pack(side="left",padx=(14,0))
        botao(faixa,"↷",self.refazer).pack(side="left")
        botao(faixa,"Atalhos",self.atalhos).pack(side="right")
        botao(faixa,"Fundo",self.configurar_grade).pack(side="right")
        self.botao_guias = botao(faixa,"Guias",self.alternar_guias)
        self.botao_guias.pack(side="right")
        self.rodape = tk.Frame(root,bg="white",padx=14,pady=4)
        self.rodape.pack(side="bottom",fill="x")
        self.modo_status = tk.StringVar()
        tk.Label(self.rodape,textvariable=self.modo_status,bg="white",fg=VERDE,font=(FONTE,9,"bold")).pack(side="left",padx=(0,12))
        tk.Label(self.rodape,textvariable=self.leitura_guias,bg="white",fg=VERDE).pack(side="right")
        tk.Label(self.rodape,textvariable=self.status,bg="white",fg="#63756d",anchor="w").pack(fill="x")
        self.area = tk.Frame(root,bg=PAPEL)
        self.area.pack(fill="both",expand=True)
        self.c = tk.Canvas(self.area,bg=PAPEL,highlightthickness=0,confine=False)
        self.c.pack(fill="both",expand=True)

        self.ferramentas = ("Selecionar","Mover",*FORMAS)
        self.paleta = tk.Canvas(self.area,width=446,height=58,bg=PAPEL,highlightthickness=0,cursor="hand2")
        self.paleta.place(relx=.5,y=12,anchor="n")
        self.paleta.bind("<Button-1>",self.clicar_ferramenta)
        self.paleta.bind("<Motion>",self.dica_ferramenta)
        self.dica = tk.Label(self.area,bg="#213b33",fg="white",padx=7,pady=3,font=(FONTE,9))
        self.paleta.bind("<Leave>",lambda e:self.dica.place_forget())
        self.painel = Cartao(self.area)
        cab = tk.Frame(self.painel.conteudo,bg="white")
        cab.pack(fill="x",padx=10,pady=7)
        self.titulo_biblioteca = tk.Label(cab,text="Componentes",bg="white",fg=TINTA,font=(FONTE,12,"bold"))
        self.titulo_biblioteca.pack(side="left")
        botao(cab,"×",self.fechar_catalogo).pack(side="right")
        arvore = ttk.Treeview(self.painel.conteudo,show="tree",selectmode="browse",height=9)
        self.arvore = arvore
        arvore.column("#0",width=210,stretch=True)
        scroll = ttk.Scrollbar(self.painel.conteudo,command=arvore.yview)
        scroll.pack(side="right",fill="y")
        arvore.configure(yscrollcommand=scroll.set)
        arvore.pack(fill="both",expand=True)
        arvore.bind("<ButtonRelease-1>",lambda e:self.escolher(arvore.identify_row(e.y)))
        arvore.bind("<Return>",lambda e:self.escolher(arvore.focus()))
        self.amostra = Cartao(self.area)
        self.amostra_tipo = None
        self.simbolo_amostra = tk.Canvas(self.amostra.conteudo,width=176,height=138,bg="white",highlightthickness=0)
        self.simbolo_amostra.pack()
        arvore.bind("<Motion>",lambda e:self.prever_componente(arvore.identify_row(e.y)))
        arvore.bind("<MouseWheel>",lambda e:arvore.after_idle(self.prever_sob_cursor))
        arvore.bind("<Leave>",lambda e:self.prever_componente(None))
        self.painel.bind("<Unmap>",lambda e:self.prever_componente(None))

        self.categorias = Cartao(self.area,padding=4)
        self.categorias.place(x=14,y=12,anchor="nw")
        self.area.bind("<Configure>",lambda e:self.limitar_bibliotecas(),add="+")
        self.pacote_catalogo = None
        self.painel_bibliotecas = Cartao(self.area,padding=12)
        cab_bib = tk.Frame(self.painel_bibliotecas.conteudo,bg="white")
        cab_bib.pack(fill="x")
        tk.Label(cab_bib,text="Bibliotecas",bg="white",fg=TINTA,font=(FONTE,12,"bold")).pack(side="left")
        botao(cab_bib,"×",self.biblioteca).pack(side="right")
        tk.Label(self.painel_bibliotecas.conteudo,text="Marque as bibliotecas que deseja usar.",bg="white",fg="#63756d").pack(anchor="w",pady=(2,8))
        self.lista_bibliotecas = tk.Frame(self.painel_bibliotecas.conteudo,bg="white")
        self.lista_bibliotecas.pack(fill="x")
        self.checks_bibliotecas = {}
        self.botoes_bibliotecas = {}
        self.timer_catalogo = None
        root.bind("<Destroy>",lambda e:self.manter_catalogo() if e.widget==root else None,add="+")
        for widget in (self.painel,self.arvore,self.categorias):
            widget.bind("<Enter>",self.manter_catalogo,add="+")
            widget.bind("<Leave>",self.agendar_fechar_catalogo,add="+")
        self.painel_grade = Cartao(self.area,padding=12)
        corpo = self.painel_grade.conteudo
        tk.Label(corpo,text="Fundo da folha",bg="white",fg=TINTA,font=(FONTE,12,"bold")).pack(anchor="w")
        self.tipo_grade = Faixa(corpo,[("linhas","Quadrados"),("pontos","Pontos"),("nenhuma","Sem grade")],lambda v:self.definir_grade("tipo",v),largura=260)
        self.tipo_grade.pack(pady=8)
        tk.Label(corpo,text="Espaçamento visual (encaixe fixo de 10)",bg="white",fg=TINTA).pack(anchor="w")
        self.passo_grade = Faixa(corpo,[(10,"Pequeno"),(20,"Médio"),(40,"Grande")],lambda v:self.definir_grade("passo",v),largura=260)
        self.passo_grade.pack(pady=8)
        botao(corpo,"Fechar",self.configurar_grade).pack(anchor="e")

        self.assinatura_catalogo = None
        self.contexto = Cartao(self.area,padding=6)
        self.acoes = tk.Frame(self.contexto.conteudo,bg="white")
        self.contagem_grupo = tk.Label(self.acoes,bg="white",fg=VERDE,font=(FONTE,9,"bold"))
        for texto,cmd in [("Girar",lambda:self.transformacao("rotacao")),("Espelhar",lambda:self.transformacao("espelho")),
                          ("Identificar",self.editar),("Excluir",self.excluir)]:
            acao = botao(self.acoes,texto,cmd)
            acao.pack(side="left")
            if texto=="Identificar":
                self.identificar_botao = acao
        self.cores = tk.Frame(self.contexto.conteudo,bg="white")
        for cor in CORES:
            botao(self.cores,"●",lambda v=cor:self.mudar_cor(v),cor=cor).pack(side="left")
        self.fios = tk.Frame(self.contexto.conteudo,bg="white")
        self.remover = botao(self.contexto.conteudo,"Excluir",self.excluir)
        self.rotulo_conexao = tk.Label(self.fios,text="Conexão",bg="white",fg=TINTA)
        self.rotulo_conexao.pack(side="left",padx=4)
        self.escolha_condutor = Faixa(self.fios,[(v,v) for v in self.pacote.conexoes["categorias"] if v not in self.pacote.conexoes.get("categorias_ocultas",[])],self.selecionar_condutor,largura=330)
        self.escolha_condutor.pack(side="left")

        moldura = tk.Canvas(self.area,bg=PAPEL,highlightthickness=0)
        self.cartao_mapa = moldura
        moldura.place(x=14,rely=1,y=-14,anchor="sw")
        cartao = tk.Frame(moldura,bg="white")
        moldura.create_window(10,8,window=cartao,anchor="nw")
        def ajustar_moldura(e):
            w,h = e.width+20,e.height+16
            moldura.configure(width=w,height=h)
            moldura.delete("fundo")
            arredondado(moldura,1,1,w-1,h-1,16,"white","#cadbd1")
            moldura.addtag_withtag("fundo",moldura.find_all()[-1])
            moldura.tag_lower("fundo")
        cartao.bind("<Configure>",ajustar_moldura)
        cab = tk.Frame(cartao,bg="white",cursor="fleur")
        cab.pack(fill="x")
        titulo = tk.Label(cab,text="⠿  Minimapa",bg="white",fg=TINTA,font=(FONTE,9,"bold"),cursor="fleur")
        titulo.pack(side="left")
        self.posicao_mapa = None
        for widget in (cab,titulo):
            widget.bind("<Button-1>",self.iniciar_arrasto_mapa)
            widget.bind("<B1-Motion>",self.arrastar_mapa)
        self.area.bind("<Configure>",lambda e:self.limitar_mapa(),add="+")
        marcar = botao(cab,"+",lambda:self.popup(marcar,menu_marcas))
        marcar.pack(side="right")
        menu_marcas = tk.Menu(root,tearoff=False)
        self.slots = {}
        for k in (1,2,3):
            menu_marcas.add_command(label=f"Marcar posição {k}",command=lambda n=k:self.marcar(n))
        self.minimapa = tk.Canvas(cartao,width=122,height=122,bg="#f3f7f4",highlightthickness=0,cursor="crosshair")
        self.minimapa.pack()
        self.minimapa.bind("<Button-1>",self.navegar_mapa)
        fila = tk.Frame(cartao,bg="white")
        fila.pack(fill="x",pady=(5,0))
        for k in (1,2,3):
            self.slots[k] = botao(fila,str(k),lambda n=k:self.visitar(n))
            self.slots[k].pack(side="left",fill="x",expand=True,padx=1)
        zoom = tk.Frame(self.area,bg="white",highlightbackground="#cfdcd5",highlightthickness=1)
        zoom.place(relx=1,rely=1,x=-14,y=-14,anchor="se")
        botao(zoom,"−",lambda:self.aplicar_zoom(self.zoom/1.2)).pack(side="left")
        botao(zoom,"",lambda:self.aplicar_zoom(1),textvariable=self.indice_zoom).pack(side="left")
        botao(zoom,"+",lambda:self.aplicar_zoom(self.zoom*1.2)).pack(side="left")

    def popup(self,widget,menu):
        menu.tk_popup(widget.winfo_rootx(),widget.winfo_rooty()+widget.winfo_height())

    def selecionar_condutor(self,valor):
        self.condutor.set(valor)
        self.escolha_condutor.set(valor)
        self.c.focus_set()

    def prever_sob_cursor(self):
        y = self.arvore.winfo_pointery()-self.arvore.winfo_rooty()
        if self.arvore.winfo_containing(self.arvore.winfo_pointerx(),self.arvore.winfo_pointery())==self.arvore:
            self.prever_componente(self.arvore.identify_row(y))

    def prever_componente(self,tipo):
        if self.amostra_tipo and self.arvore.exists(self.amostra_tipo) and (self.amostra_tipo!=tipo or not self.painel.winfo_manager()):
            self.arvore.item(self.amostra_tipo,tags=())
        if not tipo or not self.pacote_catalogo or tipo not in self.pacote_catalogo.componentes or not self.painel.winfo_manager():
            self.amostra.place_forget()
            self.amostra_tipo = None
            return
        if tipo==self.amostra_tipo:
            return
        self.amostra_tipo = tipo
        self.arvore.tag_configure("sobre",background="#e6f3eb",foreground=VERDE)
        self.arvore.item(tipo,tags=("sobre",))
        c = self.simbolo_amostra
        c.delete("all")
        item = dict(x=88,y=62,tipo=tipo,nome=tipo)
        desenhar(c,"amostra",item,self.pacote_catalogo,False,None)
        c.scale("all",88,62,1.28,1.28)
        x = self.painel.winfo_x()-self.amostra.winfo_reqwidth()-5
        if x<0:
            x = self.painel.winfo_x()+self.painel.winfo_width()+5
        self.amostra.place(x=max(0,min(x,self.area.winfo_width()-self.amostra.winfo_reqwidth())),y=self.painel.winfo_y(),anchor="nw")
        self.amostra.levantar()

    def configurar_grade(self):
        if self.painel_grade.winfo_manager():
            self.painel_grade.place_forget()
        else:
            self.tipo_grade.set(self.dados.get("grade",{}).get("tipo","linhas"))
            self.passo_grade.set(self.dados.get("grade",{}).get("passo",40))
            self.painel_grade.place(x=14,y=12)
            self.painel_grade.levantar()

    def definir_grade(self,chave,valor):
        self.lembrar()
        self.dados.setdefault("grade",{})[chave] = valor
        self.render()
        self.tipo_grade.set(self.dados["grade"].get("tipo","linhas"))
        self.passo_grade.set(self.dados["grade"].get("passo",40))

    def altura_barra(self):
        return 76

    def iniciar_arrasto_bibliotecas(self,e):
        self.fechar_catalogo()
        self.painel_bibliotecas.place_forget()
        self.origem_painel = (e.x_root-self.categorias.winfo_x(),e.y_root-self.categorias.winfo_y())

    def arrastar_bibliotecas(self,e):
        dx,dy = self.origem_painel
        self.categorias.place(x=e.x_root-dx,y=e.y_root-dy)
        self.categorias.update_idletasks()
        self.limitar_bibliotecas()

    def limitar_bibliotecas(self):
        w,h = self.area.winfo_width(),self.area.winfo_height()
        if w<=1 or h<=1:
            return
        x = min(max(0,self.categorias.winfo_x()),max(0,w-self.categorias.winfo_reqwidth()))
        y = min(max(0,self.categorias.winfo_y()),max(0,h-self.categorias.winfo_reqheight()))
        self.categorias.place(x=x,y=y)

    def posicionar_catalogo(self,painel):
        painel.place(x=0,y=0,relx=0,anchor="nw")
        self.area.update_idletasks()
        w,h = painel.winfo_reqwidth(),painel.winfo_reqheight()
        x = self.categorias.winfo_x()+self.categorias.winfo_width()+8
        if x+w>self.area.winfo_width():
            x = self.categorias.winfo_x()-w-8
        x = max(0,min(x,self.area.winfo_width()-w))
        y = max(0,min(self.categorias.winfo_y(),self.area.winfo_height()-h))
        painel.place(x=x,y=y,relx=0,anchor="nw")
        painel.levantar()

    def fechar_catalogo(self):
        self.manter_catalogo()
        self.prever_componente(None)
        self.painel.place_forget()

    def manter_catalogo(self,e=None):
        if self.timer_catalogo is not None:
            self.root.after_cancel(self.timer_catalogo)
            self.timer_catalogo = None

    def agendar_fechar_catalogo(self,e=None):
        self.manter_catalogo()
        def conferir():
            self.timer_catalogo = None
            x,y = self.root.winfo_pointerxy()
            w = self.root.winfo_containing(x,y)
            while w is not None:
                if w in (self.painel,self.categorias,self.amostra):
                    return
                w = getattr(w,"master",None)
            self.fechar_catalogo()
        self.timer_catalogo = self.root.after(350,conferir)

    def abrir_biblioteca(self,id_):
        if id_ not in {ref["id"] for ref in self.dados.get("bibliotecas",[])}:
            return
        self.manter_catalogo()
        self.painel_bibliotecas.place_forget()
        self.prever_componente(None)
        self.pacote_catalogo = obter(id_)
        self.arvore.delete(*self.arvore.get_children())
        for grupo,tipos in self.pacote_catalogo.categorias.items():
            self.arvore.insert("","end",iid=grupo,text=grupo,open=True)
            for tipo in tipos:
                self.arvore.insert(grupo,"end",iid=tipo,text=tipo)
        self.titulo_biblioteca.configure(text=self.pacote_catalogo.nome)
        self.arvore.yview_moveto(0)
        self.posicionar_catalogo(self.painel)
        self.painel.levantar()

    def biblioteca(self):
        if self.painel_bibliotecas.winfo_manager():
            self.painel_bibliotecas.place_forget()
        else:
            self.fechar_catalogo()
            self.posicionar_catalogo(self.painel_bibliotecas)
            self.painel_bibliotecas.levantar()

    def ferramentas_bibliotecas(self):
        return {t for ref in self.dados.get("bibliotecas",[])
                for t in obter(ref["id"]).dados.get("biblioteca",{}).get("ferramentas",["Ligar","Derivar"])}

    def habilitar_grupo(self,ids,habilitada):
        self.concluir_digitacao()
        self.lembrar()
        refs = [r for r in self.dados.get("bibliotecas",[]) if r["id"] not in ids]
        if habilitada:
            refs.extend(referencia(obter(k)) for k in ids)
        self.dados["bibliotecas"] = refs
        self.ferramenta("Selecionar")
        self.biblioteca_ativa = None
        self.fechar_catalogo()
        self.render()

    def ferramenta_biblioteca(self,modo):
        ids = [r["id"] for r in self.dados.get("bibliotecas",[])
               if modo in obter(r["id"]).dados.get("biblioteca",{}).get("ferramentas",["Ligar","Derivar"])]
        if ids:
            if self.biblioteca_ativa not in ids:
                self.biblioteca_ativa = ids[0]
            self.fechar_catalogo()
            self.ferramenta(modo)
            self.c.focus_set()

    def habilitar_biblioteca(self,id_,habilitada):
        refs = self.dados.get("bibliotecas",[])
        if (id_ in {ref["id"] for ref in refs})==habilitada:
            return
        self.concluir_digitacao()
        self.lembrar()
        self.dados["bibliotecas"] = [r for r in refs if r["id"]!=id_]
        if habilitada:
            self.dados["bibliotecas"].append(referencia(obter(id_)))
        elif self.biblioteca_ativa==id_ and self.modo in self.pacote.componentes:
            self.ferramenta("Selecionar")
            self.biblioteca_ativa = None
        if self.modo in ("Ligar","Derivar") and self.modo not in self.ferramentas_bibliotecas():
            self.ferramenta("Selecionar")
        self.fechar_catalogo()
        self.render()

    def pintar_paleta(self):
        p = self.paleta
        p.delete("all")
        arredondado(p,3,5,443,55,13,"#e0e7e2")
        arredondado(p,2,2,442,52,13,"white","#d2dcd5")
        self.centros = {}
        x = 24
        for modo in self.ferramentas:
            if modo in ("Ligar","Retângulo"):
                p.create_line(x-19,14,x-19,39,fill="#dbe2dd")
                x+=5
            self.centros[modo] = x
            ativo = self.modo==modo
            if ativo:
                arredondado(p,x-16,10,x+16,44,7,"#d4eee0")
            icone(p,modo,x,27,VERDE if ativo else "#42544e")
            x+=38

    def ferramenta_em(self,x):
        return next((m for m,p in self.centros.items() if abs(x-p)<=17),None)

    def clicar_ferramenta(self,e):
        modo = self.ferramenta_em(e.x)
        if modo:
            self.dica.place_forget()
            self.painel.place_forget()
            self.ferramenta(modo)
            self.c.focus_set()

    def dica_ferramenta(self,e):
        modo = self.ferramenta_em(e.x)
        if modo:
            self.dica.configure(text=modo)
            self.dica.place(x=self.paleta.winfo_x()+self.centros[modo],y=66,anchor="n")
            self.dica.lift()
        else:
            self.dica.place_forget()

    def sincronizar_catalogo(self):
        ids = tuple(ref["id"] for ref in self.dados.get("bibliotecas",[]))
        assinatura = (tuple(self.dados["folhas"]),ids,tuple(REGISTRO))
        if assinatura!=self.assinatura_catalogo:
            self.assinatura_catalogo = assinatura
            self.fechar_catalogo()
            for widget in self.barra_abas.winfo_children():
                widget.destroy()
            self.tabs.clear()
            # A single canvas needs no tab bar; preserve tabs of imported multi-sheet projects.
            if len(self.dados["folhas"])>1:
                for nome in self.dados["folhas"]:
                    def abrir(n=nome):
                        self.aba.set(n)
                        self.trocar()
                    self.tabs[nome] = botao(self.barra_abas,nome,abrir)
                    self.tabs[nome].pack(side="left",padx=(0,3))
            for widget in self.categorias.conteudo.winfo_children():
                widget.destroy()
            self.botoes_bibliotecas.clear()
            nomes_grupos = {obter(k).dados.get("biblioteca",{}).get("nome","Bibliotecas") for k in ids}
            titulo = next(iter(nomes_grupos)) if len(nomes_grupos)==1 else "Bibliotecas"
            alca = tk.Label(self.categorias.conteudo,text="⠿ "+titulo,bg="white",fg=TINTA,cursor="fleur",font=(FONTE,10,"bold"),pady=7)
            alca.grid(row=0,column=0,sticky="ew")
            alca.bind("<ButtonPress-1>",self.iniciar_arrasto_bibliotecas)
            alca.bind("<B1-Motion>",self.arrastar_bibliotecas)
            for i,id_ in enumerate(ids):
                p = obter(id_)
                b = BotaoMenu(self.categorias.conteudo,p.nome,lambda k=id_:self.abrir_biblioteca(k),largura=142)
                b.grid(row=i+1,column=0,padx=1,pady=2)
                b.bind("<Enter>",lambda e,k=id_:self.abrir_biblioteca(k),add="+")
                b.bind("<Leave>",self.agendar_fechar_catalogo,add="+")
                self.botoes_bibliotecas[id_] = b
            i = len(ids)
            for modo in ("Ligar","Derivar"):
                if modo in self.ferramentas_bibliotecas():
                    i += 1
                    btn = tk.Canvas(self.categorias.conteudo,width=140,height=34,bg="white",highlightthickness=0,cursor="hand2",takefocus=True)
                    btn.grid(row=i,column=0,padx=1,pady=2)
                    arredondado(btn,1,1,139,33,8,"#e7f0e9")
                    icone(btn,modo,70,17,VERDE)
                    for evento in ("<ButtonRelease-1>","<Return>","<space>"):
                        btn.bind(evento,lambda e,m=modo:self.ferramenta_biblioteca(m))
                    def dica_fio(e,m=modo):
                        self.dica.configure(text="Fio — ligar (L)" if m=="Ligar" else "Derivar fio (D)")
                        self.dica.place(x=e.widget.winfo_rootx()-self.area.winfo_rootx()+e.widget.winfo_width()+8,
                                        y=e.widget.winfo_rooty()-self.area.winfo_rooty())
                        self.dica.lift()
                    btn.bind("<Enter>",dica_fio)
                    btn.bind("<Leave>",lambda e:self.dica.place_forget())
            BotaoMenu(self.categorias.conteudo,"Bibliotecas +",self.biblioteca,largura=142).grid(row=i+1,column=0,padx=1,pady=2)
            for widget in self.lista_bibliotecas.winfo_children():
                widget.destroy()
            self.checks_bibliotecas.clear()
            grupos = {}
            for p in REGISTRO.values():
                grupo = p.dados.get("biblioteca")
                if grupo:
                    grupos.setdefault(grupo["id"],(grupo["nome"],[]))[1].append(p.id)
            for nome,membros in grupos.values():
                var = tk.BooleanVar(value=all(k in ids for k in membros))
                tk.Checkbutton(self.lista_bibliotecas,text=nome,variable=var,
                    command=lambda ks=tuple(membros),v=var:self.habilitar_grupo(ks,v.get()),
                    bg="white",activebackground="white",fg=TINTA,anchor="w",font=(FONTE,10,"bold"),pady=8).pack(fill="x")
            for p in REGISTRO.values():
                var = tk.BooleanVar(value=p.id in ids)
                check = tk.Checkbutton(self.lista_bibliotecas,text=p.nome,variable=var,
                    command=lambda k=p.id,v=var:self.habilitar_biblioteca(k,v.get()),
                    bg="white",activebackground="white",fg=TINTA,cursor="hand2",anchor="w",padx=4,pady=6)
                check.pack(fill="x")
                self.checks_bibliotecas[p.id] = (var,check)
        for id_,(var,_) in self.checks_bibliotecas.items():
            var.set(id_ in ids)
        self.escolha_condutor.opcoes = [(v,v) for v in self.pacote.conexoes["categorias"] if v not in self.pacote.conexoes.get("categorias_ocultas",[])]
        self.rotulo_conexao.configure(text=self.pacote.conexoes.get("rotulo","Conexão"))
        if self.condutor.get() not in dict(self.escolha_condutor.opcoes):
            self.condutor.set(self.pacote.conexoes["padrao"])
        self.escolha_condutor.set(self.condutor.get())

    def atualizar_interface(self):
        self.sincronizar_catalogo()
        self.pintar_paleta()
        self.modo_status.set(self.modo)
        self.botao_guias.configure(bg="#def0e4" if self.guias_ativas.get() else "white")
        for f,aba in self.tabs.items():
            aba.configure(bg="#244438" if self.aba.get()==f else "white",fg="white" if self.aba.get()==f else TINTA)
        self.titulo_projeto.set(self.path.stem if self.path else "Sem título")
        for grupo in (self.fios,self.acoes,self.cores):
            grupo.pack_forget()
        self.remover.pack_forget()
        if self.modo in ("Ligar","Derivar"):
            grupo = self.fios
            self.escolha_condutor.set(self.condutor.get())
        elif self.modo in FORMAS:
            grupo = self.cores
        elif self.selecao in self.folha["componentes"]:
            grupo = self.acoes
            if len(self.grupo)>1:
                self.contagem_grupo.configure(text=f"{len(self.grupo)} selecionados")
                self.contagem_grupo.pack(side="left",before=self.acoes.winfo_children()[1])
                self.identificar_botao.configure(state="disabled")
            else:
                self.contagem_grupo.pack_forget()
                self.identificar_botao.configure(state="normal")
        else:
            grupo = None
        if grupo:
            grupo.pack(side="left")
        propriedades = self.atualizar_propriedades()
        pode_excluir = self.modo=="Selecionar" and self.selecao and grupo!=self.acoes and not propriedades
        if pode_excluir:
            self.remover.pack(side="left")
        if grupo or pode_excluir:
            self.contexto.place(relx=.5,y=self.altura_barra(),anchor="n")
        else:
            self.contexto.place_forget()
        self.desenhar_mapa()

    def atalhos(self):
        janela = tk.Toplevel(self.root)
        janela.title("Atalhos"); janela.configure(bg="white")
        for linha,(teclas,acao) in enumerate([
            ("V  /  H","Selecionar / mover a tela"),("L  /  D","Fio: ligar / derivar (biblioteca habilitada)"),("Ctrl + clique em linha","Iniciar seta ramificada"),("Seta curva: Shift + clique","Fixar dobra; clique sem Shift conclui"),("R  /  E","Girar / espelhar"),
            ("G","Alternar guias"),("Shift ao inserir","Encaixar o terminal na malha de 10 unidades"),("Shift + clique","Fixar uma dobra"),("Esc  /  Delete","Cancelar / excluir"),
            ("Arrastar no fundo","Selecionar componentes por área"),("Shift / Ctrl + clique","Adicionar / alternar componente"),
            ("Botão direito + arraste","Mover a tela"),
            ("Roda","Zoom no cursor"),("1  /  2  /  3","Visitar posição marcada"),("Shift + 1, 2 ou 3","Marcar a vista atual"),
            ("Ctrl + Z / Y","Desfazer / refazer"),("Ctrl + S / O","Salvar / abrir")]):
            for coluna,valor in enumerate((teclas,acao)):
                tk.Label(janela,text=valor,bg="white",fg=TINTA,font=(FONTE,10,"bold" if coluna==0 else "normal")).grid(row=linha,column=coluna,sticky="w",padx=14,pady=5)
        janela.bind("<Escape>",lambda e:janela.destroy())
