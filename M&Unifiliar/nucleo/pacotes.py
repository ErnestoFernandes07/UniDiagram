"""API 1 de pacotes declarativos. Não importa nem executa código de extensões."""
import json
import re
from dataclasses import dataclass
from math import isfinite
from pathlib import Path


class ErroPacote(ValueError):
    pass


def numeros(valores):
    return isinstance(valores, (list, tuple)) and all(type(v) in (int, float) and isfinite(v) and abs(v)<=10000 for v in valores)


def cor(valor):
    return isinstance(valor,str) and (valor=="" or re.fullmatch(r"#[0-9a-fA-F]{6}",valor))


@dataclass(frozen=True)
class Pacote:
    dados: dict

    @property
    def id(self): return self.dados["id"]
    @property
    def nome(self): return self.dados["nome"]
    @property
    def versao(self): return self.dados["versao"]
    @property
    def categorias(self): return self.dados["categorias"]
    @property
    def componentes(self): return self.dados["componentes"]
    @property
    def conexoes(self): return self.dados["conexoes"]

    def terminais(self,tipo):
        return [tuple(p) for p in self.componentes[tipo]["terminais"]]


def exigir(condicao):
    if not condicao:
        raise ValueError("Contrato de pacote não atendido")


def ler_pacote(path):
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        exigir(d["unidade"]==10)
        exigir(d["api"]==1 and type(d["versao"])==int and d["versao"]>=1)
        exigir(re.fullmatch(r"[a-z][a-z0-9_.-]+",d["id"]))
        exigir(isinstance(d["nome"],str) and 0<len(d["nome"])<=48)
        exigir(isinstance(d["componentes"],dict) and 0<len(d["componentes"])<=500)
        exigir(isinstance(d["categorias"],dict) and 0<len(d["categorias"])<=8)
        reservados = {"Selecionar","Mover","Ligar","Derivar","Fio","Retângulo","Losango","Elipse","Linha","Seta","Lápis","Texto","Seta curva"}
        exigir(not set(d["componentes"]) & (reservados | set(d["categorias"])))
        for nome,tipos in d["categorias"].items():
            exigir(isinstance(nome,str) and nome and isinstance(tipos,list) and tipos)
            exigir(all(t in d["componentes"] for t in tipos))
        publicados = [t for grupo in d["categorias"].values() for t in grupo]
        exigir(len(publicados)==len(set(publicados)))
        for nome,c in d["componentes"].items():
            exigir(isinstance(nome,str) and nome)
            portas = c["terminais"]
            exigir(isinstance(portas,list) and 1<=len(portas)<=64)
            exigir(all(numeros(p) and len(p)==2 for p in portas))
            exigir(all(v%10==0 for p in portas for v in p))
            exigir(len(set(map(tuple,portas)))==len(portas))
            exigir(type(c.get("apoio",0))==int and 0<=c.get("apoio",0)<len(portas))
            exigir(numeros([c.get("margem_nome",13)]))
            exigir(isinstance(c["simbolo"],list) and len(c["simbolo"])<=1000)
            for p in c["simbolo"]:
                tipo,pts = p["tipo"],p["pontos"]
                exigir(tipo in ("line","rectangle","oval","polygon","text") and numeros(pts))
                permitidos = {"tipo","pontos","fill"}
                if tipo=="text":
                    permitidos |= {"text","font"}
                else:
                    permitidos |= {"width"}
                    if tipo!="line":
                        permitidos.add("outline")
                exigir(set(p)<=permitidos)
                exigir(len(pts)%2==0)
                if tipo=="polygon":
                    exigir(len(pts)>=6)
                exigir(len(pts)==2 if tipo=="text" else len(pts)==4 if tipo in ("oval","rectangle") else len(pts)>=4)
                exigir(numeros([p.get("width",1.8)]) and .1<=p.get("width",1.8)<=32)
                for k in ("fill","outline"):
                    exigir(k not in p or cor(p[k]) or p[k]=="white")
                if tipo=="text":
                    exigir(isinstance(p["text"],str) and len(p["text"])<=256)
                    ft = p.get("font",["Segoe UI",-9])
                    exigir(isinstance(ft,list) and len(ft) in (2,3))
                    exigir(isinstance(ft[0],str) and type(ft[1])==int and 1<=abs(ft[1])<=128)
                    exigir(len(ft)==2 or ft[2] in ("bold","normal","italic"))
        links = d["conexoes"]
        exigir(1<=len(links["categorias"])<=12 and links["padrao"] in links["categorias"])
        exigir(all(isinstance(k,str) and k and cor(v) and v for k,v in links["categorias"].items()))
        exigir(isinstance(links.get("categorias_ocultas",[]),list) and set(links.get("categorias_ocultas",[]))<=set(links["categorias"]))
        exigir(links["padrao"] not in links.get("categorias_ocultas",[]))
        exigir(type(links["cores_compartilhadas"])==bool)
        exigir(isinstance(links["nomes_ocultos"],list) and set(links["nomes_ocultos"])<=set(links["categorias"]))
        exigir(isinstance(links.get("rotulo","Conexão"),str))
        if "biblioteca" in d:
            grupo = d["biblioteca"]
            exigir(isinstance(grupo,dict) and set(grupo)=={"id","nome","ferramentas"})
            exigir(isinstance(grupo["id"],str) and re.fullmatch(r"[a-z][a-z0-9_.-]+",grupo["id"]))
            exigir(isinstance(grupo["nome"],str) and 0<len(grupo["nome"])<=48)
            exigir(isinstance(grupo["ferramentas"],list) and all(t in ("Ligar","Derivar") for t in grupo["ferramentas"]))
        if "ia" in d:
            notas = d["ia"]
            exigir(isinstance(notas,dict) and set(notas)<={"descricao","restricoes","exemplos"})
            exigir(isinstance(notas.get("descricao",""),str) and len(notas.get("descricao",""))<=4000)
            for chave in ("restricoes","exemplos"):
                valores = notas.get(chave,[])
                exigir(isinstance(valores,list) and len(valores)<=20)
                exigir(all(isinstance(v,str) and len(v)<=2000 for v in valores))
        return Pacote(d)
    except (AssertionError,KeyError,TypeError,ValueError,OSError) as exc:
        raise ErroPacote(f"Pacote inválido: {path}. Confira o contrato da API 1.") from exc


