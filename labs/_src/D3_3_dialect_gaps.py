# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scikit-learn>=1.6", "python-dotenv>=1.0", "openai>=1.60", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 3.3 · Dialect gaps
#
# Day 3 · Session 3 (Dialect gaps) · 25 min.
#
# An average hides groups. You measure Fahim's agreement with the gold set separately for Modern Standard Arabic,
# Gulf dialect and English, find the confusion behind the gap, and estimate what the gap does to a count in districts
# where most residents write in Gulf dialect.
#
# **AI policy: models are measured here.**
#
# **Reference state.** `data/gold.csv` (with the coders' variety), `data/model_runs_gold.csv` (recorded; synthetic),
# `data/model_labels_all.csv.gz` and `data/complaints.csv.gz`. Nothing from Labs 3.1 or 3.2.
#
# **Tasks**
# - [ ] 1 · Agreement by variety with intervals (7')
# - [ ] 2 · The confusion table of Gulf complaints (6')
# - [ ] 3 · The gap with a bootstrap interval (6')
# - [ ] 4 · What the gap does to a count (6')
# - [ ] ✱ Stretch · Does the reworded prompt narrow the gap?

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

import numpy as np
import pandas as pd
import sada as U

U.banner("Lab 3.3")
gold = U.gold()
runs = U.runs_gold()
m = runs[(runs.prompt == "P1") & (runs.run == 1)].merge(gold, on="id")
print(len(m), "gold complaints with Fahim's prompt-1 label (the run used for all complaints)")

# %% [markdown]
# ## 1 · Agreement by variety with intervals (7')
#
# ✏️ **Exercise** · For each variety: n, accuracy with its bootstrap interval, and kappa against the gold label.
# Put the human pair's kappa in the same variety next to it.

# %%
def by_variety() -> pd.DataFrame:
    # BEGIN SOLUTION
    ci = U.boot_ci(m.gold, m.label, U.accuracy, groups=m.variety).set_index("group")
    rows = []
    for v in U.VARIETIES:
        d = m[m.variety == v]
        rows.append({"variety": v, "n": len(d), "accuracy": ci.loc[v, "value"], "low": ci.loc[v, "low"],
                     "high": ci.loc[v, "high"], "kappa_model": round(U.kappa(d.label, d.gold), 3),
                     "kappa_humans": round(U.kappa(d.coder_a, d.coder_b), 3)})
    return pd.DataFrame(rows)
    # END SOLUTION


table = pd.DataFrame(U.attempt(lambda: by_variety().to_dict(orient="records"), "d3_by_variety"))
print(table.to_string(index=False))
U.check(table.set_index("variety").loc["gulf", "accuracy"] < table.set_index("variety").loc["msa", "accuracy"],
        "Gulf complaints score lower")

# %% [markdown]
# ## 2 · The confusion table of Gulf complaints (6')
#
# ✏️ **Exercise** · Cross-tabulate the gold label against Fahim's label for Gulf complaints only. Find the largest
# off-diagonal cell and read two of its complaints. What do they say, and what does Fahim call them?

# %%
gulf = m[m.variety == "gulf"]
confusion = pd.crosstab(gulf.gold, gulf.label)
print(confusion.to_string())


def biggest_confusion() -> dict:
    # BEGIN SOLUTION
    off = confusion.copy()
    for c in off.columns:
        if c in off.index:
            off.loc[c, c] = 0
    g, p = off.stack().idxmax()
    return {"gold": g, "model": p, "count": int(off.loc[g, p])}
    # END SOLUTION


top = U.attempt(biggest_confusion, "d3_top_confusion")
print(top)
for t in gulf[(gulf.gold == top["gold"]) & (gulf.label == top["model"])].text.head(2):
    print("  ·", t[:150])

# %% [markdown]
# 🔍 **Look at** the words in those complaints. Is there a word a Gulf speaker uses for water that Fahim may read as
# rain on a road?

# %% [markdown]
# ## 3 · The gap with a bootstrap interval (6')
#
# ✏️ **Exercise** · The gap is accuracy on Modern Standard Arabic minus accuracy on Gulf. Bootstrap it by resampling
# **within each group** (the two groups hold different complaints, so there is nothing to pair), 2,000 times.

