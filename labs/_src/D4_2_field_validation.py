# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "python-dotenv>=1.0", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 4.2 · Field-level validation
#
# Day 4 · Session 2 (Field-level validation) · 25 min.
#
# "The extraction is 90% accurate" says nothing about the deadline field, which is the one Khalaf's schedule runs on.
# You score the recorded extraction run over all 500 reports field by field, with empty fields counted correctly,
# find the commonest error of each field and write the rule that would catch it.
#
# **AI policy: models are measured here; the report is yours.**
#
# **Reference state.** `data/inspection_runs.jsonl` (the recorded run of the extraction prompt over 500 reports;
# synthetic), `data/inspections_reference.jsonl` (the reference extractions) and `data/inspections.jsonl` (the
# texts). Nothing from Lab 4.1.
#
# **Tasks**
# - [ ] 1 · Load the run and the reference (3')
# - [ ] 2 · Matching rules per field (5')
# - [ ] 3 · Precision and recall per field (7')
# - [ ] 4 · The commonest errors per field (6')
# - [ ] 5 · The validation report (4')
# - [ ] ✱ Stretch · An interval for the precision of the deadline field

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
else:
    while not Path("sada.py").exists() and Path.cwd() != Path.cwd().parent:
        os.chdir("..")  # solutions/ notebooks run from labs/
sys.path.insert(0, os.getcwd())

import re

import numpy as np
import pandas as pd
import sada as U

U.banner("Lab 4.2")
OUT = U.lab_dir("day4")

# %% [markdown]
# ## 1 · Load the run and the reference (3')
#
# One row per report and field: the reference value and the extracted one. The text's language and the way its date
# is written travel along, because errors often depend on them.

# %%
texts = pd.DataFrame(U.jsonl("inspections.jsonl")).set_index("id")
ref = pd.DataFrame(U.jsonl("inspections_reference.jsonl")).set_index("id")
run = pd.DataFrame(U.jsonl("inspection_runs.jsonl")).set_index("id")
print(run[["model", "prompt", "recorded"]].drop_duplicates().to_string())
texts["date_style"] = np.where(texts.text.str.translate(U.DIGITS).str.contains(r"\d{2}/\d{2}/\d{4}"), "dd/mm/yyyy",
                               np.where(texts.text.str.translate(U.DIGITS).str.contains(r"\d{4}-\d{2}-\d{2}"), "iso", "words"))
long = pd.concat([pd.DataFrame({"id": ref.index, "field": f, "ref": ref[f].to_numpy(), "got": run.loc[ref.index, f].to_numpy()})
                  for f in U.FIELDS]).merge(texts[["lang", "date_style"]], left_on="id", right_index=True).reset_index(drop=True)
long = long.astype({"ref": object, "got": object})
long.loc[long.ref.isna(), "ref"] = None
long.loc[long.got.isna(), "got"] = None
print(len(long), "field values;", long.ref.isna().sum(), "of them empty in the reference")

# %% [markdown]
# ## 2 · Matching rules per field (5')
#
# Before counting, decide what "the same value" means for each field. Exact for codes and dates; for the deadline,
# a whole number of days, so `14` and `14.0` match. And the empty field: a `None` against a `None` is right, but it is
# not a found value.
#
# ✏️ **Exercise** · `outcome(ref, got)` returns one of:
#
# | Outcome | Reference | Extracted |
# |---|---|---|
# | `tp` | a value | the same value |
# | `wrong` | a value | another value |
# | `missed` | a value | empty |
# | `invented` | empty | a value |
# | `tn` | empty | empty |

# %%
def same(a, b) -> bool:
    if isinstance(a, (int, float, np.integer, np.floating)) and not isinstance(a, bool):
        return b is not None and not isinstance(b, bool) and float(a) == float(b)
    return a == b


def outcome(r, g) -> str:
    # BEGIN SOLUTION
    if r is None:
        return "tn" if g is None else "invented"
    if g is None:
        return "missed"
    return "tp" if same(r, g) else "wrong"
    # END SOLUTION


