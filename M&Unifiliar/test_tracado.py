import unittest

from tracado import Referencias, mover_vertice


class TesteEsboco(unittest.TestCase):
    def test_juncao_arrastada_acompanha_o_joelho_de_um_projeto_antigo(self):
        caminho = [(150,80),(90,40),(420,40),(420,145)]
        novo = mover_vertice(caminho,0,(125,80))
        self.assertEqual(novo,[(125,80),(125,40),(420,40),(420,145)])
        self.assertEqual(mover_vertice(caminho[::-1],3,(125,80)),novo[::-1])

    def test_juncao_em_fio_reto_preserva_o_terminal_oposto(self):
        novo = mover_vertice([(120,80),(400,80)],0,(110,65))
        self.assertEqual(novo[0],(110,65))
        self.assertEqual(novo[-1],(400,80))
        for a,b in zip(novo,novo[1:]):
            self.assertTrue(a[0]==b[0] or a[1]==b[1])

    def test_cruzamento_combina_duas_referencias_com_tolerancia_em_pixels(self):
        for zoom in (0.4,1,2,4):
            refs = Referencias([(150,80),(420,145)])
            refs.ajustar((150,80),zoom)
            refs.ajustar((420,145),zoom)
            perto = (150+6/zoom,145-6/zoom)
            self.assertEqual(refs.ajustar(perto,zoom),(150,145))
            longe = (150+11/zoom,145-11/zoom)
            self.assertEqual(refs.ajustar(longe,zoom),longe)
            self.assertEqual(len(refs.visitados),2)


if __name__ == "__main__":
    unittest.main()
