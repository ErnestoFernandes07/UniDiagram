MOTOR_FF = "Motor · alimentação bifásica"
CARGAS = {
    "Tomada 2P+T": ("P1","P2","PE"),
    "Luminária LED": ("P1","P2"), "Luminária LED com PE": ("P1","P2","PE"),
    "Carga resistiva": ("P1","P2"), "Carga resistiva com PE": ("P1","P2","PE"),
    "Motor monofásico": ("P1","P2","PE"), MOTOR_FF: ("L1","L2","PE"),
    "Motor trifásico": ("U","V","W","PE"),
}
def migrar_projeto(data):
    uni = data["folhas"]["Unifilar"]
    refs = [fio[lado] for fio in uni["ligacoes"].values() for lado in ("a","b")]
    for forma in uni.get("formas",{}).values():
        refs.extend(forma.get("ancoras",{}).values())
    for ref in refs:
        if ref[1]==1 and uni["componentes"].get(ref[0],{}).get("tipo") in CARGAS:
            ref[1] = 0
    multi = data["folhas"]["Multifilar"]
    for fio in multi["ligacoes"].values():
        if "cor" in fio:
            multi.setdefault("cores_condutores",{}).setdefault(fio["condutor"],fio.pop("cor"))
    data["versao"] = 2


def identificar_pacotes(data):
    for nome,folha in data["folhas"].items():
        ids = {"Unifilar":"eletrica.unifilar","Multifilar":"eletrica.multifilar"}
        if nome not in ids:
            raise ValueError("Folha legada desconhecida")
        folha["pacote"] = {"id":ids[nome],"versao":1}
    data["versao"] = 3


def ajustar_geometria(data):
    import json
    from pathlib import Path
    from nucleo.geometria import transformar
    from nucleo.documento import ponta_do_projeto
    from tracado import mover_vertice
    antigos = json.loads(Path(__file__).with_name("terminais_legados.json").read_text(encoding="utf-8"))
    for nome,folha in data["folhas"].items():
        def antiga(ref):
            id_,indice = ref
            if id_ in folha.get("nos",{}):
                return tuple(folha["nos"][id_])
            item = folha["componentes"][id_]
            return transformar(item,*antigos[nome][item["tipo"]][indice])
        for fio in folha["ligacoes"].values():
            if "pontos" in fio:
                rota = [antiga(fio["a"]),*fio["pontos"],antiga(fio["b"])]
                for indice,lado in ((0,"a"),(-1,"b")):
                    rota = mover_vertice(rota,indice%len(rota),ponta_do_projeto(folha,nome,fio[lado]))
                fio["pontos"] = [list(p) for p in rota[1:-1]]