try:
    long["outcome"] = [outcome(r, g) for r, g in zip(long.ref, long.got)]
except NotImplementedError:
    print("↩️  Exercise not done yet: using the reference matching rule.")
    long["outcome"] = ["tn" if r is None and g is None else "invented" if r is None else "missed" if g is None
                       else "tp" if same(r, g) else "wrong" for r, g in zip(long.ref, long.got)]
print(pd.crosstab(long.field, long.outcome).reindex(U.FIELDS).to_string())

# %% [markdown]
# ## 3 · Precision and recall per field (7')
#
# For a field that may be empty:
#
# - **precision**: of the values the model gave, the share that are right: tp / (tp + wrong + invented);
# - **recall**: of the values the reports state, the share the model got right: tp / (tp + wrong + missed).
#
# For `hazard_to_public` both true and false are values; precision on `true` alone is the stretch of the session's
# checkpoint. ✏️ **Exercise** · Precision and recall per field, plus the share of empty reference fields that stayed
# empty. Which field is weakest, and on which side?

# %%
def scores() -> pd.DataFrame:
    # BEGIN SOLUTION
    t = pd.crosstab(long.field, long.outcome).reindex(index=U.FIELDS, columns=["tp", "wrong", "missed", "invented", "tn"], fill_value=0)
    out = pd.DataFrame({"precision": t.tp / (t.tp + t.wrong + t.invented), "recall": t.tp / (t.tp + t.wrong + t.missed),
                        "empty_kept_empty": t.tn / (t.tn + t.invented)})
    return out.round(3).reset_index()
    # END SOLUTION


per_field = pd.DataFrame(U.attempt(lambda: scores().to_dict(orient="records"), "d4_field_scores"))
print(per_field.to_string(index=False))
overall = (long.outcome.isin(["tp", "tn"])).mean()
print(f"\nall fields pooled: {overall:.1%} right. The pooled figure is the one a vendor quotes.")

# %% [markdown]
# ## 4 · The commonest errors per field (6')
#
# ✏️ **Exercise** · For each field, the most frequent (reference, extracted) pair among errors, its count, and the
# group where the field's error rate is highest (language for every field; date style for the date). Read two
# reports behind the commonest error of the date and of the hazard.

# %%
def show(x) -> str:
    """A value as text: None stays None, 14.0 becomes 14."""
    return str(int(x)) if isinstance(x, float) and x.is_integer() else str(x)


def top_errors() -> pd.DataFrame:
    # BEGIN SOLUTION
    err = long[~long.outcome.isin(["tp", "tn"])]
    rows = []
    for f in U.FIELDS:
        e = err[err.field == f]
        if e.empty:
            continue
        if f == "inspection_date":  # every wrong date is different: describe the pattern instead
            swapped = sum(str(r)[5:7] == str(g)[8:10] and str(r)[8:10] == str(g)[5:7] for r, g in zip(e.ref, e.got))
            common, count = "day and month swapped", swapped
        else:
            pair = e.assign(r=[show(x) for x in e.ref], g=[show(x) for x in e.got]).groupby(["r", "g"]).size()
            pair = pair.sort_values(ascending=False)
            common, count = f"{pair.index[0][0]} -> {pair.index[0][1]}", int(pair.iloc[0])
        group_col = "date_style" if f == "inspection_date" else "lang"
        d = long[long.field == f]
        rate = (~d.outcome.isin(["tp", "tn"])).groupby(d[group_col]).mean()
        rows.append({"field": f, "errors": len(e), "commonest": common, "count": int(count),
                     "worst_group": f"{rate.idxmax()} ({rate.max():.0%})"})
    return pd.DataFrame(rows)
    # END SOLUTION


