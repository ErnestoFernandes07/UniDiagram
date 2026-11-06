import copy
from datetime import datetime
from math import dist
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from uuid import uuid4

from nucleo.documento import carregar, novo, salvar, ponta_do_projeto
from nucleo.pacotes import pacote_da_folha, pacote_do_objeto, obter, referencia
from insercao import Insercao
from integracao_ia import IntegracaoIA
from nucleo.simbolos import desenhar, posicao_nome
from ligacoes import Ligacoes
from tracado import limpar, alinhar_gesto_fio, automatico, deslocar_trecho, mover_vertice, trechos_curvos


from interface import Interface
from navegacao import Navegacao
from formas import Desenho, FORMAS, contem, desenhar_forma
from texto import TextoNaFolha
from propriedades import Propriedades
from selecao import Selecao
from rotulos import posicao_etiqueta


class Editor(Interface, Navegacao, Desenho, Ligacoes, TextoNaFolha, Propriedades, Selecao, Insercao, IntegracaoIA):
    def __init__(self, root, pacotes=None):
        self.root = root
        root.geometry("1150x760")
        root.minsize(800, 500)
        self.dados = novo(pacotes)
        self.path = None
        self.gravado = copy.deepcopy(self.dados)
        self.historico = []
        self.futuros = []
        self.curva_fixa = []
        self.curva_previa = None
        self.modo = "Selecionar"
        self.zoom = 1.0
        self.arrasto_fio = None
        self.tamanho_nome_padrao = 12
        self.arrasto_nome = None
        self.guia_fio = None
        self.arrasto_etiqueta = None
        self.referencias = None
        self.selecao = self.origem = self.arrasto = None
        self.grupo = set()
        self.caixa_selecao = self.inicio_grupo = None
        self.biblioteca_ativa = None
        self.condutor = tk.StringVar(value="Conexão")
        self.condutores_por_folha = {n:pacote_da_folha(f,n).conexoes["padrao"] for n,f in self.dados["folhas"].items()}
        self.guias_ativas = tk.BooleanVar(value=True)
        self.leitura_guias = tk.StringVar()
        self.status = tk.StringVar()
        self.forma_previa = self.gesto_forma = None
        self.texto_rascunho = self.ima = None
        self.cameras = {}
        self.cursor_insercao = None
        self.shift_insercao = False
        self.rotacao_insercao = 0
        self.espelho_insercao = False
        self.montar_interface()
        self.preparar_entrada_texto()
        self.montar_propriedades()
        self.c.bind("<Configure>",lambda e:self.render())
        self.c.bind("<Button-1>",self.clique)
        self.c.bind("<B1-Motion>",lambda e:self.agendar_movimento(self.mover,e))
        self.c.bind("<Motion>",lambda e:self.agendar_movimento(self.movimento_livre,e))
        self.c.bind("<Leave>",self.sair_insercao)
        for tecla in ("Shift_L","Shift_R"):
            root.bind("<KeyPress-"+tecla+">",lambda e:self.alternar_snap(True))
            root.bind("<KeyRelease-"+tecla+">",lambda e:self.alternar_snap(False))
        self.c.bind("<ButtonRelease-1>",self.soltar)
        self.c.bind("<MouseWheel>",lambda e:self.aplicar_zoom(self.zoom * (1.2 if e.delta>0 else 1/1.2), e.x, e.y))
        self.c.bind("<Double-Button-1>",self.duplo_clique)
        self.c.bind("<ButtonPress-2>",lambda e:self.c.scan_mark(e.x,e.y))
        self.c.bind("<B2-Motion>",lambda e:self.agendar_movimento(self.arrastar_tela,e))
        self.c.bind("<ButtonRelease-2>",self.terminar_pan)
        self.c.bind("<ButtonPress-3>",self.iniciar_pan_direito)
        self.c.bind("<B3-Motion>",lambda e:self.agendar_movimento(self.arrastar_tela,e))
        self.c.bind("<ButtonRelease-3>",self.terminar_pan)
        for tecla,cmd in [("<Control-s>",self.salvar),("<Control-o>",self.abrir),
                          ("<Control-z>",self.desfazer),("<Control-y>",self.refazer),
                          ("r",lambda:self.transformacao("rotacao")),("e",lambda:self.transformacao("espelho")),
                          ("d",lambda:self.ferramenta("Derivar")),("l",lambda:self.ferramenta("Ligar")),
                          ("v",lambda:self.ferramenta("Selecionar")),
                          ("g",self.alternar_guias),
                          ("<Delete>",self.excluir),("<Escape>",lambda:self.ferramenta("Selecionar"))]:
            root.bind(tecla,lambda e,acao=cmd:acao())
        root.bind("h",lambda e:self.ferramenta("Mover"))
        for numero,simbolo in enumerate(("exclam","at","numbersign"),1):
            root.bind(str(numero),lambda e,n=numero:self.visitar(n))
            root.bind("<KeyPress-"+simbolo+">",lambda e,n=numero:self.marcar(n))
            root.bind("<Shift-KeyPress-"+str(numero)+">",lambda e,n=numero:self.marcar(n))
        root.protocol("WM_DELETE_WINDOW",self.fechar_editor)
        self.ferramenta("Selecionar")

    def alternar_guias(self):
        self.guias_ativas.set(not self.guias_ativas.get())
        self.atualizar_guias()

    def atualizar_guias(self):
        if self.referencias:
            self.referencias.visitados.clear()
            self.referencias.eixos = [None,None]
        self.mostrar_referencias()
        self.atualizar_interface()

    @property
    def pacote(self):
        return obter(self.biblioteca_ativa) if self.biblioteca_ativa else pacote_da_folha(self.folha,self.dados["ativa"])

    def pacote_para(self,obj):
        return pacote_do_objeto(obj,self.folha,self.dados["ativa"])

    @property
    def folha(self):
        return self.dados["folhas"][self.dados["ativa"]]

    def lembrar(self):
        self.historico.append(copy.deepcopy(self.dados))
        self.historico = self.historico[-80:]
        self.futuros.clear()

    def restaurar(self, origem, destino):
        self.concluir_digitacao()
        if origem:
            destino.append(self.dados)
            self.dados = origem.pop()
            self.condutores_por_folha = {n:pacote_da_folha(f,n).conexoes["padrao"] for n,f in self.dados["folhas"].items()}
            self.cameras = copy.deepcopy(self.dados.get("vistas",{}))
            self.posicao_mapa = self.dados.get("minimapa")
            if self.posicao_mapa is None:
                self.cartao_mapa.place(x=14,rely=1,y=-14,relx=0,anchor="sw")
            else:
                self.limitar_mapa()
            self.sincronizar()
            vista = self.cameras.get(self.dados["ativa"])
            if vista:
                self.ir_camera(**vista)

    def desfazer(self):
        self.restaurar(self.historico,self.futuros)

    def refazer(self):
        self.restaurar(self.futuros,self.historico)

    def sincronizar(self):
        self.biblioteca_ativa = None
        self.aba.set(self.dados["ativa"])
        self.selecao = self.arrasto = None
        self.ferramenta("Selecionar")

    def trocar(self):
        self.concluir_digitacao()
        anterior = self.dados["ativa"]
        self.condutores_por_folha[anterior] = self.condutor.get()
        self.cameras[anterior] = self.camera()
        self.dados["ativa"] = self.aba.get()
        self.condutor.set(self.condutores_por_folha[self.aba.get()])
        self.sincronizar()
        if self.aba.get() in self.cameras:
            self.ir_camera(**self.cameras[self.aba.get()])
        else:
            self.zoom = 1
            self.indice_zoom.set("100%")
            self.posicionar_vista(0,0)
            self.render()

    def escolher(self,tipo):
        pacote = self.pacote_catalogo
        if pacote and tipo in pacote.componentes:
            self.biblioteca_ativa = pacote.id
            self.condutor.set(pacote.conexoes["padrao"])
            self.ferramenta(tipo)
            self.painel.place_forget()
            self.c.focus_set()

    def ferramenta(self, modo):
        self.cancelar_movimento()
        if modo in ("Ligar","Derivar") and modo not in self.ferramentas_bibliotecas():
            self.status.set("Habilite uma biblioteca com ferramentas de conexão para usar fios.")
            return
        self.curva_fixa = []
        self.curva_previa = None
        self.concluir_digitacao()
        self.ima = None
        self.grupo.clear()
        self.forma_previa = self.gesto_forma = None
        self.modo = modo
        self.cursor_insercao = None
        self.rotacao_insercao = 0
        self.espelho_insercao = False
        self.ferramenta_ativa.set(modo)
        self.origem = None
        self.inicio = self.ultimo_alvo = None
        self.guias = []
        self.soltar()
        self.c.configure(cursor=self.cursor_ferramenta())
        instrucoes = {"Selecionar":"Arraste no fundo para selecionar. Use o botão direito para mover a tela.",
                      "Ligar":"Clique em um terminal ou fio para começar.",
                      "Derivar":"Clique em um fio para iniciar uma derivação."}
        instrucoes.update({tipo:"Clique e arraste para desenhar." for tipo in FORMAS})
        instrucoes["Seta curva"] = "Clique para iniciar; Shift + clique fixa dobras; clique conclui; Esc cancela."
        instrucoes.update(Texto="Clique na folha para adicionar texto.",Mover="Arraste para navegar pelo desenho.")
        self.status.set(instrucoes.get(modo,f"{modo}   ·   Terminal no cursor · Shift encaixa na malha · R gira · E espelha · Esc cancela."))
        self.render()

    def cursor_ferramenta(self):
        return {"Selecionar":"arrow","Mover":"fleur"}.get(self.modo,"crosshair")

    def iniciar_pan_direito(self,e):
        self.c.scan_mark(e.x,e.y)
        self.c.configure(cursor="fleur")

    def ponta(self, ref):
        return ponta_do_projeto(self.folha,self.dados["ativa"],ref)

    def transformacao(self, chave):
        if self.modo in self.pacote.componentes:
            if chave=="rotacao":
                self.rotacao_insercao = (self.rotacao_insercao+90)%360
            else:
                self.espelho_insercao = not self.espelho_insercao
            self.previa_componente()
            return
        if self.inicio:
            return
        forma = self.objeto_inspecionado()
        if chave=="rotacao" and forma and forma.get("tipo")=="Texto":
            self.definir_propriedade("angulo",(forma.get("angulo",0)+90)%360)
            return
        ids = self.grupo or {self.selecao}
        if self.selecao not in self.folha["componentes"]:
            self.status.set("Selecione um componente para girar ou espelhar.")
            return
        self.lembrar()
        caminhos = self.rotas_grupo() if self.grupo else self.caminhos_ligados(self.selecao)
        for k in ids:
            item = self.folha["componentes"][k]
            if chave == "rotacao":
                item[chave] = (item.get(chave,0)+90) % 360
            else:
                item[chave] = not item.get(chave,False)
        self.acompanhar_pontas(caminhos)
        self.render()

    def caminhos_ligados(self, chave):
        return {id_:self.caminho(fio) for id_,fio in self.folha["ligacoes"].items()
                if "pontos" in fio and chave in (fio["a"][0],fio["b"][0])}

    def acompanhar_pontas(self, caminhos):
        for id_,original in caminhos.items():
            fio = self.folha["ligacoes"][id_]
            pontos = original
            for lado in ("a","b"):
                indice = 0 if lado=="a" else len(pontos)-1
                destino = self.ponta(fio[lado])
                if tuple(pontos[indice]) != destino:
                    pontos = mover_vertice(pontos,indice,destino)
            pontos = limpar(pontos)
            fio["pontos"] = [list(p) for p in pontos[1:-1]]
        self.atualizar_ancoras()

    def aplicar_zoom(self, escala, x=None, y=None):
        if x is None:
            x,y = self.c.winfo_width()/2,self.c.winfo_height()/2
        px,py = self.c.canvasx(x)/self.zoom,self.c.canvasy(y)/self.zoom
        self.zoom = max(0.4,min(4,escala))
        self.indice_zoom.set(f"{self.zoom:.0%}")
        self.posicionar_vista(px*self.zoom-x,py*self.zoom-y)
        self.render()

    def caminho(self,fio):
        a,b = self.ponta(fio["a"]),self.ponta(fio["b"])
        if "pontos" in fio:
            return [a,*fio["pontos"],b]
        pontos = automatico(a,b)
        return pontos if len(pontos)>1 else [a,b]

    def cena(self,c,edicao):
        reusar=getattr(c,"reutilizar",lambda *args:False)
        for id_,forma in self.folha.get("formas",{}).items():
            if not (edicao and self.texto_rascunho is not None and id_==self.selecao):
                if not reusar("forma:"+id_,(forma,edicao and self.selecao==id_)):
                    desenhar_forma(c,id_,forma,edicao and self.selecao==id_)
        if edicao and self.curva_previa:
            desenhar_forma(c,"curva_previa",self.curva_previa)
        if edicao and self.forma_previa:
            desenhar_forma(c,"previa",self.forma_previa)
        for id_,fio in self.folha["ligacoes"].items():
            pontos = self.caminho(fio)
            ativo = edicao and self.selecao==id_
            cor = self.cor_do_condutor(fio["condutor"],fio.get("cor"),fio)
            if reusar("fio:"+id_,(fio,pontos,ativo,cor)):
                continue
            alpha = f"alpha:{fio.get('opacidade',100)}"
            for i,trecho in enumerate(trechos_curvos(pontos)):
                c.create_line(*trecho,fill=cor,width=fio.get("espessura",2),dash=(8,5) if fio.get("tracejado") else (),tags=("fio:"+id_,f"trecho:{i}",alpha))
            if ativo:
                for i,(x,y) in enumerate(pontos[1:-1]):
                    c.create_rectangle(x-4,y-4,x+4,y+4,fill="white",outline=cor,
                                       tags=("fio:"+id_,f"vertice:{i}"))
                for i,(a,b) in enumerate(zip(pontos,pontos[1:])):
                    if dist(a,b)>24:
                        x,y = (a[0]+b[0])/2,(a[1]+b[1])/2
                        c.create_oval(x-3,y-3,x+3,y+3,fill=cor,outline=cor,
                                      tags=("fio:"+id_,f"trecho:{i}"))
            if fio.get("mostrar_nome",fio["condutor"] not in self.pacote_para(fio).conexoes["nomes_ocultos"]):
                c.create_text(*posicao_etiqueta(pontos,fio.get("etiqueta")),text=fio["condutor"],
                              fill=cor,font=("Segoe UI",-11),tags=("fio:"+id_,"etiqueta",alpha))
        contagem = {}
        for fio in self.folha["ligacoes"].values():
            for ref in (fio["a"],fio["b"]):
                contagem[ref[0]] = contagem.get(ref[0],0)+1
        for id_,(x,y) in self.folha.get("nos",{}).items():
            cor = "#00786a" if edicao and self.selecao==id_ else "#263949"
            if reusar("no:"+id_,(x,y,cor,contagem.get(id_,0)>1)):
                continue
            c.create_oval(x-4,y-4,x+4,y+4,outline=cor,
                          fill=cor if contagem.get(id_,0)>1 else "white",tags="no:"+id_)
        for id_,item in self.folha["componentes"].items():
            if not reusar("item:"+id_,(item,edicao and (self.selecao==id_ or id_ in self.grupo),self.origem if edicao else None)):
                desenhar(c,id_,item,self.pacote_para(item),edicao and (self.selecao==id_ or id_ in self.grupo),self.origem if edicao else None)
        if edicao and self.texto_rascunho is not None:
            self.desenhar_digitacao(c)

    def render(self):
        c = self.c
        from canvas_retido import CanvasRetido
        if not hasattr(self,"canvas_retido"):
            self.canvas_retido=CanvasRetido(c)
        for obj in getattr(self,"sobreposicoes",()):
            c.delete(obj)
        retido=self.canvas_retido
        if getattr(retido,"folha",None) is not self.folha:
            retido.estados.clear()
            retido.folha=self.folha
        retido.iniciar(self.zoom)
        c=retido
        x,y,u,v = self.vista()
        grade = self.dados.get("grade",{})
        estilo = grade.get("tipo","linhas")
        passo = grade.get("passo",40)
        while passo*self.zoom<14:
            passo *= 2
        if estilo=="linhas":
            for i in range(int(x//passo)*passo,int(u)+passo,passo):
                c.create_line(i,y,i,v,fill="#e9eeea",tags="grade")
            for i in range(int(y//passo)*passo,int(v)+passo,passo):
                c.create_line(x,i,u,i,fill="#e9eeea",tags="grade")
        elif estilo=="pontos":
            r = 1/self.zoom
            for i in range(int(x//passo)*passo,int(u)+passo,passo):
                for j in range(int(y//passo)*passo,int(v)+passo,passo):
                    c.create_oval(i-r,j-r,i+r,j+r,fill="#cbd8d0",outline="",tags="grade")
        self.cena(c,True)
        retido.finalizar()
        c=self.c
        objetos = [*self.folha.get("formas",{}).values(),*self.folha["ligacoes"].values()]
        if self.texto_rascunho is not None:
            objetos.append(self.texto_rascunho)
        if any(obj.get("opacidade",100)<100 for obj in objetos):
            from imagem import compor_tela
            compor_tela(c)
        if self.ima is not None:
            px,py = (v*self.zoom for v in self.ima)
            c.create_oval(px-7,py-7,px+7,py+7,outline="#169b68",width=2,tags="ima")
        self.previa_componente()
        self.previa()
        self.mostrar_referencias()
        if self.guia_fio:
            eixo,valor = self.guia_fio
            coords = (x,valor,u,valor) if eixo==1 else (valor,y,valor,v)
            c.create_line(*[n*self.zoom for n in coords],fill="#4a9d70",dash=(4,5),tags="guia_fio")
        self.pintar_selecao()
        self.atualizar_interface()
        ids=set(retido.ordem)
        self.sobreposicoes=[obj for obj in c.find_all() if obj not in ids]
        self.root.title(f"{'* ' if self.dados != self.gravado else ''}{self.path.name if self.path else 'Sem título'} — M&Unifiliar")

    def clique(self,e):
        self.processar_movimento()
        self.c.focus_set()
        x,y = self.c.canvasx(e.x),self.c.canvasy(e.y)
        objetos = [self.c.gettags(obj) for obj in reversed(self.c.find_overlapping(x-4,y-4,x+4,y+4))]
        tags = [t for grupo in objetos for t in grupo]
        x,y = x/self.zoom,y/self.zoom
        if self.texto_rascunho is not None:
            if "forma:"+self.selecao in tags:
                self.posicionar_cursor((x,y))
                return
            self.concluir_digitacao()
        if self.modo=="Selecionar" and e.state&4 and self.ramificar_forma((x,y)):
            return
        if self.modo=="Seta curva":
            self.clique_curva((x,y),bool(e.state&1))
            return
        if self.modo=="Mover":
            self.pan = True
            self.c.scan_mark(e.x,e.y)
            return
        if self.modo in FORMAS:
            self.iniciar_forma((x,y),bool(e.state&1))
            self.render()
            return
        if self.modo in ("Ligar","Derivar"):
            self.clique_ligacao(e)
            return
        elif self.modo == "Selecionar":
            alvo = next((t for t in tags if t.startswith(("item:","fio:","no:","forma:"))),None)
            if any(f"forma:{self.selecao}" in grupo and any(t.startswith("alca:") for t in grupo) for grupo in objetos):
                alvo = f"forma:{self.selecao}"
            if not alvo:
                for id_,forma in reversed(self.folha.get("formas",{}).items()):
                    if contem(forma,(x,y)):
                        alvo = "forma:"+id_
                        break
            id_ = alvo.split(":")[1] if alvo else None
            mod = getattr(e,"state",0)&5
            if id_ in self.folha["componentes"] and "nome_componente" in tags and not mod and id_==self.selecao and len(self.grupo)<=1:
                item = self.folha["componentes"][id_]
                nx,ny = posicao_nome(item,self.pacote_para(item))
                self.arrasto_nome = (x,y,nx-item["x"],ny-item["y"],False)
                return
            if id_ in self.folha["componentes"]:
                self.escolher_componente(id_,mod,(x,y))
                self.render()
                return
            if alvo is None:
                self.iniciar_caixa((x,y),mod)
                self.render()
                return
            self.grupo.clear()
            self.selecao = id_
            if self.selecao in self.folha.get("formas",{}):
                alca = next((t for t in tags if t.startswith("alca:")),None)
                forma = self.folha["formas"][self.selecao]
                self.gesto_forma = ((x,y),copy.deepcopy(forma["pontos"]),int(alca.split(":")[1]) if alca else None,False)
                self.cor_forma.set(forma["cor"])
                self.status.set("Arraste para mover. Use as alças para ajustar o tamanho. Delete exclui.")
            elif self.selecao in self.folha.get("nos",{}):
                px,py = self.folha["nos"][self.selecao]
                self.arrasto = (x-px,y-py,False)
                self.rotas_arrasto = self.caminhos_ligados(self.selecao)
                ligados = [id_ for id_,fio in self.folha["ligacoes"].items()
                           if self.selecao in (fio["a"][0],fio["b"][0])]
                self.iniciar_referencias(ignorar_no=self.selecao,ignorar_fios=ligados)
                self.status.set("Arraste a junção. Passe por dois pontos para capturar suas guias de alinhamento.")
            elif self.selecao in self.folha["ligacoes"]:
                grupo = next(g for g in objetos if alvo in g)
                if "etiqueta" in grupo:
                    fio = self.folha["ligacoes"][self.selecao]
                    px,py = posicao_etiqueta(self.caminho(fio),fio.get("etiqueta"))
                    self.arrasto_etiqueta = (x,y,px-x,py-y,False)
                    self.status.set("Arraste o nome ao longo do fio. A caixa no painel controla sua visibilidade.")
                    self.render()
                    return
                trecho = next((t for t in grupo if t.startswith(("trecho:","vertice:"))),None)
                if trecho:
                    tipo,indice = trecho.split(":")
                    pontos = self.caminho(self.folha["ligacoes"][self.selecao])
                    self.arrasto_fio = (tipo,int(indice),x,y,pontos,False)
                    if tipo == "vertice":
                        self.iniciar_referencias(ignorar_fios=(self.selecao,))
                self.status.set("Arraste um canto e passe por uma junção ou terminal para capturar suas guias.")
        else:
            self.lembrar()
            self.selecao = uuid4().hex
            self.folha["componentes"][self.selecao] = self.componente_no_cursor((x,y),bool(e.state&1))
            self.cursor_insercao = None
        self.render()

    def mover_nome_componente(self,pos):
        x,y,dx,dy,iniciado = self.arrasto_nome
        if not iniciado:
            if dist((x,y),pos)*self.zoom<3:
                return
            self.lembrar()
            self.arrasto_nome = (x,y,dx,dy,True)
        self.folha["componentes"][self.selecao]["posicao_nome"] = [dx+pos[0]-x,dy+pos[1]-y]
        self.render()

    def soltar(self,e=None):
        if e is not None:
            self.processar_movimento()
        pos = (self.c.canvasx(e.x)/self.zoom,self.c.canvasy(e.y)/self.zoom) if e is not None else None
        if self.arrasto_nome and pos:
            self.mover_nome_componente(pos)
        self.arrasto_nome = None
        if self.arrasto_etiqueta and pos and self.arrasto_etiqueta[-1]:
            self.mover_etiqueta(pos)
        self.arrasto_etiqueta = None
        if self.caixa_selecao:
            if pos:
                self.estender_caixa(pos)
            self.caixa_selecao = None
            self.render()
        if self.inicio_grupo:
            if pos and self.moveu_grupo:
                self.deslocar_grupo(pos)
            elif pos and self.clique_simples and self.selecao:
                self.definir_grupo({self.selecao},self.selecao)
                self.render()
            self.inicio_grupo = None
        if e is not None and self.forma_previa:
            pos = (self.c.canvasx(e.x)/self.zoom,self.c.canvasy(e.y)/self.zoom)
            self.continuar_forma(pos,bool(e.state&1))
            pts = self.forma_previa["pontos"]
            if any(dist(pts[0],p)*self.zoom>=2 for p in pts[1:]):
                self.confirmar_forma()
            else:
                self.forma_previa = None
                self.render()
        if self.gesto_forma and e is not None and self.gesto_forma[-1]:
            self.editar_forma((self.c.canvasx(e.x)/self.zoom,self.c.canvasy(e.y)/self.zoom),bool(e.state&1))
        self.gesto_forma = None
        self.ima = None
        self.c.delete("ima")
        if e is not None and ((self.arrasto and self.arrasto[-1]) or
                              (self.arrasto_fio and self.arrasto_fio[-1])):
            self.mover(e)
        if e is not None and self.arrasto and self.arrasto[-1]:
            self.conectar_no_arrastado()
        self.arrasto = self.arrasto_fio = None
        self.guia_fio = None
        self.c.delete("guia_fio")
        self.rotas_arrasto = {}
        if not self.inicio:
            self.referencias = None
            self.c.delete("alinhamento")
            self.leitura_guias.set("")
        self.pan = False
        if self.modo=="Selecionar":
            self.c.configure(cursor="arrow")

    def duplo_clique(self,e):
        if getattr(e,"state",0)&5 or len(self.grupo)>1:
            self.clique(e)
            return
        forma = self.folha.get("formas",{}).get(self.selecao,{})
        if self.modo=="Selecionar" and forma.get("tipo")=="Texto":
            self.iniciar_texto(forma["pontos"][0],self.selecao)
        elif self.modo=="Selecionar" and self.selecao in self.folha["componentes"]:
            self.editar()
        else:
            self.clique(e)

    def mover(self,e):
        px,py = self.c.canvasx(e.x)/self.zoom,self.c.canvasy(e.y)/self.zoom
        if self.modo=="Seta curva" and self.curva_fixa:
            self.continuar_curva((px,py),bool(e.state&1))
            return
        if self.arrasto_nome:
            self.mover_nome_componente((px,py))
            return
        if self.arrasto_etiqueta:
            self.mover_etiqueta((px,py))
            return
        if self.caixa_selecao:
            self.estender_caixa((px,py))
            return
        if self.inicio_grupo:
            self.deslocar_grupo((px,py))
            return
        if self.forma_previa:
            self.continuar_forma((px,py),bool(e.state&1))
            self.render()
            return
        if self.gesto_forma:
            self.editar_forma((px,py),bool(e.state&1))
            return
        if self.inicio:
            self.movimento_livre(e)
            return
        if self.pan:
            self.arrastar_tela(e)
            return
        if self.arrasto_fio:
            tipo,indice,x,y,original,iniciado = self.arrasto_fio
            fio = self.folha["ligacoes"][self.selecao]
            if not iniciado:
                if dist((x,y),(px,py))*self.zoom < 3:
                    return
                self.lembrar()
                self.arrasto_fio = (tipo,indice,x,y,original,True)
            destino, self.guia_fio = alinhar_gesto_fio(original,tipo,indice,(px-x,py-y),self.zoom) if e.state&1 else ((px-x,py-y),None)
            if tipo=="trecho":
                pontos = deslocar_trecho(original,indice,*destino)
            else:
                antigo = original[indice+1]
                pos = (antigo[0]+destino[0],antigo[1]+destino[1])
                pos = self.encaixar(pos)
                pontos = mover_vertice(original,indice+1,pos)
            pontos = limpar(pontos)
            fio["pontos"] = [list(p) for p in pontos[1:-1]]
            self.render()
            return
        if self.arrasto:
            dx,dy,iniciado = self.arrasto
            item = self.folha["componentes"].get(self.selecao)
            anterior = (item["x"],item["y"]) if item else self.ponta([self.selecao,0])
            if item:
                x = round((px-dx)/10)*10
                y = round((py-dy)/10)*10
            else:
                pos = (px-dx,py-dy)
                ref = self.terminal_proximo(pos)
                x,y = self.ponta(ref) if ref else self.encaixar(pos)
                self.ima = (x,y) if ref else None
            if (x,y) != anterior:
                if not iniciado:
                    self.lembrar()
                    self.arrasto = (dx,dy,True)
                if item:
                    item.update(x=x,y=y)
                else:
                    self.folha["nos"][self.selecao] = [x,y]
                self.acompanhar_pontas(self.rotas_arrasto)
                self.render()
            elif self.referencias:
                self.mostrar_referencias()

    def editar(self):
        if len(self.grupo)>1:
            self.status.set("Selecione um único componente para editar sua identificação.")
            return
        item = self.folha["componentes"].get(self.selecao)
        if item:
            nome = simpledialog.askstring("Identificação","Etiqueta do componente",initialvalue=item["nome"])
            if nome and nome != item["nome"]:
                self.lembrar()
                item["nome"] = nome
                self.render()

    def excluir(self):
        id_ = self.selecao
        if id_ is None:
            return
        ids = self.grupo.copy() or {id_}
        self.ferramenta("Selecionar")
        self.lembrar()
        for k in ids:
            self.folha["componentes"].pop(k,None)
        self.folha.get("formas",{}).pop(id_,None)
        self.folha["ligacoes"] = {k:f for k,f in self.folha["ligacoes"].items()
                                 if k not in ids and f["a"][0] not in ids and f["b"][0] not in ids}
        usados = {f[lado][0] for f in self.folha["ligacoes"].values() for lado in ("a","b")}
        if "nos" in self.folha:
            self.folha["nos"] = {n:p for n,p in self.folha["nos"].items() if n in usados}
        self.atualizar_ancoras()
        self.soltar()
        self.selecao = self.origem = None
        self.render()

    def fechar_editor(self):
        if not self.confirmar():
            return
        principal = self.root._root()
        def filhas():
            return [j for j in principal.winfo_children() if isinstance(j,tk.Toplevel) and hasattr(j,"editor")]
        if self.root is principal and filhas():
            principal.withdraw()
            principal.editor_fechado = True
            return
        self.root.destroy()
        if self.root is not principal and getattr(principal,"editor_fechado",False) and not filhas():
            principal.destroy()

    def confirmar(self):
        self.concluir_digitacao()
        if self.gravado == self.dados:
            return True
        resposta = messagebox.askyesnocancel("Projeto alterado","Salvar as alterações antes de continuar?")
        return self.salvar() if resposta else resposta is False

    def salvar(self,como=False):
        self.concluir_digitacao()
        path = self.path
        if como or path is None:
            nome = filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("Projeto JSON","*.json")])
            if not nome:
                return False
            path = Path(nome)
        try:
            vistas = {**self.cameras,self.aba.get():self.camera()}
            arquivo = dict(self.dados,vistas=vistas)
            if self.posicao_mapa is not None:
                arquivo["minimapa"] = self.posicao_mapa
            salvar(path,arquivo)
        except OSError as erro:
            messagebox.showerror("Falha ao salvar",str(erro))
            return False
        self.dados["vistas"] = vistas
        if self.posicao_mapa is not None:
            self.dados["minimapa"] = self.posicao_mapa
        self.path = path
        self.gravado = copy.deepcopy(self.dados)
        self.render()
        self.status.set(f"Projeto salvo em {path}")
        return True

    def substituir(self,data,path):
        self.path,self.dados = path,data
        self.biblioteca_ativa = None
        self.condutores_por_folha = {n:pacote_da_folha(f,n).conexoes["padrao"] for n,f in self.dados["folhas"].items()}
        self.condutor.set(self.condutores_por_folha[data["ativa"]])
        self.gravado = copy.deepcopy(data)
        self.historico.clear()
        self.futuros.clear()
        self.cameras = copy.deepcopy(data.get("vistas",{}))
        self.posicao_mapa = data.get("minimapa")
        if self.posicao_mapa is None:
            self.cartao_mapa.place(x=14,rely=1,y=-14,anchor="sw")
        else:
            self.limitar_mapa()
        self.zoom = 1
        self.indice_zoom.set("100%")
        self.posicionar_vista(0,0)
        self.sincronizar()
        if self.aba.get() in self.cameras:
            self.ir_camera(**self.cameras[self.aba.get()])

    def exportar(self):
        self.concluir_digitacao()
        pasta = self.path.parent if self.path else Path(__file__).resolve().parent
        nome = self.path.stem if self.path else "Projeto"
        import re
        folha_arquivo = re.sub(r'[\\/:*?"<>|\x00-\x1f]',"_",self.aba.get())[:80]
        destino = pasta / f"{nome} - {folha_arquivo} - {datetime.now():%Y%m%d-%H%M%S-%f}.png"
        canvas = tk.Canvas(self.root)
        try:
            from imagem import gravar_png
            self.cena(canvas,False)
            gravar_png(canvas,destino)
        except ImportError:
            messagebox.showerror("Exportar PNG","Instale o Pillow no Python do aplicativo com python -m pip install Pillow.")
            return
        except (OSError,ValueError) as erro:
            messagebox.showerror("Falha ao exportar",str(erro))
            return
        finally:
            canvas.destroy()
        self.status.set(f"Imagem salva em {destino}")

    def novo(self,pacotes=None):
        if self.confirmar():
            self.substituir(novo(pacotes),None)

    def abrir(self):
        nome = filedialog.askopenfilename(filetypes=[("Projeto JSON","*.json")])
        if nome and self.confirmar():
            try:
                data = carregar(nome)
            except (OSError,ValueError) as erro:
                messagebox.showerror("Falha ao abrir",str(erro))
                return
            self.substituir(data,Path(nome))


if __name__ == "__main__":
    janela = tk.Tk()
    import argparse
    parser = argparse.ArgumentParser(description="Editor de diagramas com pacotes declarativos")
    parser.add_argument("--pacote",action="append",help="ID da biblioteca a habilitar na folha genérica")
    args = parser.parse_args()
    Editor(janela,pacotes=args.pacote)
    janela.mainloop()
