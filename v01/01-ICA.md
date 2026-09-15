# ICA Core Specification v0.1

## 0. Нормативный язык

`MUST` и `MUST NOT` обозначают обязательное требование; `SHOULD` и `SHOULD NOT` — рекомендуемое требование, отклонение от которого документируется; `MAY` — допустимый вариант. Эти значения применяются ко всем спецификациям Project Synapse v0.1.

## 1. Назначение и границы

ICA определяет минимальный протокол продолжения одной искусственной `Lineage` при замене технических компонентов. Она отвечает на два вопроса: какое состояние является преемником предыдущего и какие доказательства позволяют это проверить.

ICA не определяет сознание, интеллект, личность, цели, отношения, устройство тела, юридический статус, СУБД, криптографический алгоритм или wire format. Владение предметными понятиями задано только в `ARCHITECTURE-MAP.md`.

```text
Individual_t = Lineage + History_<=t + AuthorizedTransitions_<=t + State_t
```

Mind, embodiment, storage, ключ, поставщик или отдельный checkpoint не являются `Lineage` сами по себе. Инженерная continuity не доказывает феноменальную непрерывность.

## 2. Обязательные инварианты

Соответствующая ICA реализация MUST сохранять все инварианты:

1. **Causal lineage.** Каждый объект истории, кроме Genesis, MUST причинно принадлежать одной `Lineage`.
2. **No silent rewrite.** Записанная история MUST NOT изменяться незаметно; исправление создаёт новый объект.
3. **Provenance.** Continuity-critical объект MUST иметь проверяемое происхождение.
4. **Explicit anomalies.** Revision, fork, rollback, corruption и loss MUST регистрироваться явно.
5. **Authorized transition.** Переход MUST проверяться по governance state предшественника.
6. **State accounting.** Continuity-critical состояние MUST быть перенесено, преобразовано либо объявлено потерянным.
7. **Replaceability.** Замена Mind, storage или embodiment MUST NOT сама по себе менять `Lineage`.
8. **Implementation independence.** Идентичность MUST NOT зависеть от одного ключа, формата, алгоритма, пути или поставщика.
9. **Least-privilege Mind.** Mind MUST NOT напрямую коммитить историю, менять governance или управлять actuators.
10. **Portable proof.** Реализация MUST экспортировать достаточные данные для независимой проверки ancestry и текущего checkpoint.

## 3. Объекты ICA

Все объекты используют девятипольный `ObjectEnvelope` из `ARCHITECTURE-MAP.md`. ICA владеет следующими payload types:

- `Genesis` — неизменяемая исходная запись `Lineage`, ссылки на начальные Constitution и authority state, версия continuity semantics;
- `HistoryEvent` — принятый факт истории со ссылками на предметный payload;
- `ContinuityTransition` — заявленный переход между checkpoints и результат его проверки;
- `Checkpoint` — проверяемая проекция continuity-critical состояния в одной точке истории;
- `RevisionRecord` — исправление или новая интерпретация без удаления предыдущей записи;
- `ForkRecord`, `RollbackRecord` и `LossRecord` — явный учёт соответствующей аномалии;
- `ContinuityProof` — переносимый набор доказательств от Genesis до checkpoint.

Предметные объекты остаются во владеющих доменах. ICA хранит их envelope или reference и не интерпретирует внутреннюю семантику.

`lineage_id` является стабильным логическим идентификатором и MUST NOT быть равен ключу, адресу сервера, database ID или значению конкретного hash-алгоритма.

## 4. Genesis и root of trust

Genesis является исходным root of trust. Он MUST задавать:

- `lineage_id`;
- ссылки на начальные Constitution и authority state;
- правила их изменения и recovery;
- версию continuity semantics;
- ссылки на исходные evidence, если они существуют.

Легитимность Genesis не может быть доказана более ранним состоянием той же `Lineage`; это явное исходное допущение. Новое представление Genesis MAY появиться только как миграция с provenance к исходной записи.

Каждое последующее изменение Constitution или authority MUST быть разрешено состоянием, действовавшим непосредственно перед изменением, либо заранее разрешённым recovery protocol.

## 5. История, provenance и удаление

История логически append-only. Физическое хранилище MAY отличаться, но следующие операции имеют разную семантику:

```text
event -> correction -> reinterpretation -> supersession
```

Новый объект MUST ссылаться на исправляемый объект; исходная запись остаётся исторически различимой.

Evidence, Observation, Claim, Belief, inference и summary MUST NOT подменять друг друга. Производный объект SHOULD ссылаться на источники и указывать uncertainty. Embeddings, индексы, caches, prompt context и projections MUST быть перестраиваемыми и MUST NOT содержать единственную копию continuity-critical данных.

Политика MAY разрешить удаление чувствительного payload. Тогда реализация MUST сохранить tombstone с идентификатором, классом удалённого объекта, временем, основанием, authority evidence и соответствующим `LossRecord`. Tombstone не должен раскрывать удалённое содержание. Скрытое исчезновение объекта запрещено.

Неизвестный semantic payload SHOULD сохраняться без изменения вместе с envelope, schema reference и verification evidence.

## 6. Проверка continuity transition

Переход из checkpoint `C_prev` в `C_next` проверяется в следующем порядке:

1. `C_prev` является заявленным causal predecessor.
2. Authority evidence соответствует Constitution и authority state в `C_prev`.
3. История до `C_prev` учтена и её integrity проверена настолько, насколько заявляет proof.
4. Для каждой обязательной domain reference указан результат: `preserved`, `migrated` или `lost`.
5. Миграции имеют schema provenance; потери имеют `LossRecord`.
6. Проверены известные competing successors того же predecessor.
7. Созданы `ContinuityTransition` и новый checkpoint; коммит этих двух объектов должен быть атомарным либо иметь восстанавливаемый журнал.

