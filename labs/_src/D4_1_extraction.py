# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "pydantic>=2.8", "python-dotenv>=1.0", "openai>=1.60", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 4.1 · Six fields, validated
#
# Day 4 · Session 1 (Schema-constrained extraction) · 25 min.
#
# Khalaf Al-Baqmi's field inspectors file free-text reports in Arabic and English. He wants six fields in a table:
# district, date, defect, severity, whether the public is at risk, and the repair deadline. You write the schema the
# model must fill, validate every reply, send back the ones that fail, and make sure a field the report does not
# state comes back empty instead of invented.
#
# **AI policy: models are measured here.** The extractions come from the model; the schema and the checks are yours.
#
# **Model access.** With a free key in `labs/.env`, the model is `google/gemma-4-31b-it:free` on OpenRouter (about
# fifteen requests in this lab). Without one, the scripted stand-in replays the course's **recorded extraction run**,
# which is synthetic: `prepare_data.py` wrote it with the error patterns Lab 4.2 measures. The banner says which.
#
# **Reference state.** `data/inspections.jsonl` (500 synthetic reports) and `data/prompts/extract_v1.md`. Nothing
# from Day 3.
#
# **Tasks**
# - [ ] 1 · The schema with Pydantic (6')
# - [ ] 2 · The prompt and three reports (6')
# - [ ] 3 · Validate and repair (6')
# - [ ] 4 · A null, not an invented value (4')
# - [ ] 5 · Twelve reports, saved with the version (3')
# - [ ] ✱ Stretch · A seventh field, the street number, measured on the twelve reports

# %%
import os, sys, subprocess
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    REPO_URL = "https://github.com/SDAIAAcademy/ds-306.git"
    if not Path("/content/ds-306").exists():
        subprocess.run(["git", "clone", "-q", REPO_URL, "/content/ds-306"], check=True)
    os.chdir("/content/ds-306/labs")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements-colab.txt"], check=True)
    try:
        from google.colab import userdata
        os.environ.setdefault("OPENROUTER_API_KEY", userdata.get("OPENROUTER_API_KEY") or "")
    except Exception:  # noqa: BLE001  no secret set: the stand-in answers
        pass
else:
    while not Path("sada.py").exists() and Path.cwd() != Path.cwd().parent:
        os.chdir("..")  # solutions/ notebooks run from labs/
sys.path.insert(0, os.getcwd())

import json
import re
from datetime import date
from typing import Literal, Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
import sada as U

U.banner("Lab 4.1")
OUT = U.lab_dir("day4")
reports = {r["id"]: r for r in U.jsonl("inspections.jsonl")}
CODES = tuple(U.districts().district)
print(len(reports), "reports;", reports["IR-0005"]["text"])

# %% [markdown]
# ## 1 · The schema with Pydantic (6')
#
# A schema states what a valid answer is before any model answers: the type of each field, the allowed values and
# the ranges. Every field may be `None`, because a report may not state it.
#
# ✏️ **Exercise** · Write the class `Inspection` inside `make_schema()`:
#
# | Field | Type and rule |
# |---|---|
# | `district` | one of the 12 codes in `CODES` |
# | `inspection_date` | a date in 2026 |
# | `defect_type` | one of `U.DEFECTS` |
# | `severity` | one of `U.SEVERITIES` |
# | `hazard_to_public` | true or false |
# | `repair_deadline_days` | a whole number from 1 to 90 |
#
# Forbid extra keys (`model_config = ConfigDict(extra="forbid")`).

# %%
def make_schema():
    # BEGIN SOLUTION
    class Inspection(BaseModel):
        model_config = ConfigDict(extra="forbid")
        district: Optional[Literal[CODES]] = None  # type: ignore[valid-type]
        inspection_date: Optional[date] = None
        defect_type: Optional[Literal[tuple(U.DEFECTS)]] = None  # type: ignore[valid-type]
        severity: Optional[Literal[tuple(U.SEVERITIES)]] = None  # type: ignore[valid-type]
        hazard_to_public: Optional[bool] = None
        repair_deadline_days: Optional[int] = Field(default=None, ge=1, le=90)

        @field_validator("inspection_date")
        @classmethod
        def in_2026(cls, v):
            if v is not None and v.year != 2026:
                raise ValueError("inspections in this file are from 2026")
            return v

    return Inspection
    # END SOLUTION


try:
    Inspection = make_schema()
except NotImplementedError:
    print("↩️  Exercise not done yet: using the reference schema.")
    Inspection = U.inspection_schema()
SCHEMA_SHA = U.sha(json.dumps(Inspection.model_json_schema(), sort_keys=True))
print(list(Inspection.model_fields), "| schema", SCHEMA_SHA)
U.check(list(Inspection.model_fields) == U.FIELDS, "six fields, in the course's order")

