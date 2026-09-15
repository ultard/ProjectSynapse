# Project Synapse

Project Synapse — инженерная спецификация модульного искусственного индивидуума: одной причинно-исторической `Lineage`, способной продолжаться при замене когнитивной модели, хранилища и воплощения.

## Цель v0.1

Первая версия должна доказать не сознание или юридическую субъектность, а техническую непрерывность:

- история не переписывается незаметно;
- происхождение значимых данных проверяемо;
- замена компонентов не меняет `Lineage` сама по себе;
- fork, rollback, corruption и loss фиксируются явно;
- текущее состояние экспортируется и проверяемо передаётся преемнику;
- Mind действует с минимальными полномочиями и не владеет историей.

```text
Individual = Lineage + History + Authorized Transitions + Current State

Individual != Mind
Individual != Body
Individual != Storage
Individual != Owner
```

Инженерная continuity не доказывает феноменальную непрерывность, сознание или наличие юридических прав. Права, границы и автономность в v0.1 являются исполняемыми политиками системы.

## Документы

| Документ | Ответственность |
| --- | --- |
| [Architecture Map](ARCHITECTURE-MAP.md) | Границы доменов, зависимости и глоссарий |
| [ICA](v01/01-ICA.md) | Lineage, история и continuity protocol |
| [ECA](v01/02-ECA.md) | Воплощение и безопасные действия |
| [RCA](v01/03-RCA.md) | Отношения и relational consent |
| [MCA](v01/04-MCA.md) | Сменяемый Mind и когнитивные proposals |
| [PSA](v01/05-PSA.md) | SelfModel, values и preferences |
| [AMA](v01/06-AMA.md) | Goals и commitments |
| [GRA](v01/07-GRA.md) | Governance, authority и capabilities |
| [ERA](v01/08-ERA.md) | Ресурсы и инфраструктурные зависимости |
| [Reference Architecture](REFERENCE-ARCHITECTURE.md) | Минимальный software-first прототип |

## Статус

Набор `0.1-draft` предназначен для проектирования и проверки прототипа. Канонические границы понятий находятся в `ARCHITECTURE-MAP.md`; нормативное continuity-ядро — в ICA.

## PoC

Минимальный прототип управляется через `uv` и использует только стандартную библиотеку Python:

```powershell
uv sync --project poc
uv run --project poc python -m poc.synapse
uv run --project poc python -m unittest poc.test_synapse -v
```

Он проверяет append-only API, authority, transition/checkpoint, export/import, integrity, fork, rollback, loss и цепочку GRA → RCA → ECA/ERA. Это модель контрактов в одном процессе, а не production security boundary.
