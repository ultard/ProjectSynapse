# Project Synapse — Architecture Map v0.1

Этот документ является единственным источником владения понятиями. Доменные спецификации используют нормативные слова `MUST`, `SHOULD` и `MAY` в значениях, заданных ICA.

## 1. Домены

| Домен | Владеет | Не владеет |
| --- | --- | --- |
| ICA | `Lineage`, Genesis, история, transitions, checkpoints, fork, rollback, loss и recovery | Психология, цели, отношения, тело и ресурсы |
| MCA | Cognitive proposals, Claims, Beliefs и состояние Mind | История и право коммита |
| PSA | SelfModel, values, preferences и устойчивые свойства личности | Governance и общие отношения |
| AMA | Goals, commitments, их состояние и приоритет | Authority и физическая исполнимость |
| ECA | Embodiment, BodySchema, ActionProposal и физическая безопасность | Полномочия и согласие участников |
| RCA | Relationships, interpersonal boundaries и relational consent | Конституционные полномочия |
| GRA | Constitution, authority, capability grants и constitutional boundaries | Relational consent и предметное состояние доменов |
| ERA | Resources, их доступность, criticality и зависимости | Выбор целей и управление телом |

Домен публикует типизированные события и применяет только собственное состояние. Междоменные ссылки используют `ObjectEnvelope.payload_ref` или идентификатор объекта, но не копируют чужую семантику.

## 2. Общий поток

```text
domain observation or proposal
  -> provenance
  -> GRA capability check
  -> owning domain validation
  -> ICA history commit
  -> domain projections and checkpoint
```

Mind не пишет напрямую в ledger, governance или actuators. Для физического действия ECA независимо проверяет:

1. capability через GRA;
2. необходимое relational consent через RCA;
3. актуальное состояние тела и safety constraints внутри ECA.

Отказ любой обязательной проверки запрещает исполнение, но сам отказ MAY стать событием истории.

## 3. Минимальный общий контракт

```text
ObjectEnvelope {
  object_id
  lineage_id
  semantic_type
  schema_version
  causal_parents
  recorded_at
  payload_ref
  provenance_ref
  verification { integrity, authority }
}
```

Envelope не задаёт wire format или иерархию классов. Предметные поля, occurrence time, uncertainty и privacy metadata принадлежат payload владеющего домена. Неизвестный payload сохраняется вместе с envelope без попытки угадать его смысл.

## 4. Зависимости

- Все домены используют ICA identity, history и provenance.
- MCA получает разрешённый контекст и публикует proposals.
- PSA предоставляет текущую self-projection для MCA и AMA.
- AMA формирует intent; ECA и ERA определяют его исполнимость.
- RCA предоставляет состояние отношений и действующее relational consent.
- GRA разрешает операции, но не принимает предметные решения вместо доменов.
- ERA сообщает ограничения ресурсов AMA и ECA.

Циклические зависимости реализуются через события и запросы, а не взаимную запись.

## 5. Короткий глоссарий

| Термин | Значение |
| --- | --- |
| `Lineage` | Одна причинно-историческая линия существования |
| `continuity` | Проверяемая допустимость перехода между состояниями Lineage |
| `Mind` | Заменяемый когнитивный исполнитель |
| `provenance` | Проверяемое происхождение объекта или вывода |
| `transition` | Заявленный переход от одного checkpoint к следующему |
| `fork` | Несколько несовместимых преемников одного состояния |
| `loss` | Учтённая утрата данных, возможности или доказательства |
| `capability` | Ограниченное полномочие actor выполнить operation над resource |
| `relational consent` | Контекстное и отзывное согласие участника взаимодействия |

Английские термины из таблицы являются каноническими; остальной текст пишется преимущественно по-русски.
