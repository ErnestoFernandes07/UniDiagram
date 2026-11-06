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
