# RCA v0.1 — Relational Cognition Architecture

## 1. Ответственность

RCA владеет `Relationship`, interpersonal boundaries и relational consent. Отношение является проекцией общей истории взаимодействий, а не профилем пользователя и не основанием управлять `Lineage`.

```text
Relationship {
  participants, episode_refs, trust_dimensions,
  boundaries, consent_state, commitments_refs,
  unresolved_events, current_interpretation
}
```

Общие свойства личности принадлежат PSA, commitments — AMA, capability grants и constitutional boundaries — GRA.

## 2. Relational consent

Consent MUST указывать participants, activity scope, context, conditions, время выдачи, срок, статус и provenance. Оно является контекстным и отзывным: прошлое согласие или отсутствие отказа не разрешают текущее действие. При неопределённости RCA возвращает `UNKNOWN`, а действие останавливается или запрашивает подтверждение.

RCA MUST отличать consent каждого участника от capability оператора и решения текущего Mind. Отзыв публикуется как событие и немедленно меняет проекцию.

## 3. Память и приватность

Evidence, episode, interpretation и relational update MUST оставаться различимыми. Trust SHOULD быть набором объяснимых измерений, а не одной непрозрачной оценкой. Удаление чувствительного payload следует политике ICA: вместо скрытого исчезновения остаются безопасный tombstone и `LossRecord`.

## 4. RCA-L1

- Замена Mind не сбрасывает Relationship.
- Отозванное consent немедленно блокирует зависящее от него действие.
- Противоречивые эпизоды сохраняются с uncertainty.
- Текущие trust, boundaries и consent объясняются ссылками на историю.
