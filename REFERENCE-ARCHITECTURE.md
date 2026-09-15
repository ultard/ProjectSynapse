# Project Synapse — Reference Architecture v0.1

Статус: software-first реализационный эскиз без привязки к поставщику.

## 1. Цель прототипа

Прототип должен доказать continuity при замене Mind и storage, а также корректно обработать fork, rollback и loss. Физический робот не требуется: ECA проверяется через симулированное воплощение.

## 2. Минимальные компоненты

```text
Cognitive Provider
  -> Cognitive Adapter
  -> Context and Capability Broker
       -> Domain Services and Projections
       -> Action Service -> Simulated ECA Safety Controller
  -> Continuity Kernel
       -> Event Ledger
       -> Evidence/Object Store
       -> GRA Policy Store
       -> Checkpoint and Export
```

- Cognitive Adapter преобразует ответы модели в типизированные proposals.
- Broker выдаёт минимально необходимый контекст и проверяет capability.
- Domain services валидируют и применяют только собственную семантику.
- Continuity Kernel валидирует causal parents, authority evidence и continuity status перед коммитом.
- Ledger хранит логически append-only историю; object store — payload и evidence.
- Projections, summaries, embeddings и индексы перестраиваются из исходных объектов.

Mind не имеет прямого write-доступа к ledger, policy store или actuator API.

## 3. Вертикальный сценарий

1. Создать Genesis и первый checkpoint.
2. Записать эпизоды, Claims, SelfModel, Relationship и Commitment через доменные services.
3. Заменить cognitive provider и передать ему разрешённый bootstrap context.
4. Исполнить безопасное действие в симуляции после проверок GRA, RCA и ECA.
5. Экспортировать envelope, payload, schemas, checkpoints и verification evidence.
6. Импортировать данные в другую storage implementation и проверить continuity proof.
7. Запустить adversarial scenarios: rollback, competing successor, удалённый payload и попытка Mind обойти полномочия.

## 4. Критерий успеха

Прототип соответствует v0.1, если все сценарии ICA-L1 и доменные L1-тесты проходят после полной замены cognitive provider и storage. Качество диалога, физическая моторика, юридическая субъектность и доказательство сознания не входят в критерий.

Сложные схемы репликации, multi-party approval и физическое тело добавляются только при появлении соответствующей модели угроз или задачи прототипа.
