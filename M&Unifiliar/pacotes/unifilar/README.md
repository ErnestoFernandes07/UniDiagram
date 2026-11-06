# Elétrica — Unifilar

ID `eletrica.unifilar`, versão 1, API 1, malha 10. Incluído na distribuição.

Um único terminal representa a entrada de um circuito nas cargas unifilares. Disjuntores e dispositivos de passagem têm entrada e saída. O traço pode representar um conjunto de condutores; não equivale a cada condutor físico separadamente. As cores das ligações podem ser individuais.

O manifesto define todas as portas e símbolos. Os índices das portas são persistidos nas ligações e devem permanecer estáveis. O barramento fica disponível apenas para abrir desenhos antigos, fora da biblioteca de inserção.

Os terminais foram ajustados para múltiplos de 10 na separação da fundação. Projetos elétricos v1/v2 são migrados por `pacotes/legado.py`. Não há conversão automática para multifilar nem certificação de conformidade normativa.

Ative esta biblioteca na caixa Bibliotecas +. Ela pode coexistir com a Multifilar na mesma folha, e cada objeto mantém seus próprios terminais.
