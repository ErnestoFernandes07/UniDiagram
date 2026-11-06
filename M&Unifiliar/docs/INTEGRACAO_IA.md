# Integração universal com IA

Esta integração usa a área de transferência, Markdown e o JSON nativo v4. O aplicativo não chama modelos, não exige chaves, não usa serviços remotos e não implementa MCP.

## Fluxo

1. Habilite as bibliotecas que deseja oferecer à IA.
2. Em Arquivo → Copiar contexto para IA, escolha Projeto atual ou Projeto novo. A segunda opção omite o desenho atual e leva somente as bibliotecas habilitadas e um documento vazio.
3. Cole o texto no assistente de sua preferência, acrescente seu pedido e, se necessário, uma fotografia.
4. Use Arquivo → Importar resposta da IA. Cole a resposta ou escolha um JSON local.
5. Clique em Validar e revisar. Leia o resumo e os avisos antes de aplicar.
6. Abra em nova janela para manter o trabalho atual aberto, ou escolha Substituir atual. Cancelar não modifica o projeto.

Copiar o contexto do projeto atual inclui seus textos e objetos. O aplicativo apenas copia; você escolhe onde colar. Não são incluídos caminhos dos arquivos locais nem bibliotecas não relevantes.

## Recuperação

Antes da substituição, o estado anterior é salvo como JSON em `.recuperacao` junto ao projeto, ou na pasta do aplicativo se ainda não houver arquivo salvo. Se essa cópia falhar, a substituição é interrompida. Ctrl+Z restaura o estado anterior durante a sessão; Arquivo → Abrir JSON permite abrir a cópia depois. O caminho da cópia é informado na interface.

Abrir em nova janela cria um documento ainda não salvo e mantém o original aberto. Nenhuma opção sobrescreve automaticamente um arquivo. Não há mesclagem automática.

## Referências

- [Contrato para modelos](CONTRATO_IA.md)
- [Exemplos reais](EXEMPLOS_IA.md)
- [JSON v4](FORMATO_JSON.md)
- [Criação de bibliotecas](CRIAR_PACOTE.md)

Validação estrutural não equivale a aprovação técnica ou elétrica. Uma resposta pode ser válida e representar um circuito inadequado; revise o desenho e suas decisões de engenharia.

### Categorias de conexões legadas

A API 1 aceita `conexoes.categorias_ocultas`, uma lista opcional de categorias existentes que não são oferecidas para novas escolhas. O padrão não pode estar oculto. Leitores continuam aceitando objetos antigos dessas categorias. Nos dois pacotes elétricos, Circuito é legado; para novas conexões use L1/L2/L3/N/PE/Retorno conforme o desenho. Novos fios mostram o nome; a opção individual `mostrar_nome:false` continua válida. As duas bibliotecas agora compartilham cores por categoria, cada uma em seu escopo na folha. No unifilar, um traço pode representar um conjunto de condutores: um rótulo L1 não descreve sozinho sua composição completa. O editor não verifica a adequação elétrica das ligações.

Manutenção de desempenho: leia a seção Canvas retido em docs/ARQUITETURA.md (ARQUITETURA.md a partir de docs). Preserve o agrupamento de movimentos e a reutilização de primitivas. Não serialize caches nem altere os vínculos elétricos para melhorar pan. Use medir_desempenho.py e os testes gráficos para verificar mudanças de interação.
