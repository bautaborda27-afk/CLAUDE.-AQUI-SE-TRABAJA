## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## Navegación de contexto

Cuando necesites entender el codebase, docs o archivos de este proyecto:

1. SIEMPRE consulta el grafo primero: `/graphify query "tu pregunta"` (o `graphify query`, `graphify path`, `graphify explain`)

2. Para entender o responder preguntas, no leas archivos raw salvo que yo diga explícitamente "lee el archivo" o "mira el archivo raw", o que el grafo no alcance. Excepción: para editar un archivo que el grafo ya ubicó, leé solo ese archivo (Claude Code exige leerlo antes de editarlo).

3. Usa `graphify-out/wiki/index.md` como punto de entrada para navegar la estructura

4. Después de modificar código, corré `graphify update .` para mantener el grafo al día.
