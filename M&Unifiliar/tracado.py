"""Geometria dos fios em coordenadas da folha, independente do zoom."""
from math import dist


def projetar(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    comprimento = dx*dx + dy*dy
    t = ((p[0]-a[0])*dx + (p[1]-a[1])*dy)/comprimento if comprimento else 0
    t = max(0, min(1, t))
    return (a[0]+dx*t, a[1]+dy*t)


def limpar(pontos):
    resultado = []
    for p in map(tuple,pontos):
        if resultado and dist(resultado[-1],p) < 0.001:
            continue
        resultado.append(p)
        while len(resultado) >= 3:
            a,b,c = resultado[-3:]
            if dist(b,projetar(b,a,c)) > 0.001:
                break
            resultado.pop(-2)
    return resultado


def automatico(a,b):
    meio = (a[1]+b[1])/2
    return limpar([a,(a[0],meio),(b[0],meio),b])


def trechos_curvos(pontos, raio=10):
    """Distribui a curva entre os dois trechos para manter a seleção por trecho."""
    trechos = [[] for _ in pontos[1:]]
    if not trechos:
        return []
    trechos[0].append(pontos[0])
    for i in range(1,len(pontos)-1):
        a,b,c = pontos[i-1:i+2]
        ab,bc = dist(a,b),dist(b,c)
        r = min(raio,ab/2,bc/2)
        entrada = [b[k]+(a[k]-b[k])*r/(ab or 1) for k in (0,1)]
        saida = [b[k]+(c[k]-b[k])*r/(bc or 1) for k in (0,1)]
        for j in range(9):
            t = j/8
            ponto = tuple((1-t)**2*entrada[k]+2*t*(1-t)*b[k]+t*t*saida[k] for k in (0,1))
            if j <= 4:
                trechos[i-1].append(ponto)
            if j >= 4:
                trechos[i].append(ponto)
    trechos[-1].append(pontos[-1])
    return trechos


def deslocar_trecho(pontos, indice, dx, dy):
    """Translada um trecho pela normal e conserva os dois terminais."""
    a,b = pontos[indice:indice+2]
    ux,uy = b[0]-a[0],b[1]-a[1]
    norma = ux*ux+uy*uy
    fator = (dy*ux-dx*uy)/norma if norma else 0
    deslocados = [(x-uy*fator,y+ux*fator) for x,y in (a,b)]
    antes = pontos[:indice] or [a]
    depois = pontos[indice+2:] or [b]
    return limpar([*antes,*deslocados,*depois])


def mover_vertice(pontos, indice, destino):
    """Move um ponto e prolonga as pernas adjacentes sem deslocar terminais fixos."""
    original = list(map(tuple, pontos))
    destino = tuple(destino)
    if destino == original[indice]:
        return original
    editado = original.copy()
    editado[indice] = destino
    desvios = {}
    for vizinho in (indice-1, indice+1):
        if not 0 <= vizinho < len(pontos):
            continue
        a,b = original[indice],original[vizinho]
        # Uma perna vertical compartilha x. Uma horizontal compartilha y.
        eixo = 0 if abs(a[0]-b[0]) < abs(a[1]-b[1]) else 1
        seguinte = vizinho+(vizinho-indice)
        if a[0]!=b[0] and a[1]!=b[1] and 0 <= seguinte < len(original):
            # Recupera também joelhos antigos que já foram arrastados em diagonal.
            c = original[seguinte]
            if b[1]==c[1] and b[0]!=c[0]:
                eixo = 0
            elif b[0]==c[0] and b[1]!=c[1]:
                eixo = 1
        outro = 1-eixo
        if destino[eixo] == b[eixo]:
            continue
        if 0 < vizinho < len(pontos)-1:
            joelho = list(b)
            joelho[eixo] = destino[eixo]
            editado[vizinho] = tuple(joelho)
        else:
            # O terminal oposto fica fixo. Duas dobras conservam a direção de saída.
            meio = (destino[outro]+b[outro])/2
            par = [list(destino),list(b)]
            for p in par:
                p[outro] = meio
            desvios[min(indice,vizinho)] = par if indice<vizinho else par[::-1]
    rota = []
    for i,p in enumerate(editado):
        rota.append(p)
        rota.extend(desvios.get(i, ()))
    rota = limpar(rota)
    return rota if len(rota)>1 else [rota[0],rota[0]]


class Referencias:
    """Referências adquiridas ao passar o cursor por um ponto durante um gesto."""
    def __init__(self, pontos):
        self.pontos = list(dict.fromkeys(map(tuple,pontos)))
        self.visitados = []
        self.eixos = [None,None]
        self.pos = None

    def ajustar(self, pos, zoom):
        perto = min(self.pontos, key=lambda p: dist(pos,p), default=None)
        if perto is not None and dist(pos,perto)*zoom <= 9:
            self.visitados = [perto,*[p for p in self.visitados if p!=perto]][:2]
        destino = list(pos)
        for eixo in (0,1):
            ref = min(self.visitados,key=lambda p:abs(p[eixo]-pos[eixo]),default=None)
            if ref is not None and abs(ref[eixo]-pos[eixo])*zoom <= 7:
                destino[eixo] = ref[eixo]
            else:
                ref = None
            self.eixos[eixo] = ref
        self.pos = tuple(destino)
        return self.pos


def alinhar_gesto_fio(pontos,tipo,indice,delta,zoom):
    """Snap em eixos dos outros vértices, com tolerância constante na tela."""
    dx,dy = delta
    if tipo=="trecho":
        a,b = pontos[indice:indice+2]
        eixo = 1 if abs(b[0]-a[0])>=abs(b[1]-a[1]) else 0
        origem = a
        ignorados = {indice,indice+1}
        eixos = [eixo]
    else:
        origem = pontos[indice+1]
        ignorados = {indice+1}
        eixos = [0,1]
    resultado = [dx,dy]
    guia = None
    for eixo in eixos:
        valor = origem[eixo]+resultado[eixo]
        candidatos = [p[eixo] for i,p in enumerate(pontos) if i not in ignorados]
        alvo = min(candidatos,key=lambda n:abs(n-valor),default=None)
        if alvo is not None and abs(alvo-valor)*zoom<=9:
            resultado[eixo] = alvo-origem[eixo]
            guia = (eixo,alvo)
    return tuple(resultado),guia
