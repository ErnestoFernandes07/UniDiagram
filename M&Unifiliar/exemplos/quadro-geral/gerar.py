"""Reprodução editável da referência enviada pelo usuário; não dimensiona circuitos."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from nucleo.documento import validar_dados, ponta_do_projeto

OUT=Path(__file__).resolve().parent
LIB={"id":"eletrica.multifilar","versao":1}
f={"componentes":{},"ligacoes":{},"nos":{},"formas":{},"cores_bibliotecas":{LIB["id"]:{"L1":"#283b46","L2":"#ad3550","L3":"#8553a0","N":"#327cbb","PE":"#a27612","Retorno":"#af5739"}}}
d={"versao":4,"ativa":"Quadro geral","bibliotecas":[LIB],"folhas":{"Quadro geral":f},"grade":{"tipo":"nenhuma","passo":20},"vistas":{"Quadro geral":{"x":530,"y":760,"zoom":0.4}}}
n=0
def ident(prefix):
 global n
 n+=1
 return f"{prefix}-{n}"
def node(x,y):
 k=ident("no");f["nos"][k]=[x,y];return [k,0]
def wire(a,b,cat,points=None):
 k=ident("fio");f["ligacoes"][k]={"a":a,"b":b,"condutor":cat,"pacote":LIB,"mostrar_nome":False,"espessura":1.5,"pontos":points or []};return k
def text(x,y,t,size=16):
 f["formas"][ident("texto")]={"tipo":"Texto","pontos":[[x,y]],"texto":t,"tamanho":size,"fonte":"Arial","cor":"#283b46"}
def line(a,b):
 f["formas"][ident("linha")]={"tipo":"Linha","pontos":[a,b],"cor":"#283b46","espessura":1}
def box(x,y,label,height=52):
 f["formas"][ident("carga")]={"tipo":"Retângulo","pontos":[[x-65,y-height/2],[x+65,y+height/2]],"cor":"#283b46","espessura":0.7}
 text(x,y,label)
def breaker(k,x,y,poles,rating,rotation=90,scale=1):
 f["componentes"][k]={"tipo":f"Disjuntor NEMA {poles}P","nome":rating,"x":x,"y":y,"rotacao":rotation,"escala":scale,"pacote":LIB,"tamanho_nome":16,"posicao_nome":[0,-35 if scale==1 else -105]}
def point(ref):return ponta_do_projeto(f,"Quadro geral",ref)
xs={"L1":440,"L2":500,"L3":560,"N":620,"PE":680}
taps={c:{} for c in xs}
def tap(c,y):
 if y not in taps[c]:taps[c][y]=node(xs[c],y)
 return taps[c][y]
text(520,12,"QUADRO GERAL",25)
text(160,75,"DIAGRAMA MULTIFILAR",22)
text(135,101,"SEM ESCALA · REPRODUÇÃO",12)
for c,label in [("L1","Fase R"),("L2","Fase S"),("L3","Fase T"),("N","N"),("PE","T / PE")]:text(xs[c],45,label,15)
breaker("geral",500,180,3,"200 A",0,3)
for i,c in enumerate(("L1","L2","L3")):
 a=node(xs[c],65);port=point(["geral",i]);wire(a,["geral",i],c,[[xs[c],75],[port[0],75]])
 port=point(["geral",i+3]);wire(["geral",i+3],tap(c,300),c,[[port[0],285],[xs[c],285]])
tap("N",65);tap("PE",65)
wire(tap("N",95),node(835,95),"N");text(925,95,"BARRA DE NEUTRO",14)
wire(tap("PE",180),node(845,245),"PE",[[845,180]])
for y,w in [(252,26),(259,18),(266,8)]:line([845-w/2,y],[845+w/2,y])
text(935,205,"BARRA DE COBRE\nDO FIO TERRA",14)

def circuit(side,row,label,rating,phases,neutral=False,earth=True,offset=0):
 y=350+row*110+offset
 bx=300 if side=="E" else 800
 end=190 if side=="E" else 910
 boxx=125 if side=="E" else 975
 k=f"{side}-{row}-{offset}"
 breaker(k,bx,y,len(phases),rating)
 for i,cat in enumerate(phases):
  # Rotation 90: the first bank is on the right, the second on the left.
  busport=i if side=="E" else i+len(phases)
  loadport=i+len(phases) if side=="E" else i
  yy=point([k,busport])[1]
  wire(tap(cat,yy),[k,busport],cat)
  wire([k,loadport],node(end,yy),cat)
 if neutral:wire(tap("N",y-20),node(end,y-20),"N")
 if earth:wire(tap("PE",y+30 if len(phases)>1 else y+20),node(end,y+30 if len(phases)>1 else y+20),"PE")
 box(boxx,y+5,label,44 if row==4 and side=="D" else 60)
left=[("Máquina Sorv.\n380 V","32 A",["L1","L2","L3"],False,False),("COPA","25 A",["L1","L2"],False,True),("Forno","25 A",["L1","L3"],False,True),("Resfr.\nLanch","25 A",["L2","L3"],False,True),("NO break","32 A",["L1","L2"],False,True),("COPA","25 A",["L2"],True,True),("Refresqueira","25 A",["L1"],True,True),("Reserva","25 A",["L1","L2"],False,True),("Reserva","25 A",["L2","L3"],False,True),("Reserva","20 A",["L2"],True,True)]
right=[("QD-AC","150 A",["L1","L2","L3"],False,False),("Tomada\nServiço","25 A",["L1","L2"],False,True),("Geladeira\nlanch","25 A",["L1","L3"],False,True),("Balcão\nSalgados","25 A",["L2","L3"],False,True),None,("TomadaServ","25 A",["L3"],True,True),("Reserva","25 A",["L3"],True,True),("Reserva","25 A",["L1","L2"],False,True),("Reserva","25 A",["L2","L3"],False,True),("Reserva","20 A",["L3"],True,True)]
for i,args in enumerate(left):circuit("E",i,*args)
for i,args in enumerate(right):
 if args:circuit("D",i,*args)
circuit("D",4,"ILUM SUB.","16 A",["L1"],False,True,-22)
circuit("D",4,"ILUM SALÃO","20 A",["L2"],False,True,32)
for y,c in [(1430,"L2"),(1450,"L3"),(1480,"L1"),(1500,"L3")]:
 ref=tap(c,y);wire(node(190,y),ref,c);wire(ref,node(910,y),c)
text(115,1465,"BARRAS\nRESERVAS",14);text(975,1465,"4 BARRAS\nRESERVAS",14)
for c in xs:
 tap(c,1510)
 entries=sorted(taps[c].items())
 for (_,a),(_,b) in zip(entries,entries[1:]):wire(a,b,c)
text(560,1555,"Reprodução da imagem fornecida · ligações inferiores parcialmente cortadas na referência",13)
text(560,1578,"Identificações e correntes transcritas; dimensionamento e adequação elétrica não verificados.",13)
f["componentes"]["geral"]["posicao_nome"]=[-120,0]
for k in ("D-4--22","D-4-32"):
 f["componentes"][k]["posicao_nome"]=[50,-14]
d=validar_dados(d)
(OUT/"quadro-geral-multifilar.json").write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n","utf-8")
if __name__=="__main__":
 import tkinter as tk
 from app import Editor
 from imagem import gravar_png
 r=tk.Tk();r.withdraw();e=Editor(r);e.substituir(d,None)
 c=tk.Canvas(r);e.cena(c,False);gravar_png(c,OUT/"quadro-geral-multifilar.png");r.destroy()
 print("JSON e PNG gerados em",OUT)
