import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from nucleo.pacotes import REGISTRO, ler_pacote, registrar, ErroPacote
from nucleo.documento import novo, salvar, carregar, ponta_do_projeto

BASE = Path(__file__).resolve().parent


class PacotesTest(unittest.TestCase):
    def test_migracao_v3_preserva_folhas_e_identifica_cada_objeto(self):
        from apoio_testes import eletrico_v3
        d = eletrico_v3()
        f = d["folhas"]["Multifilar"]
        f["componentes"]["m"] = dict(tipo="Motor trifásico",nome="M1",x=300,y=300)
        f["nos"] = {"n":[400,270]}
        f["ligacoes"]["f"] = dict(a=["m",2],b=["n",0],condutor="L1")
        f["cores_condutores"] = {"L1":"#5665c1"}
        with TemporaryDirectory() as pasta:
            path = Path(pasta)/"v3.json"
            salvar(path,d)
            atual = carregar(path)
            self.assertEqual(tuple(atual["folhas"]),("Unifilar","Multifilar"))
            f = atual["folhas"]["Multifilar"]
            self.assertEqual(f["componentes"]["m"]["pacote"]["id"],"eletrica.multifilar")
            self.assertEqual(f["ligacoes"]["f"]["pacote"]["id"],"eletrica.multifilar")
            self.assertEqual(f["cores_bibliotecas"]["eletrica.multifilar"]["L1"],"#5665c1")
            self.assertEqual(ponta_do_projeto(f,"Multifilar",["m",2]),(320,270))

    def test_contrato_malha_e_erros(self):
        for p in REGISTRO.values():
            for c in p.componentes.values():
                self.assertTrue(all(v%10==0 for xy in c["terminais"] for v in xy))
        d = json.loads((BASE/"exemplos/fluxograma/pacote.json").read_text(encoding="utf-8"))
        with TemporaryDirectory() as pasta:
            path = Path(pasta)/"pacote.json"
            for alteracao in (lambda c:c.update(terminais=[[1,0]]),
                              lambda c:c.update(apoio=99),
                              lambda c:c.update(simbolo=[{"tipo":"exec","pontos":[0,0]}])):
                ruim = copy.deepcopy(d)
                alteracao(ruim["componentes"]["Processo"])
                path.write_text(json.dumps(ruim),encoding="utf-8")
                with self.assertRaises(ErroPacote):
                    ler_pacote(path)

    def test_pacote_externo_e_dependencia_ausente(self):
        p = ler_pacote(BASE/"exemplos/fluxograma/pacote.json")
        registrar(p)
        try:
            doc = novo([p.id])
            with TemporaryDirectory() as pasta:
                path = Path(pasta)/"projeto.json"
                salvar(path,doc)
                self.assertEqual(carregar(path),doc)
                REGISTRO.pop(p.id)
                with self.assertRaisesRegex(ErroPacote,"não instalado"):
                    carregar(path)
        finally:
            REGISTRO.pop(p.id,None)

    def test_migracao_v2_ajusta_rota_e_nao_regrava_original(self):
        doc = {"versao":2,"ativa":"Unifilar","folhas":{
            "Unifilar":{"componentes":{"s":dict(tipo="Interruptor",nome="S",x=100,y=100)},
                        "nos":{"n":[200,200]},
                        "ligacoes":{"f":dict(a=["s",0],b=["n",0],condutor="L1",pontos=[[100,40],[200,40]])}},
            "Multifilar":{"componentes":{},"ligacoes":{}}}}
        with TemporaryDirectory() as pasta:
            path = Path(pasta)/"antigo.json"
            salvar(path,doc)
            antes = path.read_bytes()
            atual = carregar(path)
            self.assertEqual(atual["versao"],4)
            self.assertEqual(path.read_bytes(),antes)
            folha = atual["folhas"]["Unifilar"]
            fio = folha["ligacoes"]["f"]
            rota = [ponta_do_projeto(folha,"Unifilar",fio["a"]),*fio["pontos"],ponta_do_projeto(folha,"Unifilar",fio["b"])]
            self.assertEqual(rota[0],(100,70))
            self.assertTrue(all(a[0]==b[0] or a[1]==b[1] for a,b in zip(rota,rota[1:])))