# %% [markdown]
# ## 2 · The prompt and three reports (6')
#
# Read the prompt: it gives the district codes with their Arabic and English names, says how to read a date with
# slashes, and says what to do when a field is not stated. ✏️ **Exercise** · Write `messages(report)`: the prompt as
# the system message and the report (id and text) as the user message. Send three reports with
# `U.chat(..., temperature=0)` (JSON mode is on by default) and print the raw replies.

# %%
PROMPT = U.prompt("extract_v1")
print(PROMPT)


def messages(report: dict) -> list[dict]:
    # BEGIN SOLUTION
    return [{"role": "system", "content": PROMPT}, {"role": "user", "content": f"{report['id']}\n{report['text']}"}]
    # END SOLUTION


try:
    messages(reports["IR-0001"])
except NotImplementedError:
    print("↩️  Exercise not done yet: using the reference message builder.")

    def messages(report):
        return [{"role": "system", "content": PROMPT}, {"role": "user", "content": f"{report['id']}\n{report['text']}"}]

for rid in ("IR-0001", "IR-0002", "IR-0005"):
    reply = U.chat(messages(reports[rid]), temperature=0)
    print(rid, "·", "stand-in (recorded, synthetic)" if reply["standin"] else reply["model"], "·", reply["text"])

# %% [markdown]
# ## 3 · Validate and repair (6')
#
# JSON mode makes a reply parse; it does not make it right. The schema catches values that cannot be right: a
# district written as a name, a date with slashes, a severity outside the four levels.
#
# ✏️ **Exercise** ·
# 1. `validate(text)`: returns `(record, [])` when the reply fits the schema, `(None, errors)` when it does not, one
#    short string per failing field (`f"{field}: {message}"` from `ValidationError.errors()`).
# 2. `extract(report, first=None)`: asks the model (or uses `first`, a reply already received), validates, and on
#    failure sends **one** repair request that quotes the errors. It returns the record (or `None`), the errors left
#    and the number of requests.

# %%
BROKEN = ('{"district": "Al Marwa", "inspection_date": "07/06/2026", "defect_type": "illegal_dumping", '
          '"severity": "Minor", "hazard_to_public": false, "repair_deadline_days": 30}')


def validate(text: str) -> tuple[dict | None, list[str]]:
    # BEGIN SOLUTION
    try:
        return Inspection.model_validate_json(text).model_dump(mode="json"), []
    except ValidationError as err:
        return None, [f"{'.'.join(str(x) for x in e['loc']) or 'reply'}: {e['msg']}" for e in err.errors()]
    # END SOLUTION


def extract(report: dict, first: str | None = None) -> tuple[dict | None, list[str], int]:
    # BEGIN SOLUTION
    msgs = messages(report)
    requests = 0
    text = first
    if text is None:
        text, requests = U.chat(msgs, temperature=0)["text"], 1
    record, errors = validate(text)
    if errors:
        fix = msgs + [{"role": "assistant", "content": text},
                      {"role": "user", "content": "Your reply failed validation:\n- " + "\n- ".join(errors)
                       + "\nReply again with the corrected JSON object only."}]
        record, errors = validate(U.chat(fix, temperature=0)["text"])
        requests += 1
    return record, errors, requests
    # END SOLUTION


try:
    print(validate(BROKEN)[1])
    fixed, left, n = extract(reports["IR-0002"], first=BROKEN)
except NotImplementedError:
    print("↩️  Exercise not done yet: showing the reference result.")
    fixed, left, n = {"district": None, "inspection_date": "2026-07-06", "defect_type": "illegal_dumping",
                      "severity": "low", "hazard_to_public": True, "repair_deadline_days": 30}, [], 1
print("after repair:", fixed, "| errors left:", left, "| requests:", n)
truth = {r["id"]: r for r in U.jsonl("inspections_reference.jsonl")}
print("reference:   ", {k: truth["IR-0002"][k] for k in U.FIELDS})

# %% [markdown]
# 🔍 **Look at** the repaired record next to the reference. It is valid. Is it right? Which field would no schema
# catch?

# %% [markdown]
# ## 4 · A null, not an invented value (4')
#
# The worst extraction error looks like a correct one: a deadline the report never gave, filled in from the
# severity. ✏️ **Exercise** · `grounded(text, days)`: is the number `days` written in the report as a number of
# days (in either digit system)? Then, over the **recorded run of all 500 reports**, the share of reports that state no deadline but got
# one.

# %%
def grounded(text: str, days) -> bool:
    # BEGIN SOLUTION
    if days is None:
        return True
    # the number followed by the word for days: "30" alone could be a street or a date
    return re.search(rf"(?<!\d){int(days)}\s*(?:days|أيام|يوما|يوم)", text.translate(U.DIGITS)) is not None
    # END SOLUTION