errors = pd.DataFrame(U.attempt(lambda: top_errors().to_dict(orient="records"), "d4_top_errors"))
print(errors.to_string(index=False))
for f in ("inspection_date", "hazard_to_public"):
    bad = long[(long.field == f) & (long.outcome == "wrong")].head(2)
    for _, b in bad.iterrows():
        print(f"\n{f}: reference {b.ref}, extracted {b.got}\n  {texts.loc[b.id, 'text'][:170]}")

# %% [markdown]
# 🔍 **Look at** the date errors. Which dates can be swapped at all? Why does the date style matter more than the
# language?

# %% [markdown]
# ## 5 · The validation report (4')
#
# ✏️ **Exercise** · For each field write one line: precision, recall, the commonest error, and the **rule** that would
# catch it before the table reaches Khalaf (a check against the text, a list of name variants, a second reading).
# The report is saved to `artifacts/day4/validation_report.md`.

# %%
def report() -> str:
    # BEGIN SOLUTION
    rules = {
        "district": "accept every spelling variant of each name (Al X, Al-X, X, حي X) in a list kept with the schema",
        "inspection_date": "parse dd/mm/yyyy in code, day first, and use the model's date only for dates in words",
        "defect_type": "add the pothole and pavement definitions to the prompt; review the pairs that swap",
        "severity": "map the four severity words of each language in code; flag a mismatch with the text",
        "hazard_to_public": "check for the negated phrase (no risk / لا يوجد خطر) and override to false",
        "repair_deadline_days": "keep a deadline only when the number of days is written in the text (Lab 4.1)",
    }
    s = per_field.set_index("field")
    e = errors.set_index("field")
    lines = ["# Validation report: extraction prompt extract_v1", "",
             "Recorded run over 500 synthetic inspection reports, scored against the reference extractions.", "",
             "| Field | Precision | Recall | Commonest error | Rule |", "|---|---|---|---|---|"]
    for f in U.FIELDS:
        common = f"{e.loc[f, 'commonest']} ({e.loc[f, 'count']})" if f in e.index else "none"
        lines.append(f"| {f} | {s.loc[f, 'precision']} | {s.loc[f, 'recall']} | {common} | {rules[f]} |")
    return "\n".join(lines) + "\n"
    # END SOLUTION


try:
    text = report()
except NotImplementedError:
    text = "# Validation report\n\n(write it in report())\n"
(OUT / "validation_report.md").write_text(text, encoding="utf-8")
print(text)
weakest = per_field.set_index("field").precision.idxmin()
U.check(weakest in ("repair_deadline_days", "hazard_to_public"), f"the weakest precision is on {weakest}")

# %% [markdown]
# ## ✱ Stretch · An interval for the deadline's precision
#
# The precision of `repair_deadline_days` comes from a few hundred values. Bootstrap the reports (2,000 times) and
# give its 95% interval.

# %%
def stretch():
    # BEGIN SOLUTION
    d = long[(long.field == "repair_deadline_days") & long.outcome.isin(["tp", "wrong", "invented"])]
    ok = (d.outcome == "tp").to_numpy()
    rng = np.random.default_rng(306)
    stats = [ok[rng.integers(0, len(ok), len(ok))].mean() for _ in range(U.pick(2000, 300))]
    print(f"deadline precision {ok.mean():.3f} [{np.percentile(stats, 2.5):.3f}, {np.percentile(stats, 97.5):.3f}] on {len(ok)} values")
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. Why is an invented value a precision error and not a recall error?
# 2. The pooled accuracy over all fields is high. Why report each field separately?
# 3. Which of the six rules in the report does not need a model at all?
#
# <details><summary>Answers</summary>
#
# 1. Precision asks whether the values given are right; an invented value is a value given where none exists. Recall
#    asks whether stated values were found.
# 2. Each field feeds a different decision; the deadline field drives the repair schedule, and the pooled figure
#    hides its weakness behind the easy fields.
# 3. Most of them: date parsing, the name variants, the severity words, the negation check and the grounding of the
#    deadline are plain code. The model is left with what code cannot read.
# </details>
#
# **Carry forward.** `artifacts/day4/validation_report.md`.