# %%
def gap_ci(a: np.ndarray, b: np.ndarray, n: int, seed: int = 306) -> tuple[float, float, float]:
    # BEGIN SOLUTION
    rng = np.random.default_rng(seed)
    diffs = [a[rng.integers(0, len(a), len(a))].mean() - b[rng.integers(0, len(b), len(b))].mean() for _ in range(n)]
    return float(a.mean() - b.mean()), float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))
    # END SOLUTION


ok = (m.label == m.gold).astype(int)
a, b = ok[m.variety == "msa"].to_numpy(), ok[m.variety == "gulf"].to_numpy()
try:
    gap = gap_ci(a, b, U.pick(2000, 300))
except NotImplementedError:
    gap = (float(a.mean() - b.mean()), float("nan"), float("nan"))
print(f"MSA minus Gulf: {gap[0]:+.3f} [{gap[1]:+.3f}, {gap[2]:+.3f}]")
U.keep("d3_gap", {"estimate": round(gap[0], 3), "low": round(gap[1], 3), "high": round(gap[2], 3)})

# %% [markdown]
# ## 4 · What the gap does to a count (6')
#
# For the whole corpus nobody coded the variety, so first an instrument for it: `U.guess_variety` (English by
# script; Gulf when a Gulf marker word appears). ✏️ **Exercise** ·
#
# 1. Measure the guess against the coders' variety on the gold set.
# 2. From the gold set, Fahim's **recall** of water and sewage by variety: of the gold `water_sewage` complaints,
#    the share Fahim labels `water_sewage`.
# 3. For each district, the expected recall: the guessed variety mix of its complaints times the recall of each
#    variety. Which districts lose most?

# %%
c = U.complaints()
if U.QUICK:
    c = c.sample(5000, random_state=306)
c["variety"] = c.text.map(U.guess_variety)
gold_guess = gold.text.map(U.guess_variety)
print(f"variety guess agrees with the coders on {np.mean(gold_guess == gold.variety):.1%} of gold complaints")
print(pd.crosstab(gold.variety, gold_guess, rownames=["coders"], colnames=["guess"]))


def expected_recall() -> pd.DataFrame:
    # BEGIN SOLUTION
    ws = m[m.gold == "water_sewage"]
    recall = ws.groupby("variety").apply(lambda d: (d.label == "water_sewage").mean(), include_groups=False)
    mix = pd.crosstab(c.district, c.variety, normalize="index")
    out = (mix * recall).sum(axis=1).rename("expected_recall").to_frame()
    out["gulf_share"] = mix["gulf"]
    return out.sort_values("expected_recall").round(3).reset_index()
    # END SOLUTION


try:
    er = expected_recall()
except NotImplementedError:
    er = pd.DataFrame(U.reference("d3_expected_recall"))
U.keep("d3_expected_recall", er.to_dict(orient="records"))
print(er.to_string(index=False))

# %% [markdown]
# ## ✱ Stretch · Does the reworded prompt narrow the gap?
#
# Repeat task 3 with prompt 2, run 1. Does the gap close, and is the change larger than the interval?

# %%
def stretch():
    # BEGIN SOLUTION
    m2 = runs[(runs.prompt == "P2") & (runs.run == 1)].merge(gold, on="id")
    ok2 = (m2.label == m2.gold).astype(int)
    g2 = gap_ci(ok2[m2.variety == "msa"].to_numpy(), ok2[m2.variety == "gulf"].to_numpy(), U.pick(2000, 300))
    print(f"prompt 2, MSA minus Gulf: {g2[0]:+.3f} [{g2[1]:+.3f}, {g2[2]:+.3f}] against prompt 1 {gap[0]:+.3f}")
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. Fahim's overall accuracy is fine for the director. Why is that not enough?
# 2. The variety guess is itself an instrument. What error does it add to task 4?
# 3. Which SDAIA reference names the bias that a gap like this carries into an estimate?
#
# <details><summary>Answers</summary>
#
# 1. The average mixes groups; the Gulf group is weaker, and its districts get under-counted.
# 2. Gulf complaints guessed as MSA (about one in ten in the gold set) get MSA's recall; the expected recall of
#    Gulf-heavy districts is then slightly too high, so the true loss is a little larger.
# 3. The AI Bias Reference Guide (measurement bias: values systematically over- or under-estimated).
# </details>
#
# **Carry forward.** Lab 4.4 corrects the district rates for exactly this gap.
