# Uso do editor

O aplicativo inicia com uma folha genérica, sem abas elétricas e sem bibliotecas marcadas. As ferramentas de formas, texto, navegação e exportação estão disponíveis imediatamente.

Abra **Bibliotecas +** na barra flutuante (ou Bibliotecas no topo). Marque Unifilar, Multifilar ou outro pacote instalado. As bibliotecas habilitadas aparecem na barra. Desmarcar uma opção preserva todos os componentes e ligações já desenhados, apenas retira o catálogo da barra. Essa escolha é salva no JSON e acompanha desfazer/refazer.

Projetos antigos com várias folhas mantêm suas abas para preservar o trabalho. Ativar uma biblioteca em um novo projeto não cria outra folha.

## Inserir um componente

Passe o mouse sobre uma biblioteca na barra flutuante para abrir suas categorias e componentes. Um clique também abre o catálogo, e Enter escolhe o item em foco. Passe sobre um componente para ver o símbolo e clique na opção desejada. Ao voltar ao canvas, uma prévia acompanha o cursor pelo terminal de apoio. Clique para inserir; Esc volta à seleção.

Durante a prévia:

- Shift mantido encaixa na malha de 10 unidades e mostra pontos auxiliares.
- Soltar Shift volta à posição livre.
- R gira 90° em torno do terminal de apoio.
- E espelha, também preservando o apoio.

Na mesma folha, o motor trifásico da biblioteca Unifilar continua com um terminal e o da Multifilar com seus terminais individuais. Selecionar outra biblioteca não converte objetos existentes. As conexões assumem a biblioteca do componente ou fio em que começam; as cores compartilhadas respeitam também essa biblioteca.

O snap não cria uma ligação elétrica automaticamente. Use Ligar ou Derivar para registrar conexões; sobrepor símbolos não cria uma conexão.

## Fundo e padronização

O botão Fundo oferece quadrados, pontos e nenhuma grade, com espaçamento visual pequeno (10), médio (20) ou grande (40). Trocar essas opções não move componentes nem altera fios. Para projetos padronizados, insira com Shift. Mesmo com grade espaçada ou invisível, os pontos auxiliares mostram a malha lógica perto da prévia.

## Principais atalhos

| Ação | Atalho ou gesto |
| --- | --- |
| Selecionar / mão | V / H |
| Navegar | Botão direito e arraste |
| Zoom | Roda do mouse, sobre o ponto de interesse |
| Seleção por área | Botão esquerdo e arraste no fundo |
| Adicionar / alternar componente na seleção | Shift / Ctrl + clique |
| Girar / espelhar | R / E |
| Ligar / derivar | L / D |
| Fixar dobra durante ligação | Shift + clique |
| Guias de alinhamento | G |
| Cancelar / excluir | Esc / Delete |
| Visitar waypoint | 1, 2, 3 |
| Marcar waypoint | Shift + 1, 2, 3 |
| Salvar / abrir | Ctrl + S / O |
| Desfazer / refazer | Ctrl + Z / Y |

A janela Atalhos também está disponível na interface. O efeito de Shift depende da ferramenta: inserir componente, selecionar múltiplos ou fixar dobra são gestos diferentes.

## Propriedades e saída

Selecionar um componente mostra a opção de exibir seu nome. Fios têm cor, espessura, tracejado, opacidade e visibilidade da etiqueta. O primeiro botão de Traço alterna o tracejado sem afinar o fio. Arraste a etiqueta para reposicioná-la.

Textos são editados na folha e têm fonte, tamanho, cor, opacidade e rotação no painel lateral. Formas geométricas compartilham os controles de estilo pertinentes.

Salvar JSON preserva o documento editável. Exportar folha em PNG salva a folha ativa na pasta do arquivo do projeto; antes de salvar o projeto, usa a pasta do aplicativo. O PNG exclui barras, prévias, seleção e grade de fundo.

## Troca de projetos com IA

Os comandos de copiar contexto e importar resposta ficam no menu Arquivo. A interface gráfica permanece a mesma. A importação exige validação e revisão antes de aplicar. Veja [INTEGRACAO_IA.md](INTEGRACAO_IA.md) para as opções de projeto novo, nova janela, substituição e recuperação.
