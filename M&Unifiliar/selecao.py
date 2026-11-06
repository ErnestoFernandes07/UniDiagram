from math import dist


class Selecao:
    def definir_grupo(self,ids,preferido=None):
        self.grupo = set(ids)
        self.selecao = preferido if preferido in self.grupo else next(iter(sorted(self.grupo)),None)
        if len(self.grupo)>1:
            self.status.set(f"{len(self.grupo)} componentes selecionados. Arraste um deles para mover o conjunto.")
        elif self.grupo:
            self.status.set("Shift + clique adiciona componentes. Ctrl + clique alterna a seleção.")
        else:
            self.status.set("Arraste no fundo para selecionar componentes. Botão direito para mover a tela.")

    def escolher_componente(self,id_,mod,pos):
        anterior = self.grupo.copy()
        if self.selecao in self.folha["componentes"]:
            anterior.add(self.selecao)
        if mod:
            grupo = anterior ^ {id_} if mod&4 else anterior | {id_}
            self.definir_grupo(grupo,id_)
            if id_ not in grupo:
                return
        elif id_ not in anterior or len(anterior)<2:
            self.definir_grupo({id_},id_)
        else:
            self.definir_grupo(anterior,id_)
        self.inicio_grupo = pos
        self.clique_simples = not mod
        self.origens_grupo = {k:(self.folha["componentes"][k]["x"],self.folha["componentes"][k]["y"]) for k in self.grupo}
        self.rotas_arrasto = self.rotas_grupo()
        self.moveu_grupo = False

    def rotas_grupo(self):
        return {id_:self.caminho(f) for id_,f in self.folha["ligacoes"].items()
                if "pontos" in f and (f["a"][0] in self.grupo or f["b"][0] in self.grupo)}

    def deslocar_grupo(self,pos):
        x,y = self.inicio_grupo
        dx,dy = round((pos[0]-x)/10)*10,round((pos[1]-y)/10)*10
        if not self.moveu_grupo:
            if dx==dy==0:
                return
            self.lembrar()
            self.moveu_grupo = True
        for k,(a,b) in self.origens_grupo.items():
            self.folha["componentes"][k].update(x=a+dx,y=b+dy)
        externas = {}
        for k,pontos in self.rotas_arrasto.items():
            fio = self.folha["ligacoes"][k]
            if fio["a"][0] in self.grupo and fio["b"][0] in self.grupo:
                fio["pontos"] = [[a+dx,b+dy] for a,b in pontos[1:-1]]
            else:
                externas[k] = pontos
        self.acompanhar_pontas(externas)
        self.render()

    def iniciar_caixa(self,pos,mod):
        base = self.grupo.copy()
        if self.selecao in self.folha["componentes"]:
            base.add(self.selecao)
        self.caixa_selecao = (pos,pos,mod,base)
        self.definir_grupo(base if mod else set())

    def estender_caixa(self,pos):
        inicio,_,mod,base = self.caixa_selecao
        self.caixa_selecao = (inicio,pos,mod,base)
        x,u = sorted((inicio[0],pos[0]))
        y,v = sorted((inicio[1],pos[1]))
        ids = {k for k,item in self.folha["componentes"].items() if x<=item["x"]<=u and y<=item["y"]<=v}
        if dist(inicio,pos)*self.zoom<3:
            ids.clear()
        if mod&4:
            ids = base ^ ids
        elif mod&1:
            ids |= base
        self.definir_grupo(ids)
        self.render()

    def pintar_selecao(self):
        c = self.c
        for k in self.grupo:
            box = c.bbox("item:"+k)
            if box:
                x,y,u,v = box
                c.create_rectangle(x-3,y-3,u+3,v+3,outline="#42977a",dash=(3,3))
        if self.caixa_selecao:
            a,b,_,_ = self.caixa_selecao
            c.create_rectangle(*(v*self.zoom for p in (a,b) for v in p),outline="#188267",dash=(5,3),width=2)
