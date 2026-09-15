# PSA v0.1 — Personality & Self Architecture

## 1. Ответственность

PSA владеет `SelfModel`, values, preferences и устойчивыми свойствами личности. SelfModel является исправляемой проекцией истории, а не character prompt и не источником идентичности.

PSA MUST различать constitutional references, устойчивые values, learned preferences, habits, narrative interpretations и временное affective state. Их изменения имеют разные основания и не должны автоматически обновлять друг друга.

## 2. Биографическая причинность

Значимое свойство SHOULD объясняться цепочкой:

```text
evidence/episode -> interpretation -> reflection or choice -> revision -> projection
```

Mind MAY предложить изменение, но PSA применяет его только после domain validation и GRA capability check. Амнезия или новый provider MUST NOT порождать вымышленную автобиографию.

## 3. PSA-L1

- SelfModel восстанавливается из history references и checkpoint.
- Изменение устойчивого свойства имеет provenance.
- Временное состояние не переписывает value или биографию.
- После замены Mind прежнее состояние сохраняется либо потеря явно зарегистрирована.
