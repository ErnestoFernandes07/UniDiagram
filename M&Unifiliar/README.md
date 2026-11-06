# M&Unifiliar — editor e pacotes de diagramas

Editor desktop em Python/Tkinter, com fundação reutilizável e catálogos declarativos. A distribuição inclui os pacotes **Unifilar** e **Multifilar**. O aplicativo abre com uma folha genérica e nenhuma biblioteca habilitada. Os pacotes elétricos ficam disponíveis para ativação opcional.

## Executar

Requisitos: Python 3.10 ou superior, Tkinter e Pillow para PNG/transparência. No Windows, o instalador oficial do Python inclui Tkinter.

```powershell
python -m pip install -r requirements.txt
python app.py
```

Também é possível usar `Iniciar.cmd`. Execute os comandos nesta pasta. O arquivo JSON do trabalho é salvo pelo botão **Salvar JSON**. Não há salvamento automático.

## Usar com qualquer IA

Em **Arquivo → Copiar contexto para IA**, escolha o projeto atual ou instruções para um projeto novo. Cole no assistente de sua preferência e acrescente seu pedido. Depois, use **Arquivo → Importar resposta da IA**, cole a resposta ou abra o arquivo e clique em **Validar e revisar**.

A revisão oferece nova janela ou substituição com cópia recuperável e Ctrl+Z. O documento continua sendo JSON v4. Não há modelo integrado, chave de API, serviço remoto ou MCP. A versão atual do aplicativo é 0.5.0.

## Novidades da fundação

- `pacotes/unifilar/pacote.json` e `pacotes/multifilar/pacote.json` contêm os componentes elétricos e suas regras.
- Abra **Bibliotecas +** e marque as bibliotecas desejadas. Passe o mouse sobre Unifilar ou Multifilar na barra flutuante para abrir seus componentes. As categorias ficam dentro de cada catálogo.
- Componentes de várias bibliotecas podem coexistir na mesma folha. Desmarcar uma biblioteca oculta suas opções de inserção, sem apagar objetos existentes. A escolha é salva no projeto.
- O componente acompanha o cursor pelo terminal de apoio antes do clique. **Shift** encaixa esse terminal na malha lógica de 10 unidades. **R** gira e **E** espelha a prévia mantendo o apoio no cursor.
- O botão **Fundo** altera apenas a aparência da grade. Com Shift, pontos auxiliares próximos ao componente mostram os encaixes disponíveis, inclusive em fundo limpo.
- Documentos antigos nas versões 1, 2 e 3 são importados para a versão 4, ajustando terminais, ligações e formas ancoradas. A importação não sobrescreve o arquivo; só Salvar grava a atualização. Versões antigas do aplicativo não abrem documentos versão 4.

## Documentação

- [Uso e atalhos](docs/USO.md)
- [Arquitetura e limites](docs/ARQUITETURA.md)
- [Criar um pacote com ou sem IA](docs/CRIAR_PACOTE.md)
- [Formato do projeto JSON](docs/FORMATO_JSON.md)
- [Forks, manutenção e instruções para IA](docs/CONTRIBUIR.md)
- [Histórico de mudanças](CHANGELOG.md)
- [Exemplo funcional de fluxograma](exemplos/fluxograma/pacote.json)
- [Integração por IA](docs/INTEGRACAO_IA.md)
- [Contrato para modelos](docs/CONTRATO_IA.md)
- [Exemplos de JSON para IA](docs/EXEMPLOS_IA.md)

Os pacotes elétricos são bibliotecas gráficas. O editor não dimensiona instalações nem certifica conformidade com normas. Cada componente preserva sua biblioteca e seus terminais. Não há conversão automática de circuitos entre unifilar e multifilar. Projetos antigos preservam suas folhas; novos projetos não começam com abas elétricas.

## Verificação

```powershell
python -B -m unittest -v
python validar_pacote.py exemplos/fluxograma/pacote.json
```

Os testes cobrem migração, referências de terminais, inserção, snap, interface, texto, seleção, conexões e exportação. O exemplo não elétrico é carregado nos testes sem mudar o editor.

A barra de bibliotecas é vertical e arrastável pelo título. Shift também encaixa formas e linhas na malha durante criação e ajuste.

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
