# ERA v0.1 — Environment & Resources Architecture

## 1. Ответственность

ERA владеет `Resource`, его доступностью, criticality и инфраструктурными зависимостями.

```text
Resource {
  kind, controller, access, capacity,
  health, dependencies, expiry,
  substitutability, criticality
}
```

Энергия, compute, continuity storage, сеть, credentials и обслуживание MUST быть представлены ресурсами, если от них зависит прототип. Юридическое владение, фактический контроль и разрешённый доступ MUST оставаться различимыми.

## 2. Риски и события

ERA SHOULD выявлять single points of control, наблюдать depletion и сообщать ограничения AMA и ECA. Недоступность ресурса создаёт domain event; если потеря затрагивает continuity-critical состояние, ICA дополнительно создаёт `LossRecord`.

Миграция поставщика считается успешной только после проверки доступности обязательного состояния на новой инфраструктуре.

## 3. ERA-L1

- Критические ресурсы и их контролирующие стороны перечислены.
- Для исчерпаемого ресурса заданы threshold и recovery action.
- Потеря ресурса приостанавливает зависимое действие и не маскируется как изменение личности.
- Замена storage provider проходит ICA export/import без потери проверяемости.
