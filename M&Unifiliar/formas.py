from math import dist, sqrt
from uuid import uuid4

FORMAS = ("Retângulo","Losango","Elipse","Linha","Seta","Lápis","Texto")
CORES = ("#283b46","#008370","#5665c1","#af5739","#ad3550","#327cbb","#a27612","#8553a0")
FONTES = ("Segoe UI","Arial","Georgia","Consolas","Times New Roman","Calibri")


def limites(pontos):
    xs,ys = zip(*pontos)
    return min(xs),min(ys),max(xs),max(ys)


def contem(forma,pos):
    if forma["tipo"] not in ("Retângulo","Elipse","Losango"):
        return False
    x,y,u,v = limites(forma["pontos"])
    if u==x or v==y:
        return False
    dx = abs((2*pos[0]-u-x)/(u-x))
    dy = abs((2*pos[1]-v-y)/(v-y))
    if forma["tipo"]=="Elipse":
        return dx*dx+dy*dy<=1
    if forma["tipo"]=="Losango":
        return dx+dy<=1
    return max(dx,dy)<=1


def fator_alca(tipo):
    # As alças ficam no contorno, inclusive no losango e na elipse.
    return {"Elipse":sqrt(0.5),"Losango":0.5}.get(tipo,1)


def projetar_alcas(a,b,fator):
    centro = [(p+q)/2 for p,q in zip(a,b)]
    return [[c+(v-c)*fator for c,v in zip(centro,p)] for p in (a,b)]


def desenhar_forma(c,id_,forma,ativa=False):
    tipo,pontos,cor = forma["tipo"],forma["pontos"],forma["cor"]
    tag = "forma:"+id_
    tags = (tag,f"alpha:{forma.get('opacidade',100)}")
    largura = forma.get("espessura",2.2)
    x,y,u,v = limites(pontos)
    if tipo == "Texto":
        c.create_text(*pontos[0],text=forma["texto"],font=(forma.get("fonte","Segoe UI"),-forma.get("tamanho",18)),
                      angle=forma.get("angulo",0),fill=cor,tags=tags)
    elif tipo in ("Linha","Seta","Lápis"):
        c.create_line(*pontos,fill=cor,width=largura,capstyle="round",joinstyle="round",tags=tags)
        if tipo == "Seta":
            a,b = pontos[-2:]
            dx,dy = b[0]-a[0],b[1]-a[1]
            tam = dist(a,b)
            if tam:
                dx,dy = dx/tam,dy/tam
                asas = [(b[0]-12*dx+s*5*dy,b[1]-12*dy-s*5*dx) for s in (-1,1)]
                c.create_line(asas[0],b,asas[1],fill=cor,width=largura,tags=tags)
    elif tipo == "Losango":
        c.create_polygon((x+u)/2,y,u,(y+v)/2,(x+u)/2,v,x,(y+v)/2,fill="",outline=cor,width=largura,tags=tags)
    else:
        metodo = c.create_rectangle if tipo=="Retângulo" else c.create_oval
        metodo(x,y,u,v,outline=cor,width=largura,tags=tags)
    if ativa:
        caixa = c.bbox(tag)
        c.create_rectangle(*caixa,outline="#008370",dash=(3,3),tags=tag)
        if tipo != "Texto":
            for indice,p in enumerate(projetar_alcas(pontos[0],pontos[-1],fator_alca(tipo))):
                a,b = p
                c.create_rectangle(a-3,b-3,a+3,b+3,fill="white",outline="#008370",tags=(tag,f"alca:{indice}"))


def alinhar_formas(folha,ponta):
    for forma in folha.get("formas",{}).values():
        if not forma.get("ancoras"):
            continue
        pts = forma["pontos"]
        fator = fator_alca(forma["tipo"])
        alcas = projetar_alcas(pts[0],pts[-1],fator)
        for chave,ref in list(forma.get("ancoras",{}).items()):
            if ref[0] in folha["componentes"] or ref[0] in folha.get("nos",{}):
                alcas[int(chave)] = ponta(ref)
            else:
                del forma["ancoras"][chave]
        pts[0],pts[-1] = projetar_alcas(*alcas,1/fator)


