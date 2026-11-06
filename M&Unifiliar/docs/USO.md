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

## Formas com Shift e barra lateral

Durante a criação de formas e linhas, segure Shift para encaixar na malha de 10 unidades. O mesmo vale para mover formas ou ajustar suas alças; terminais e nós próximos continuam tendo prioridade de conexão.

As bibliotecas aparecem em uma barra vertical à esquerda. Arraste o título ⠿ Bibliotecas para levá-la à direita ou a outra posição. Os catálogos abrem no lado disponível. A posição é mantida durante a sessão, sem alterar o JSON do projeto.

Selecione um componente e arraste seu nome para reposicioná-lo. No painel lateral, Escala oferece 1× a 4×, preservando o terminal de apoio e acompanhando as ligações. Tamanho do nome altera o selecionado e vira padrão para as próximas inserções na sessão; os demais componentes não mudam. Shift ao arrastar um trecho de fio encaixa nos eixos próximos e remove dobras redundantes. Junções de derivação reais são preservadas.

## Biblioteca de domínio e setas com dobras

O início é genérico: uma folha, formas e nenhuma biblioteca habilitada. Em **Bibliotecas +**, marque **Diagrama elétrico** para habilitar Unifilar e Multifilar juntos. As opções individuais permitem habilitar apenas um catálogo. A barra lateral arrastável mostra os catálogos e **Fio · Ligar** / **Fio · Derivar**; passe o mouse nos catálogos para acessar componentes. Desmarcar oculta ferramentas, preserva objetos e não cria nem remove folhas. A escolha é salva no JSON.

Na barra horizontal, **Seta curva** desenha caminhos com joelhos arredondados. Clique no início, mova o cursor para ver a prévia, use **Shift + clique** para fixar dobras na malha de 10 unidades e clique sem Shift para concluir. Esc cancela. Selecione a seta para arrastar suas alças.

Em Selecionar, **Ctrl + clique sobre uma linha, seta ou traço livre** começa uma nova seta no ponto clicado. Essa ramificação é visual e independente: não cria nó elétrico nem acompanha automaticamente movimentos futuros da linha original. Ctrl + clique em componentes mantém a seleção múltipla. L/D só ativam ferramentas de conexão quando há biblioteca habilitada; a derivação elétrica permanece em Fio · Derivar.

### Fios e vínculo de terminais (2026-11-06)

Os botões laterais de ligar e derivar usam ícones, sem seta de dropdown; o nome e atalho aparecem ao passar o mouse. Os novos fios elétricos usam L1 inicialmente e mostram o nome por padrão. Arrastar uma ponta livre até 10 pixels de um terminal conecta de fato ao componente: todas as ligações e formas ancoradas naquele nó passam a referenciar a porta. Mover o componente passa a levar os fios junto. Desfazer restaura a ponta livre.

Unifilar e Multifilar compartilham cores por categoria dentro de cada biblioteca e folha. Alterar L1 atualiza todos os L1 daquele catálogo, incluindo novas ligações. Bibliotecas diferentes permanecem independentes. Cores locais antigas não prevalecem sobre essa política compartilhada. “Circuito” fica oculto para novas escolhas, mas continua reconhecido em arquivos antigos para evitar renomear silenciosamente o conteúdo.

## Fluidez do canvas — 2026-11-06

O canvas e o minimapa reutilizam as primitivas já desenhadas. Arrastar um componente atualiza o componente e seus fios, sem reconstruir os objetos que não mudaram. Eventos de movimento pendentes são agrupados e apenas a posição mais recente é processada; soltar o botão aplica o último movimento antes de encerrar o gesto. Isso evita reproduzir um trajeto atrasado do cursor. Zoom, seleção e exportação continuam disponíveis.

A otimização não desativa vínculos: fios conectados continuam acompanhando componentes, inclusive sem Shift. Shift mantém seu papel de encaixe e alinhamento assistido. Não foi necessário mudar a biblioteca gráfica. Projetos com muita transparência ainda exigem composição raster e podem custar mais.

Para medir com o quadro de exemplo, execute `python -B medir_desempenho.py`. O script abre uma janela temporária e mede redesenho, pan e arraste circular; não salva alterações no projeto. As medições dependem do computador e do desenho.
