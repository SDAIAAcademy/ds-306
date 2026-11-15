# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scikit-learn>=1.6", "python-dotenv>=1.0", "openai>=1.60", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 2.2 · A character n-gram classifier
#
# Day 2 · Session 2 (Sparse baselines) · 25 min.
#
# The baseline every other classifier this week must beat: character n-grams with TF-IDF weights and a logistic
# regression, trained on 3,000 complaints routed by the intake team and scored on the 300-complaint gold set. It
# trains in seconds on a laptop, costs nothing per document and never sends text anywhere.
#
# **AI policy: AI-tutor.**
#
# **Reference state.** `data/pool.csv` (redacted, with routing labels nobody checked) and `data/gold.csv`. The
# course's reference `U.normalise()` and `U.dialect()`. Nothing from Lab 2.1.
#
# **Tasks**
# - [ ] 1 · Load the pool and the gold set (3')
# - [ ] 2 · Character n-grams with TF-IDF (6')
# - [ ] 3 · A logistic classifier (5')
# - [ ] 4 · Macro F1 and accuracy on the gold set (5')
# - [ ] 5 · Bootstrap intervals by language (6')
# - [ ] ✱ Stretch · Word n-grams instead: which language loses most?

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

import time

import numpy as np
import pandas as pd
import sada as U
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

U.banner("Lab 2.2")
OUT = U.lab_dir("day2")

# %% [markdown]
# ## 1 · Load the pool and the gold set (3')
#
# The pool's labels are the intake team's routing decisions: fast, unchecked, sometimes wrong. The gold set's
# labels were coded twice and adjudicated. Train on the first, score on the second, never the other way round.

# %%
pool, gold = U.pool(), U.gold()
print(len(pool), "pool |", len(gold), "gold | gold by variety:", gold.variety.value_counts().to_dict())
print(pool.routing_label.value_counts(normalize=True).round(3).to_dict())
U.check(not set(pool.id) & set(gold.id), "no complaint is in both")


def prep(texts) -> list[str]:
    return [U.dialect(U.normalise(t)) for t in texts]


X_pool_text, X_gold_text = prep(pool.text), prep(gold.text)

# %% [markdown]
# ## 2 · Character n-grams with TF-IDF (6')
#
# ✏️ **Exercise** · Build a `TfidfVectorizer` over character n-grams of 2 to 5 characters inside word boundaries
# (`analyzer="char_wb"`), dropping n-grams seen in fewer than 2 documents, with sublinear term frequency. Fit it on
# the pool only, then transform both sets. How many features?

# %%
def vectoriser() -> TfidfVectorizer:
    # BEGIN SOLUTION
    return TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True)
    # END SOLUTION


try:
    vec = vectoriser()
except NotImplementedError:
    print("↩️  Exercise not done yet: using the reference settings.")
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True)
t0 = time.perf_counter()
X_pool = vec.fit_transform(X_pool_text)
X_gold = vec.transform(X_gold_text)
print(X_pool.shape[1], "features")

# %% [markdown]
# ## 3 · A logistic classifier (5')
#
# ✏️ **Exercise** · Train a `LogisticRegression` (`max_iter=2000`, `C=5`) on the pool and predict the gold set.

# %%
def train_and_predict(X_train, y_train, X_test):
    # BEGIN SOLUTION
    model = LogisticRegression(max_iter=2000, C=5)
    model.fit(X_train, y_train)
    return model.predict(X_test)
    # END SOLUTION


try:
    pred = train_and_predict(X_pool, pool.routing_label, X_gold)
except NotImplementedError:
    pred = LogisticRegression(max_iter=2000, C=5).fit(X_pool, pool.routing_label).predict(X_gold)
seconds = time.perf_counter() - t0
print(f"trained and predicted in {seconds:.1f} s on this computer")
pd.DataFrame({"id": gold.id, "pred": pred}).to_csv(OUT / "pred_sparse.csv", index=False)
U.keep("d2_pred_sparse", {"id": gold.id.tolist(), "pred": list(map(str, pred))})

# %% [markdown]
# ## 4 · Macro F1 and accuracy on the gold set (5')
#
# Accuracy counts every complaint once; macro F1 averages the F1 of the eight categories, so a rare category counts
# as much as a common one. ✏️ **Exercise** · Compute both against `gold.gold`.

# %%
def scores(y, p) -> dict:
    # BEGIN SOLUTION
    return {"accuracy": round(U.accuracy(y, p), 3), "macro_f1": round(U.macro_f1(y, p), 3)}
    # END SOLUTION


s = U.attempt(lambda: scores(gold.gold, pred), "d2_sparse_scores")
print(s)
U.check(s["accuracy"] > 0.7, "the baseline beats 0.7 accuracy")

# %% [markdown]
# ## 5 · Bootstrap intervals by language (6')
#
# 300 complaints are a sample. ✏️ **Exercise** · Use `U.boot_ci(y, p, metric, groups=gold.variety)` for accuracy:
# it resamples complaints 2,000 times and returns the 95% interval, overall and by variety. Which variety has the
# widest interval, and why?

# %%
def intervals():
    # BEGIN SOLUTION
    return U.boot_ci(gold.gold, pred, U.accuracy, groups=gold.variety)
    # END SOLUTION


try:
    ci = intervals()
except NotImplementedError:
    ci = U.boot_ci(gold.gold, pred, U.accuracy, groups=gold.variety)
print(ci.to_string(index=False))
U.keep("d2_sparse_ci", ci.to_dict(orient="records"))
U.check(ci.set_index("group").loc["en", "n"] < 100, "English has the fewest gold complaints")

# %% [markdown]
# 🔍 **Look at** the pool's routing labels against what the gold set says. The classifier learnt the intake team's
# habits, errors included: where would you expect it to copy them?

# %% [markdown]
# ## ✱ Stretch · Word n-grams instead
#
# Swap to `analyzer="word"`, `ngram_range=(1, 2)` and score again by variety. Which variety loses most, and what
# about Arabic words explains it?

# %%
def stretch():
    # BEGIN SOLUTION
    wv = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    p2 = LogisticRegression(max_iter=2000, C=5).fit(wv.fit_transform(X_pool_text), pool.routing_label).predict(wv.transform(X_gold_text))
    print(U.boot_ci(gold.gold, p2, U.accuracy, groups=gold.variety, n=300)[["group", "value"]].to_string(index=False))
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. Why is the vectoriser fitted on the pool only?
# 2. The gold accuracy is higher than the pool's own routing labels are correct. How can a model beat its teacher?
# 3. What does this classifier cost per thousand complaints?
#
# <details><summary>Answers</summary>
#
# 1. Fitting on the gold set lets its vocabulary and weights leak into training: the score would no longer be on
#    unseen text.
# 2. The routing errors are scattered; the model learns the regular pattern under them. It still copies systematic
#    errors, which is why it is scored on a clean gold set.
# 3. Seconds of laptop time, and nothing per call: no text leaves the computer.
# </details>
#
# **Carry forward.** `artifacts/day2/pred_sparse.csv`. Lab 2.4 uses the reference predictions if it is missing.