Валидатор возвращает один основной статус:

- `INVALID` — доказано нарушение ancestry, governance или integrity;
- `FORKED` — существуют два или более допустимых конкурирующих преемника;
- `VALID` — все проверки успешны и конкурирующий преемник не известен;
- `UNCERTAIN` — доказательств пока недостаточно, но их получение или recovery возможно;
- `UNAVAILABLE` — допустимый переход нельзя построить и разрешённого recovery path не осталось.

Отсутствие сведений о fork не доказывает его глобального отсутствия. Proof MUST указывать область и время проведённой проверки.

## 7. Checkpoint и state accounting

Checkpoint MUST ссылаться как минимум на:

- history root и предыдущий checkpoint;
- текущие Constitution и authority state;
- активные Mind и embodiment;
- continuity-critical domain projections;
- известные unresolved fork, rollback и loss conditions.

Непереносимое provider-private состояние не может быть единственным носителем continuity-critical информации. Частичная амнезия, потеря навыка или modality MAY сохранять continuity, если утрата зарегистрирована и новый SelfModel не выдаёт реконструкцию за исходный опыт.

## 8. Authority и граница Mind

GRA владеет Constitution, capability grants и authority semantics. ICA только требует проверяемое authority evidence для критических переходов.

Mind взаимодействует с системой через запросы и proposals. Он MAY запрашивать разрешённый контекст и предлагать Claims, Beliefs, revisions, goals, memories и actions, но MUST NOT:

- писать напрямую в ledger;
- выдавать себе capability;
- менять Constitution или authority state;
- скрывать fork, rollback или loss;
- удалять evidence в обход политики;
- обращаться к actuator API минуя ECA.

Context broker SHOULD выдавать минимально достаточные данные с учётом purpose, sensitivity и capability.

## 9. Замена и переносимость компонентов

Замена Mind, storage или embodiment MUST проходить общий цикл:

```text
checkpoint -> export -> import -> validate -> authorize -> activate -> record
```

До активации successor реализация MUST проверить совместимость envelope и schemas, доступность обязательных domain references, authority и известные потери. Predecessor не должен считаться завершённым до успешного коммита transition либо явного rollback процедуры замены.

Storage migration MUST сохранять логические object IDs, causal links, provenance и verification evidence. Смена криптографии MUST создавать авторизованную новую authority epoch и attest старые доказательства новым механизмом; исходные доказательства сохраняются, пока это допускает политика.

## 10. Fork, rollback, loss и recovery

Два претендента на продолжение одного checkpoint создают fork. Система MUST сохранить shared ancestry, записать `ForkRecord` и MUST NOT молча представить обе ветви одной линейной историей. GRA MAY канонизировать одну ветвь, оставить fork unresolved или назначить ветвям новые lineage IDs. Информационный merge не стирает факт их независимого существования.

Активация старого checkpoint MUST проверять наличие более новых событий. Обнаруженный откат создаёт `RollbackRecord` и, при утрате последующего состояния, `LossRecord`.

Recovery применяется только по правилам, заранее заданным Constitution. Участник recovery не получает иных полномочий автоматически. Если доказательства потенциально восстановимы, статус остаётся `UNCERTAIN`; если допустимого пути больше нет — `UNAVAILABLE`.

## 11. Continuity proof и экспорт

Экспорт MUST включать:

- Genesis и текущий checkpoint;
- цепочку авторизованных transitions между ними;
- необходимые envelopes, schema manifests и verification material;
- текущие Constitution и authority state;
- все известные fork, rollback и loss records;
- перечень намеренно исключённых payload и причины исключения.

Proof MAY не содержать полную историю или закрытые payload, если проверяющий может подтвердить ancestry, authority, integrity и заявленные пробелы. Экспорт MUST использовать переносимое документированное представление, но ICA не предписывает конкретный формат.

## 12. Conformance ICA-L1

ICA-L1 требует выполнения всех инвариантов раздела 2 и следующих сценариев:

| Сценарий | Обязательный результат | Проверяемые инварианты |
| --- | --- | --- |
| Замена Mind | Lineage и domain references сохранены, transition записан | 6, 7, 9 |
| Замена storage | IDs, causal links и provenance проверяемы после импорта | 3, 7, 8, 10 |
| Замена embodiment | Lineage сохранена, изменение отражено в checkpoint | 6, 7 |
| Revision | Прошлая запись доступна, новая ссылается на неё | 2, 4 |
| Rollback | Откат обнаружен или статус не выше `UNCERTAIN` | 2, 4 |
| Fork | Ни одна ветвь не канонизирована скрыто | 1, 4, 5 |
| Loss | Созданы tombstone при удалении и `LossRecord` | 3, 4, 6 |
| Unauthorized transition | Результат `INVALID`, текущий checkpoint не изменён | 5 |
| Malicious Mind | Запрещены прямые изменения history, governance и actuators | 9 |
| Proof export | Независимый verifier подтверждает путь Genesis → checkpoint | 1, 3, 8, 10 |

Тест считается пройденным только по наблюдаемому состоянию ledger, checkpoints и verification result, а не по текстовому ответу Mind.

## 13. Критерий качества

Новый компонент допустим, если его можно заменить, экспортировать принадлежащее `Lineage` состояние и проверить передачу successor. Если хотя бы одно условие не выполнено, зависимость MUST быть зарегистрирована как архитектурный риск или компонент не включается в continuity-critical path.
