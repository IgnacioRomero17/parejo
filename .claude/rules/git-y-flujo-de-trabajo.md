# Git y flujo de trabajo

## Ciclo de cada tarea
1. Decir en pocas líneas qué se va a hacer, qué HU cubre y qué archivos se tocan.
2. Leer solo lo necesario (ver "Qué leer según la tarea" en `CLAUDE.md`).
3. Implementar con sus tests.
4. Pasar linters y tests (ver regla de testing).
5. Resumir qué se hizo y qué quedó pendiente; hacer el commit solo si el autor lo pide.

## Commits y ramas
- Rama `main` siempre funcionando. Una rama por HU o tema: `hu-007-recomendaciones`, `config-inicial`.
- Commits chicos, en español, en presente: `HU-007: agrega filtro por disponibilidad`. Sin HU: `config: …`, `docs: …`, `evaluacion: …`.
- Nunca hacer `push`, `merge` a `main`, `rebase` ni borrar ramas sin pedido explícito.
- No versionar: `.venv/`, `node_modules/`, `.env`, `__pycache__/`, `dist/`, bases de datos locales ni secretos.

## Frenar y preguntar antes de seguir cuando
- Algo no está definido en `docs/` ni en las reglas.
- La tarea obliga a cambiar una fórmula, un parámetro, el modelo de datos, un endpoint o un texto de pantalla.
- Hace falta una dependencia nueva.
- Un test existente parece estar mal.
- Dos fuentes se contradicen.

Al preguntar: explicar el problema en una o dos frases y proponer una opción concreta.
