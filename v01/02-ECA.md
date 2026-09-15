# ECA v0.1 — Embodied Cognition Architecture

## 1. Ответственность

ECA владеет текущим `Embodiment`, `BodySchema`, `ActionProposal` и физической безопасностью. Тело участвует в SelfModel, но не определяет `Lineage`.

`BodySchema` MUST описывать capabilities, sensors, effectors, geometry, ограничения, health, uncertainty и актуальность измерений. Навык SHOULD разделяться на переносимую процедуру AMA и body-specific binding ECA.

## 2. ActionProposal

```text
ActionProposal {
  intent_ref, capability, target, parameters,
  expected_effect, risk, reversibility,
  required_consent, valid_until
}
```

До исполнения ECA MUST получить действующую capability от GRA, необходимое relational consent от RCA и проверить актуальное body state, collision/injury risk и safety envelope. Отказ любой проверки запрещает действие.

Mind MUST NOT управлять actuators напрямую. Safety controller действует независимо от Mind и MUST поддерживать остановку и обратную связь о результате.

## 3. Смена воплощения

Новое тело получает новый embodiment ID. ECA публикует transition event; ICA учитывает его в checkpoint, а PSA обновляет SelfModel. Недоступная modality не удаляет прошлый опыт, но её текущая недоступность MUST быть отражена.

## 4. ECA-L1

- Симулированное embodiment предоставляет BodySchema и feedback.
- Просроченная capability, отозванное consent или опасное состояние блокируют действие.
- Попытка Mind обойти safety controller не достигает actuator.
- Замена embodiment сохраняет `Lineage` и историю, инвалидируя только несовместимые bindings.
