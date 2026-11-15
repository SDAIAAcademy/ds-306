# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scikit-learn>=1.6", "python-dotenv>=1.0", "openai>=1.60", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 3.4 · A good annotator?
#
# Day 3 · Session 4 (Is the model a good annotator) · 25 min.
#
# Sumayah Al-Dakhil's team codes every complaint of the monthly sample twice. Dr. Ebtisam asks whether Fahim can
# replace the second coder. You write the criteria **before** looking at the results, apply them to agreement,
# stability and the dialect gap, and draft the reliability memo that answers her.
#
# **AI policy: models are measured here; the memo is yours.**
#
# **Reference state.** `data/gold.csv` (two coders and the adjudicated label) and `data/model_runs_gold.csv`
# (recorded; synthetic). Nothing from earlier labs.
#
# **Tasks**
# - [ ] 1 · Agreement between the two human coders (4')
# - [ ] 2 · Fahim against each coder and the gold label (6')
# - [ ] 3 · Write the criteria before looking (4')
# - [ ] 4 · Apply them: agreement, stability, gaps (6')
# - [ ] 5 · Draft the reliability memo (5')
# - [ ] ✱ Stretch · Leave one coder out: how often does Fahim agree with the other coder as often as a human does?

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

import json

import pandas as pd
import sada as U

U.banner("Lab 3.4")
OUT = U.lab_dir("day3")
gold = U.gold()
runs = U.runs_gold()
w = runs.pivot_table(index="id", columns=["prompt", "run"], values="label", aggfunc="first")
w.columns = [f"{p}_r{r}" for p, r in w.columns]
w = gold.set_index("id").join(w)

# %% [markdown]
# ## 1 · Agreement between the two human coders (4')
#
# The bar is not perfection: it is what a second person adds. ✏️ **Exercise** · Kappa between `coder_a` and
# `coder_b`, overall and by variety.

# %%
def human_bar() -> dict:
    # BEGIN SOLUTION
    out = {"all": round(U.kappa(w.coder_a, w.coder_b), 3)}
    out.update({v: round(U.kappa(d.coder_a, d.coder_b), 3) for v, d in w.groupby("variety")})
    return out
    # END SOLUTION


humans = U.attempt(human_bar, "d3_humans")
print("human pair kappa:", humans)

# %% [markdown]
# ## 2 · Fahim against each coder and the gold label (6')
#
# ✏️ **Exercise** · Kappa of Fahim (prompt 1, run 1) against coder A, coder B and the adjudicated gold label,
# overall and by variety.

# %%
def model_vs() -> pd.DataFrame:
    # BEGIN SOLUTION
    rows = []
    for v, d in [("all", w)] + list(w.groupby("variety")):
        rows.append({"variety": v, "vs_coder_a": round(U.kappa(d.P1_r1, d.coder_a), 3),
                     "vs_coder_b": round(U.kappa(d.P1_r1, d.coder_b), 3), "vs_gold": round(U.kappa(d.P1_r1, d.gold), 3)})
    return pd.DataFrame(rows)
    # END SOLUTION


mv = pd.DataFrame(U.attempt(lambda: model_vs().to_dict(orient="records"), "d3_model_vs"))
print(mv.to_string(index=False))

# %% [markdown]
# ## 3 · Write the criteria before looking (4')
#
# Write the bar now, in the cell below, before task 4 prints a verdict. A criterion written after the results is a
# description of the results. The solution's criteria are one defensible set; yours may differ if you can say why.
#
# ✏️ **Exercise** · Fill `CRITERIA`: the largest allowed shortfall of Fahim's kappa (against the gold label) below
# the human pair's kappa, in every variety; the smallest share of complaints whose three runs agree; the largest
# allowed accuracy gap between varieties.

# %%
def criteria() -> dict:
    # BEGIN SOLUTION
    return {"max_kappa_shortfall": 0.05, "min_three_run_agreement": 0.90, "max_accuracy_gap": 0.05}
    # END SOLUTION


try:
    CRITERIA = criteria()
except NotImplementedError:
    CRITERIA = {"max_kappa_shortfall": 0.05, "min_three_run_agreement": 0.90, "max_accuracy_gap": 0.05}
    print("↩️  Using the course's criteria.")
print(CRITERIA)

# %% [markdown]
# ## 4 · Apply them: agreement, stability, gaps (6')
#
# ✏️ **Exercise** · Compute each measure and whether it passes.

