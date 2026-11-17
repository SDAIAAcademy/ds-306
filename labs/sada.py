"""Shared plumbing for the DS-306 labs: the Sada Citizen Voice Centre case.

The ideas are taught in the notebooks. This module holds the repeated parts: paths and quick mode,
loading the case data, reference results for the safety nets, scores with bootstrap intervals,
and one cached call to a hosted model (chat or embeddings) with a scripted stand-in for when no
key works. The stand-in is not a model: it replays the course's recorded runs (which are
synthetic) or applies keyword rules, and says so every time it is used.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

LABS = Path(__file__).resolve().parent
DATA = LABS / "data"
REFERENCE = DATA / "reference"
ARTIFACTS = LABS / "artifacts"
CACHE = LABS / "cache"

try:
    from dotenv import load_dotenv
    load_dotenv(LABS / ".env")
except ImportError:
    pass

QUICK = os.getenv("SADA_QUICK", "0") == "1"
PROVIDER_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("LLM_API_KEY", "")
CHAT_MODEL = os.getenv("SADA_MODEL", "google/gemma-4-31b-it:free")
EMBED_MODEL = os.getenv("SADA_EMBED_MODEL", "nvidia/nemotron-3.5-embed-1b:free")
FALLBACKS = [m for m in os.getenv("SADA_FALLBACKS", "google/gemma-4-26b-a4b-it:free").split(",") if m]
USE_CACHE = os.getenv("SADA_CACHE", "1") == "1"
MIN_INTERVAL = float(os.getenv("SADA_MIN_INTERVAL", "3.1"))  # free endpoints allow 20 requests a minute
_STANDIN = os.getenv("SADA_STANDIN", "0") == "1" or not API_KEY

CATEGORIES = ["water_sewage", "roads", "waste", "lighting", "noise", "permits", "parks", "staff_service"]
VARIETIES = ["msa", "gulf", "en"]
CALLS = {"chat": 0, "embed": 0, "cached": 0, "prompt_tokens": 0, "completion_tokens": 0}


def pick(full, quick):
    """The small value in quick mode (SADA_QUICK=1), the full one otherwise."""
    return quick if QUICK else full


def standin() -> bool:
    return _STANDIN


def banner(lab: str) -> None:
    mode = ("STAND-IN (scripted, not a model: it replays the course's synthetic recorded runs)" if _STANDIN
            else f"{PROVIDER_URL} · {CHAT_MODEL}")
    print(f"{lab} · quick mode: {QUICK} · model access: {mode}")


def lab_dir(name: str) -> Path:
    path = ARTIFACTS / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def check(ok: bool, what: str) -> None:
    print(("✅ " if ok else "❌ ") + what)


# ---------- reference results for the safety nets ----------

def reference(name: str):
    return json.loads((REFERENCE / f"{name}.json").read_text(encoding="utf-8"))


def keep(name: str, value) -> None:
    """Writes a reference result when SADA_WRITE_REF=1 (the course team's full solution run)."""
    if os.getenv("SADA_WRITE_REF") == "1" and not QUICK:
        REFERENCE.mkdir(parents=True, exist_ok=True)
        (REFERENCE / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n",
                                                encoding="utf-8", newline="\n")


def attempt(fn, name: str):
    """Runs an exercise. When it is not written yet, returns the course's reference result so later cells run."""
    try:
        value = fn()
    except NotImplementedError:
        print(f"↩️  Exercise not done yet: the cells below use the reference result '{name}'.")
        return reference(name)
    keep(name, value)
    return value


# ---------- the case data ----------

def complaints() -> pd.DataFrame:
    """20,000 complaints as received: id, received, channel, form_lang, district, text (with personal data)."""
    return pd.read_csv(DATA / "complaints.csv.gz", parse_dates=["received"])


def districts() -> pd.DataFrame:
    return pd.read_csv(DATA / "districts.csv")


def gold() -> pd.DataFrame:
    """300 redacted complaints: district, variety, two coders and the adjudicated label (`gold`)."""
    return pd.read_csv(DATA / "gold.csv")


def pool() -> pd.DataFrame:
    """3,000 redacted complaints with the intake team's routing label (noisy: nobody checked it)."""
    return pd.read_csv(DATA / "pool.csv")


def pair40() -> pd.DataFrame:
    return pd.read_csv(DATA / "pair40.csv")


def redaction_audit() -> pd.DataFrame:
    a = pd.read_csv(DATA / "redaction_audit.csv")
    a["pii"] = a["pii"].map(json.loads)
    return a


def runs_gold() -> pd.DataFrame:
    """Recorded labels of Fahim on the gold set: two prompts x three runs. Synthetic (see labs/README.md)."""
    return pd.read_csv(DATA / "model_runs_gold.csv")


def labels_all() -> pd.DataFrame:
    """Recorded labels of Fahim (prompt 1, run 1) for all 20,000 complaints. Synthetic."""
    return pd.read_csv(DATA / "model_labels_all.csv.gz")


def jsonl(name: str) -> list[dict]:
    return [json.loads(x) for x in (DATA / name).read_text(encoding="utf-8").splitlines() if x.strip()]


def codebook() -> str:
    return (DATA / "codebook.md").read_text(encoding="utf-8")


def prompt(version: str) -> str:
    """Fahim's prompts by version ("P1", "P2"), or another prompt file by name ("extract_v1")."""
    name = f"fahim_{version.lower()}" if version.upper() in ("P1", "P2") else version
    return (DATA / "prompts" / f"{name}.md").read_text(encoding="utf-8")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


# ---------- Arabic text: the reference versions of the Day 1 exercises ----------

DIACRITICS = re.compile("[ً-ْٰ]")
TATWEEL = "ـ"
DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
LAYERS = ["unicode", "persian", "marks", "alef", "yeh_teh", "digits"]


def normalise(text: str, layers: list[str] | None = None) -> str:
    """The course rules, applied in order. They mirror CAMeL Tools' normalize_unicode, normalize_alef_ar,
    normalize_alef_maksura_ar and normalize_teh_marbuta_ar, plus Persian letters, marks and digits."""
    layers = LAYERS if layers is None else layers
    t = text or ""
    if "unicode" in layers:
        t = unicodedata.normalize("NFKC", t)
    if "persian" in layers:
        t = t.replace("ی", "ي").replace("ک", "ك")
    if "marks" in layers:
        t = DIACRITICS.sub("", t).replace(TATWEEL, "")
    if "alef" in layers:
        t = re.sub("[أإآٱ]", "ا", t)
    if "yeh_teh" in layers:
        t = t.replace("ى", "ي").replace("ة", "ه")
    if "digits" in layers:
        t = t.translate(DIGITS)
    return re.sub(r"\s+", " ", t).strip()


def dialect(text: str, rules: pd.DataFrame | None = None) -> str:
    """Collapses letters repeated three times or more, then applies the course's Gulf spelling map."""
    rules = pd.read_csv(DATA / "dialect_map.csv") if rules is None else rules
    t = re.sub(r"(.)\1{2,}", r"\1", text)
    for v, c in zip(rules.variant, rules.canonical):
        t = re.sub(rf"(?<!\S){re.escape(normalise(v))}(?!\S)", normalise(c), t)
    return t


def tokens(text: str) -> list[str]:
    return re.findall(r"[\w؀-ۿ]+", text.lower())


def script_language(text: str) -> str:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return "none"
    arabic = sum("؀" <= c <= "ۿ" or "ﭐ" <= c <= "﻿" for c in letters) / len(letters)
    return "ar" if arabic >= 0.8 else "en" if arabic <= 0.2 else "mixed"


GULF_MARKERS = {"وايد", "الحين", "محد", "شلون", "ليش", "مويه", "الماي", "ماي", "زين", "يبي", "نبي", "ترى", "اللي",
                "مره", "جنب", "وش", "تكفون", "يكبون", "الياهل", "سكروا", "قعدت", "مسكره", "ماطور", "حطوا", "طافيه",
                "شي", "مو", "هالحال", "يسوء", "يتاذون", "العيال", "الشيبان"}


def guess_variety(text: str) -> str:
    """A rough variety guess for any complaint: English by script, Gulf when a Gulf marker word appears, else MSA.

    It is an instrument like any other: Lab 3.3 measures it against the coders' variety on the gold set.
    """
    if script_language(text) == "en":
        return "en"
    words = set(tokens(dialect(normalise(text))))
    return "gulf" if words & {normalise(w) for w in GULF_MARKERS} else "msa"


PII_TAGS = {"phone": "[PHONE]", "national_id": "[ID]", "email": "[EMAIL]", "name": "[NAME]"}


def misses(redacted: str, pii: list[dict]) -> list[dict]:
    """The marked values that are still readable after redaction.

    A phone or an identity number counts as missed when seven or more of its digits are still there in a row,
    in either digit system. A name counts as missed when its family name is still there; an email when its
    local part is.
    """
    flat = re.sub(r"[\s\-+]", "", redacted.translate(DIGITS))
    out = []
    for p in pii:
        v = p["value"]
        if p["type"] in ("phone", "national_id"):
            d = re.sub(r"\D", "", v.translate(DIGITS))
            if any(d[i:i + 7] in flat for i in range(0, len(d) - 6)):
                out.append(p)
        elif p["type"] == "name":
            if v.split()[-1] in redacted:
                out.append(p)
        elif p["type"] == "email" and v.split("@")[0] in redacted:
            out.append(p)
    return out


# ---------- scores with intervals ----------

def boot_ci(y_true, y_pred, metric, groups=None, n: int | None = None, seed: int = 306) -> pd.DataFrame:
    """A metric with a 95% percentile bootstrap interval, overall and for each group (resampling documents)."""
    n = n or pick(2000, 300)
    df = pd.DataFrame({"y": list(y_true), "p": list(y_pred), "g": list(groups) if groups is not None else "all"})
    rows = []
    for g, d in [("all", df)] + ([(g, df[df.g == g]) for g in sorted(df.g.unique())] if groups is not None else []):
        y, p = d.y.to_numpy(), d.p.to_numpy()
        rng = np.random.default_rng(seed)
        stats = [metric(y[i], p[i]) for i in (rng.integers(0, len(y), len(y)) for _ in range(n))]
        rows.append({"group": g, "n": len(d), "value": round(float(metric(y, p)), 3),
                     "low": round(float(np.percentile(stats, 2.5)), 3), "high": round(float(np.percentile(stats, 97.5)), 3)})
    return pd.DataFrame(rows)


def macro_f1(y, p) -> float:
    from sklearn.metrics import f1_score
    return f1_score(y, p, average="macro", labels=CATEGORIES, zero_division=0)


def accuracy(y, p) -> float:
    return float(np.mean(np.asarray(y) == np.asarray(p)))


def kappa(a, b) -> float:
    from sklearn.metrics import cohen_kappa_score
    return float(cohen_kappa_score(a, b))


# ---------- prices (checked on OpenRouter's public model list on 2026-11-15) ----------

def prices() -> dict:
    """USD per token for the paid endpoint of the default chat model: the cost at volume once the free limit is passed."""
    return reference("prices")


def cost_per_1000(prompt_tokens: float, completion_tokens: float, per_doc: bool = True) -> float:
    p = prices()["chat_paid"]
    return round(1000 * (prompt_tokens * p["prompt"] + completion_tokens * p["completion"]), 4)


# ---------- hosted models ----------

_client = None


def _openai():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(base_url=PROVIDER_URL, api_key=API_KEY, timeout=90, max_retries=1)
    return _client


def _key(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]


def _cached(kind: str, key: str):
    path = CACHE / kind / f"{key}.json"
    if USE_CACHE and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _store(kind: str, key: str, value) -> None:
    path = CACHE / kind / f"{key}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


_last = 0.0


def _call(model: str, fn):
    """One request, paced for a free model and retried after a rate limit (429) or a busy server (5xx)."""
    global _last
    for attempt_ in range(3):
        if model.endswith(":free"):
            time.sleep(max(0.0, _last + MIN_INTERVAL - time.monotonic()))
        _last = time.monotonic()
        try:
            return fn()
        except Exception as err:  # noqa: BLE001
            status = getattr(err, "status_code", None) or 0
            if attempt_ == 2 or not (status == 429 or status >= 500):
                raise
            print(f"  {model}: {'rate limit' if status == 429 else 'busy'} ({status}); waiting {30 * (attempt_ + 1)} s")
            time.sleep(30 * (attempt_ + 1))


def _fall_back(err: Exception) -> None:
    global _STANDIN
    print(f"⚠️  The hosted model refused ({type(err).__name__}: {str(err)[:100]}). Switching to the scripted stand-in.")
    _STANDIN = True


def chat(messages: list[dict], temperature: float = 0.0, max_tokens: int = 600, json_mode: bool = True,
         sample: int = 0, model: str | None = None) -> dict:
    """One chat call: text, tokens, model, and whether the stand-in answered. `sample` keeps repeated calls apart in the cache."""
    model = model or CHAT_MODEL
    req = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens,
           "json": json_mode, "sample": sample, "standin": _STANDIN}
    key = _key(req)
    hit = _cached("chat", key)
    if hit:
        CALLS["cached"] += 1
        return hit
    if not _STANDIN:
        for m in [model] + [f for f in FALLBACKS if f != model]:
            try:
                kw = {"response_format": {"type": "json_object"}} if json_mode else {}
                r = _call(m, lambda: _openai().chat.completions.create(
                    model=m, messages=messages, temperature=temperature, max_tokens=max_tokens, **kw))
                out = {"text": r.choices[0].message.content or "", "model": m, "standin": False,
                       "prompt_tokens": r.usage.prompt_tokens if r.usage else 0,
                       "completion_tokens": r.usage.completion_tokens if r.usage else 0}
                CALLS["chat"] += 1
                CALLS["prompt_tokens"] += out["prompt_tokens"]
                CALLS["completion_tokens"] += out["completion_tokens"]
                _store("chat", key, out)
                return out
            except Exception as err:  # noqa: BLE001
                status = getattr(err, "status_code", None)
                if status in (401, 403):
                    _fall_back(err)
                    break
                print(f"  {m} did not answer ({status or type(err).__name__}); trying the next model")
        else:
            _fall_back(RuntimeError("no model answered"))
    text = StandIn(sample).reply(messages)
    prompt_text = " ".join(str(m["content"]) for m in messages)
    CALLS["chat"] += 1
    return {"text": text, "model": model, "standin": True, "prompt_tokens": len(prompt_text) // 3,
            "completion_tokens": len(text) // 4}


def embed(texts: list[str], batch: int = 64, model: str | None = None) -> np.ndarray:
    """Unit-length vectors from the hosted embedding model, cached per text; the lexical stand-in without a key."""
    model = model or EMBED_MODEL
    started_real = not _STANDIN
    out, todo = [None] * len(texts), []
    for i, t in enumerate(texts):
        hit = _cached("embed", _key([model, t, _STANDIN]))
        if hit:
            out[i] = hit
        else:
            todo.append(i)
    for s in range(0, len(todo), batch):
        idx = todo[s:s + batch]
        vecs = None
        if not _STANDIN:
            try:
                r = _call(model, lambda: _openai().embeddings.create(model=model, input=[texts[i] for i in idx]))
                vecs = [d.embedding for d in r.data]
                CALLS["embed"] += 1
            except Exception as err:  # noqa: BLE001
                _fall_back(err)
        if vecs is None:
            vecs = [standin_vector(texts[i]) for i in idx]
            CALLS["embed"] += 1
        for i, v in zip(idx, vecs):
            out[i] = v
            _store("embed", _key([model, texts[i], _STANDIN]), v)
    if started_real and _STANDIN:  # never mix a model's vectors with the stand-in's
        out = [standin_vector(t) for t in texts]
    a = np.asarray(out, dtype=np.float32)
    return a / np.linalg.norm(a, axis=1, keepdims=True).clip(1e-9)


def standin_vector(text: str, dim: int = 384) -> list[float]:
    """Hashed character 3- to 5-grams and words of the normalised text: a lexical stand-in, not an embedding model."""
    v = np.zeros(dim, dtype=np.float32)
    t = f" {dialect(normalise(text))} "
    grams = [t[i:i + n] for n in (3, 4, 5) for i in range(len(t) - n + 1)] + [f"w:{w}" for w in tokens(t)]
    for g in grams:
        h = int(hashlib.md5(g.encode()).hexdigest()[:8], 16)
        v[h % dim] += 1.0 if (h >> 20) & 1 else -1.0
    return v.tolist()


# ---------- the batch format the labs use with Fahim ----------

def batch_message(docs: pd.DataFrame) -> str:
    return "\n".join(f"{i}: {t}" for i, t in zip(docs["id"], docs["text"]))


def parse_labels(text: str, ids: list[str]) -> dict[str, str | None]:
    """{id: label} from a reply; a missing id or a label outside the codebook becomes None (never guessed)."""
    try:
        data = json.loads(text[text.find("{"): text.rfind("}") + 1])
        got = {str(x.get("id")): x.get("label") for x in data.get("labels", [])}
    except (ValueError, AttributeError):
        got = {}
    return {i: (got.get(i) if got.get(i) in CATEGORIES else None) for i in ids}


# ---------- Day 4: inspection reports ----------

FIELDS = ["district", "inspection_date", "defect_type", "severity", "hazard_to_public", "repair_deadline_days"]
DEFECTS = ["pothole", "sewage_overflow", "broken_light", "illegal_dumping", "damaged_pavement", "fallen_sign"]
SEVERITIES = ["low", "medium", "high", "critical"]


def inspection_schema():
    """The reference schema of Lab 4.1, for the cells that follow when the exercise is not done yet."""
    from datetime import date as _date
    from typing import Literal, Optional

    from pydantic import BaseModel, ConfigDict, Field, field_validator

    codes = tuple(districts().district)

    class Inspection(BaseModel):
        model_config = ConfigDict(extra="forbid")
        district: Optional[Literal[codes]] = None  # type: ignore[valid-type]
        inspection_date: Optional[_date] = None
        defect_type: Optional[Literal[tuple(DEFECTS)]] = None  # type: ignore[valid-type]
        severity: Optional[Literal[tuple(SEVERITIES)]] = None  # type: ignore[valid-type]
        hazard_to_public: Optional[bool] = None
        repair_deadline_days: Optional[int] = Field(default=None, ge=1, le=90)

        @field_validator("inspection_date")
        @classmethod
        def in_2026(cls, v):
            if v is not None and v.year != 2026:
                raise ValueError("inspections in this file are from 2026")
            return v

    return Inspection


# ---------- the scripted stand-in ----------

_RECORDED: dict | None = None
_KEYWORDS = {
    "water_sewage": ["مياه", "ماي", "مويه", "مجاري", "صرف", "ضغط", "تسريب", "تسرب", "water", "sewage", "pipe", "manhole"],
    "roads": ["حفر", "رصيف", "مطب", "جسر", "سفلت", "pothole", "pavement", "bump", "bridge", "resurfaced"],
    "waste": ["نفايات", "زباله", "حاوي", "مخلفات", "rubbish", "bin", "waste"],
    "lighting": ["انار", "لمبات", "عمود", "نور", "انوار", "light"],
    "noise": ["ورشه", "ضوضاء", "ازعاج", "سماعات", "مولد", "ماطور", "noise", "music", "generator", "workshop"],
    "permits": ["رخصه", "تصريح", "ترخيص", "permit", "licence"],
    "parks": ["حديقه", "العاب", "ممشى", "حمامات", "park", "garden", "play", "benches"],
    "staff_service": ["موظف", "الرقم الموحد", "البلاغ", "الفرع", "employee", "hotline", "branch", "closed my"],
}


def keyword_label(text: str) -> str:
    t = normalise(text).lower()
    scores = {c: sum(normalise(k) in t for k in ks) for c, ks in _KEYWORDS.items()}
    return max(scores, key=scores.get)


def _recorded() -> dict:
    global _RECORDED
    if _RECORDED is None:
        r = runs_gold()
        _RECORDED = {"runs": {(i, p, n): lab for i, p, n, lab in zip(r.id, r.prompt, r.run, r.label)},
                     "all": dict(zip(*labels_all()[["id", "label"]].T.values)),
                     "extract": {x["id"]: x for x in jsonl("inspection_runs.jsonl")},
                     "p": {sha(prompt("P1")): "P1", sha(prompt("P2")): "P2"}}
    return _RECORDED


class StandIn:
    """Replays the recorded (synthetic) runs for the course's prompts; keyword rules for anything else. Not a model."""

    def __init__(self, sample: int):
        self.run = (sample % 3) + 1

    def reply(self, messages: list[dict]) -> str:
        system = " ".join(m["content"] for m in messages if m["role"] == "system")
        user = [m["content"] for m in messages if m["role"] == "user"][-1]
        rec = _recorded()
        if "repair_deadline_days" in system:  # the extraction prompt of Day 4
            m = re.search(r"IR-\d{4}", " ".join(str(x["content"]) for x in messages if x["role"] == "user"))
            got = rec["extract"].get(m.group(0)) if m else None
            fields = ["district", "inspection_date", "defect_type", "severity", "hazard_to_public", "repair_deadline_days"]
            return json.dumps({k: got[k] for k in fields} if got else {k: None for k in fields})
        if sha(system) not in rec["p"] and "water_sewage" not in system:  # not a labelling prompt
            return json.dumps({"standin": True, "note": "scripted stand-in: no model answered this request"})
        version = rec["p"].get(sha(system), "P1")
        labels = []
        for line in user.splitlines():
            if ":" not in line:
                continue
            i, text = line.split(":", 1)
            i = i.strip()
            lab = rec["runs"].get((i, version, self.run)) or rec["all"].get(i) or keyword_label(text)
            labels.append({"id": i, "label": lab})
        return json.dumps({"labels": labels}, ensure_ascii=False)
