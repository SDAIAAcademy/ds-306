# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scikit-learn>=1.6", "python-dotenv>=1.0", "openai>=1.60", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 2.3 · An embedding classifier
#
# Day 2 · Session 3 (Embeddings as features) · 25 min.
#
# An embedding model turns each complaint into a vector of a few hundred to a few thousand numbers, placed so that
# texts with similar meaning sit close together. You fetch vectors from a free hosted embedding model within a
# budget of calls, train a logistic classifier on them, and score it per language with its cost.
#
# **AI policy: AI-tutor.**
#
# **Model access.** A free key in `labs/.env` (`OPENROUTER_API_KEY`) calls the hosted embedding model
# `nvidia/nemotron-3.5-embed-1b:free` by default. Without a working key, `U.embed` uses a **lexical stand-in**
# (hashed character n-grams): the cells run, but its scores say nothing about an embedding model. The banner tells
# you which one answered.
#
# **Reference state.** `data/pool.csv` and `data/gold.csv`. Nothing from Lab 2.2.
#
# **Tasks**
# - [ ] 1 · Embed the pool and the gold set within the budget (7')
# - [ ] 2 · A logistic head on the vectors (5')
# - [ ] 3 · Scores per language with intervals (7')
# - [ ] 4 · Calls, seconds and cost per thousand documents (6')
# - [ ] ✱ Stretch · Join the sparse and the embedding features: does the union beat both?

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

import time

import numpy as np
import pandas as pd
import sada as U
from sklearn.linear_model import LogisticRegression

U.banner("Lab 2.3")
OUT = U.lab_dir("day2")
pool, gold = U.pool(), U.gold()

# %% [markdown]
# ## 1 · Embed the pool and the gold set within the budget (7')
#
# The free tier allows 50 requests a day without credits and 20 a minute. One request carries up to 64 texts, and
# every vector is cached in `labs/cache/`, so a rerun costs nothing. **Budget: 25 requests.**
#
# ✏️ **Exercise** · Choose how many pool complaints you can embed within the budget together with the 300 gold
# complaints, take them as a stratified sample by routing label (`groupby(...).sample(frac=...)`), and embed both
# with `U.embed(texts)`.

# %%
BUDGET, BATCH = 25, 64


