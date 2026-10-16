import fcntl
import json
import os
import re
import tempfile
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).isoformat()


def _safe_id(value):
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(value))
    if not safe or safe in {".", ".."}:
        raise ValueError("Identificador de rodada inválido")
    return safe


class ImportProgress:
    def __init__(self, storage_root, ronda_id, initial_status):
        self.status_dir = os.path.join(storage_root, "import_status")
        os.makedirs(self.status_dir, exist_ok=True)

        safe_id = _safe_id(ronda_id)
        self.status_path = os.path.join(self.status_dir, safe_id + ".json")
        self.lock_file = open(
            os.path.join(self.status_dir, safe_id + ".lock"), "a"
        )

        try:
            fcntl.flock(
                self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB
            )
        except (BlockingIOError, OSError):
            self.lock_file.close()
            raise RuntimeError(
                "Já existe uma execução ativa com esta rodada: " + safe_id
            )

        self.status = dict(initial_status)
        self.status.update({
            "ronda_id": str(ronda_id),
            "state": "running",
            "started_at": _now(),
            "updated_at": _now(),
            "finished_at": None,
        })
        self.update()

    def update(self, **changes):
        self.status.update(changes)
        self.status["updated_at"] = _now()

        fd, temp_path = tempfile.mkstemp(
            prefix=".import-status-", dir=self.status_dir
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(
                    self.status, handle, ensure_ascii=False, indent=2
                )
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, self.status_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def finish(self, state, **changes):
        self.status.update(changes)
        self.status["state"] = state
        self.status["finished_at"] = _now()
        self.update()
        self.close()

    def close(self):
        if self.lock_file and not self.lock_file.closed:
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
            self.lock_file.close()


def read_status(storage_root, ronda_id):
    path = os.path.join(
        storage_root, "import_status", _safe_id(ronda_id) + ".json"
    )
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)
