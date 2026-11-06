# Reprodução do quadro geral multifilar

Abra `quadro-geral-multifilar.json` em Arquivo → Abrir no aplicativo. O PNG é a exportação do mesmo documento, renderizada pelo aplicativo. `gerar.py` recria ambos; execute com Python e Pillow a partir de qualquer diretório.

Referência: imagem enviada pelo usuário neste chat. A reprodução tem 22 disjuntores NEMA editáveis (incluindo o geral), fases R/S/T representadas pelas categorias L1/L2/L3, neutro, PE, cargas identificadas e reservas. Os circuitos se conectam por referências reais de portas e nós; cruzamentos sem nó não são junções. As barras verticais são fios segmentados, sem acrescentar um componente de barramento ao catálogo.

## Diferenças e limites da transcrição

- Símbolos do catálogo atual, espaçamento e cores da paleta do app: não é cópia pixel a pixel. PE usa o tom ocre disponível, em vez do amarelo muito claro da referência; isso é uma opção gráfica, não uma especificação da cor física do condutor.
- Cargas são retângulos e textos editáveis, com pontas de fio livres nas bordas, não equipamentos elétricos parametrizados. Mover somente a caixa não move os fios; use seleção conjunta.
- Etiquetas repetidas dos fios ficam ocultas neste desenho, como na referência. As fases estão identificadas no topo. O padrão do aplicativo para novas ligações não foi alterado.
- Correntes e combinações de fases foram transcritas visualmente. Iluminação mantém os traços visíveis; não foi acrescentado neutro não mostrado na imagem.
- A parte inferior está cortada: somente os quatro traços de reserva visíveis foram representados. Nada foi inferido abaixo do recorte.
- Não foi feita validação elétrica, cálculo de proteção, seção dos condutores ou avaliação normativa.

O JSON usa documento v4 e biblioteca eletrica.multifilar v1. Não altera o código do editor nem projetos existentes.
