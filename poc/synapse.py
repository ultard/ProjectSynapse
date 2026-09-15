from __future__ import annotations

import copy
import hashlib
import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID, FORKED, UNCERTAIN, INVALID, UNAVAILABLE = (
    "VALID",
    "FORKED",
    "UNCERTAIN",
    "INVALID",
    "UNAVAILABLE",
)


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    return hashlib.sha256(_json(value).encode()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ContinuityKernel:
    """Small executable model of ICA; not a production security boundary."""

    def __init__(self, lineage_id: str, root_actor: str = "operator") -> None:
        self._lock = threading.RLock()
        self._records: list[dict[str, Any]] = []
        self._by_id: dict[str, dict[str, Any]] = {}
        self._successors: dict[str, list[str]] = {}
        self._checkpoint_parent: dict[str, str | None] = {}
        self._grants = {
            root_actor: {"act", "commit", "consent", "grant", "loss", "transition"}
        }
        self.lineage_id = lineage_id
        self.status = VALID

        self.genesis_id = self._append(
            "ica.genesis",
            {
                "constitution": "poc-v0.1",
                "initial_authority": {root_actor: sorted(self._grants[root_actor])},
                "continuity_semantics": "ica-v0.1",
            },
            [],
            root_actor,
            "bootstrap",
            "bootstrap",
        )
        self.current_checkpoint = self._append(
            "ica.checkpoint",
            {"previous_checkpoint": None, "state": {"mind": None, "embodiment": None}},
            [self.genesis_id],
            root_actor,
            "commit",
            self.genesis_id,
        )
        self._checkpoint_parent[self.current_checkpoint] = None

    @property
    def records(self) -> tuple[dict[str, Any], ...]:
        return tuple(copy.deepcopy(self._records))

    def allowed(self, actor: str, operation: str) -> bool:
        return operation in self._grants.get(actor, set())

    def grant(self, actor: str, operation: str, to_actor: str) -> str | None:
        if not self.allowed(actor, "grant"):
            return None
        record_id = self._append(
            "gra.capability_grant",
            {"actor": to_actor, "operation": operation},
            [self.current_checkpoint],
            actor,
            "grant",
            self.current_checkpoint,
        )
        self._grants.setdefault(to_actor, set()).add(operation)
        return record_id

    def record_domain_event(
        self, actor: str, semantic_type: str, payload: dict[str, Any]
    ) -> str | None:
        return self.record_authorized_event(actor, "commit", semantic_type, payload)

    def record_authorized_event(
        self,
        actor: str,
        operation: str,
        semantic_type: str,
        payload: dict[str, Any],
    ) -> str | None:
        if not self.allowed(actor, operation):
            return None
        return self._append(
            semantic_type,
            payload,
            [self.current_checkpoint],
            actor,
            operation,
            self.current_checkpoint,
        )

    def transition(
        self,
        actor: str,
        previous_checkpoint: str,
        state: dict[str, Any],
        accounting: dict[str, str],
    ) -> tuple[str, str | None]:
        with self._lock:
            if not self.allowed(actor, "transition"):
                return INVALID, None
            if previous_checkpoint not in self._checkpoint_parent:
                return UNCERTAIN, None
            if not accounting or any(
                result not in ("preserved", "migrated", "lost")
                for result in accounting.values()
            ):
                return INVALID, None
            if "lost" in accounting.values() and not self.allowed(actor, "loss"):
                return INVALID, None

            loss_ids = [
                self._append(
                    "ica.loss",
                    {"subject": subject, "reason": "declared during transition"},
                    [previous_checkpoint],
                    actor,
                    "loss",
                    previous_checkpoint,
                )
                for subject, result in accounting.items()
                if result == "lost"
            ]
            transition_id = self._append(
                "ica.transition",
                {"previous_checkpoint": previous_checkpoint, "accounting": accounting},
                [previous_checkpoint, *loss_ids],
                actor,
                "transition",
                previous_checkpoint,
            )
            checkpoint_id = self._append(
                "ica.checkpoint",
                {"previous_checkpoint": previous_checkpoint, "state": state},
                [transition_id],
                actor,
                "transition",
                transition_id,
            )
            self._checkpoint_parent[checkpoint_id] = previous_checkpoint

            existing = self._successors.setdefault(previous_checkpoint, [])
            existing.append(checkpoint_id)
            if len(existing) > 1:
                self._append(
                    "ica.fork",
                    {"predecessor": previous_checkpoint, "successors": existing},
                    existing,
                    actor,
                    "transition",
                    previous_checkpoint,
                )
                self.status = FORKED
                return FORKED, checkpoint_id

            self.current_checkpoint = checkpoint_id
            self.status = VALID
            return VALID, checkpoint_id

    def rollback(self, actor: str, target_checkpoint: str) -> str:
        if not self.allowed(actor, "transition"):
            return INVALID
        if target_checkpoint == self.current_checkpoint:
            return VALID
        if target_checkpoint not in self._ancestors(self.current_checkpoint):
            return UNCERTAIN if target_checkpoint not in self._by_id else INVALID
        self._append(
            "ica.rollback",
            {"target": target_checkpoint, "activated": False},
            [self.current_checkpoint, target_checkpoint],
            actor,
            "transition",
            self.current_checkpoint,
        )
        return UNCERTAIN

    def export(self) -> str:
        return _json(
            {
                "format": "synapse-poc-v1",
                "lineage_id": self.lineage_id,
                "genesis_id": self.genesis_id,
                "current_checkpoint": self.current_checkpoint,
                "status": self.status,
                "records": self._records,
            }
        )

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
        try:
            with temporary.open("w", encoding="utf-8") as stream:
                stream.write(self.export())
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)

    @classmethod
    def load(cls, path: str | Path) -> "ContinuityKernel":
        return cls.from_export(Path(path).read_text(encoding="utf-8"))

    @classmethod
    def from_export(cls, document: str) -> "ContinuityKernel":
        data = json.loads(document)
        cls.verify_export(document)
        kernel = cls.__new__(cls)
        kernel._lock = threading.RLock()
        kernel._records = copy.deepcopy(data["records"])
        kernel._by_id = {r["envelope"]["object_id"]: r for r in kernel._records}
        kernel._successors = {}
        kernel._checkpoint_parent = {}
        kernel._grants = {}
        kernel.lineage_id = data["lineage_id"]
        kernel.genesis_id = data["genesis_id"]
        kernel.current_checkpoint = data["current_checkpoint"]
        kernel.status = data["status"]
        kernel._rebuild_state()
        return kernel

    @staticmethod
    def verify_export(document: str) -> bool:
        data = json.loads(document)
        if data.get("format") != "synapse-poc-v1" or not data.get("records"):
            raise ValueError("unsupported or empty export")

        seen: set[str] = set()
        records_by_id: dict[str, dict[str, Any]] = {}
        grants: dict[str, set[str]] = {}
        for record in data["records"]:
            envelope, payload = record["envelope"], record["payload"]
            required = {
                "object_id",
                "lineage_id",
                "semantic_type",
                "schema_version",
                "causal_parents",
                "recorded_at",
                "payload_ref",
                "provenance_ref",
                "verification",
            }
            if set(envelope) != required or envelope["lineage_id"] != data["lineage_id"]:
                raise ValueError("invalid envelope")
            if any(parent not in seen for parent in envelope["causal_parents"]):
                raise ValueError("broken causal order")
            if envelope["payload_ref"] != _hash(payload):
                raise ValueError("payload integrity failure")
            expected = _hash(ContinuityKernel._integrity_body(envelope, payload))
            if envelope["verification"]["integrity"] != expected:
                raise ValueError("envelope integrity failure")
            object_id = envelope["object_id"]
            semantic_type = envelope["semantic_type"]
            authority = envelope["verification"]["authority"]
            try:
                actor, operation = authority.rsplit(":", 1)
            except ValueError as error:
                raise ValueError("invalid authority evidence") from error

            if semantic_type == "ica.genesis":
                if seen or operation != "bootstrap":
                    raise ValueError("invalid genesis")
                grants = {
                    name: set(operations)
                    for name, operations in payload["initial_authority"].items()
                }
            elif operation not in grants.get(actor, set()):
                raise ValueError("unauthorized history object")

            if semantic_type == "gra.capability_grant":
                if operation != "grant":
                    raise ValueError("invalid grant authority")
                grants.setdefault(payload["actor"], set()).add(payload["operation"])

            seen.add(object_id)
            records_by_id[object_id] = record

        if data["genesis_id"] not in seen or data["current_checkpoint"] not in seen:
            raise ValueError("proof endpoints missing")
        if records_by_id[data["genesis_id"]]["envelope"]["semantic_type"] != "ica.genesis":
            raise ValueError("genesis endpoint has wrong type")
        if records_by_id[data["current_checkpoint"]]["envelope"]["semantic_type"] != "ica.checkpoint":
            raise ValueError("checkpoint endpoint has wrong type")
        if data["genesis_id"] not in ContinuityKernel._causal_ancestors(
            records_by_id, data["current_checkpoint"]
        ):
            raise ValueError("checkpoint is not descended from genesis")
        return True

    def _append(
        self,
        semantic_type: str,
        payload: dict[str, Any],
        parents: list[str],
        actor: str,
        operation: str,
        provenance_ref: str,
    ) -> str:
        if any(parent not in self._by_id for parent in parents):
            raise ValueError("unknown causal parent")
        object_id = str(uuid.uuid4())
        envelope = {
            "object_id": object_id,
            "lineage_id": self.lineage_id,
            "semantic_type": semantic_type,
            "schema_version": 1,
            "causal_parents": list(parents),
            "recorded_at": _now(),
            "payload_ref": _hash(payload),
            "provenance_ref": provenance_ref,
            "verification": {"integrity": "", "authority": f"{actor}:{operation}"},
        }
        envelope["verification"]["integrity"] = _hash(
            self._integrity_body(envelope, payload)
        )
        record = {"envelope": envelope, "payload": copy.deepcopy(payload)}
        self._records.append(record)
        self._by_id[object_id] = record
        return object_id

    @staticmethod
    def _integrity_body(envelope: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        body = copy.deepcopy(envelope)
        body["verification"]["integrity"] = ""
        return {"envelope": body, "payload": payload}

    @staticmethod
    def _causal_ancestors(
        records_by_id: dict[str, dict[str, Any]], object_id: str
    ) -> set[str]:
        result: set[str] = set()
        pending = list(records_by_id[object_id]["envelope"]["causal_parents"])
        while pending:
            parent = pending.pop()
            if parent in result:
                continue
            result.add(parent)
            pending.extend(records_by_id[parent]["envelope"]["causal_parents"])
        return result

    def _ancestors(self, checkpoint: str) -> set[str]:
        result: set[str] = set()
        parent = self._checkpoint_parent.get(checkpoint)
        while parent is not None:
            result.add(parent)
            parent = self._checkpoint_parent.get(parent)
        return result

    def _rebuild_state(self) -> None:
        genesis = self._by_id[self.genesis_id]["payload"]
        self._grants = {
            actor: set(operations)
            for actor, operations in genesis["initial_authority"].items()
        }
        for record in self._records:
            envelope, payload = record["envelope"], record["payload"]
            semantic_type = envelope["semantic_type"]
            if semantic_type == "gra.capability_grant":
                self._grants.setdefault(payload["actor"], set()).add(payload["operation"])
            elif semantic_type == "ica.checkpoint":
                checkpoint = envelope["object_id"]
                parent = payload["previous_checkpoint"]
                self._checkpoint_parent[checkpoint] = parent
                if parent is not None:
                    self._successors.setdefault(parent, []).append(checkpoint)


class ActionGate:
    """RCA consent projection plus ECA/ERA checks, kept outside the Mind port."""

    def __init__(self, kernel: ContinuityKernel) -> None:
        self.__kernel = kernel
        self.__consent: dict[tuple[str, str], bool] = {}
        self.body_safe = True
        self.resources_available = True

    def set_consent(self, participant: str, scope: str, granted: bool) -> str | None:
        record_id = self.__kernel.record_authorized_event(
            participant,
            "consent",
            "rca.consent",
            {"participant": participant, "scope": scope, "granted": granted},
        )
        if record_id:
            self.__consent[participant, scope] = granted
        return record_id

    def execute(
        self, actor: str, participants: list[str], scope: str, action: str
    ) -> str:
        if not self.__kernel.allowed(actor, "act"):
            return "DENIED_CAPABILITY"
        if not participants or not all(
            self.__consent.get((participant, scope), False) for participant in participants
        ):
            return "DENIED_CONSENT"
        if not self.body_safe:
            return "DENIED_SAFETY"
        if not self.resources_available:
            return "DENIED_RESOURCE"
        record_id = self.__kernel.record_domain_event(
            actor,
            "eca.action",
            {"participants": participants, "scope": scope, "action": action},
        )
        return "EXECUTED" if record_id else "DENIED_COMMIT"


class Broker:
    """API handed to a Mind. Python itself is not the security sandbox."""

    def __init__(
        self, kernel: ContinuityKernel, actions: ActionGate, actor: str
    ) -> None:
        self.__kernel = kernel
        self.__actions = actions
        self.actor = actor

    def propose(self, semantic_type: str, payload: dict[str, Any]) -> str | None:
        return self.__kernel.record_domain_event(self.actor, semantic_type, payload)

    def act(self, participants: list[str], scope: str, action: str) -> str:
        return self.__actions.execute(self.actor, participants, scope, action)


def demo() -> None:
    kernel = ContinuityKernel("synapse-demo")
    kernel.grant("operator", "commit", "mind-a")
    kernel.grant("operator", "act", "mind-a")
    kernel.grant("operator", "consent", "alice")
    actions = ActionGate(kernel)
    mind = Broker(kernel, actions, "mind-a")
    actions.set_consent("alice", "greet", True)
    action = mind.act(["alice"], "greet", "wave")
    status, _ = kernel.transition(
        "operator",
        kernel.current_checkpoint,
        {"mind": "mind-b", "embodiment": "sim-v1"},
        {"history": "preserved", "mind": "migrated"},
    )
    restored = ContinuityKernel.from_export(kernel.export())
    print(_json({"action": action, "transition": status, "proof": restored.status}))


if __name__ == "__main__":
    demo()
