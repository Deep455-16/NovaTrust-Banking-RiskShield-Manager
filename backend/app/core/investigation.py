"""Investigation System - Case management without database."""
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import threading

# Resolve data/runtime relative to THIS file's location (backend/app/core/),
# going up 3 levels to the project root, then into data/runtime/.
# This ensures the path is correct regardless of the CWD when uvicorn starts.
_HERE = Path(__file__).resolve().parent          # backend/app/core
_PROJECT_ROOT = _HERE.parent.parent.parent        # project root
RUNTIME_DIR = _PROJECT_ROOT / "data" / "runtime"
CASES_FILE = RUNTIME_DIR / "cases.json"
AUDIT_FILE = RUNTIME_DIR / "audit.json"
_lock = threading.Lock()


@dataclass
class InvestigationCase:
    id: str
    transaction_id: str
    status: str
    risk_score: float
    risk_level: str
    created_at: str
    updated_at: str
    assigned_to: Optional[str] = None
    notes: List[Dict] = None
    actions: List[Dict] = None

    def __post_init__(self):
        if self.notes is None:
            self.notes = []
        if self.actions is None:
            self.actions = []


class InvestigationManager:
    def __init__(self):
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_files()

    def _ensure_files(self):
        for f in [CASES_FILE, AUDIT_FILE]:
            if not f.exists():
                with open(f, "w") as fp:
                    json.dump([], fp)
        # Auto-seed sample cases if empty so the UI has data to display
        cases = self._load_json(CASES_FILE)
        if len(cases) == 0:
            from datetime import datetime, timezone, timedelta
            now = datetime.now(timezone.utc)
            seed_cases = [
                {"id":"CASE_001_TXN001","transaction_id":"TXN-BNK-001234","status":"OPEN","risk_score":87.3,"risk_level":"CRITICAL","created_at":(now-timedelta(hours=2)).isoformat(),"updated_at":(now-timedelta(hours=2)).isoformat(),"assigned_to":"analyst1","notes":[],"actions":[]},
                {"id":"CASE_002_TXN002","transaction_id":"TXN-BNK-005678","status":"IN_PROGRESS","risk_score":72.1,"risk_level":"HIGH","created_at":(now-timedelta(hours=5)).isoformat(),"updated_at":(now-timedelta(hours=1)).isoformat(),"assigned_to":"analyst2","notes":[],"actions":[{"action":"Opened investigation","user":"analyst2","timestamp":(now-timedelta(hours=1)).isoformat(),"notes":"Suspicious high-velocity pattern"}]},
                {"id":"CASE_003_TXN003","transaction_id":"TXN-SFN-009012","status":"OPEN","risk_score":91.5,"risk_level":"CRITICAL","created_at":(now-timedelta(hours=8)).isoformat(),"updated_at":(now-timedelta(hours=8)).isoformat(),"assigned_to":None,"notes":[],"actions":[]},
                {"id":"CASE_004_TXN004","transaction_id":"TXN-GLB-003456","status":"RESOLVED","risk_score":65.0,"risk_level":"HIGH","created_at":(now-timedelta(days=1)).isoformat(),"updated_at":(now-timedelta(hours=3)).isoformat(),"assigned_to":"analyst1","notes":[],"actions":[{"action":"APPROVE","user":"analyst1","timestamp":(now-timedelta(hours=3)).isoformat(),"notes":"Confirmed fraud - customer notified"}]},
                {"id":"CASE_005_TXN005","transaction_id":"TXN-BNK-007890","status":"ESCALATED","risk_score":95.8,"risk_level":"CRITICAL","created_at":(now-timedelta(days=2)).isoformat(),"updated_at":(now-timedelta(hours=6)).isoformat(),"assigned_to":"senior_analyst","notes":[],"actions":[{"action":"ESCALATE","user":"analyst1","timestamp":(now-timedelta(hours=6)).isoformat(),"notes":"OTP scam detected - needs senior review"}]},
                {"id":"CASE_006_TXN006","transaction_id":"TXN-SFN-011234","status":"OPEN","risk_score":55.2,"risk_level":"MEDIUM","created_at":(now-timedelta(hours=12)).isoformat(),"updated_at":(now-timedelta(hours=12)).isoformat(),"assigned_to":"analyst2","notes":[],"actions":[]},
                {"id":"CASE_007_TXN007","transaction_id":"TXN-GLB-013456","status":"RESOLVED","risk_score":42.0,"risk_level":"MEDIUM","created_at":(now-timedelta(days=3)).isoformat(),"updated_at":(now-timedelta(days=1)).isoformat(),"assigned_to":"analyst1","notes":[],"actions":[{"action":"REJECT","user":"analyst1","timestamp":(now-timedelta(days=1)).isoformat(),"notes":"False positive - verified legitimate transaction"}]},
                {"id":"CASE_008_TXN008","transaction_id":"TXN-BNK-015678","status":"IN_PROGRESS","risk_score":78.9,"risk_level":"HIGH","created_at":(now-timedelta(hours=3)).isoformat(),"updated_at":(now-timedelta(minutes=30)).isoformat(),"assigned_to":"analyst2","notes":[],"actions":[{"action":"Reviewing merchant history","user":"analyst2","timestamp":(now-timedelta(minutes=30)).isoformat(),"notes":"Merchant has 3 prior fraud flags"}]},
            ]
            self._atomic_write(CASES_FILE, seed_cases)

    def _atomic_write(self, path: Path, data: Any):
        tmp_path = path.with_suffix(".tmp")
        with open(tmp_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        os.replace(tmp_path, path)

    def _load_json(self, path: Path) -> List[Dict]:
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def create_case(self, transaction_id: str, risk_score: float, risk_level: str, assigned_to: Optional[str] = None) -> InvestigationCase:
        case_id = f"CASE_{int(time.time() * 1000)}_{transaction_id[-6:]}"
        now = datetime.now(timezone.utc).isoformat()
        case = InvestigationCase(
            id=case_id, transaction_id=transaction_id, status="OPEN",
            risk_score=risk_score, risk_level=risk_level,
            created_at=now, updated_at=now, assigned_to=assigned_to
        )
        with _lock:
            cases = self._load_json(CASES_FILE)
            cases.append(asdict(case))
            self._atomic_write(CASES_FILE, cases)
            self._log_audit("CASE_CREATED", case_id, transaction_id, f"Created case for risk level {risk_level}")
        return case

    def get_case(self, case_id: str) -> Optional[InvestigationCase]:
        cases = self._load_json(CASES_FILE)
        for c in cases:
            if c["id"] == case_id:
                return InvestigationCase(**c)
        return None

    def list_cases(self, status: Optional[str] = None) -> List[InvestigationCase]:
        cases = self._load_json(CASES_FILE)
        if status:
            cases = [c for c in cases if c["status"] == status]
        return [InvestigationCase(**c) for c in cases]

    def update_case_status(self, case_id: str, new_status: str, user: str = "system", notes: str = "") -> bool:
        with _lock:
            cases = self._load_json(CASES_FILE)
            for case in cases:
                if case["id"] == case_id:
                    old_status = case["status"]
                    case["status"] = new_status
                    case["updated_at"] = datetime.now(timezone.utc).isoformat()
                    case["actions"] = case.get("actions", [])
                    case["actions"].append({
                        "action": f"STATUS_CHANGE: {old_status} -> {new_status}",
                        "user": user, "timestamp": datetime.now(timezone.utc).isoformat(), "notes": notes
                    })
                    self._atomic_write(CASES_FILE, cases)
                    self._log_audit("CASE_STATUS_UPDATE", case_id, case["transaction_id"], f"Status changed from {old_status} to {new_status} by {user}")
                    return True
        return False

    def perform_action(self, case_id: str, action: str, user: str, notes: str = "") -> bool:
        with _lock:
            cases = self._load_json(CASES_FILE)
            for case in cases:
                if case["id"] == case_id:
                    case["actions"] = case.get("actions", [])
                    case["actions"].append({
                        "action": action, "user": user,
                        "timestamp": datetime.now(timezone.utc).isoformat(), "notes": notes
                    })
                    if action == "APPROVE":
                        case["status"] = "RESOLVED"
                    elif action == "REJECT":
                        case["status"] = "RESOLVED"
                    elif action == "ESCALATE":
                        case["status"] = "ESCALATED"
                    case["updated_at"] = datetime.now(timezone.utc).isoformat()
                    self._atomic_write(CASES_FILE, cases)
                    self._log_audit("CASE_ACTION", case_id, case["transaction_id"], f"Action {action} performed by {user}")
                    return True
        return False

    def _log_audit(self, event_type: str, case_id: str, transaction_id: str, details: str):
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type, "case_id": case_id,
            "transaction_id": transaction_id, "details": details
        }
        audits = self._load_json(AUDIT_FILE)
        audits.append(audit_entry)
        self._atomic_write(AUDIT_FILE, audits)

    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        audits = self._load_json(AUDIT_FILE)
        return audits[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        cases = self._load_json(CASES_FILE)
        statuses = {}
        for c in cases:
            s = c["status"]
            statuses[s] = statuses.get(s, 0) + 1
        return {
            "total_cases": len(cases),
            "status_breakdown": statuses,
            "open_cases": statuses.get("OPEN", 0),
            "investigating_cases": statuses.get("INVESTIGATING", 0),
            "escalated_cases": statuses.get("ESCALATED", 0),
            "resolved_cases": statuses.get("RESOLVED", 0)
        }
