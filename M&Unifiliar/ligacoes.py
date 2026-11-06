from dataclasses import dataclass
from math import dist
from uuid import uuid4

from nucleo.pacotes import referencia
from tracado import Referencias, automatico, limpar, projetar, trechos_curvos
from rotulos import ancorar_etiqueta, posicao_etiqueta


@dataclass
class Alvo:
    pos: tuple
    ref: list | None = None
    fio: str | None = None
    trecho: int = 0


class Ligacoes:
    def cor_do_condutor(self,categoria,local=None,obj=None):
        pacote = self.pacote_para(obj) if obj is not None else self.pacote
        if pacote.conexoes["cores_compartilhadas"]:
            return self.folha.get("cores_bibliotecas",{}).get(pacote.id,{}).get(categoria,pacote.conexoes["categorias"][categoria])
        return local or pacote.conexoes["categorias"][categoria]

    def terminal_proximo(self,pos):
        candidatos = [(dist(pos,self.ponta([id_,i])),[id_,i])
            for id_,item in self.folha["componentes"].items()
            for i in range(len(self.pacote_para(item).terminais(item["tipo"])))]
        distancia,ref = min(candidatos,default=(float("inf"),None),key=lambda p:p[0])
        return ref if distancia*self.zoom<=10 else None

    def conectar_no_arrastado(self):
        no = self.selecao
        if no not in self.folha.get("nos",{}):
            return
        ref = self.terminal_proximo(self.folha["nos"][no])
        if ref is None:
            return
        rotas = self.caminhos_ligados(no)
        for fio in self.folha["ligacoes"].values():
            for lado in ("a","b"):
                if fio[lado]==[no,0]:
                    fio[lado] = list(ref)
        for forma in self.folha.get("formas",{}).values():
            for chave,ancora in forma.get("ancoras",{}).items():
                if ancora==[no,0]:
                    forma["ancoras"][chave] = list(ref)
        del self.folha["nos"][no]
        self.acompanhar_pontas(rotas)
        self.selecao = ref[0]
        self.status.set("Fio conectado ao terminal do componente.")
        self.render()

    def mover_etiqueta(self,pos):
        x,y,dx,dy,iniciado = self.arrasto_etiqueta
        if not iniciado:
            if dist((x,y),pos)*self.zoom<3:
                return
            self.lembrar()
            self.arrasto_etiqueta = (x,y,dx,dy,True)
        fio = self.folha["ligacoes"][self.selecao]
        fio["etiqueta"] = ancorar_etiqueta(self.caminho(fio),(pos[0]+dx,pos[1]+dy))
        self.render()

    def iniciar_referencias(self, ignorar_no=None, ignorar_fios=()):
        pontos = [p for chave,p in self.folha.get("nos",{}).items() if chave!=ignorar_no]
        for chave,item in self.folha["componentes"].items():
            portas = self.pacote_para(item).terminais(item["tipo"])
            pontos.extend(self.ponta([chave,i]) for i in range(len(portas)))
        for chave,fio in self.folha["ligacoes"].items():
            if chave not in ignorar_fios:
                pontos.extend(self.caminho(fio)[1:-1])
        self.referencias = Referencias(pontos)

    def mostrar_referencias(self):
        c = self.c
        c.delete("alinhamento")
        refs = self.referencias
        if not self.guias_ativas.get() or not refs or not refs.visitados:
            self.leitura_guias.set("")
            return
        texto = ("Vertical" if refs.eixos[0] else "", "Horizontal" if refs.eixos[1] else "")
        self.leitura_guias.set(" + ".join(filter(None,texto)) or "Referência capturada")
        esquerda,direita = c.canvasx(0),c.canvasx(c.winfo_width())
        topo,base = c.canvasy(0),c.canvasy(c.winfo_height())
        for ref in refs.visitados:
            x,y = (v*self.zoom for v in ref)
            for eixo,coords in enumerate(((x,topo,x,base),(esquerda,y,direita,y))):
                cor = "#4a9d70" if refs.eixos[eixo]==ref else "#a8cdb6"
                c.create_line(*coords,fill=cor,width=1,dash=(3,5),tags="alinhamento")
            c.create_oval(x-3,y-3,x+3,y+3,outline="#629f76",tags="alinhamento")
        if all(p is not None for p in refs.eixos):
            x,y = (v*self.zoom for v in refs.pos)
            c.create_rectangle(x-4,y-4,x+4,y+4,outline="#18804e",width=2,tags="alinhamento")

    def encaixar(self,pos):
        if self.guias_ativas.get() and self.referencias:
            return self.referencias.ajustar(pos,self.zoom)
        return pos

    def alvo_alinhado(self,e):
        alvo = self.alvo_fio(e)
        if self.referencias:
            pos = self.encaixar(alvo.pos)
            if alvo.ref is None and alvo.fio is None:
                alvo.pos = pos
        return alvo

    def alvo_fio(self,e):
        x,y = self.c.canvasx(e.x),self.c.canvasy(e.y)
        pos = (x/self.zoom,y/self.zoom)
        objetos = reversed(self.c.find_overlapping(x-6,y-6,x+6,y+6))
        grupos = [self.c.gettags(obj) for obj in objetos]
        candidatos = []
        for grupo in grupos:
            for tag in grupo:
                if tag.startswith("porta:"):
                    _,id_,p = tag.split(":")
                    ref = [id_,int(p)]
                    return Alvo(self.ponta(ref),ref)
                if tag.startswith("no:"):
                    ref = [tag[3:],0]
                    return Alvo(self.ponta(ref),ref)
        for grupo in grupos:
            if len(grupo)>=2 and grupo[0].startswith("fio:") and grupo[1].startswith("trecho:"):
                id_ = grupo[0][4:]
                i = int(grupo[1][7:])
                fio = self.folha["ligacoes"][id_]
                pontos = self.caminho(fio)
                p = projetar(pos,*pontos[i:i+2])
                candidatos.append((dist(pos,p),Alvo(p,fio=id_,trecho=i)))
        if candidatos:
            _,alvo = min(candidatos,key=lambda par:par[0])
            fio = self.folha["ligacoes"][alvo.fio]
            for lado in ("a","b"):
                ref = fio[lado]
                if dist(alvo.pos,self.ponta(ref))*self.zoom < 5:
                    return Alvo(self.ponta(ref),ref)
            return alvo
        return Alvo(pos)

    def materializar(self,alvo):
        if alvo.ref:
            return alvo.ref
        ref = [uuid4().hex,0]
        self.folha.setdefault("nos",{})[ref[0]] = list(alvo.pos)
        if alvo.fio:
            fios = self.folha["ligacoes"]
            fio = fios[alvo.fio]
            pontos = self.caminho(fio)
            i = alvo.trecho
            esquerda = limpar([*pontos[:i+1],alvo.pos])
            direita = limpar([alvo.pos,*pontos[i+1:]])
            outro = dict(fio,a=ref,pontos=[list(p) for p in direita[1:-1]])
            fios[uuid4().hex] = outro
            fio.update(b=ref,pontos=[list(p) for p in esquerda[1:-1]])
            if "etiqueta" in fio:
                pos = posicao_etiqueta(pontos,fio.pop("etiqueta"))
                outro.pop("etiqueta")
                def distancia(rota):
                    return min((dist(pos,projetar(pos,a,b)) for a,b in zip(rota,rota[1:])),default=dist(pos,rota[0]))
                dono,restante,rota = (fio,outro,esquerda) if distancia(esquerda)<=distancia(direita) else (outro,fio,direita)
                dono["etiqueta"] = ancorar_etiqueta(rota,pos)
                restante["mostrar_nome"] = False
        return ref

    def rota_rascunho(self,alvo):
        fixos = [self.inicio.pos,*self.guias]
        return limpar([*fixos[:-1],*automatico(fixos[-1],alvo.pos)])

    def clique_ligacao(self,e):
        alvo = self.alvo_alinhado(e)
        if self.inicio is None:
            if self.modo == "Derivar" and not (alvo.fio or (alvo.ref and alvo.ref[0] in self.folha.get("nos",{}))):
                self.status.set("Clique sobre o fio que deseja derivar.")
                return
            if self.modo == "Ligar" and not (alvo.ref or alvo.fio):
                self.status.set("Comece em um terminal, em uma ponta livre ou em um fio.")
                return
            fonte = self.folha["ligacoes"].get(alvo.fio)
            if fonte is None and alvo.ref:
                fonte = self.folha["componentes"].get(alvo.ref[0])
                if fonte is None:
                    ligados = [f for f in self.folha["ligacoes"].values() if alvo.ref in (f["a"],f["b"])]
                    if ligados:
                        fonte = ligados[0]
            if fonte is not None:
                pacote = self.pacote_para(fonte)
                if self.pacote.id!=pacote.id or self.condutor.get() not in pacote.conexoes["categorias"]:
                    self.condutor.set(pacote.conexoes["padrao"])
                self.biblioteca_ativa = pacote.id
            self.inicio = alvo
            self.estilo_inicio = {}
            self.origem = alvo.ref
            self.iniciar_referencias()
            self.referencias.pontos.append(alvo.pos)
            self.encaixar(alvo.pos)
            if alvo.fio:
                origem = self.folha["ligacoes"][alvo.fio]
                self.condutor.set(origem["condutor"])
                self.estilo_inicio = {k:origem[k] for k in ("espessura","cor","opacidade") if k in origem}
            elif alvo.ref[0] in self.folha.get("nos",{}):
                condutores = {f["condutor"] for f in self.folha["ligacoes"].values()
                              if alvo.ref in (f["a"],f["b"])}
                if len(condutores)==1:
                    self.condutor.set(condutores.pop())
            self.status.set("Clique para terminar. Shift + clique fixa uma dobra. Esc cancela.")
        elif e.state & 1 and not (alvo.fio or alvo.ref):
            self.guias = self.rota_rascunho(alvo)[1:]
        else:
            if dist(alvo.pos,self.inicio.pos)<1 or (alvo.fio and alvo.fio==self.inicio.fio):
                self.status.set("Escolha outro fio, um terminal ou um ponto livre para terminar.")
                return
            pontos = self.rota_rascunho(alvo)
            self.lembrar()
            a,b = self.materializar(self.inicio),self.materializar(alvo)
            fio = dict(a=a,b=b,condutor=self.condutor.get(),pacote=referencia(self.pacote),mostrar_nome=self.condutor.get() not in self.pacote.conexoes["nomes_ocultos"],**self.estilo_inicio)
            if self.guias:
                fio["pontos"] = [list(p) for p in pontos[1:-1]]
            self.folha["ligacoes"][uuid4().hex] = fio
            self.ferramenta("Selecionar")
            return
        self.ultimo_alvo = alvo
        self.render()

    def movimento_livre(self,e):
        if self.modo=="Seta curva" and self.curva_fixa:
            self.continuar_curva((self.c.canvasx(e.x)/self.zoom,self.c.canvasy(e.y)/self.zoom),bool(e.state&1))
            return
        if self.modo in self.pacote.componentes:
            self.atualizar_insercao(e)
            return
        if self.inicio is not None:
            self.ultimo_alvo = self.alvo_alinhado(e)
            self.previa()
            self.mostrar_referencias()

    def previa(self):
        self.c.delete("previa")
        if self.inicio is None or self.ultimo_alvo is None:
            return
        alvo = self.ultimo_alvo
        cor = self.cor_do_condutor(self.condutor.get(),self.estilo_inicio.get("cor"))
        for trecho in trechos_curvos(self.rota_rascunho(alvo)):
            coords = [v*self.zoom for p in trecho for v in p]
            self.c.create_line(*coords,fill=cor,width=max(1,self.estilo_inicio.get("espessura",2)*self.zoom),tags="previa")
        for pos in (self.inicio.pos,alvo.pos):
            x,y = (v*self.zoom for v in pos)
            self.c.create_oval(x-4,y-4,x+4,y+4,fill="white",outline="#00786a",width=2,tags="previa")