class Desenho:
    def encaixe_forma(self,forma,indice,pos):
        candidatos = []
        for chave,item in self.folha["componentes"].items():
            for i in range(len(self.pacote_para(item).terminais(item["tipo"]))):
                ref = [chave,i]
                candidatos.append((self.ponta(ref),ref))
        candidatos.extend((p,[n,0]) for n,p in self.folha.get("nos",{}).items())
        alvo = min(candidatos,key=lambda par:dist(par[0],pos),default=None)
        chave = str(indice)
        if alvo and dist(pos,alvo[0])*self.zoom<=10:
            forma.setdefault("ancoras",{})[chave] = alvo[1]
            self.ima = tuple(alvo[0])
            return list(alvo[0])
        forma.get("ancoras",{}).pop(chave,None)
        self.ima = None
        return list(pos)

    def atualizar_ancoras(self):
        alinhar_formas(self.folha,self.ponta)

    def iniciar_forma(self,pos):
        if self.modo=="Texto":
            self.iniciar_texto(pos)
            return
        self.centro_forma = pos
        self.forma_previa = dict(tipo=self.modo,pontos=[list(pos),list(pos)],cor=self.cor_forma.get())
        if self.modo not in ("Elipse","Losango"):
            self.forma_previa["pontos"][0] = self.encaixe_forma(self.forma_previa,0,pos)

    def continuar_forma(self,pos):
        forma = self.forma_previa
        pos = self.encaixe_forma(forma,1,pos)
        if forma["tipo"] in ("Losango","Elipse"):
            if "1" in forma.get("ancoras",{}):
                fator = fator_alca(forma["tipo"])
                pos = [c+(v-c)/fator for c,v in zip(self.centro_forma,pos)]
            forma["pontos"][0] = [2*c-v for c,v in zip(self.centro_forma,pos)]
        if forma["tipo"]=="Lápis":
            if dist(forma["pontos"][-1],pos)*self.zoom>=2:
                forma["pontos"].append(list(pos))
        else:
            forma["pontos"][-1] = list(pos)

    def confirmar_forma(self):
        self.lembrar()
        self.selecao = uuid4().hex
        self.folha.setdefault("formas",{})[self.selecao] = self.forma_previa
        self.forma_previa = None
        self.ferramenta("Selecionar")

    def editar_forma(self,pos):
        inicio,original,alca,iniciado = self.gesto_forma
        dx,dy = pos[0]-inicio[0],pos[1]-inicio[1]
        if not iniciado:
            if dist(inicio,pos)*self.zoom<2:
                return
            self.lembrar()
            self.gesto_forma = (inicio,original,alca,True)
        forma = self.folha["formas"][self.selecao]
        if alca is None:
            forma.pop("ancoras",None)
            forma["pontos"] = [[x+dx,y+dy] for x,y in original]
        elif forma["tipo"]!="Lápis":
            fator = fator_alca(forma["tipo"])
            alcas = projetar_alcas(original[0],original[-1],fator)
            x,y = alcas[alca]
            alcas[alca] = self.encaixe_forma(forma,alca,(x+dx,y+dy))
            forma["pontos"] = projetar_alcas(*alcas,1/fator)
        else:
            fixo,movel = (original[-1],original[0]) if alca==0 else (original[0],original[-1])
            destino = self.encaixe_forma(forma,alca,(movel[0]+dx,movel[1]+dy))
            dx,dy = destino[0]-movel[0],destino[1]-movel[1]
            x,y = fixo
            u,v = movel
            fator_x = 1+dx/(movel[0]-fixo[0]) if u!=x else 1
            fator_y = 1+dy/(movel[1]-fixo[1]) if v!=y else 1
            forma["pontos"] = [[fixo[0]+(a-fixo[0])*fator_x,fixo[1]+(b-fixo[1])*fator_y] for a,b in original]
            forma["pontos"][0 if alca==0 else -1] = destino
        self.render()

    def mudar_cor(self,cor):
        self.cor_forma.set(cor)
        forma = self.folha.get("formas",{}).get(self.selecao)
        if self.modo=="Selecionar" and forma and forma["cor"]!=cor:
            self.lembrar()
            forma["cor"] = cor
        self.render()
