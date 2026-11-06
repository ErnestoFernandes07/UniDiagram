import tkinter as tk

from nucleo.geometria import transformar
from formas import CORES, FONTES
from paineis import Cartao, Faixa, Opacidade, TINTA


PADRAO = dict(fonte="Segoe UI",tamanho=18,angulo=0,espessura=2.2,opacidade=100)
TAMANHOS = (10,12,14,16,18,20,24,28,32,40,48,64,96)
TRACOS = (1,2,2.2,3,4,6,8,12)


class Propriedades:
    def montar_propriedades(self):
        self.inspector = Cartao(self.area,padding=12)
        corpo = self.inspector.conteudo
        self.titulo_inspector = tk.StringVar()
        tk.Label(corpo,textvariable=self.titulo_inspector,bg="white",fg=TINTA,
                 font=("Segoe UI",12,"bold")).pack(anchor="w")
        self.campos = tk.Frame(corpo,bg="white")
        self.campos.pack(fill="x")
        self.parametros = {}
        nomes = (("cor","Cor"),("fonte","Fonte"),("tamanho","Tamanho"),("espessura","Traço"),
                 ("angulo","Rotação"),("opacidade","Opacidade"))
        for chave,nome in nomes:
            linha = tk.Frame(self.campos,bg="white")
            cab = tk.Frame(linha,bg="white")
            cab.pack(fill="x")
            tk.Label(cab,text=nome,bg="white",fg="#56675d",font=("Segoe UI",9)).pack(side="left")
            leitura = tk.StringVar()
            tk.Label(cab,textvariable=leitura,bg="white",fg="#5f7467",font=("Segoe UI",8)).pack(side="right")
            acao = lambda v,k=chave:self.definir_propriedade(k,v)
            if chave=="opacidade":
                controle = Opacidade(linha,self.ajustar_opacidade)
            elif chave=="cor":
                controle = Faixa(linha,[(v,v) for v in CORES],acao,cores=True)
            elif chave=="fonte":
                controle = Faixa(linha,[(v,("Aa",(v,11))) for v in FONTES],acao)
            elif chave=="tamanho":
                controle = Faixa(linha,[("-", "−"),(14,"S"),(18,"M"),(28,"L"),(48,"XL"),("+","+")],
                                 lambda v:self.passo_ou_valor("tamanho",v,TAMANHOS))
            elif chave=="espessura":
                controle = Faixa(linha,[("-","−"),(1,"─"),(3,"━"),(6,"▬"),("+","+")],
                                 self.escolher_traco)
            else:
                controle = Faixa(linha,[(-15,"−15°"),(15,"+15°"),(90,"↻ 90°")],
                                 lambda v:self.definir_propriedade("angulo",(self.objeto_inspecionado().get("angulo",0)+v)%360))
            controle.pack(fill="x")
            self.parametros[chave] = (linha,controle,leitura)
        self.escala_componente = tk.Frame(corpo,bg="white")
        tk.Label(self.escala_componente,text="Escala · malha preservada",bg="white",fg=TINTA).pack(anchor="w")
        self.controle_escala = Faixa(self.escala_componente,[(n,f"{n}×") for n in (1,2,3,4)],lambda v:self.definir_propriedade("escala",v))
        self.controle_escala.pack()
        tk.Label(self.escala_componente,text="Tamanho do nome · próximos também",bg="white",fg=TINTA).pack(anchor="w",pady=(5,0))
        self.controle_nome = Faixa(self.escala_componente,[(n,str(n)) for n in (10,12,16,20,24,32)],lambda v:self.definir_propriedade("tamanho_nome",v))
        self.controle_nome.pack()
        rodape = tk.Frame(corpo,bg="white")
        self.exibir_nome = tk.BooleanVar()
        self.caixa_nome = tk.Checkbutton(corpo,text="Mostrar nome do fio",variable=self.exibir_nome,
                                         command=lambda:self.definir_propriedade("mostrar_nome",self.exibir_nome.get()),
                                         bg="white",activebackground="white",fg=TINTA,cursor="hand2")
        rodape.pack(fill="x",pady=(6,0))
        self.rodape_propriedades = rodape
        self.editar_rotulo = tk.Button(rodape,text="Editar texto",relief="flat",bd=0,bg="#e5f1eb",
                                      fg="#145943",command=self.reeditar_texto,cursor="hand2")
        self.excluir_objeto = tk.Button(rodape,text="Excluir",relief="flat",bd=0,bg="white",fg="#995047",
                                       command=self.excluir,cursor="hand2")

    def objeto_inspecionado(self):
        if self.texto_rascunho is not None:
            return self.texto_rascunho
        if self.modo=="Selecionar":
            return self.folha.get("formas",{}).get(self.selecao) or self.folha["ligacoes"].get(self.selecao) or self.folha["componentes"].get(self.selecao)
        return None

    def escolher_traco(self,valor):
        obj = self.objeto_inspecionado()
        if valor=="-" and "condutor" in obj:
            self.definir_propriedade("tracejado",not obj.get("tracejado",False))
        else:
            self.passo_ou_valor("espessura",valor,TRACOS)

    def passo_ou_valor(self,chave,v,opcoes):
        atual = self.objeto_inspecionado().get(chave,PADRAO[chave])
        if v=="-":
            v = next((n for n in reversed(opcoes) if n<atual),opcoes[0])
        elif v=="+":
            v = next((n for n in opcoes if n>atual),opcoes[-1])
        self.definir_propriedade(chave,v)

    def ajustar_opacidade(self,valor,inicio):
        if inicio:
            self.opacidade_alterada = False
        obj = self.objeto_inspecionado()
        if obj is not None and obj.get("opacidade",100)!=valor:
            self.definir_propriedade("opacidade",valor,lembrar=not self.opacidade_alterada)
            self.opacidade_alterada = True

    def definir_propriedade(self,chave,valor,lembrar=True):
        objeto = self.objeto_inspecionado()
        if objeto is None:
            return
        if chave=="tamanho_nome":
            self.tamanho_nome_padrao = valor
        if chave=="escala" and self.selecao in self.folha["componentes"]:
            if valor==objeto.get("escala",1):
                return
            self.lembrar()
            rotas = self.caminhos_ligados(self.selecao)
            definicao = self.pacote_para(objeto).componentes[objeto["tipo"]]
            porta = definicao["terminais"][definicao.get("apoio",0)]
            antes = transformar(objeto,*porta)
            objeto["escala"] = valor
            depois = transformar(objeto,*porta)
            objeto["x"] += antes[0]-depois[0]
            objeto["y"] += antes[1]-depois[1]
            self.acompanhar_pontas(rotas)
            self.render()
            return
        if chave=="cor" and "condutor" in objeto and self.pacote_para(objeto).conexoes["cores_compartilhadas"]:
            categoria = objeto["condutor"]
            if self.cor_do_condutor(categoria,obj=objeto)!=valor:
                self.lembrar()
                self.folha.setdefault("cores_bibliotecas",{}).setdefault(self.pacote_para(objeto).id,{})[categoria] = valor
                self.status.set(f"Cor aplicada a todos os fios {categoria} da biblioteca nesta folha.")
                self.render()
            self.c.focus_set()
            return
        if objeto.get(chave)!=valor:
            if self.texto_rascunho is None and lembrar:
                self.lembrar()
            objeto[chave] = valor
            self.render()
        if self.texto_rascunho is not None:
            self.entrada_texto.focus_set()
        else:
            self.c.focus_set()

    def reeditar_texto(self):
        texto = self.folha["formas"][self.selecao]
        self.iniciar_texto(texto["pontos"][0],self.selecao)

    def atualizar_propriedades(self):
        obj = self.objeto_inspecionado()
        if obj is None:
            self.inspector.place_forget()
            return False
        tipo = obj.get("tipo","Fio")
        componente = self.selecao in self.folha["componentes"] and self.texto_rascunho is None
        if componente:
            self.escala_componente.pack(before=self.rodape_propriedades,pady=5)
            self.controle_escala.set(obj.get("escala",1))
            self.controle_nome.set(obj.get("tamanho_nome",12))
        else:
            self.escala_componente.pack_forget()
        texto = tipo=="Texto"
        self.titulo_inspector.set(tipo if tipo!="Fio" else f"Fio · {obj['condutor']}")
        cor = self.cor_do_condutor(obj["condutor"],obj.get("cor"),obj) if tipo=="Fio" else obj.get("cor",CORES[0])
        if tipo=="Fio" or componente:
            self.caixa_nome.configure(text="Mostrar nome do componente" if componente else "Mostrar nome do fio")
            self.exibir_nome.set(obj.get("mostrar_nome",componente or obj["condutor"] not in self.pacote_para(obj).conexoes["nomes_ocultos"]))
            self.caixa_nome.pack(anchor="w",before=self.rodape_propriedades,pady=(3,0))
        else:
            self.caixa_nome.pack_forget()
        for i,(chave,(linha,controle,leitura)) in enumerate(self.parametros.items()):
            if componente or (chave not in ("cor","opacidade") and ((chave=="espessura")==texto)):
                linha.grid_remove()
                continue
            linha.grid(row=i,column=0,sticky="ew",pady=(3,0))
            valor = cor if chave=="cor" else obj.get(chave,2 if chave=="espessura" and tipo=="Fio" else PADRAO[chave])
            unidade = {"tamanho":" px","angulo":"°","espessura":" px","opacidade":"%"}.get(chave,"")
            leitura.set(f"{valor}{unidade}")
            if chave=="espessura":
                controle.opcoes[0] = ("-","┄" if tipo=="Fio" else "−")
                if tipo=="Fio" and obj.get("tracejado",False):
                    valor = "-"
                    leitura.set(f"{obj.get('espessura',2)} px · tracejado")
            controle.set(valor)
        if texto and self.texto_rascunho is None:
            self.editar_rotulo.pack(side="left")
        else:
            self.editar_rotulo.pack_forget()
        if self.texto_rascunho is None:
            self.excluir_objeto.pack(side="right")
        else:
            self.excluir_objeto.pack_forget()
        y = min(76,max(5,self.area.winfo_height()-self.inspector.winfo_reqheight()-8))
        self.inspector.place(x=-12,relx=1,y=y,anchor="ne")
        return True
