"""
Cleaning rules — raw export → cleaned rows + quarantine.

Baseline gồm các failure mode mở rộng (allowlist doc_id, parse ngày, HR stale version).
Các rule mới của Sprint 2 tập trung vào:
- làm sạch ký tự vô hình / BOM để tránh nội dung nhìn như nhau nhưng hash khác nhau,
- chuẩn hóa exported_at sang ISO 8601 để phục vụ freshness / lineage,
- quarantine chunk_id nguồn trùng để bắt lỗi export lặp trước khi embed.
"""

from __future__ import annotations

import csv
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Khớp export hợp lệ trong lab (mở rộng khi nhóm thêm doc mới — phải đồng bộ contract).
ALLOWED_DOC_IDS = frozenset(
    {
        "policy_refund_v4",
        "sla_p1_2026",
        "it_helpdesk_faq",
        "hr_leave_policy",
    }
)

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DMY_SLASH = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")
_INVISIBLE_CHARS = re.compile(r"[\u200b\u200c\u200d\ufeff]")
_COLLAPSE_WS = re.compile(r"\s+")


def _norm_text(s: str) -> str:
    return " ".join((s or "").strip().split()).lower()


def _normalize_chunk_text(raw: str) -> Tuple[str, bool]:
    """Remove invisible control characters and collapse repeated whitespace."""
    original = raw or ""
    sanitized = _INVISIBLE_CHARS.sub("", original)
    normalized = _COLLAPSE_WS.sub(" ", sanitized).strip()
    return normalized, normalized != original


def _normalize_exported_at(raw: str) -> Tuple[str, str]:
    """Normalize exported_at to canonical ISO 8601 string with Z suffix."""
    s = (raw or "").strip()
    if not s:
        return "", "missing_exported_at"
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00") if s.endswith("Z") else s)
    except ValueError:
        return "", "invalid_exported_at_format"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z"), ""


def _stable_chunk_id(doc_id: str, chunk_text: str, seq: int) -> str:
    h = hashlib.sha256(f"{doc_id}|{chunk_text}|{seq}".encode("utf-8")).hexdigest()[:16]
    return f"{doc_id}_{seq}_{h}"


def _normalize_effective_date(raw: str) -> Tuple[str, str]:
    """
    Trả về (iso_date, error_reason).
    iso_date rỗng nếu không parse được.
    """
    s = (raw or "").strip()
    if not s:
        return "", "empty_effective_date"
    if _ISO_DATE.match(s):
        return s, ""
    m = _DMY_SLASH.match(s)
    if m:
        dd, mm, yyyy = m.group(1), m.group(2), m.group(3)
        return f"{yyyy}-{mm}-{dd}", ""
    return "", "invalid_effective_date_format"


def load_raw_csv(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({k: (v or "").strip() for k, v in r.items()})
    return rows


def clean_rows(
    rows: List[Dict[str, str]],
    *,
    apply_refund_window_fix: bool = True,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Trả về (cleaned, quarantine).

    Baseline (mở rộng theo narrative Day 10):
    1) Quarantine: doc_id không thuộc allowlist (export lạ / catalog sai).
    2) Chuẩn hoá effective_date sang YYYY-MM-DD; quarantine nếu không parse được.
    3) Quarantine: chunk hr_leave_policy có effective_date < 2026-01-01 (bản HR cũ / conflict version).
    4) Quarantine: chunk_text rỗng hoặc effective_date rỗng sau chuẩn hoá.
    5) Loại trùng nội dung chunk_text (giữ bản đầu).
    6) Fix stale refund: policy_refund_v4 chứa '14 ngày làm việc' → 7 ngày.
    7) Quarantine source chunk_id bị lặp để bắt export replay / duplicate batch.
    8) Chuẩn hóa exported_at sang ISO 8601 để freshness và lineage đọc ổn định.
    9) Loại ký tự vô hình / BOM trong chunk_text để dedupe không bị lệch bởi payload bẩn.
    """
    quarantine: List[Dict[str, Any]] = []
    seen_text: set[str] = set()
    seen_source_ids: set[str] = set()
    cleaned: List[Dict[str, Any]] = []
    seq = 0

    for raw in rows:
        source_chunk_id = (raw.get("chunk_id") or "").strip()
        if not source_chunk_id:
            quarantine.append({**raw, "reason": "missing_source_chunk_id"})
            continue
        if source_chunk_id in seen_source_ids:
            quarantine.append({**raw, "reason": "duplicate_source_chunk_id"})
            continue
        seen_source_ids.add(source_chunk_id)

        doc_id = raw.get("doc_id", "")
        text_raw = raw.get("chunk_text", "")
        text, _ = _normalize_chunk_text(text_raw)
        eff_raw = raw.get("effective_date", "")
        exported_at_raw = raw.get("exported_at", "")

        if doc_id not in ALLOWED_DOC_IDS:
            quarantine.append({**raw, "reason": "unknown_doc_id"})
            continue

        eff_norm, eff_err = _normalize_effective_date(eff_raw)
        if eff_err == "empty_effective_date":
            quarantine.append({**raw, "reason": "missing_effective_date"})
            continue
        if eff_err == "invalid_effective_date_format":
            quarantine.append({**raw, "reason": eff_err, "effective_date_raw": eff_raw})
            continue

        if doc_id == "hr_leave_policy" and eff_norm < "2026-01-01":
            quarantine.append(
                {
                    **raw,
                    "reason": "stale_hr_policy_effective_date",
                    "effective_date_normalized": eff_norm,
                }
            )
            continue

        if not text:
            quarantine.append({**raw, "reason": "missing_chunk_text"})
            continue

        exported_at, exported_at_err = _normalize_exported_at(exported_at_raw)
        if exported_at_err == "missing_exported_at":
            quarantine.append({**raw, "reason": exported_at_err})
            continue
        if exported_at_err == "invalid_exported_at_format":
            quarantine.append({**raw, "reason": exported_at_err, "exported_at_raw": exported_at_raw})
            continue

        key = _norm_text(text)
        if key in seen_text:
            quarantine.append({**raw, "reason": "duplicate_chunk_text"})
            continue
        seen_text.add(key)

        fixed_text = text
        if apply_refund_window_fix and doc_id == "policy_refund_v4":
            if "14 ngày làm việc" in fixed_text:
                fixed_text = fixed_text.replace(
                    "14 ngày làm việc",
                    "7 ngày làm việc",
                )
                fixed_text += " [cleaned: stale_refund_window]"

        seq += 1
        cleaned.append(
            {
                "chunk_id": _stable_chunk_id(doc_id, fixed_text, seq),
                "doc_id": doc_id,
                "chunk_text": fixed_text,
                "effective_date": eff_norm,
                "exported_at": exported_at or "",
            }
        )

    return cleaned, quarantine


def write_cleaned_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("chunk_id,doc_id,chunk_text,effective_date,exported_at\n", encoding="utf-8")
        return
    fieldnames = ["chunk_id", "doc_id", "chunk_text", "effective_date", "exported_at"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def write_quarantine_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("chunk_id,doc_id,chunk_text,effective_date,exported_at,reason\n", encoding="utf-8")
        return
    keys: List[str] = []
    seen_k: set[str] = set()
    for r in rows:
        for k in r.keys():
            if k not in seen_k:
                seen_k.add(k)
                keys.append(k)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore", restval="")
        w.writeheader()
        for r in rows:
            w.writerow(r)
