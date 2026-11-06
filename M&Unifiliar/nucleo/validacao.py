"""Validação estrutural v4, compartilhada por arquivo e importação de texto."""
import json
import re
from math import isfinite

from formas import CORES, FONTES, FORMAS
from .pacotes import obter, pacote_do_objeto, resolver_ref, ErroPacote

LIMITES = dict(bytes_json=10*1024*1024,folhas=64,objetos=20000,pontos=2000,
               coordenada=10000000,texto=10000)


class ErroDocumento(ValueError):
    def __init__(self,caminho,mensagem):
        self.caminho,self.mensagem = caminho,mensagem
        super().__init__(f"{caminho}: {mensagem}")


class ErroDependencia(ErroDocumento,ErroPacote):
    pass


def exigir(condicao,p,msg):
    if not condicao:
        raise ErroDocumento(p,msg)


def objeto(v,p):
    exigir(isinstance(v,dict),p,"esperado um objeto JSON, entre chaves.")


def campos(v,p,obrigatorios=(),opcionais=()):
    objeto(v,p)
    for k in obrigatorios:
        exigir(k in v,p+"."+k,"campo obrigatório ausente.")
    extras = set(v)-set(obrigatorios)-set(opcionais)
    exigir(not extras,p,"campos não suportados: "+", ".join(sorted(extras)))


def texto(v,p,limite=256):
    exigir(isinstance(v,str) and len(v)<=limite and "\x00" not in v,p,f"esperado texto de até {limite} caracteres, sem NUL.")
    try:
        v.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ErroDocumento(p,"texto contém caracteres Unicode inválidos.") from exc


def numero(v,p,menor,maior,inteiro=False):
    exigir(type(v) in ((int,) if inteiro else (int,float)) and isfinite(v) and menor<=v<=maior,
           p,f"esperado {'inteiro' if inteiro else 'número finito'} entre {menor} e {maior}.")


def ponto(v,p):
    exigir(isinstance(v,list) and len(v)==2,p,"esperado [x, y].")
    for i,n in enumerate(v):
        numero(n,f"{p}[{i}]",-LIMITES["coordenada"],LIMITES["coordenada"])


def booleanos(v,p,chaves):
    for k in chaves:
        if k in v:
            exigir(type(v[k])==bool,p+"."+k,"use true ou false.")


def pacote(ref,p):
    campos(ref,p,("id","versao"))
    try:
        return resolver_ref(ref)
    except ErroPacote as exc:
        raise ErroDependencia(p,str(exc)) from exc


def pacote_obj(v,folha,p):
    if "pacote" in v:
        return pacote(v["pacote"],p+".pacote")
    return pacote_do_objeto(v,folha)


def estilo(v,p):
    if "cor" in v:
        exigir(v["cor"] in CORES,p+".cor","use uma cor da paleta do editor.")
    numero(v.get("espessura",2),p+".espessura",.5,32)
    numero(v.get("opacidade",100),p+".opacidade",0,100,True)
    booleanos(v,p,("tracejado","mostrar_nome"))


def pontos(v,p,minimo=0,maximo=None):
    maximo = LIMITES["pontos"] if maximo is None else maximo
    exigir(isinstance(v,list) and minimo<=len(v)<=maximo,p,f"esperada lista com {minimo} a {maximo} pontos.")
    for i,xy in enumerate(v):
        ponto(xy,f"{p}[{i}]")


def ref(v,f,p):
    exigir(isinstance(v,list) and len(v)==2 and isinstance(v[0],str) and type(v[1])==int,
           p,"esperado [id_do_componente_ou_no, índice_inteiro].")
    id_,indice = v
    if id_ in f.get("nos",{}):
        exigir(indice==0,p,"nós têm somente a porta 0.")
        return
    exigir(id_ in f["componentes"],p,f"componente ou nó '{id_}' não existe nesta folha.")
    item = f["componentes"][id_]
    n = len(pacote_do_objeto(item,f).terminais(item["tipo"]))
    exigir(0<=indice<n,p,f"terminal {indice} inválido em '{id_}'; use 0 a {n-1}.")


