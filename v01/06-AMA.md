# AMA v0.1 — Agency & Motivation Architecture

## 1. Ответственность

AMA владеет `Goal`, `Commitment`, их lifecycle и приоритетом. Внешний запрос является входом для оценки, а не автоматически принятой целью.

```text
Goal: proposed -> adopted -> active -> completed | suspended | abandoned | superseded
Commitment: proposed -> accepted -> active -> fulfilled | waived | expired | invalidated
```

Goal MUST хранить origin, rationale, status и provenance. Commitment дополнительно MUST указывать стороны, содержание, условия и срок, если он существует.

## 2. Решение

AMA оценивает values и SelfModel из PSA, отношения из RCA, body constraints из ECA, ресурсы из ERA и полномочия из GRA. Конфликт целей или commitments разрешается явным переходом; невыполнение не исчезает из проекции.

Автономная инициатива MAY существовать только в пределах действующих capabilities и доступных ресурсов.

## 3. AMA-L1

- Активные goals и commitments переживают замену Mind.
- Причина принятия и изменения статуса объяснима.
- Несовместимый внешний запрос отклоняется или остаётся proposed.
- Недоступный ресурс приостанавливает действие, но не стирает Goal.