recorded = {r["id"]: r for r in U.jsonl("inspection_runs.jsonl")}


def invented_share() -> dict:
    # BEGIN SOLUTION
    no_deadline = [i for i in reports if truth[i]["repair_deadline_days"] is None]
    invented = [i for i in no_deadline if recorded[i]["repair_deadline_days"] is not None]
    caught = [i for i in invented if not grounded(reports[i]["text"], recorded[i]["repair_deadline_days"])]
    return {"reports_without_deadline": len(no_deadline), "invented": len(invented),
            "share": round(len(invented) / len(no_deadline), 3), "caught_by_grounding": len(caught)}
    # END SOLUTION


inv = U.attempt(invented_share, "d4_invented")
print(inv)
U.check(inv["caught_by_grounding"] == inv["invented"], "the grounding rule catches every invented deadline")

# %% [markdown]
# ## 5 · Twelve reports, saved with the version (3')
#
# ✏️ **Exercise** · Extract twelve reports (six that give a deadline, six that do not), apply `grounded` to the
# deadline (set it to `None` and note it when it fails), and save one line per report with the version record:
# model, prompt hash, schema hash, temperature, date.

# %%
with_dl = [i for i in sorted(reports) if truth[i]["repair_deadline_days"] is not None][:6]
without = [i for i in sorted(reports) if truth[i]["repair_deadline_days"] is None][:6]
TWELVE = sorted(with_dl + without)
VERSION = {"model": U.CHAT_MODEL, "prompt": "extract_v1", "prompt_sha": U.sha(PROMPT), "schema_sha": SCHEMA_SHA,
           "temperature": 0, "date": date.today().isoformat(), "standin": U.standin()}


def run_twelve() -> list[dict]:
    # BEGIN SOLUTION
    rows = []
    for rid in TWELVE:
        record, errors, n = extract(reports[rid])
        record = record or {k: None for k in U.FIELDS}
        note = ""
        if not grounded(reports[rid]["text"], record["repair_deadline_days"]):
            record["repair_deadline_days"], note = None, "deadline not in the text: set to null"
        rows.append({"id": rid, **record, "errors": errors, "requests": n, "note": note, **VERSION})
    return rows
    # END SOLUTION


try:
    rows = run_twelve()
except NotImplementedError:
    rows = [{"id": i, **{k: recorded[i][k] for k in U.FIELDS}, "errors": [], "requests": 0, "note": "reference: recorded run",
             **VERSION} for i in TWELVE]
(OUT / "extractions_12.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
table = pd.DataFrame(rows)
print(table[["id"] + U.FIELDS + ["note"]].to_string(index=False))
right = sum(all(r[k] == (truth[r["id"]][k]) for k in U.FIELDS) for r in rows)
print(f"all six fields right in {right} of 12 | requests {int(table.requests.sum())}")

# %% [markdown]
# ## ✱ Stretch · A seventh field
#
# Add `street: Optional[int]` (1 to 200) to the schema and one line to the prompt, extract the twelve reports again
# and score the new field against the street number in the text. With the stand-in the recorded run has no street
# field, so nothing is measured: say so.

# %%
def stretch():
    # BEGIN SOLUTION
    class WithStreet(Inspection):
        street: Optional[int] = Field(default=None, ge=1, le=200)

    prompt7 = PROMPT + "- street: the street number of the defect, as an integer\n"
    hits = 0
    for rid in TWELVE:
        text = reports[rid]["text"]
        reply = U.chat([{"role": "system", "content": prompt7}, {"role": "user", "content": f"{rid}\n{text}"}], temperature=0)
        try:
            got = WithStreet.model_validate_json(reply["text"]).street
        except ValidationError:
            got = None
        want = int(re.search(r"(?:Street|شارع) (\d+)", text.translate(U.DIGITS)).group(1))
        hits += got == want
    print(f"street right in {hits} of 12" + (" (stand-in: the recorded run has no street field, not measured)" if U.standin() else ""))
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. JSON mode was on. Why validate the reply against a schema anyway?
# 2. The repaired record for IR-0002 passed validation. What was still wrong with it, and why can no schema see it?
# 3. Why is an invented deadline worse than a missing one?
#
# <details><summary>Answers</summary>
#
# 1. JSON mode guarantees that the reply parses, not that the district is a known code, the date a 2026 date or the
#    severity one of four levels.
# 2. The date had day and month swapped and the hazard was true where the report says there is no risk: both are
#    valid values. Only a comparison with the text or a reference finds them (Lab 4.2).
# 3. A missing deadline is visible and gets checked; an invented one looks like data and goes into the inspection
#    schedule.
# </details>
#
# **Carry forward.** `artifacts/day4/extractions_12.jsonl`, with its version record.
