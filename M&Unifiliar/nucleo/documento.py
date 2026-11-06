import copy
import json
import os
import tempfile
from math import isfinite
from pathlib import Path

from formas import FORMAS, CORES, FONTES, alinhar_formas


from .pacotes import obter, pacote_da_folha, pacote_do_objeto, resolver_ref, referencia, ErroPacote
from .geometria import transformar
from .validacao import ErroDocumento, LIMITES, ler_json, validar_v4


def novo(pacotes=None):
    if pacotes is None:
        from configuracao import PACOTES_PADRAO
        pacotes = PACOTES_PADRAO
    habilitadas = [referencia(obter(id_)) for id_ in dict.fromkeys(pacotes)]
    return {"versao":4,"ativa":"Folha 1","bibliotecas":habilitadas,
            "folhas":{"Folha 1":{"componentes":{},"ligacoes":{}}}}


def migrar_bibliotecas(data):
    bibliotecas = {}
    for folha in data["folhas"].values():
        p = pacote_da_folha(folha)
        ref = referencia(p)
        bibliotecas[p.id] = ref
        for obj in [*folha["componentes"].values(),*folha["ligacoes"].values()]:
            obj["pacote"] = dict(ref)
        if "cores_condutores" in folha:
            folha["cores_bibliotecas"] = {p.id:folha.pop("cores_condutores")}
    data["bibliotecas"] = list(bibliotecas.values())
    data["versao"] = 4


def terminais(tipo, pacote):
    return obter(pacote).terminais(tipo)


def ponta_do_projeto(folha,nome,ref):
    id_,porta = ref
    if id_ in folha.get("nos",{}):
        return tuple(folha["nos"][id_])
    item = folha["componentes"][id_]
    return transformar(item,*pacote_do_objeto(item,folha,nome).terminais(item["tipo"])[porta])


def validar_dados(data):
    """Retorna uma cópia validada e migrada, sem alterar o argumento."""
    try:
        data = copy.deepcopy(data)
        if not isinstance(data,dict) or type(data.get("versao"))!=int:
            raise ErroDocumento("$.versao","esperado documento com versão inteira.")
        migrando = data["versao"] in (1,2)
        if migrando:
            from pacotes.legado import migrar_projeto, identificar_pacotes, ajustar_geometria
            if data["versao"]==1:
                migrar_projeto(data)
            identificar_pacotes(data)
            ajustar_geometria(data)
        if data["versao"]==3:
            migrar_bibliotecas(data)
        validar_v4(data)
        if migrando:
            for nome,folha in data["folhas"].items():
                alinhar_formas(folha,lambda ref:ponta_do_projeto(folha,nome,ref))
        return data
    except (ErroDocumento,ErroPacote):
        raise
    except (KeyError,IndexError,TypeError,AttributeError,ValueError,OverflowError,RecursionError) as exc:
        raise ErroDocumento("$","estrutura incompatível ou migração inválida: "+str(exc)) from exc


def carregar_texto(texto):
    return validar_dados(ler_json(texto))


def carregar(path):
    path = Path(path)
    if path.stat().st_size>LIMITES["bytes_json"]:
        raise ErroDocumento("$","JSON excede 10 MiB.")
    return carregar_texto(path.read_text(encoding="utf-8-sig"))


def ponto_valido(p):
    return isinstance(p,list) and len(p)==2 and all(type(v) in (int,float) and isfinite(v) for v in p)


def validar_estilo(obj):
    if type(obj.get("tracejado",False))!=bool:
        raise ValueError
    alpha,largura = obj.get("opacidade",100),obj.get("espessura",2)
    if type(alpha)!=int or not 0<=alpha<=100 or type(largura) not in (int,float) or not 0.5<=largura<=32:
        raise ValueError
    if "cor" in obj and obj["cor"] not in CORES:
        raise ValueError


def validar_ref(ref,folha,nome):
    chave,p = ref
    if type(p)!=int:
        raise ValueError
    if chave in folha.get("nos",{}) and p==0:
        return
    if not 0<=p<len(pacote_do_objeto(folha["componentes"][chave],folha,nome).terminais(folha["componentes"][chave]["tipo"])):
        raise ValueError


def vista_valida(vista):
    return ponto_valido([vista["x"],vista["y"]]) and type(vista["zoom"]) in (int,float) and 0.4<=vista["zoom"]<=4


def salvar(path, data):
    path = Path(path)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        temporario = tmp.name
    try:
        Path(temporario).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        os.replace(temporario, path)
    finally:
        Path(temporario).unlink(missing_ok=True)
