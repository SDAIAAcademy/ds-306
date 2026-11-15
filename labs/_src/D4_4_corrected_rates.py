# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "python-dotenv>=1.0", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 4.4 · Corrected rates
#
# Day 4 · Session 4 (Errors downstream) · 25 min.
#
# Dr. Ebtisam publishes one number per district each quarter: water and sewage complaints per 10,000 residents.
# Fahim labels every complaint, and Day 3 showed that it misses more sewage complaints written in Gulf dialect. You
# compute the naive rate from the model's labels, correct it with the human gold set **stratified by language
# variety**, put an interval on it, and see which districts move. Then you choose your capstone corpus.
#
# **AI policy: models are measured here; the estimate and its defence are yours.**
#
# **Reference state.** `data/model_labels_all.csv.gz` (Fahim's labels for all 20,000 complaints; recorded,
# synthetic), `data/gold.csv`, `data/districts.csv`, `data/complaints.csv.gz` and the keep flags of Lab 1.3
# (`data/reference/d1_keep.json`). Nothing else from earlier labs.
#
# **Tasks**
# - [ ] 1 · Naive rates per district from model labels (5')
# - [ ] 2 · The correction from the gold set, by language (6')
# - [ ] 3 · Corrected rates per district (6')
# - [ ] 4 · Bootstrap intervals (5')
# - [ ] 5 · Choose the capstone corpus (3')
# - [ ] ✱ Stretch · What does the campaign do to Al-Naseem's rate, with and without it?

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
from datetime import date

import numpy as np
import pandas as pd
import sada as U

U.banner("Lab 4.4")
OUT = U.lab_dir("day4")
TARGET = "water_sewage"
pop = U.districts().set_index("district").population
c = U.complaints()[["id", "district", "text"]]
flags = pd.DataFrame(U.reference("d1_keep"))
c = c.merge(flags, on="id", how="left").fillna({"keep": True, "campaign": False})
c = c.merge(U.labels_all()[["id", "label"]], on="id")
c["variety"] = c.text.map(U.guess_variety)  # the instrument measured in Lab 3.3
counted = c[c.keep & ~c.campaign]
print(f"{len(c)} complaints; {len(counted)} counted (copies removed, the campaign set aside as one issue)")

# %% [markdown]
# ## 1 · Naive rates per district from model labels (5')
#
# ✏️ **Exercise** · For each district: the number of complaints Fahim labels `water_sewage` among those counted, and
# the rate per 10,000 residents.

# %%
def naive() -> pd.DataFrame:
    # BEGIN SOLUTION
    n = counted[counted.label == TARGET].groupby("district").size().reindex(pop.index, fill_value=0)
    return pd.DataFrame({"district": pop.index, "naive_count": n.to_numpy(), "naive_rate": (n / pop * 10000).round(1).to_numpy()})
    # END SOLUTION


rates = pd.DataFrame(U.attempt(lambda: naive().to_dict(orient="records"), "d4_naive")).set_index("district")
print(rates.sort_values("naive_rate", ascending=False).to_string())

# %% [markdown]
# ## 2 · The correction from the gold set, by language (6')
#
# On the 300 gold complaints we know both Fahim's label and the right one. For an indicator ("is it water and
# sewage?") the model's share is off by the mean of (model − truth): that is the **rectifier** of prediction-powered
# inference (Angelopoulos and others, 2023). Day 3 showed the error differs by variety, so estimate one rectifier
# per variety, with the variety **guessed** on the gold set exactly as on the corpus.
#
# ✏️ **Exercise** · For each guessed variety: n, the model's share, the true share, and the rectifier
# `delta = mean(model) − mean(truth)`. Also the single rectifier for all varieties together.

# %%
g = U.gold()[["id", "text", "gold"]].merge(U.labels_all()[["id", "label"]], on="id")
g["variety"] = g.text.map(U.guess_variety)
g["f"] = (g.label == TARGET).astype(int)
g["y"] = (g.gold == TARGET).astype(int)


def rectifiers(gs: pd.DataFrame) -> dict:
    # BEGIN SOLUTION
    out = {v: float(d.f.mean() - d.y.mean()) for v, d in gs.groupby("variety")}
    out["all"] = float(gs.f.mean() - gs.y.mean())
    return out
    # END SOLUTION


try:
    delta = rectifiers(g)
except NotImplementedError:
    print("↩️  Exercise not done yet: using the reference rectifiers.")
    delta = {v: float(d.f.mean() - d.y.mean()) for v, d in g.groupby("variety")} | {"all": float(g.f.mean() - g.y.mean())}
