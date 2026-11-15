# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scikit-learn>=1.6", "python-dotenv>=1.0"]
# ///
# %% [markdown]
# # Pre-work · Classification metrics
#
# About two hours, before Day 1. The course scores classifiers, prompted models and extractions all week; this
# notebook makes sure the scores mean the same thing to everyone. It uses no model: the "classifier" is a list of
# keywords (`U.keyword_label`), scored against the 300 human-coded complaints of Sada Citizen Voice Centre's gold
# set. The course team wrote the list after reading the codebook and the complaints; keep its score in mind as the
# baseline every method of the week has to beat.
#
# **AI policy: AI-off.** The entry quiz on the practice page checks these ideas without help.
#
# **Tasks**
# - [ ] 1 · The confusion table (20')
# - [ ] 2 · Precision, recall and F1 per category (30')
# - [ ] 3 · Accuracy, macro F1 and the prevalence trap (30')
# - [ ] 4 · An interval for accuracy (30')
# - [ ] 5 · Five questions (10')

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
from sklearn.metrics import classification_report
import sada as U

gold = U.gold()
gold["pred"] = gold.text.map(U.keyword_label)
print(len(gold), "gold complaints; categories:", U.CATEGORIES)
print(gold[["text", "gold", "pred"]].head(3).to_string())

# %% [markdown]
# ## 1 · The confusion table (20')
#
# Rows are the true category, columns the predicted one. The diagonal holds the right answers.
#
# ✏️ **Exercise** · Build the table with `pd.crosstab`, rows and columns in the order of `U.CATEGORIES`, and find the
# largest cell off the diagonal. Read two complaints from that cell: why does the keyword list fail on them?

# %%
def confusion() -> pd.DataFrame:
    # BEGIN SOLUTION
    return pd.crosstab(gold.gold, gold.pred).reindex(index=U.CATEGORIES, columns=U.CATEGORIES, fill_value=0)
    # END SOLUTION


try:
    cm = confusion()
except NotImplementedError:
    cm = pd.crosstab(gold.gold, gold.pred).reindex(index=U.CATEGORIES, columns=U.CATEGORIES, fill_value=0)
    print("↩️  Exercise not done yet: using the reference table.")
print(cm.to_string())
off = cm.copy()
for k in U.CATEGORIES:
    off.loc[k, k] = 0
t, p = off.stack().idxmax()
print(f"\nlargest error: true {t}, predicted {p} ({off.loc[t, p]})")
for x in gold[(gold.gold == t) & (gold.pred == p)].text.head(2):
    print("  ·", x[:140])

# %% [markdown]
# ## 2 · Precision, recall and F1 per category (30')
#
# For one category:
#
# - **precision**: of the complaints predicted in it, the share that truly belong (column-wise);
# - **recall**: of the complaints that truly belong, the share predicted in it (row-wise);
# - **F1**: their harmonic mean, `2PR / (P + R)`.
#
# ✏️ **Exercise** · Compute the three from `cm` for every category, then compare with
# `sklearn.metrics.classification_report`.