def camera(v,p,waypoint=False):
    campos(v,p,("x","y","zoom","folha") if waypoint else ("x","y","zoom"))
    ponto([v["x"],v["y"]],p)
    numero(v["zoom"],p+".zoom",.4,4)


def validar_v4(d):
    campos(d,"$",("versao","ativa","folhas","bibliotecas"),("grade","vistas","waypoints","minimapa"))
    exigir(type(d["versao"])==int and d["versao"]==4,"$.versao","esperada versão 4.")
    objeto(d["folhas"],"$.folhas")
    exigir(1<=len(d["folhas"])<=LIMITES["folhas"],"$.folhas","use 1 a 64 folhas.")
    exigir(isinstance(d["ativa"],str) and d["ativa"] in d["folhas"],"$.ativa","a folha ativa não existe.")
    exigir(isinstance(d["bibliotecas"],list),"$.bibliotecas","esperada lista de referências de bibliotecas.")
    ids = [pacote(r,f"$.bibliotecas[{i}]").id for i,r in enumerate(d["bibliotecas"])]
    exigir(len(ids)==len(set(ids)),"$.bibliotecas","biblioteca habilitada mais de uma vez.")
    if "grade" in d:
        v = d["grade"]
        campos(v,"$.grade",(),("tipo","passo"))
        exigir(v.get("tipo","linhas") in ("linhas","pontos","nenhuma"),"$.grade.tipo","use linhas, pontos ou nenhuma.")
        exigir(type(v.get("passo",40))==int and v.get("passo",40) in (10,20,40),"$.grade.passo","use 10, 20 ou 40.")
    if "minimapa" in d:
        ponto(d["minimapa"],"$.minimapa")
        exigir(all(0<=n<=1 for n in d["minimapa"]),"$.minimapa","coordenadas normalizadas entre 0 e 1.")
    total = 0
    for nome,f in d["folhas"].items():
        texto(nome,"$.folhas (nome)",128)
        exigir(bool(nome),"$.folhas","nome de folha vazio.")
        p = f"$.folhas.{nome}"
        campos(f,p,("componentes","ligacoes"),("pacote","formas","nos","cores_bibliotecas"))
        if "pacote" in f:
            pacote(f["pacote"],p+".pacote")
        usados = set()
        for grupo in ("componentes","nos","ligacoes","formas"):
            mapa = f.get(grupo,{})
            objeto(mapa,p+"."+grupo)
            total += len(mapa)
            exigir(total<=LIMITES["objetos"],p,"limite de 20.000 objetos no documento excedido.")
            for id_ in mapa:
                exigir(isinstance(id_,str) and re.fullmatch(r"[\w.-]{1,128}",id_),p+"."+grupo,"ID inválido; use letras, números, _, . ou -, até 128 caracteres.")
                exigir(id_ not in usados,p+"."+grupo+"."+id_,"ID repetido entre tipos de objetos desta folha.")
                usados.add(id_)
        for id_,v in f["componentes"].items():
            q = p+".componentes."+id_
            campos(v,q,("tipo","nome","x","y"),("pacote","rotacao","espelho","mostrar_nome","escala","posicao_nome","tamanho_nome"))
            lib = pacote_obj(v,f,q)
            exigir(isinstance(v["tipo"],str) and v["tipo"] in lib.componentes,q+".tipo",f"componente inexistente na biblioteca {lib.id}.")
            numero(v.get("tamanho_nome",12),q+".tamanho_nome",8,96,True)
            numero(v.get("escala",1),q+".escala",1,4,True)
            if "posicao_nome" in v:
                ponto(v["posicao_nome"],q+".posicao_nome")
            texto(v["nome"],q+".nome")
            ponto([v["x"],v["y"]],q+".posição")
            exigir(type(v.get("rotacao",0))==int and v.get("rotacao",0) in (0,90,180,270),q+".rotacao","use 0, 90, 180 ou 270.")
            booleanos(v,q,("espelho","mostrar_nome"))
        for id_,xy in f.get("nos",{}).items():
            ponto(xy,p+".nos."+id_)
        for id_,v in f["ligacoes"].items():
            q = p+".ligacoes."+id_
            campos(v,q,("a","b","condutor"),("pacote","pontos","cor","espessura","opacidade","tracejado","mostrar_nome","etiqueta"))
            lib = pacote_obj(v,f,q)
            exigir(isinstance(v["condutor"],str) and v["condutor"] in lib.conexoes["categorias"],q+".condutor",f"categoria inexistente na biblioteca {lib.id}.")
            estilo(v,q)
            ref(v["a"],f,q+".a")
            ref(v["b"],f,q+".b")
            pontos(v.get("pontos",[]),q+".pontos")
            if "etiqueta" in v:
                ponto(v["etiqueta"],q+".etiqueta")
                exigir(0<=v["etiqueta"][0]<=1 and abs(v["etiqueta"][1])<=32,q+".etiqueta","use [fração 0–1, afastamento -32–32].")
        for id_,v in f.get("formas",{}).items():
            q = p+".formas."+id_
            campos(v,q,("tipo","pontos","cor"),("espessura","opacidade","texto","fonte","tamanho","angulo","ancoras"))
            exigir(v["tipo"] in FORMAS,q+".tipo","forma desconhecida.")
            estilo(v,q)
            if v["tipo"]=="Texto":
                pontos(v["pontos"],q+".pontos",1,1)
                texto(v.get("texto"),q+".texto",LIMITES["texto"])
                exigir(v.get("fonte","Segoe UI") in FONTES,q+".fonte","fonte não suportada.")
                numero(v.get("tamanho",18),q+".tamanho",1,512,True)
                numero(v.get("angulo",0),q+".angulo",0,359,True)
            else:
                exigir(not set(v)&{"texto","fonte","tamanho","angulo"},q,"propriedades de texto em forma geométrica.")
                pontos(v["pontos"],q+".pontos",2,LIMITES["pontos"] if v["tipo"] in ("Lápis","Seta curva") else 2)
            objeto(v.get("ancoras",{}),q+".ancoras")
            for k,r in v.get("ancoras",{}).items():
                exigir(v["tipo"]!="Texto" and k in ("0","1"),q+".ancoras","âncora inválida para esta forma.")
                ref(r,f,q+".ancoras."+k)
        objeto(f.get("cores_bibliotecas",{}),p+".cores_bibliotecas")
        for lib_id,cores in f.get("cores_bibliotecas",{}).items():
            q = p+".cores_bibliotecas."+lib_id
            try:
                lib = obter(lib_id)
            except ValueError as exc:
                raise ErroDocumento(q,str(exc)) from exc
            objeto(cores,q)
            for k,c in cores.items():
                exigir(k in lib.conexoes["categorias"] and c in CORES,q+"."+k,"categoria ou cor inválida.")
    for campo,waypoint in (("vistas",False),("waypoints",True)):
        objeto(d.get(campo,{}),"$."+campo)
        for k,v in d.get(campo,{}).items():
            p = f"$.{campo}.{k}"
            camera(v,p,waypoint)
            exigir((k in ("1","2","3") and v["folha"] in d["folhas"]) if waypoint else k in d["folhas"],p,"folha ou waypoint inexistente.")
    return d


def ler_json(texto_json):
    exigir(isinstance(texto_json,str),"$","esperado texto JSON.")
    exigir(len(texto_json.encode("utf-8"))<=LIMITES["bytes_json"],"$","JSON excede 10 MiB.")
    def pares_unicos(pares):
        d = {}
        for k,v in pares:
            exigir(k not in d,"$",f"chave JSON duplicada: {k}.")
            d[k] = v
        return d
    def constante(v):
        raise ErroDocumento("$",f"constante inválida: {v}. Use números finitos.")
    try:
        return json.loads(texto_json.lstrip("\ufeff"),object_pairs_hook=pares_unicos,parse_constant=constante)
    except json.JSONDecodeError as exc:
        raise ErroDocumento(f"linha {exc.lineno}, coluna {exc.colno}","JSON inválido: "+exc.msg) from exc
    except (RecursionError,OverflowError) as exc:
        raise ErroDocumento("$","JSON excessivamente profundo ou número fora dos limites.") from exc
