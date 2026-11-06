"""Posição da etiqueta como fração do percurso e distância lateral à linha."""
from math import dist
from tracado import projetar


def segmentos(pontos):
    inicio = 0.0
    for a,b in zip(pontos,pontos[1:]):
        comprimento = dist(a,b)
        if comprimento:
            dx,dy = (b[0]-a[0])/comprimento,(b[1]-a[1])/comprimento
            yield inicio,comprimento,a,b,dx,dy
            inicio += comprimento


def ancorar_etiqueta(pontos,pos):
    trechos = list(segmentos(pontos))
    if not trechos:
        return [0.0,0.0]
    inicio,tam,a,b,dx,dy = min(trechos,key=lambda s:dist(pos,projetar(pos,s[2],s[3])))
    q = projetar(pos,a,b)
    total = sum(s[1] for s in trechos)
    lateral = (pos[1]-q[1])*dx-(pos[0]-q[0])*dy
    return [min(1,(inicio+dist(a,q))/total),max(-32,min(32,lateral))]


def posicao_etiqueta(pontos,ancora):
    trechos = list(segmentos(pontos))
    if not trechos:
        return pontos[0][0],pontos[0][1]-11
    if ancora is None:
        _,tam,a,b,dx,dy = max(trechos,key=lambda s:s[1])
        sinal = -1 if dx>0 or (dx==0 and dy<0) else 1
        return (a[0]+b[0])/2-sinal*dy*11,(a[1]+b[1])/2+sinal*dx*11
    fracao,lateral = ancora
    alvo = fracao*sum(s[1] for s in trechos)
    inicio,tam,a,b,dx,dy = next((s for s in trechos if alvo<=s[0]+s[1]),trechos[-1])
    avanco = max(0,min(tam,alvo-inicio))
    return a[0]+dx*avanco-dy*lateral,a[1]+dy*avanco+dx*lateral
