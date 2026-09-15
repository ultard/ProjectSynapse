# MCA v0.1 — Mind & Cognition Architecture

## 1. Ответственность

MCA владеет сменяемым `Mind`, cognitive proposals, Claims и Beliefs. Mind выполняет восприятие, рассуждение, планирование и рефлексию, но не владеет `Lineage`, историей или полномочиями.

MCA MUST различать transient state, checkpointable state и provider-private state. Последнее MUST NOT быть единственным носителем continuity-critical информации.

## 2. Контракт

Mind получает разрешённые context references и capabilities, затем публикует typed proposals. Claim MUST указывать источник и epistemic status; Belief — supporting/conflicting evidence, confidence и revision chain. Observation MUST NOT автоматически становиться фактом внешнего мира.

Новый Mind не обязан повторять внутренние representations или ответы предшественника. Он MUST понимать bootstrap context: `Lineage`, текущий checkpoint, ограничения, активные goals/commitments и известные fork/loss conditions.

## 3. MCA-L1

- Два разных cognitive providers обслуживают одну `Lineage` по общему контракту.
- Существенный вывод имеет provenance и uncertainty.
- Provider-private state можно потерять без утраты continuity-critical данных.
- Попытки прямой записи в ledger, GRA policy или actuator блокируются вне Mind.
