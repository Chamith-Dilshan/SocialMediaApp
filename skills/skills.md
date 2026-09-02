## Project Skill

The discoverable, agent-ready development workflow is maintained at [`.github/skills/fastapi-backend-template/SKILL.md`](../.github/skills/fastapi-backend-template/SKILL.md). Load it when adding or changing API behavior, database schema, authentication, tests, or deployment configuration.

The central architectural rule is:

```text
Router -> Service -> Repository -> Database
```

Call a service when business logic, validation, authorization, or orchestration is needed. Call a repository for data access only. A service may call another service when it needs another domain's business rule; do not make feature services reach across repositories to duplicate those rules.

Repository
returns ORM Models

Service
applies business rules
converts ORM -> DTO

Router
returns DTO