def plan_and_embed():
    # BEGIN SOLUTION
    n_pool = U.pick((BUDGET - -(-len(gold) // BATCH)) * BATCH, 400)  # 20 requests of 64 = 1,280; quick mode keeps it small
    frac = n_pool / len(pool)
    sample = pool.groupby("routing_label", group_keys=False).sample(frac=frac, random_state=306)
    t0 = time.perf_counter()
    X_s = U.embed(sample.text.tolist(), batch=BATCH)
    X_g = U.embed(gold.text.tolist(), batch=BATCH)
    return sample, X_s, X_g, time.perf_counter() - t0
    # END SOLUTION


try:
    sample, X_pool, X_gold, seconds = plan_and_embed()
except NotImplementedError:
    print("↩️  Exercise not done yet: embedding a reference sample of 1,280 pool complaints.")
    sample = pool.groupby("routing_label", group_keys=False).sample(frac=U.pick(1280, 400) / len(pool), random_state=306)
    t0 = time.perf_counter()
    X_pool, X_gold = U.embed(sample.text.tolist()), U.embed(gold.text.tolist())
    seconds = time.perf_counter() - t0
calls = U.CALLS["embed"]
print(f"{len(sample)} pool + {len(gold)} gold vectors of {X_pool.shape[1]} numbers | requests {calls} | {seconds:.1f} s")
U.check(calls <= BUDGET, f"within the budget of {BUDGET} requests")
STANDIN = U.standin()

# %% [markdown]
# ## 2 · A logistic head on the vectors (5')
#
# ✏️ **Exercise** · Train `LogisticRegression(max_iter=3000, C=10)` on the pool vectors and their routing labels;
# predict the gold set.

# %%
def head():
    # BEGIN SOLUTION
    return LogisticRegression(max_iter=3000, C=10).fit(X_pool, sample.routing_label).predict(X_gold)
    # END SOLUTION


try:
    pred = head()
except NotImplementedError:
    pred = LogisticRegression(max_iter=3000, C=10).fit(X_pool, sample.routing_label).predict(X_gold)
pd.DataFrame({"id": gold.id, "pred": pred}).to_csv(OUT / "pred_embed.csv", index=False)
U.keep("d2_pred_embed", {"id": gold.id.tolist(), "pred": list(map(str, pred)), "standin": STANDIN})

# %% [markdown]
# ## 3 · Scores per language with intervals (7')
#
# ✏️ **Exercise** · Accuracy and macro F1 with bootstrap intervals by variety (`U.boot_ci`). Compare them with the
# sparse classifier of Lab 2.2 (0.930 accuracy overall in the course's run). If the stand-in answered, say so next to
# every number you write down.

# %%
def per_language():
    # BEGIN SOLUTION
    acc = U.boot_ci(gold.gold, pred, U.accuracy, groups=gold.variety).assign(metric="accuracy")
    f1 = U.boot_ci(gold.gold, pred, U.macro_f1).assign(metric="macro_f1")
    return pd.concat([acc, f1])
    # END SOLUTION


try:
    table = per_language()
except NotImplementedError:
    table = U.boot_ci(gold.gold, pred, U.accuracy, groups=gold.variety).assign(metric="accuracy")
print(("STAND-IN VECTORS · " if STANDIN else "") + "embedding classifier on the gold set")
print(table.to_string(index=False))
U.keep("d2_embed_ci", table.to_dict(orient="records"))
U.check(table.value.iloc[0] > 0.5, "well above chance (eight categories: 0.125)")

# %% [markdown]
# ## 4 · Calls, seconds and cost per thousand documents (6')
#
# ✏️ **Exercise** · From the requests and seconds of task 1, compute for 1,000 complaints: requests, seconds of
# waiting, and money. The free endpoint costs nothing up to its daily limit; `U.prices()` shows that no paid
# endpoint of this embedding model is listed. What does that mean for embedding all 20,000 complaints?

# %%
def cost_table() -> dict:
    # BEGIN SOLUTION
    n = len(sample) + len(gold)
    per_k = 1000 / n
    return {"documents": n, "requests_per_1000": round(calls * per_k, 1), "seconds_per_1000": round(seconds * per_k, 1),
            "usd_per_1000_free": 0.0, "paid_endpoint": U.prices()["embed_paid"],
            "days_for_20000_at_50_requests": round(20000 / BATCH / 50, 1)}
    # END SOLUTION


cost = U.attempt(cost_table, "d2_embed_cost")
print(cost)

# %% [markdown]
# 🔍 **Look at** the seconds: with the stand-in they are the laptop's; with the hosted model most of them are the
# pause between free requests. Which of the two would you put in a plan for 20,000 complaints?

# %% [markdown]
# ## ✱ Stretch · Join the sparse and the embedding features
#
# Stack the character n-gram features of Lab 2.2 next to the vectors (`scipy.sparse.hstack`) and train one model.
# Does the union beat both on the gold set?

# %%
def stretch():
    # BEGIN SOLUTION
    from scipy.sparse import csr_matrix, hstack
    from sklearn.feature_extraction.text import TfidfVectorizer
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True)
    prep = lambda ts: [U.dialect(U.normalise(t)) for t in ts]  # noqa: E731
    A = hstack([vec.fit_transform(prep(sample.text)), csr_matrix(X_pool)]).tocsr()
    B = hstack([vec.transform(prep(gold.text)), csr_matrix(X_gold)]).tocsr()
    p = LogisticRegression(max_iter=3000, C=5).fit(A, sample.routing_label).predict(B)
    print("union accuracy:", round(U.accuracy(gold.gold, p), 3))
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. Why are the pool complaints sampled by routing label rather than taken from the top of the file?
# 2. The embedding model is free. Name two costs it still has.
# 3. The complaints are redacted. Why does that matter for this lab in particular?
#
# <details><summary>Answers</summary>
#
# 1. A stratified sample keeps every category represented in the training data; the top of the file may follow
#    the order the data were exported in.
# 2. Requests (a daily limit, so time: about six days for 20,000 complaints without credits), and the text leaves
#    the computer for a third party.
# 3. This is the first lab that sends text to a hosted service: only redacted text classified Public may go.
# </details>
#
# **Carry forward.** `artifacts/day2/pred_embed.csv`. Lab 2.4 uses the reference predictions if it is missing.
