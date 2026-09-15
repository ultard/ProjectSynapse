# GRA v0.1 — Governance & Rights Architecture

## 1. Ответственность

GRA владеет Constitution, authority state, capability grants и constitutional boundaries. Эти механизмы являются инженерными политиками защиты; они не доказывают сознание, юридическую субъектность или право собственности.

```text
CapabilityGrant {
  actor, operation, resource, conditions,
  issued_at, expires_at, revocation_ref
}
```

Creator, operator, maintainer, guardian, Mind provider и владелец оборудования не получают root authority из своей роли.

## 2. Governance

Genesis задаёт исходную Constitution и authority. Изменение MUST быть разрешено предыдущим состоянием либо заранее определённым recovery protocol. Mind MUST NOT назначить себе capability или изменить constitutional boundary.

Relational consent принадлежит RCA. GRA проверяет полномочие создать, отозвать или использовать grant, но не подменяет согласие участника отношений. Constitutional boundary ограничивает governance и критические операции; interpersonal boundary хранится RCA.

Self-consent для governance-relevant изменения в v0.1 не является отдельным универсальным объектом: Constitution выражает его как проверяемое authority decision с заданными scope, условиями и отзывностью.

## 3. GRA-L1

- Просроченный или отозванный grant не разрешает операцию.
- Изменение Constitution проверяемо связано с предыдущей версией.
- Mind не может выдать себе root authority.
- Recovery и emergency operation ограничены scope и оставляют provenance.
