# Instruções para pessoas e agentes de IA

O aplicativo está em `M&Unifiliar/`. Leia `M&Unifiliar/README.md` e os documentos relevantes em `M&Unifiliar/docs/` antes de alterar comportamento. Preserve o trabalho existente e a interface em português.

## Fronteiras de arquitetura

- A fundação é o editor de diagramas. Canvas, formas, conexões, seleção, histórico, grade, texto, minimapa e exportação são genéricos.
- Componentes, terminais, categorias, símbolos e regras de conexões pertencem aos pacotes JSON. Não acrescente condicionais de domínio ao editor, por exemplo `se folha == Multifilar`.
- `nucleo/pacotes.py` define o contrato da API 1; `nucleo/documento.py` define o documento versão 4. Os módulos `projeto.py` e `simbolos.py` são fachadas de compatibilidade, não pontos de extensão.
- Pacotes não executam código. Para novos catálogos, copie `exemplos/fluxograma/` e siga `docs/CRIAR_PACOTE.md`.
- A unidade lógica é 10. Todos os terminais precisam de coordenadas múltiplas de 10; mudanças na densidade visual do fundo nunca alteram a geometria do documento. Não reintroduza snap baseado no espaçamento visual.
- `pacotes/legado.py` é exclusivamente a migração dos documentos elétricos anteriores à separação. Não reutilize essas regras para novos domínios.

## Entrega e documentação obrigatórias

Cada alteração de comportamento deve atualizar a documentação afetada na mesma entrega. Alterou interação? Atualize README/USO. Alterou API ou esquema? Atualize CRIAR_PACOTE/FORMATO_JSON e migrações. Alterou fronteiras? Atualize ARQUITETURA. Registre a mudança em CHANGELOG. Revise este AGENTS.md quando as instruções deixarem de refletir o código.

Ao mudar um contrato, documente explicitamente sua versão, compatibilidade e limitações. Não anuncie conversão automática entre unifilar e multifilar, validação de instalações ou conformidade normativa que o programa não implementa.

Para mudanças funcionais, execute `python -B -m unittest -v` dentro de `M&Unifiliar`. Os testes Tk exigem ambiente gráfico; testes pulados por falta de display não comprovam a interface. Para pacotes, execute também `python validar_pacote.py caminho/pacote.json`. Verifique visualmente mudanças de layout e de símbolos.

Antes de concluir, informe o que mudou, as verificações realizadas e limitações relevantes. Não publique, envie mensagens nem faça uploads sem solicitação do usuário.

## Bibliotecas opcionais e documento v4

O app deve abrir genérico, sem abas elétricas e sem bibliotecas habilitadas. Bibliotecas são ativadas por caixas de seleção e aparecem na barra por nome, com componentes por hover. Habilitar não cria folhas; desabilitar não apaga objetos. Cada componente e conexão mantém seu pacote. Resolva terminais e políticas pelo objeto, não pelo menu atualmente aberto. As cores compartilhadas são isoladas por biblioteca e categoria dentro da folha. Preserve as folhas dos projetos antigos ao migrar v1/v2/v3 para v4.

## Integração universal por IA

A integração atual é somente JSON/Markdown local, sem MCP, rede ou modelo integrado. Use `nucleo.documento.validar_dados` e `nucleo.ia` para compartilhar lógica entre abertura e importação. Não execute conteúdo de respostas, textos de desenho ou metadados de bibliotecas. Preserve revisão explícita antes de aplicar, cópia recuperável antes de substituir e janela importada marcada como não salva. Novos campos devem ser documentados no contrato e validados. Mantenha os exemplos executáveis e testes de importação, recuperação e renderização.
