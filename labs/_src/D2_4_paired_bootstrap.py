# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scikit-learn>=1.6", "python-dotenv>=1.0", "openai>=1.60", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 2.4 · Compare classifiers fairly
#
# Day 2 · Session 4 (Comparing classifiers fairly) · 25 min.
#
# Two classifiers were scored on the same 300 gold complaints. That makes every complaint a pair of results, and the
# question "which is better?" a question about 300 paired differences. You put a paired bootstrap interval on the
# difference, overall and by language, and write the decision with its cost.
#
# **AI policy: AI-tutor.**
#
# **Reference state.** The predictions of Labs 2.2 and 2.3 from `artifacts/day2/`, or the course's reference
# predictions when they are missing.
#
# **Tasks**
# - [ ] 1 · Load both classifiers' predictions on the gold set (4')
# - [ ] 2 · Paired differences per document (5')
# - [ ] 3 · A paired bootstrap interval (7')
# - [ ] 4 · The same, by language (5')
# - [ ] 5 · The decision, with cost (4')
# - [ ] ✱ Stretch · An unpaired bootstrap of the same difference: how much wider is it?

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

U.banner("Lab 2.4")
OUT = U.lab_dir("day2")
gold = U.gold()

# %% [markdown]
# ## 1 · Load both classifiers' predictions (4')

# %%
def load(name: str) -> pd.DataFrame:
    path = OUT / f"pred_{name}.csv"
    if path.exists():
        return pd.read_csv(path)
    print(f"↩️  {path.name} not found: using the reference predictions.")
    ref = U.reference(f"d2_pred_{name}")
    return pd.DataFrame({"id": ref["id"], "pred": ref["pred"]})


d = gold[["id", "variety", "gold"]].merge(load("sparse"), on="id").merge(load("embed"), on="id", suffixes=("_sparse", "_embed"))
standin = U.reference("d2_pred_embed").get("standin", True) if not (OUT / "pred_embed.csv").exists() else None
print(len(d), "gold complaints with both predictions")
U.check(len(d) == 300, "all 300 paired")

# %% [markdown]
# ## 2 · Paired differences per document (5')
#
# ✏️ **Exercise** · Add `ok_sparse` and `ok_embed` (1 when right, 0 when wrong) and `diff = ok_sparse − ok_embed`.
# Count the complaints where only one of the two is right: they are the only ones that carry information about the
# difference.

# %%
def paired(d: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    d = d.assign(ok_sparse=(d.pred_sparse == d.gold).astype(int), ok_embed=(d.pred_embed == d.gold).astype(int))
    return d.assign(diff=d.ok_sparse - d.ok_embed)
    # END SOLUTION


try:
    d = paired(d)
except NotImplementedError:
    d = d.assign(ok_sparse=(d.pred_sparse == d.gold).astype(int), ok_embed=(d.pred_embed == d.gold).astype(int))
    d["diff"] = d.ok_sparse - d.ok_embed
print(pd.crosstab(d.ok_sparse, d.ok_embed, rownames=["sparse right"], colnames=["embedding right"]))
print(f"accuracy: sparse {d.ok_sparse.mean():.3f}, embedding {d.ok_embed.mean():.3f}, difference {d['diff'].mean():+.3f}")

# %% [markdown]
# ## 3 · A paired bootstrap interval (7')
#
# ✏️ **Exercise** · Resample the 300 complaints with replacement 2,000 times, **keeping each complaint's pair
# together**, and take the 2.5th and 97.5th percentiles of the mean difference.

# %%
def paired_ci(diff: np.ndarray, n: int, seed: int = 306) -> tuple[float, float, float]:
    # BEGIN SOLUTION
    rng = np.random.default_rng(seed)
    means = [diff[rng.integers(0, len(diff), len(diff))].mean() for _ in range(n)]
    return float(diff.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))
    # END SOLUTION


N = U.pick(2000, 300)
try:
    est, lo, hi = paired_ci(d["diff"].to_numpy(), N)
except NotImplementedError:
    rng = np.random.default_rng(306)
    x = d["diff"].to_numpy()
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(N)]
    est, lo, hi = float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))
print(f"sparse minus embedding: {est:+.3f} [{lo:+.3f}, {hi:+.3f}]")
U.check(lo <= est <= hi, "the estimate sits inside its interval")

# %% [markdown]
# ## 4 · The same, by language (5')
#
# ✏️ **Exercise** · Repeat the paired interval inside each variety. Where is the difference clear, and where can
# the gold set not tell the two apart?

# %%
def by_language() -> list[dict]:
    # BEGIN SOLUTION
    rows = []
    for v, g in d.groupby("variety"):
        e, l, h = paired_ci(g["diff"].to_numpy(), N)
        rows.append({"variety": v, "n": len(g), "difference": round(e, 3), "low": round(l, 3), "high": round(h, 3)})
    return rows
    # END SOLUTION


langs = pd.DataFrame(U.attempt(by_language, "d2_paired_by_language"))
print(langs.to_string(index=False))

# %% [markdown]
# ## 5 · The decision, with cost (4')
#
# ✏️ **Exercise** · Write the decision in two sentences in `decision()`: which classifier the centre should use for
# routing, on what evidence, and what the other one costs that this one does not. If the embedding vectors came
# from the stand-in, the decision is about the method only, and the sentence must say so.

# %%
def decision() -> str:
    # BEGIN SOLUTION
    return (f"Keep the character n-gram classifier: on the same 300 gold complaints its accuracy differs by {est:+.3f} "
            f"from the embedding classifier [{lo:+.3f}, {hi:+.3f}], and no variety favours the embeddings clearly. "
            "It also runs on a laptop in seconds, sends no text out and has no request limit; the embedding run "
            "needs requests to a third party (and, here, the scores came from stand-in vectors, so the comparison "
            "must be rerun with the hosted model before it is final).")
    # END SOLUTION


try:
    DECISION = decision()
except NotImplementedError:
    DECISION = ""
print(DECISION or "Write your decision in decision().")
(OUT / "decision.txt").write_text(DECISION, encoding="utf-8")

# %% [markdown]
# ## ✱ Stretch · An unpaired bootstrap
#
# Resample the two columns **independently** and compute the interval of the difference again. How much wider is
# it, and why?

# %%
def stretch():
    # BEGIN SOLUTION
    rng = np.random.default_rng(306)
    a, b = d.ok_sparse.to_numpy(), d.ok_embed.to_numpy()
    m = [a[rng.integers(0, 300, 300)].mean() - b[rng.integers(0, 300, 300)].mean() for _ in range(N)]
    print(f"unpaired interval width {np.percentile(m, 97.5) - np.percentile(m, 2.5):.3f} against paired {hi - lo:.3f}")
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. Of the 300 complaints, which ones decide the comparison?
# 2. Why is the paired interval narrower than the unpaired one?
# 3. DS-204 paired folds. What is paired here?
#
# <details><summary>Answers</summary>
#
# 1. Those where exactly one classifier is right; when both are right or both wrong the difference is zero.
# 2. The complaints that are hard (or easy) for both cancel out in the difference; resampling them independently
#    adds their variation twice.
# 3. Documents: both classifiers labelled the same 300 complaints.
# </details>
