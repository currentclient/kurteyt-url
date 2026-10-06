# CLAUDE.md

Guidance for Claude Code in this repository.

## Architecture model

`cc-architecture` holds the C4 model of the platform (LikeC4, one file per domain under `src/domains/`). Blaster's model sweep is its one writer for shipped changes. If a change adds, removes, or renames a deployable (Lambda module, Argo app, CronJob, Vercel project, droplet service), a queue or topic, an external provider, or a call to another CurrentClient service, say so in your PR body as `Architecture: <what moved>` and leave the model alone; the sweep reads that line with the merged diff and opens the model PR once the change ships.