print(g.groupby("variety").agg(n=("f", "size"), model=("f", "mean"), truth=("y", "mean")).round(3).to_string())
print("rectifiers:", {k: round(v, 3) for k, v in delta.items()})
U.keep("d4_delta", {k: round(v, 4) for k, v in delta.items()})

# %% [markdown]
# 🔍 **Look at** the sign of each rectifier. Negative means the model labels fewer complaints `water_sewage` than
# there are: it under-counts. Which variety under-counts most?

# %% [markdown]
# ## 3 · Corrected rates per district (6')
#
# ✏️ **Exercise** · For each district, the corrected count is, summed over varieties, the model's count minus the
# district's number of complaints in that variety times the variety's rectifier. Compute it with the stratified
# rectifiers and, for comparison, with the single one. Which districts move most, and in which direction?

# %%
cells = counted.assign(f=(counted.label == TARGET).astype(int)).groupby(["district", "variety"]).f.agg(["sum", "size"])


def corrected(d: dict) -> pd.Series:
    # BEGIN SOLUTION
    adj = cells["sum"] - cells["size"] * cells.index.get_level_values("variety").map(d).to_numpy()
    return adj.groupby("district").sum().reindex(pop.index)
    # END SOLUTION


try:
    strat = corrected(delta)
    single = corrected({v: delta["all"] for v in U.VARIETIES})
except NotImplementedError:
    strat = single = rates.naive_count.astype(float)
rates["corrected_rate"] = (strat / pop * 10000).round(1)
rates["single_rect_rate"] = (single / pop * 10000).round(1)
rates["gulf_share"] = counted.groupby("district").variety.apply(lambda s: (s == "gulf").mean()).round(3)
rates["change"] = (rates.corrected_rate - rates.naive_rate).round(1)
print(rates.sort_values("gulf_share", ascending=False).to_string())

# %% [markdown]
# ## 4 · Bootstrap intervals (5')
#
# The 20,000 complaints are all the complaints received, a census, so the counts carry no sampling error. The
# correction does: it comes from 300 complaints. ✏️ **Exercise** · Resample the gold set **within each variety**
# 2,000 times, recompute the rectifiers and the corrected rates, and give the 95% interval of each district's rate.
# Does the gap between Al-Naseem and Al-Khalij survive?

# %%
def intervals(n: int, seed: int = 306) -> pd.DataFrame:
    # BEGIN SOLUTION
    rng = np.random.default_rng(seed)
    parts = {v: d for v, d in g.groupby("variety")}
    sims = []
    for _ in range(n):
        d = {v: float((p.f.to_numpy() - p.y.to_numpy())[rng.integers(0, len(p), len(p))].mean()) for v, p in parts.items()}
        sims.append(corrected(d) / pop * 10000)
    sims = pd.DataFrame(sims)
    return pd.DataFrame({"low": sims.quantile(0.025), "high": sims.quantile(0.975)}).round(1)
    # END SOLUTION


try:
    ci = intervals(U.pick(2000, 300))
except NotImplementedError:
    ci = pd.DataFrame({"low": np.nan, "high": np.nan}, index=pop.index)
rates = rates.join(ci)
show = rates[["naive_rate", "corrected_rate", "low", "high", "gulf_share"]].sort_values("corrected_rate", ascending=False)
print(show.to_string())
U.keep("d4_rates", rates.reset_index().to_dict(orient="records"))

# %% [markdown]
# ### Only in a course: the truth
#
# The corpus is synthetic, so the true category of every complaint exists (`solutions/truth/`, the trainer's file).
# In a real project this cell cannot be written: the gold set **is** the only access to the truth.

