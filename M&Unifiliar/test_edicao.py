import tkinter as tk
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from PIL import Image

from app import Editor
from apoio_testes import eletrico
from formas import CORES, fator_alca, projetar_alcas
from projeto import carregar


class EdicaoTest(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as erro:
            self.skipTest(str(erro))
        self.addCleanup(self.root.destroy)
        self.erros = []
        self.root.report_callback_exception = lambda tipo,erro,tb:self.erros.append(str(erro))
        self.editor = Editor(self.root)
        self.assertEqual(self.editor.dados["bibliotecas"],[])
        self.assertEqual(self.editor.tabs,{})
        self.editor.substituir(eletrico(),None)
        self.editor.categorias.place(x=980,y=350)
        self.root.update()

    def tearDown(self):
        self.assertEqual(self.erros,[])

    def mouse(self,nome,p):
        e = self.editor
        x = round(p[0]*e.zoom-e.c.canvasx(0))
        y = round(p[1]*e.zoom-e.c.canvasy(0))
        e.c.event_generate(nome,x=x,y=y,state=256 if nome=="<B1-Motion>" else 0)
        self.root.update()

    def clique(self,p):
        self.mouse("<ButtonPress-1>",p)
        self.mouse("<ButtonRelease-1>",p)

    def arrastar(self,a,b):
        self.mouse("<ButtonPress-1>",a)
        self.mouse("<B1-Motion>",b)
        self.mouse("<ButtonRelease-1>",b)

    def test_biblioteca_opcional_e_seta_curva(self):
        from nucleo.documento import novo, validar_dados
        from nucleo.pacotes import REGISTRO
        from types import SimpleNamespace
        from imagem import rasterizar
        e = self.editor
        e.substituir(novo(),None)
        self.assertNotIn("Ligar",e.ferramentas)
        self.assertNotIn("Derivar",e.ferramentas)
        e.ferramenta("Ligar")
        self.assertEqual(e.modo,"Selecionar")
        ids = tuple(p.id for p in REGISTRO.values() if p.dados.get("biblioteca",{}).get("id")=="diagrama.eletrico")
        self.assertEqual(len(ids),2)
        e.habilitar_grupo(ids,True)
        self.assertEqual(len(e.dados["folhas"]),1)
        e.ferramenta_biblioteca("Ligar")
        self.assertEqual(e.modo,"Ligar")
        e.habilitar_grupo(ids,False)
        self.assertEqual(e.modo,"Selecionar")
        e.ferramenta("Seta curva")
        e.clique_curva((300,200))
        e.continuar_curva((500,350))
        self.assertGreater(len(e.curva_previa["pontos"]),2)
        self.assertEqual(len(e.folha.get("formas",{})),0)
        e.clique_curva((500,350),True)
        e.clique_curva((700,400))
        chave = e.selecao
        self.assertEqual(e.folha["formas"][chave]["tipo"],"Seta curva")
        self.assertIsNone(e.curva_previa)
        # Ctrl+clique percorre o mesmo handler dos eventos reais.
        pts = e.folha["formas"][chave]["pontos"]
        x,y = [(a+b)/2 for a,b in zip(pts[0],pts[1])]
        e.clique(SimpleNamespace(x=x*e.zoom-e.c.canvasx(0),y=y*e.zoom-e.c.canvasy(0),state=4))
        self.assertEqual(e.modo,"Seta curva")
        self.assertAlmostEqual(e.curva_fixa[0][0],x,delta=1/e.zoom)
        self.assertAlmostEqual(e.curva_fixa[0][1],y,delta=1/e.zoom)
        e.clique_curva((200,450))
        self.assertEqual(len(e.folha["formas"]),2)
        self.assertEqual(e.folha["ligacoes"],{})
        self.assertEqual(validar_dados(e.dados),e.dados)
        self.assertGreater(rasterizar(e.c,e.c.bbox("all"),1,"white",e.c.find_all()).width,0)
        e.ramificar_forma((x,y))
        e.ferramenta("Selecionar")
        self.assertIsNone(e.curva_previa)
        self.assertEqual(len(e.folha["formas"]),2)

    def test_canvas_retido_e_movimento_mais_recente(self):
        from types import SimpleNamespace
        e=self.editor
        e.folha["formas"]={"caixa":dict(tipo="Retângulo",pontos=[[300,200],[400,300]],cor=CORES[0])}
        e.selecao="caixa"
        e.render()
        ids=e.c.find_withtag("forma:caixa")
        caixa=e.c.bbox("forma:caixa")
        for _ in range(5):e.render()
        self.assertEqual(e.c.find_withtag("forma:caixa"),ids)
        self.assertEqual(e.c.bbox("forma:caixa"),caixa)
        for i in range(10):
            e.folha["formas"]["caixa"]["pontos"]=[[300+i,200],[400+i,300]]
            e.render()
        box=e.c.bbox("forma:caixa")
        self.assertEqual(box[2]-box[0],caixa[2]-caixa[0])
        vistos=[]
        for i in range(200):
            e.agendar_movimento(lambda evento:vistos.append(evento.x),SimpleNamespace(x=i))
        self.root.update()
        self.assertEqual(vistos,[199])
        e.agendar_movimento(lambda evento:vistos.append(evento.x),SimpleNamespace(x=201))
        e.terminar_pan()
        self.root.update()
        self.assertEqual(vistos,[199,201])
        e.folha["formas"].clear()
        e.render()
        self.assertFalse(e.c.find_withtag("forma:caixa"))

    def test_tracejado_nome_grade_e_categorias(self):
        from imagem import rasterizar
        e = self.editor
        e.folha["componentes"]["s"] = dict(tipo="Interruptor",nome="Nome ocultável",x=300,y=250)
        e.selecao = "s"
        e.render()
        self.root.update()
        self.assertTrue(e.caixa_nome.winfo_ismapped())
        e.caixa_nome.invoke()
        self.assertFalse(e.folha["componentes"]["s"]["mostrar_nome"])
        self.assertFalse(any(e.c.type(i)=="text" and e.c.itemcget(i,"text")=="Nome ocultável" for i in e.c.find_all()))
        e.folha["nos"] = {"a":[100,200],"b":[500,200]}
        e.folha["ligacoes"]["f"] = dict(a=["a",0],b=["b",0],condutor="L1",espessura=3,mostrar_nome=False)
        e.selecao = "f"
        e.render()
        self.root.update()
        e.parametros["espessura"][1].event_generate("<Button-1>",x=10,y=10)
        self.root.update()
        self.assertTrue(e.folha["ligacoes"]["f"]["tracejado"])
        self.assertEqual(e.folha["ligacoes"]["f"]["espessura"],3)
        c = tk.Canvas(self.root)
        e.cena(c,False)
        im = rasterizar(c,(150,190,450,210),1,"white",c.find_all())
        linha = [im.getpixel((x,10)) for x in range(300)]
        self.assertIn((255,255,255),linha)
        self.assertTrue(any(cor!=(255,255,255) for cor in linha))
        c.destroy()
        e.definir_grade("tipo","pontos")
        e.definir_grade("passo",10)
        e.abrir_biblioteca("eletrica.unifilar")
        self.root.update()
        self.assertIn("Proteção",e.arvore.get_children())
        e.abrir_biblioteca("eletrica.multifilar")
        self.assertIn("Comando e cargas",e.arvore.get_children())
        with TemporaryDirectory() as pasta:
            e.path = Path(pasta)/"ensaio.json"
            e.salvar()
            data = carregar(e.path)
            self.assertEqual(data["grade"],dict(tipo="pontos",passo=10))
            self.assertTrue(data["folhas"]["Unifilar"]["ligacoes"]["f"]["tracejado"])
            self.assertFalse(data["folhas"]["Unifilar"]["componentes"]["s"]["mostrar_nome"])

    def test_insercao_pelo_terminal_shift_grade_zoom_e_rotacao(self):
        from nucleo.geometria import transformar
        e = self.editor
        e.ferramenta("Disjuntor DIN 2P")
        self.mouse("<Motion>",(317,213))
        self.assertTrue(e.c.find_withtag("previa_componente"))
        self.assertFalse(e.folha["componentes"])
        e.alternar_snap(True)
        item = e.componente_no_cursor((317,213),True)
        self.assertEqual(transformar(item,*e.pacote.terminais(e.modo)[0]),(320,210))
        e.transformacao("rotacao")
        e.transformacao("espelho")
        item = e.componente_no_cursor((317,213),True)
        self.assertEqual(transformar(item,*e.pacote.terminais(e.modo)[0]),(320,210))
        for fundo in ("linhas","pontos","nenhuma"):
            for passo in (10,20,40):
                e.definir_grade("tipo",fundo)
                e.definir_grade("passo",passo)
                self.assertEqual(e.componente_no_cursor((317,213),True),item)
        e.aplicar_zoom(1.5,0,0)
        x = round(317*e.zoom-e.c.canvasx(0))
        y = round(213*e.zoom-e.c.canvasy(0))
        e.c.event_generate("<ButtonPress-1>",x=x,y=y,state=1)
        e.c.event_generate("<ButtonRelease-1>",x=x,y=y,state=1)
        self.root.update()
        salvo = e.folha["componentes"][e.selecao]
        for p in e.pacote.terminais(e.modo):
            self.assertTrue(all(v%10==0 for v in transformar(salvo,*p)))
        self.assertEqual(salvo,item)
        e.ferramenta("Selecionar")
        self.assertFalse(e.c.find_withtag("previa_componente"))
        e.desfazer()
        self.assertFalse(e.folha["componentes"])
        e.refazer()
        self.assertEqual(next(iter(e.folha["componentes"].values())),item)

    def test_fluxograma_sem_alterar_editor(self):
        from nucleo.pacotes import ler_pacote, registrar, REGISTRO
        from nucleo.documento import novo
        p = ler_pacote(Path(__file__).with_name("exemplos")/"fluxograma/pacote.json")
        registrar(p)
        self.addCleanup(lambda:REGISTRO.pop(p.id,None))
        e = self.editor
        e.substituir(novo([p.id]),None)
        self.root.update()
        self.assertEqual(e.tabs,{})
        e.abrir_biblioteca(p.id)
        self.assertEqual(e.arvore.get_children(),("Fluxo",))
        e.escolher("Processo")
        self.assertEqual(e.condutor.get(),"Fluxo")
        self.mouse("<Motion>",(317,213))
        self.clique((317,213))
        self.assertEqual(e.ponta([e.selecao,0]),(317,213))
        e.ferramenta("Selecionar")
        with TemporaryDirectory() as pasta:
            e.path = Path(pasta)/"fluxo.json"
            e.salvar()
            e.substituir(carregar(e.path),e.path)
            e.exportar()
            self.assertTrue(list(Path(pasta).glob("*.png")))

    def test_documento_generico_formas_sem_bibliotecas(self):
        from nucleo.documento import novo
        e = self.editor
        e.substituir(novo(),None)
        e.ferramenta("Retângulo")
        self.arrastar((300,220),(440,320))
        self.assertEqual(len(e.folha["formas"]),1)
        self.assertEqual(e.dados["bibliotecas"],[])
        self.assertEqual(e.tabs,{})
        with TemporaryDirectory() as pasta:
            e.path = Path(pasta)/"generico.json"
            e.salvar()
            e.substituir(carregar(e.path),e.path)
            self.assertEqual(len(e.folha["formas"]),1)
            self.assertEqual(e.dados["bibliotecas"],[])
            e.exportar()
            self.assertTrue(list(Path(pasta).glob("*.png")))

    def test_bibliotecas_checkbox_hover_mesma_folha_e_reabertura(self):
        import copy
        from nucleo.documento import novo
        e = self.editor
        e.substituir(novo(),None)
        self.root.update()
        self.assertEqual(e.tabs,{})
        self.assertEqual(e.botoes_bibliotecas,{})
        self.assertEqual(len(e.dados["folhas"]),1)
        e.biblioteca()
        self.root.update()
        self.assertTrue(e.painel_bibliotecas.winfo_ismapped())
        for id_ in ("eletrica.unifilar","eletrica.multifilar"):
            var,check = e.checks_bibliotecas[id_]
            self.assertFalse(var.get())
            check.invoke()
            self.root.update()
            self.assertTrue(e.checks_bibliotecas[id_][0].get())
        self.assertEqual(set(e.botoes_bibliotecas),{"eletrica.unifilar","eletrica.multifilar"})
        ids = []
        for id_,pos in (("eletrica.unifilar",(320,240)),("eletrica.multifilar",(580,240))):
            e.botoes_bibliotecas[id_].event_generate("<Enter>")
            self.root.update()
            self.assertTrue(e.painel.winfo_ismapped())
            self.assertEqual(e.pacote_catalogo.id,id_)
            e.prever_componente("Motor trifásico")
            self.root.update()
            e.escolher("Motor trifásico")
            self.clique(pos)
            ids.append(e.selecao)
        self.assertEqual(len(e.pacote_para(e.folha["componentes"][ids[0]]).terminais("Motor trifásico")),1)
        self.assertEqual(len(e.pacote_para(e.folha["componentes"][ids[1]]).terminais("Motor trifásico")),4)
        # Start and finish links through actual hit-tested terminals; each stores its source library.
        for k,id_ in enumerate(ids):
            e.ferramenta("Ligar")
            self.clique(e.ponta([id_,0]))
            self.clique((320+260*k,170))
        self.assertEqual({f["pacote"]["id"] for f in e.folha["ligacoes"].values()},
                         {"eletrica.unifilar","eletrica.multifilar"})
        e.ferramenta("Selecionar")
        objetos = copy.deepcopy(e.folha)
        for id_ in ("eletrica.unifilar","eletrica.multifilar"):
            e.checks_bibliotecas[id_][1].invoke()
            self.root.update()
        self.assertEqual(e.dados["bibliotecas"],[])
        self.assertEqual(e.botoes_bibliotecas,{})
        self.assertEqual(e.folha,objetos)
        self.assertFalse(e.painel.winfo_ismapped())
        e.desfazer()
        self.assertTrue(e.checks_bibliotecas["eletrica.multifilar"][0].get())
        e.refazer()
        self.assertEqual(e.dados["bibliotecas"],[])
        with TemporaryDirectory() as pasta:
            e.path = Path(pasta)/"misto.json"
            e.salvar()
            e.substituir(carregar(e.path),e.path)
            self.assertEqual(e.dados["bibliotecas"],[])
            self.assertEqual(e.folha,objetos)
            self.assertTrue(e.c.find_withtag("porta:"+ids[1]+":3"))
            e.exportar()
            self.assertTrue(list(Path(pasta).glob("*.png")))

    def test_ponta_livre_conecta_ao_arrastar(self):
        from nucleo.documento import validar_dados
        e = self.editor
        e.folha["componentes"]["alvo"] = dict(tipo="Interruptor",nome="Alvo",x=550,y=300)
        e.folha["nos"] = {"livre":[350,300],"origem":[250,200]}
        e.folha["ligacoes"]["f"] = dict(a=["origem",0],b=["livre",0],condutor="L1",pontos=[[250,300]])
        e.render();self.root.update()
        destino = e.ponta(["alvo",0])
        self.arrastar((350,300),(destino[0]+2,destino[1]+2))
        self.assertEqual(e.folha["ligacoes"]["f"]["b"],["alvo",0])
        self.assertNotIn("livre",e.folha["nos"])
        rotas=e.caminhos_ligados("alvo")
        e.folha["componentes"]["alvo"]["x"]+=100
        e.acompanhar_pontas(rotas)
        self.assertEqual(tuple(e.caminho(e.folha["ligacoes"]["f"])[-1]),e.ponta(["alvo",0]))
        self.assertEqual(validar_dados(e.dados),e.dados)
        e.ferramenta_biblioteca("Ligar")
        self.assertNotIn("Circuito",dict(e.escolha_condutor.opcoes))
        self.clique(e.ponta(["alvo",1]))
        self.clique((750,430))
        novos=[f for id_,f in e.folha["ligacoes"].items() if id_!="f"]
        self.assertEqual(len(novos),1)
        self.assertTrue(novos[0]["mostrar_nome"])

    def test_cor_compartilhada_isolada_por_biblioteca(self):
        from nucleo.documento import novo
        from nucleo.pacotes import obter,referencia
        e = self.editor
        e.substituir(novo(),None)
        e.folha["nos"] = {"a":[300,230],"b":[600,230]}
        for id_,lib in (("u","eletrica.unifilar"),("u2","eletrica.unifilar"),("m","eletrica.multifilar"),("m2","eletrica.multifilar")):
            e.folha["ligacoes"][id_] = dict(a=["a",0],b=["b",0],condutor="L1",pacote=referencia(obter(lib)))
        e.selecao = "m"
        e.render()
        e.definir_propriedade("cor",CORES[2])
        for id_ in ("u","m","m2"):
            fio = e.folha["ligacoes"][id_]
            cor = e.cor_do_condutor("L1",obj=fio)
            self.assertEqual(cor==CORES[2],id_!="u")
        e.selecao = "u"
        e.definir_propriedade("cor",CORES[1])
        self.assertEqual(e.cor_do_condutor("L1",obj=e.folha["ligacoes"]["u"]),CORES[1])
        self.assertEqual(e.cor_do_condutor("L1",obj=e.folha["ligacoes"]["u2"]),CORES[1])
        self.assertEqual(e.cor_do_condutor("L1",obj=e.folha["ligacoes"]["m"]),CORES[2])

    def test_importacao_ia_revisao_cancelamento_e_texto_alterado(self):
        import copy
        e = self.editor
        antes = copy.deepcopy(e.dados)
        d = e.importar_resposta_ia()
        self.root.update()
        self.assertEqual(d.botao_substituir.cget("state"),"disabled")
        d.preencher('{"versao":4}')
        self.assertFalse(d.validar())
        self.assertFalse(d.aplicar(True))
        self.assertEqual(e.dados,antes)
        bruto = (Path(__file__).with_name("exemplos")/"ia/unifilar.json").read_text(encoding="utf-8")
        d.preencher(bruto)
        self.assertTrue(d.validar())
        self.assertIn("2 componentes",d.resumo.get())
        self.assertEqual(e.dados,antes)
        d.entrada.insert("end"," alterado")
        self.assertFalse(d.aplicar(True))
        self.assertEqual(e.dados,antes)
        d.cancelar()
        self.assertEqual(e.dados,antes)

    def test_importacao_ia_substitui_backup_undo_e_falha_segura(self):
        import copy
        from unittest.mock import patch
        e = self.editor
        data = carregar(Path(__file__).with_name("exemplos")/"ia/multifilar.json")
        with TemporaryDirectory() as pasta:
            e.path = Path(pasta)/"original.json"
            e.salvar()
            antes = e.estado_para_ia()
            arquivo_antes = e.path.read_bytes()
            with patch("integracao_ia.salvar",side_effect=OSError("disco cheio")):
                with self.assertRaises(OSError):
                    e.aplicar_documento_ia(data,True,Path(pasta)/"backup")
            self.assertEqual(e.dados,antes)
            copia = e.aplicar_documento_ia(data,True,Path(pasta)/"backup")
            self.assertEqual(carregar(copia),antes)
            self.assertEqual(e.path.read_bytes(),arquivo_antes)
            self.assertTrue(e.c.find_withtag("item:q1"))
            self.assertTrue(e.c.find_withtag("fio:f0"))
            e.desfazer()
            self.assertEqual(e.dados,antes)
            e.aba.set("Multifilar")
            e.trocar()
            self.assertEqual(e.dados["ativa"],"Multifilar")
            e.refazer()
            self.assertEqual(e.dados,data)
            e.salvar()
            self.assertEqual(carregar(e.path),e.dados)

    def test_importacao_ia_fluxo_completo_nova_janela_e_arquivo(self):
        import copy
        from unittest.mock import patch
        e = self.editor
        antes = copy.deepcopy(e.dados)
        path = Path(__file__).with_name("exemplos")/"ia/unifilar.json"
        d = e.importar_resposta_ia()
        with patch("integracao_ia.filedialog.askopenfilename",return_value=str(path)):
            d.abrir_arquivo()
        self.assertTrue(d.validar())
        novo_editor = d.aplicar(False)
        self.root.update()
        self.assertEqual(e.dados,antes)
        self.assertIsNone(novo_editor.path)
        self.assertIsNone(novo_editor.gravado)
        self.assertTrue(novo_editor.c.find_withtag("item:luz"))
        self.assertTrue(novo_editor.c.find_withtag("fio:c1"))
        with TemporaryDirectory() as pasta:
            novo_editor.path = Path(pasta)/"importado.json"
            novo_editor.salvar()
            dados = copy.deepcopy(novo_editor.dados)
            novo_editor.substituir(carregar(novo_editor.path),novo_editor.path)
            self.assertEqual(novo_editor.dados,dados)
            novo_editor.exportar()
            self.assertTrue(list(Path(pasta).glob("*.png")))
        novo_editor.root.destroy()
        self.assertTrue(e.root.winfo_exists())

    def test_contexto_ia_clipboard_atual_e_novo(self):
        e = self.editor
        e.folha["formas"] = {"texto":dict(tipo="Texto",pontos=[[300,300]],texto="DADO_PRIVADO_TESTE",cor=CORES[0])}
        self.assertIn("DADO_PRIVADO_TESTE",e.copiar_contexto_ia())
        self.assertIn("DADO_PRIVADO_TESTE",e.root.clipboard_get())
        e.copiar_contexto_ia(False)
        self.assertNotIn("DADO_PRIVADO_TESTE",e.root.clipboard_get())

    def test_shift_formas_e_painel_vertical(self):
        e = self.editor
        e.aplicar_zoom(1.5,0,0)
        def evento(nome,pos):
            e.c.event_generate(nome,x=round(pos[0]*e.zoom-e.c.canvasx(0)),y=round(pos[1]*e.zoom-e.c.canvasy(0)),state=1)
            self.root.update()
        for tipo in ("Linha","Seta","Retângulo","Elipse","Losango"):
            e.ferramenta(tipo)
            evento("<ButtonPress-1>",(313,227))
            evento("<B1-Motion>",(467,343))
            evento("<ButtonRelease-1>",(467,343))
            forma = e.folha["formas"][e.selecao]
            self.assertTrue(all(v%10==0 for p in forma["pontos"] for v in p))
        e.folha["formas"].clear()
        e.ferramenta("Linha")
        evento("<ButtonPress-1>",(313,227))
        evento("<B1-Motion>",(467,343))
        evento("<ButtonRelease-1>",(467,343))
        e.ferramenta("Selecionar")
        e.gesto_forma = ((470,340),[[310,230],[470,340]],1,False)
        e.editar_forma((493,367),True)
        self.assertEqual(e.folha["formas"][e.selecao]["pontos"][-1],[490,370])
        alca = e.categorias.conteudo.winfo_children()[0]
        alca.event_generate("<ButtonPress-1>",x=8,y=8)
        alca.event_generate("<B1-Motion>",x=700,y=80,state=256)
        self.root.update()
        self.assertGreater(e.categorias.winfo_x(),500)
        botoes = list(e.botoes_bibliotecas.values())
        self.assertEqual(botoes[0].winfo_x(),botoes[1].winfo_x())
        self.assertLess(botoes[0].winfo_y(),botoes[1].winfo_y())
        e.abrir_biblioteca("eletrica.unifilar")
        self.root.update()
        self.assertGreaterEqual(e.painel.winfo_x(),0)
        self.assertLessEqual(e.painel.winfo_x()+e.painel.winfo_width(),e.area.winfo_width())

    def test_nome_escala_e_padrao_dos_proximos(self):
        from nucleo.simbolos import posicao_nome
        e = self.editor
        e.folha["componentes"] = {
            "a":dict(tipo="Interruptor",nome="S1",x=300,y=300),
            "b":dict(tipo="Interruptor",nome="S2",x=600,y=300)}
        e.selecao = "a"
        e.render()
        self.root.update()
        item = e.folha["componentes"]["a"]
        pos = posicao_nome(item,e.pacote_para(item))
        self.arrastar(pos,(pos[0]+70,pos[1]+25))
        self.assertEqual((item["x"],item["y"]),(300,300))
        self.assertEqual(posicao_nome(item,e.pacote_para(item)),(pos[0]+70,pos[1]+25))
        apoio = e.ponta(["a",0])
        e.definir_propriedade("escala",3)
        self.assertEqual(e.ponta(["a",0]),apoio)
        self.assertTrue(all(v%10==0 for i in range(2) for v in e.ponta(["a",i])))
        e.definir_propriedade("tamanho_nome",24)
        self.assertEqual(item["tamanho_nome"],24)
        self.assertEqual(e.folha["componentes"]["b"].get("tamanho_nome",12),12)
        e.ferramenta("Interruptor")
        novo = e.componente_no_cursor((800,300),True)
        self.assertEqual(novo["tamanho_nome"],24)
        e.ferramenta("Selecionar")
        with TemporaryDirectory() as pasta:
            e.path = Path(pasta)/"escala.json"
            e.salvar()
            e.substituir(carregar(e.path),e.path)
            self.assertEqual(e.folha["componentes"]["a"],item)
            e.exportar()
            self.assertTrue(list(Path(pasta).glob("*.png")))

    def test_shift_endireita_desvio_do_fio(self):
        from tracado import alinhar_gesto_fio, deslocar_trecho
        rota = [(0,0),(30,0),(30,30),(70,30),(70,0),(100,0)]
        delta,guia = alinhar_gesto_fio(rota,"trecho",2,(0,-26),1)
        self.assertEqual(guia,(1,0))
        self.assertEqual(deslocar_trecho(rota,2,*delta),[(0,0),(100,0)])
        delta,guia = alinhar_gesto_fio(rota,"trecho",2,(0,-26),4)
        self.assertIsNone(guia)
        self.assertGreater(len(deslocar_trecho(rota,2,*delta)),2)

    def test_texto_inline_e_estilo_persistido(self):
        e = self.editor
        e.ferramenta("Texto")
        self.clique((310,210))
        self.assertTrue(e.inspector.winfo_ismapped())
        e.entrada_texto.focus_force()
        for tecla in ("r","d","g","1"):
            e.entrada_texto.event_generate("<KeyPress-"+tecla+">")
            self.root.update()
        self.assertEqual(e.texto_rascunho["texto"],"rdg1")
        self.assertTrue(e.c.find_withtag("forma:"+e.selecao))
        for chave,valor in dict(cor=CORES[-1],fonte="Georgia",tamanho=32,angulo=45,opacidade=50).items():
            e.definir_propriedade(chave,valor)
        e.entrada_texto.event_generate("<Return>")
        self.root.update()
        forma = e.folha["formas"][e.selecao]
        self.assertEqual((forma["angulo"],forma["opacidade"],forma["fonte"]),(45,50,"Georgia"))
        e.reeditar_texto()
        e.entrada_texto.insert("end"," descartado")
        e.entrada_texto.event_generate("<Escape>")
        self.root.update()
        self.assertEqual(e.folha["formas"][e.selecao]["texto"],"rdg1")
        with TemporaryDirectory() as pasta:
            e.path = Path(pasta)/"ensaio.json"
            self.assertTrue(e.salvar())
            self.assertEqual(carregar(e.path),e.dados)
            e.exportar()
            with Image.open(next(Path(pasta).glob("*.png"))) as im:
                self.assertLess(im.getextrema()[0][0],250)

    def test_alcas_magneticas_e_centro(self):
        e = self.editor
        e.folha["componentes"]["q"] = dict(tipo="Interruptor",nome="S1",x=300,y=200)
        e.folha["nos"] = {"j":[480,280]}
        e.folha["ligacoes"]["f"] = dict(a=["q",0],b=["j",0],condutor="N")
        e.render()
        e.ferramenta("Linha")
        self.arrastar((160,145),(410,235))
        linha = e.folha["formas"][e.selecao]
        self.arrastar((410,235),(483,282))
        self.arrastar((160,145),(304,178))
        self.assertEqual(linha["ancoras"],{"0":["q",0],"1":["j",0]})
        self.assertEqual(linha["pontos"],[[300,170],[480,280]])
        self.clique((560,180))
        self.arrastar((480,280),(510,300))
        self.assertEqual(linha["pontos"][-1],[510,300])
        for tipo in ("Losango","Elipse"):
            e.ferramenta(tipo)
            self.arrastar((240,330),(303,178))
            f = e.folha["formas"][e.selecao]
            a,b = f["pontos"]
            self.assertEqual([(u+v)/2 for u,v in zip(a,b)],[240,330])
            alca = projetar_alcas(a,b,fator_alca(tipo))[1]
            self.assertAlmostEqual(alca[0],300)
            self.assertAlmostEqual(alca[1],170)

    def test_painel_do_fio_e_posicao_do_mapa(self):
        e = self.editor
        e.folha["nos"] = {"a":[300,180],"b":[500,180]}
        e.folha["ligacoes"] = {"f":dict(a=["a",0],b=["b",0],condutor="L1")}
        e.render()
        self.clique((400,180))
        self.assertEqual(e.selecao,"f")
        for chave,fracao in (("espessura",3.5/5),("opacidade",0.5),("cor",5.5/8)):
            campo = e.parametros[chave][1]
            campo.event_generate("<ButtonPress-1>",x=round(campo.winfo_width()*fracao),y=12)
            self.root.update()
        cab = e.minimapa.master.winfo_children()[0]
        cab.event_generate("<ButtonPress-1>",x=8,y=8)
        cab.event_generate("<B1-Motion>",x=88,y=-32,state=256)
        self.root.update()
        self.assertGreater(e.cartao_mapa.winfo_x(),14)
        pos = list(e.posicao_mapa)
        with TemporaryDirectory() as pasta:
            e.path = Path(pasta)/"ensaio.json"
            e.salvar()
            e.substituir(carregar(e.path),e.path)
            self.assertEqual(pos,e.posicao_mapa)
            self.assertEqual(e.folha["ligacoes"]["f"]["espessura"],6)
            e.exportar()
            with Image.open(next(Path(pasta).glob("*.png"))) as im:
                self.assertIn((152,189,221),im.getdata())

    def test_caixa_modificadores_arrasto_e_pan(self):
        e = self.editor
        for i in range(3):
            e.folha["componentes"][str(i)] = dict(tipo="Interruptor",nome=str(i),x=280+i*120,y=220)
        e.folha["ligacoes"]["f"] = dict(a=["0",1],b=["1",0],condutor="N",pontos=[[280,270],[400,270]])
        e.render()
        e.aplicar_zoom(1.2,0,0)
        self.arrastar((238,150),(435,280))
        self.assertEqual(e.grupo,{"0","1"})
        def mod(p,estado):
            c = e.c
            x = round(p[0]*e.zoom-c.canvasx(0))
            y = round(p[1]*e.zoom-c.canvasy(0))
            c.event_generate("<ButtonPress-1>",x=x,y=y,state=estado)
            c.event_generate("<ButtonRelease-1>",x=x,y=y,state=estado)
            self.root.update()
        mod((520,257),1)
        self.assertEqual(e.grupo,{"0","1","2"})
        mod((520,257),4)
        self.assertEqual(e.grupo,{"0","1"})
        self.arrastar((280,257),(310,267))
        self.assertEqual([v["x"] for v in e.folha["componentes"].values()],[310,430,520])
        self.assertEqual(e.folha["ligacoes"]["f"]["pontos"],[[310,280],[430,280]])
        e.c.event_generate("<ButtonPress-3>",x=245,y=208)
        antes = e.camera()
        e.c.event_generate("<B3-Motion>",x=285,y=246,state=1024)
        e.c.event_generate("<ButtonRelease-3>",x=285,y=246)
        self.root.update()
        self.assertNotEqual(antes["x"],e.camera()["x"])
        self.assertEqual(e.grupo,{"0","1"})
        e.excluir()
        self.assertEqual(set(e.folha["componentes"]),{"2"})
        e.desfazer()
        self.assertEqual(len(e.folha["componentes"]),3)

    def test_previa_do_componente_ao_passar_mouse(self):
        e = self.editor
        e.abrir_biblioteca("eletrica.unifilar")
        self.root.update()
        tipo = "Disjuntor DIN 3P"
        e.arvore.see(tipo)
        self.root.update()
        x,y,w,h = e.arvore.bbox(tipo)
        e.arvore.event_generate("<Motion>",x=x+35,y=y+h//2)
        self.root.update()
        self.assertEqual(e.amostra_tipo,tipo)
        self.assertTrue(e.simbolo_amostra.find_withtag("item:amostra"))
        e.arvore.event_generate("<Leave>")
        self.root.update()
        self.assertFalse(e.amostra.winfo_ismapped())

    def test_motor_trifasico_liga_cada_borne_e_reabre(self):
        e = self.editor
        e.aba.set("Multifilar")
        e.trocar()
        e.folha["componentes"] = {
            "m":dict(tipo="Motor trifásico",nome="M1",x=470,y=390),
            "q":dict(tipo="Quadro de distribuição",nome="QD",x=320,y=190)}
        e.render()
        for i,(categoria,borne) in enumerate(zip(("L1","L2","L3","PE"),(5,6,7,9))):
            e.condutor.set(categoria)
            e.ferramenta("Ligar")
            self.clique(e.ponta(["q",borne]))
            self.clique(e.ponta(["m",i]))
            self.assertTrue(e.c.find_withtag(f"porta:m:{i}"))
        refs = [f["b"] for f in e.folha["ligacoes"].values()]
        self.assertEqual(refs,[["m",i] for i in range(4)])
        self.assertEqual([f["condutor"] for f in e.folha["ligacoes"].values()],["L1","L2","L3","PE"])
        with TemporaryDirectory() as pasta:
            e.path = Path(pasta)/"motor.json"
            e.salvar()
            e.substituir(carregar(e.path),e.path)
            self.assertEqual([f["b"] for f in e.folha["ligacoes"].values()],refs)

    def test_etiqueta_arrastavel_e_cor_por_categoria(self):
        e = self.editor
        e.aba.set("Multifilar")
        e.trocar()
        e.folha["nos"] = {"a":[230,180],"b":[480,180],"c":[650,180],"d":[650,280]}
        for k,origem,destino,categoria in (("f","a","b","L1"),("g","b","c","L1"),("h","c","d","N")):
            e.folha["ligacoes"][k] = dict(a=[origem,0],b=[destino,0],condutor=categoria)
        e.render()
        e.aplicar_zoom(1.2,0,0)
        self.arrastar((355,169),(422,160))
        fio = e.folha["ligacoes"]["f"]
        self.assertIn("etiqueta",fio)
        self.assertEqual(e.caminho(fio),[(230,180),(480,180)])
        e.caixa_nome.invoke()
        self.assertFalse(fio["mostrar_nome"])
        self.assertFalse(any("etiqueta" in e.c.gettags(i) for i in e.c.find_withtag("fio:f")))
        e.definir_propriedade("cor",CORES[2])
        for k in ("f","g","h"):
            item = next(i for i in e.c.find_withtag("fio:"+k) if e.c.type(i)=="line")
            self.assertEqual(e.c.itemcget(item,"fill")==CORES[2],k!="h")
        e.caixa_nome.invoke()
        item = next(i for i in e.c.find_withtag("fio:f") if "etiqueta" in e.c.gettags(i))
        self.assertAlmostEqual(e.c.coords(item)[0]/e.zoom,422,delta=1)
        e.ferramenta("Derivar")
        self.clique((320,180))
        self.clique((330,290))
        self.assertEqual(len(e.folha["ligacoes"]),5)
        for k,f in e.folha["ligacoes"].items():
            if f["condutor"]=="L1":
                item = next(i for i in e.c.find_withtag("fio:"+k) if e.c.type(i)=="line")
                self.assertEqual(e.c.itemcget(item,"fill"),CORES[2])
        dono = next(k for k,f in e.folha["ligacoes"].items() if "etiqueta" in f)
        item = next(i for i in e.c.find_withtag("fio:"+dono) if "etiqueta" in e.c.gettags(i))
        self.assertAlmostEqual(e.c.coords(item)[0]/e.zoom,422,delta=1)
        with TemporaryDirectory() as pasta:
            e.path = Path(pasta)/"rotulos.json"
            e.salvar()
            self.assertEqual(carregar(e.path),e.dados)
            e.exportar()
            self.assertTrue(list(Path(pasta).glob("*.png")))