GENERICO = Pacote(dict(id="nucleo.generico",nome="Genérico",versao=1,categorias={},componentes={},
    conexoes=dict(categorias={"Conexão":"#34445a"},padrao="Conexão",cores_compartilhadas=False,
                  nomes_ocultos=["Conexão"],rotulo="Conexão")))
REGISTRO = {}


def registrar(pacote):
    if pacote.id in REGISTRO or any(p.nome==pacote.nome for p in REGISTRO.values()):
        raise ErroPacote(f"ID ou nome de pacote duplicado: {pacote.id}")
    REGISTRO[pacote.id] = pacote


def obter(id_ou_nome):
    if id_ou_nome==GENERICO.id:
        return GENERICO
    pacote = REGISTRO.get(id_ou_nome) or next((p for p in REGISTRO.values() if p.nome==id_ou_nome),None)
    if pacote is None:
        raise ErroPacote(f"Pacote não instalado: {id_ou_nome}. Instale sua pasta em pacotes/ e reinicie o aplicativo.")
    return pacote


def referencia(pacote):
    return {"id":pacote.id,"versao":pacote.versao}


def resolver_ref(ref):
    if not isinstance(ref,dict) or not isinstance(ref.get("id"),str) or type(ref.get("versao"))!=int:
        raise ErroPacote("Referência de biblioteca inválida.")
    pacote = obter(ref["id"])
    if ref["versao"]!=pacote.versao:
        raise ErroPacote(f"O projeto exige {pacote.id} versão {ref['versao']}; instalada: {pacote.versao}.")
    return pacote


def pacote_da_folha(folha,nome=None):
    # Only old sheets carry a fallback. New sheets are generic.
    return resolver_ref(folha["pacote"]) if "pacote" in folha else GENERICO


def pacote_do_objeto(obj,folha,nome=None):
    return resolver_ref(obj["pacote"]) if "pacote" in obj else pacote_da_folha(folha,nome)


for manifesto in sorted((Path(__file__).resolve().parents[1]/"pacotes").glob("*/pacote.json")):
    registrar(ler_pacote(manifesto))
