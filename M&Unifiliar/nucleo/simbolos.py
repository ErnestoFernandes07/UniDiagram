from .geometria import transformar
from .pacotes import obter


def posicao_nome(item,pacote):
    if "posicao_nome" in item:
        dx,dy = item["posicao_nome"]
        return item["x"]+dx,item["y"]+dy
    altura = max(abs(transformar(item,*p)[1]-item["y"]) for p in pacote.terminais(item["tipo"]))
    return item["x"],item["y"]+max(24*item.get("escala",1),altura)+pacote.componentes[item["tipo"]].get("margem_nome",13)


def desenhar(c,id_,item,pacote,selecionado=False,origem=None):
    pacote = obter(pacote) if isinstance(pacote,str) else pacote
    definicao = pacote.componentes[item["tipo"]]
    tag = "item:"+id_
    tinta = "#00786a" if selecionado else "#203b46"
    for primitiva in definicao["simbolo"]:
        tipo = primitiva["tipo"]
        pts = primitiva["pontos"]
        coords = [v for x,y in zip(pts[::2],pts[1::2]) for v in transformar(item,x,y)]
        kw = {k:v for k,v in primitiva.items() if k not in ("tipo","pontos")}
        for chave in ("fill","outline"):
            if kw.get(chave)=="#203b46":
                kw[chave] = tinta
        if "font" in kw:
            kw["font"] = (kw["font"][0],kw["font"][1]*item.get("escala",1),*kw["font"][2:])
        if "width" in kw:
            kw["width"] *= item.get("escala",1)
        if tipo in ("oval","rectangle"):
            coords = [min(coords[0],coords[2]),min(coords[1],coords[3]),max(coords[0],coords[2]),max(coords[1],coords[3])]
        getattr(c,"create_"+tipo)(*coords,**kw,tags=tag)
    portas = pacote.terminais(item["tipo"])
    altura = max(abs(transformar(item,*p)[1]-item["y"]) for p in portas)
    if item.get("mostrar_nome",True):
        c.create_text(*posicao_nome(item,pacote),
                      text=item["nome"],font=("Segoe UI",-item.get("tamanho_nome",12)),fill=tinta,tags=(tag,"nome_componente"))
    for i,p in enumerate(portas):
        x,y = transformar(item,*p)
        c.create_oval(x-3,y-3,x+3,y+3,outline=tinta,fill="#ffba40" if origem==[id_,i] else "white",
                      width=1.5,tags=(tag,f"porta:{id_}:{i}"))