# %%
truth_file = Path("solutions/truth/complaints_truth.csv.gz")
if truth_file.exists():
    t = counted[["id", "district"]].merge(pd.read_csv(truth_file)[["id", "category"]], on="id")
    true_rate = (t[t.category == TARGET].groupby("district").size().reindex(pop.index) / pop * 10000).round(1)
    cmp = rates[["naive_rate", "corrected_rate", "low", "high"]].assign(true_rate=true_rate)
    cmp["covered"] = (cmp.true_rate >= cmp.low) & (cmp.true_rate <= cmp.high)
    print(cmp.sort_values("true_rate", ascending=False).to_string())
    print(f"\nmean absolute error: naive {abs(cmp.naive_rate - cmp.true_rate).mean():.1f}, corrected "
          f"{abs(cmp.corrected_rate - cmp.true_rate).mean():.1f} per 10,000 | intervals covering the truth: {int(cmp.covered.sum())} of 12")
    gap = {k: round(float(cmp.loc["al_naseem", k] - cmp.loc["al_khalij", k]), 1) for k in ("naive_rate", "corrected_rate", "true_rate")}
    print("Al-Naseem minus Al-Khalij:", gap)
    U.keep("d4_truth_check", {"mae_naive": round(abs(cmp.naive_rate - cmp.true_rate).mean(), 1),
                              "mae_corrected": round(abs(cmp.corrected_rate - cmp.true_rate).mean(), 1),
                              "covered": int(cmp.covered.sum()), "gap": gap})

# %% [markdown]
# 🔍 **Look at** the two errors. The correction barely lowers the average error: its rectifiers come from 300
# complaints and carry their own noise. What it fixes is the **comparison**: the naive gap between the most and the
# least Gulf-speaking districts is too small, the corrected gap is close to the true one. The director compares
# districts.

# %% [markdown]
# ## 5 · Choose the capstone corpus (3')
#
# Read the two briefs in `data/capstone/` (Nadwa libraries, Raafid social support). Each has documents with personal
# data, a 200-document gold set with two coders, recorded model runs and a director's question. A public corpus is
# possible with the trainer's approval. ✏️ **Exercise** · Fill your choice: the corpus, the question in one sentence,
# and the measurement choice you expect to defend hardest.

# %%
for k in ("nadwa", "raafid"):
    print((U.DATA / "capstone" / k / "brief.md").read_text(encoding="utf-8").split("\n\n")[1], "\n")


def choice() -> dict:
    # BEGIN SOLUTION
    return {"corpus": "nadwa", "question": "Facilities feedback share per branch, corrected for the model's errors by variety",
            "hardest_choice": "whether 200 gold documents are enough to correct six branches"}
    # END SOLUTION


try:
    mine = choice()
except NotImplementedError:
    mine = {"corpus": "(to choose)", "question": "", "hardest_choice": ""}
VERSION = {"labels": "model_labels_all.csv.gz (Fahim P1 run 1, recorded, synthetic)", "gold": "gold.csv (300)",
           "variety": "U.guess_variety", "target": TARGET, "date": date.today().isoformat()}
(OUT / "capstone_choice.json").write_text(json.dumps({**mine, "rates_version": VERSION}, indent=1), encoding="utf-8")
print(mine)

# %% [markdown]
# ## ✱ Stretch · The campaign and Al-Naseem
#
# Lab 1.3 set 576 campaign messages aside as one issue. Recompute Al-Naseem's naive and corrected rates with them
# counted as separate complaints. How much of the published rate would one organised campaign be?

# %%
def stretch():
    # BEGIN SOLUTION
    with_c = c[c.keep]
    cells_c = with_c.assign(f=(with_c.label == TARGET).astype(int)).groupby(["district", "variety"]).f.agg(["sum", "size"])
    adj = cells_c["sum"] - cells_c["size"] * cells_c.index.get_level_values("variety").map(delta).to_numpy()
    n = adj.groupby("district").sum()
    naive_c = with_c[with_c.label == TARGET].groupby("district").size()
    p = pop["al_naseem"]
    print(f"Al-Naseem, campaign as one issue: naive {rates.loc['al_naseem', 'naive_rate']}, corrected "
          f"{rates.loc['al_naseem', 'corrected_rate']} | campaign counted: naive {naive_c['al_naseem'] / p * 10000:.1f}, "
          f"corrected {n['al_naseem'] / p * 10000:.1f} per 10,000")
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. Why are the rectifiers estimated with the **guessed** variety on the gold set, not the coders' variety?
# 2. The corrected rate has an interval and the naive one does not. Is the naive rate more precise?
# 3. What does the correction assume about the districts?
#
# <details><summary>Answers</summary>
#
# 1. The corpus is stratified by the guess; the rectifier must describe the same strata, guessing errors included.
# 2. No: it is precisely wrong. Its error is a bias the interval-free number hides; the correction trades the bias
#    for a variance you can see.
# 3. That within a variety, Fahim errs at the same rate in every district. A district with its own vocabulary would
#    break it; a larger gold set stratified by district too would test it.
# </details>
#
# **Carry forward.** `artifacts/day4/capstone_choice.json`, and the corrected rates for the capstone's method.
