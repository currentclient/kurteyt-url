# CLAUDE.md

Guidance for Claude Code in this repository.

## Architecture model

`cc-architecture` holds the C4 model of the platform (LikeC4, one file per domain under `src/domains/`). If a change adds, removes, or renames a deployable (Lambda module, Argo app, CronJob, Vercel project, droplet service), a queue or topic, an external provider, or a call to another CurrentClient service, update the matching `src/domains/<domain>.c4` in `cc-architecture` in a companion PR and link it from the change. Its `CLAUDE.md` has the conventions.
