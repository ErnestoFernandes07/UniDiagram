"""Fixtures elétricas explícitas, independentes da abertura genérica do app."""
from nucleo.documento import migrar_bibliotecas


def eletrico_v3():
    return {"versao":3,"ativa":"Unifilar","folhas":{
        nome:{"pacote":{"id":"eletrica."+nome.lower(),"versao":1},"componentes":{},"ligacoes":{}}
        for nome in ("Unifilar","Multifilar")}}


def eletrico():
    d = eletrico_v3()
    migrar_bibliotecas(d)
    return d
