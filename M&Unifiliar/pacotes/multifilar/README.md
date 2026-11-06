# Elétrica — Multifilar

ID `eletrica.multifilar`, versão 1, API 1, malha 10. Incluído na distribuição.

Portas representam conexões individuais. O motor trifásico expõe U, V, W e PE. A opção de alimentação bifásica representa a alimentação fase-fase, sem afirmar que o motor tem enrolamento de um sistema bifásico verdadeiro. Cargas com e sem PE são componentes distintos quando disponíveis.

Cores são compartilhadas por categoria e biblioteca dentro da folha. Alterar L1, por exemplo, atualiza a cor de todas as ligações L1. O manifesto define as categorias e os terminais; mantenha seus índices estáveis. O barramento legado não aparece para novas inserções.

Os terminais foram ajustados para múltiplos de 10 na separação da fundação. Projetos elétricos v1/v2 são migrados por `pacotes/legado.py`. O editor não dimensiona condutores ou proteções e não converte automaticamente componentes para unifilar. Ative esta biblioteca na caixa Bibliotecas +; ela pode coexistir com outras na mesma folha.