# %%
def apply_criteria() -> list[dict]:
    # BEGIN SOLUTION
    rows = []
    for v in U.VARIETIES:
        d = w[w.variety == v]
        short = humans[v] - U.kappa(d.P1_r1, d.gold)
        rows.append({"test": f"kappa shortfall, {v}", "value": round(short, 3), "pass": short <= CRITERIA["max_kappa_shortfall"]})
    agree3 = float(((w.P1_r1 == w.P1_r2) & (w.P1_r1 == w.P1_r3)).mean())
    rows.append({"test": "three runs agree", "value": round(agree3, 3), "pass": agree3 >= CRITERIA["min_three_run_agreement"]})
    acc = {v: U.accuracy(d.gold, d.P1_r1) for v, d in w.groupby("variety")}
    gap = max(acc.values()) - min(acc.values())
    rows.append({"test": "accuracy gap between varieties", "value": round(gap, 3), "pass": gap <= CRITERIA["max_accuracy_gap"]})
    return rows
    # END SOLUTION


results = pd.DataFrame(U.attempt(apply_criteria, "d3_criteria_results"))
print(results.to_string(index=False))
replace_ok = bool(results["pass"].all())
print("Fahim can replace the second coder:", replace_ok)

# %% [markdown]
# ## 5 · Draft the reliability memo (5')
#
# ✏️ **Exercise** · Write the memo for Dr. Ebtisam in five short paragraphs: the question; the evidence
# (agreement, stability, gaps, each with its number); the decision; what the labels **can** still be used for, and
# with what safeguard; the limits (synthetic recorded runs, the size of each group). It is saved to
# `artifacts/day3/reliability_memo.md` and is the draft of the LO5 evidence.

# %%
def memo() -> str:
    # BEGIN SOLUTION
    r = results.set_index("test")
    return "\n\n".join([
        "# Reliability memo: Fahim as a second coder",
        "**Question.** Can Fahim (prompt 1, model and settings in the version record) replace the second human coder "
        "of the monthly sample, and can its labels feed the district complaint rates?",
        f"**Evidence.** On the 300-complaint gold set the two coders reach kappa {humans['all']}; Fahim reaches "
        f"{mv.iloc[0].vs_gold} against the adjudicated label. The shortfall is {r.loc['kappa shortfall, msa', 'value']} "
        f"on formal Arabic, {r.loc['kappa shortfall, gulf', 'value']} on Gulf dialect and "
        f"{r.loc['kappa shortfall, en', 'value']} on English. Its three runs agree on "
        f"{r.loc['three runs agree', 'value']:.0%} of complaints; the accuracy gap between varieties is "
        f"{r.loc['accuracy gap between varieties', 'value']}.",
        "**Decision.** Not as a replacement for the second coder: it fails the criteria set in advance on Gulf "
        "dialect and on stability.",
        "**What the labels can do.** Label all complaints for the monthly counts, provided each count is corrected "
        "with the human gold sample, stratified by variety, and reported with its interval (Lab 4.4).",
        "**Limits.** The model runs in this course are synthetic recordings; the English group has 66 gold "
        "complaints and wide intervals; prompt and model versions must be kept with every label set and the test "
        "repeated when either changes.",
    ])
    # END SOLUTION


try:
    text = memo()
except NotImplementedError:
    text = "# Reliability memo\n\n(write your memo in memo())"
(OUT / "reliability_memo.md").write_text(text, encoding="utf-8")
print(text)
U.check(not replace_ok, "the criteria reject Fahim as a second coder")

# %% [markdown]
# ## ✱ Stretch · Leave one coder out
#
# The alternative annotator test (Calderon, Reichart and Dror, 2025) asks whether the model agrees with the
# remaining annotators at least as often as the annotator it would replace. With two coders: does Fahim agree with
# coder B as often as coder A does, and with coder A as often as coder B does?

# %%
def stretch():
    # BEGIN SOLUTION
    for left_out, other in (("coder_a", "coder_b"), ("coder_b", "coder_a")):
        human = (w[left_out] == w[other]).mean()
        model = (w.P1_r1 == w[other]).mean()
        print(f"replace {left_out}: human agrees with {other} on {human:.3f}, Fahim on {model:.3f}")
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. Why compare Fahim with the human pair instead of with a fixed bar such as kappa 0.8?
# 2. Fahim fails as a second coder. Why can its labels still feed an estimate?
# 3. What must be done again when the model behind the endpoint changes?
#
# <details><summary>Answers</summary>
#
# 1. The task's own difficulty sets what is achievable: the human pair shows what a second careful reader adds on
#    these complaints.
# 2. An estimate can be corrected with a human sample; a per-complaint decision cannot. Day 4 does the correction.
# 3. The whole test: agreement, stability and gaps on the gold set, with a new version record.
# </details>