# %%
def per_category(cm: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    tp = np.diag(cm.values).astype(float)
    precision = np.divide(tp, cm.sum(axis=0).values, out=np.zeros_like(tp), where=cm.sum(axis=0).values > 0)
    recall = np.divide(tp, cm.sum(axis=1).values, out=np.zeros_like(tp), where=cm.sum(axis=1).values > 0)
    f1 = np.divide(2 * precision * recall, precision + recall, out=np.zeros_like(tp), where=(precision + recall) > 0)
    return pd.DataFrame({"precision": precision, "recall": recall, "f1": f1, "support": cm.sum(axis=1).values},
                        index=cm.index).round(3)
    # END SOLUTION


try:
    pc = per_category(cm)
    print(pc.to_string())
except NotImplementedError:
    print("↩️  Exercise not done yet.")
print(classification_report(gold.gold, gold.pred, labels=U.CATEGORIES, zero_division=0, digits=3))

# %% [markdown]
# 🔍 **Look at** one category with high precision and low recall. What does the keyword list do there: say too
# much, or too little?

# %% [markdown]
# ## 3 · Accuracy, macro F1 and the prevalence trap (30')
#
# Accuracy weighs every complaint equally, so large categories dominate it. Macro F1 averages the categories'
# F1 scores, so a small category counts as much as a large one.
#
# ✏️ **Exercise** ·
# 1. Accuracy and macro F1 of the keyword list.
# 2. A lazy detector for `parks` that always says "not parks". Its accuracy **as a parks detector** (a yes-or-no
#    question over the 300 complaints), and its recall of parks complaints.

# %%
def summary() -> dict:
    # BEGIN SOLUTION
    is_parks = (gold.gold == "parks").to_numpy()
    lazy = np.zeros_like(is_parks)
    return {"accuracy": round(U.accuracy(gold.gold, gold.pred), 3), "macro_f1": round(U.macro_f1(gold.gold, gold.pred), 3),
            "parks_share": round(float(is_parks.mean()), 3), "lazy_accuracy": round(float((lazy == is_parks).mean()), 3),
            "lazy_recall": 0.0}
    # END SOLUTION


try:
    s = summary()
    print(s)
    U.check(s["lazy_accuracy"] > 0.9 and s["lazy_recall"] == 0, "the lazy detector is accurate and useless")
except NotImplementedError:
    print("↩️  Exercise not done yet.")

# %% [markdown]
# ## 4 · An interval for accuracy (30')
#
# 300 complaints are a sample. Another 300 would give another accuracy. The **bootstrap** estimates how much:
# draw 300 complaints from the 300 with replacement, score them, repeat 2,000 times, and take the 2.5th and 97.5th
# percentiles.
#
# ✏️ **Exercise** · Write the bootstrap for accuracy. Compare it with `U.boot_ci(gold.gold, gold.pred, U.accuracy)`,
# which the course uses all week.

# %%
def bootstrap_accuracy(y: np.ndarray, p: np.ndarray, n: int = 2000, seed: int = 306) -> tuple[float, float]:
    # BEGIN SOLUTION
    rng = np.random.default_rng(seed)
    stats = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        stats.append((y[i] == p[i]).mean())
    return float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5))
    # END SOLUTION


try:
    lo, hi = bootstrap_accuracy(gold.gold.to_numpy(), gold.pred.to_numpy(), U.pick(2000, 300))
    print(f"accuracy {U.accuracy(gold.gold, gold.pred):.3f}, 95% interval {lo:.3f} to {hi:.3f}")
except NotImplementedError:
    print("↩️  Exercise not done yet.")
print(U.boot_ci(gold.gold, gold.pred, U.accuracy, groups=gold.variety).to_string(index=False))

# %% [markdown]
# 🔍 **Look at** the intervals by language variety. Why is the English one widest?

# %% [markdown]
# ## 5 · Five questions (10')
#
# 1. A classifier has precision 0.95 and recall 0.40 for `water_sewage`. What happens to a count of sewage
#    complaints made from its labels?
# 2. Why can accuracy rise while macro F1 falls?
# 3. A category holds 3% of complaints. What accuracy does "never predict it" reach?
# 4. Two classifiers score 0.81 and 0.84 on the same 300 complaints, each with an interval about 0.09 wide. Can you
#    say the second is better?
# 5. Which metric would you report to a director who decides by category?
#
# <details><summary>Answers</summary>
#
# 1. It is far too low: fewer than half the true sewage complaints are found, and the few it finds are right.
# 2. A change that helps a large category and hurts a small one raises accuracy and lowers the average of the
#    categories' F1.
# 3. 97%, with zero recall.
# 4. Not from the two intervals: a paired comparison on the same complaints is needed (Day 2, Lab 2.4).
# 5. Precision and recall per category, with intervals; the director's decision is about one category at a time.
# </details>
