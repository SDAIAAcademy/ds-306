# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scikit-learn>=1.6", "python-dotenv>=1.0", "openai>=1.60", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 2.1 · Agreement with a partner
#
# Day 2 · Session 1 (Gold sets and agreement) · 25 min.
#
# Every score this week is computed against labels people made. How far do two careful people agree when they
# apply the same codebook? You label 40 complaints with a partner, compute percent agreement and Cohen's kappa by
# hand, and meet the case where a high agreement means little.
#
# **AI policy: AI-off for the labelling.** The labels are yours and your partner's: no assistant, no model.
#
# **Reference state.** `data/codebook.md`, `data/pair40.csv` (40 redacted complaints and two reference coders) and
# `data/gold.csv` (300 complaints coded by two people). Nothing from Day 1.
#
# **Tasks**
# - [ ] 1 · Read the codebook (5')
# - [ ] 2 · Label 40 complaints with a partner, AI-off (10')
# - [ ] 3 · Percent agreement and kappa by hand (5')
# - [ ] 4 · The prevalence trap (5')
# - [ ] ✱ Stretch · Krippendorff's alpha for the two coders of the gold set

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
from sklearn.metrics import cohen_kappa_score

U.banner("Lab 2.1")
OUT = U.lab_dir("day2")

# %% [markdown]
# ## 1 · Read the codebook (5')
#
# Read the whole codebook, including the "does not include" column: most disagreements live there.

# %%
print(U.codebook())

# %% [markdown]
# ## 2 · Label 40 complaints with a partner (10')
#
# The cell below writes `artifacts/day2/pair40_to_label.csv`. Open it in a spreadsheet. You fill the column `me`,
# your partner fills `partner`, each **without looking** at the other's column and without any AI tool. Use the
# codes exactly as written in the codebook. Save the file as CSV in the same place, then run the next cell.
#
# If the file is not filled, the next cell uses the two reference coders that come with the data, and says so.

# %%
pair = U.pair40()
sheet = OUT / "pair40_to_label.csv"
if not sheet.exists():
    pair.assign(me="", partner="")[["id", "text", "me", "partner"]].to_csv(sheet, index=False, encoding="utf-8-sig")
print("Label this file:", sheet)
print(pair.text.head(3).to_string())

# %%
filled = pd.read_csv(sheet, dtype=str).fillna("")
ok = filled.me.isin(U.CATEGORIES).all() and filled.partner.isin(U.CATEGORIES).all()
if ok:
    a, b = filled.me.tolist(), filled.partner.tolist()
    print("Using your labels.")
else:
    a, b = pair.coder_1.tolist(), pair.coder_2.tolist()
    print("↩️  The sheet is not complete: using the two reference coders.")

# %% [markdown]
# ## 3 · Percent agreement and kappa by hand (5')
#
# Percent agreement `p_o` is the share of complaints with the same label. Chance agreement `p_e` is what two coders
# would reach by labelling at random with their own label frequencies: the sum over categories of
# `share of A in k × share of B in k`. Kappa is `(p_o − p_e) / (1 − p_e)`.
#
# ✏️ **Exercise** · Write `kappa_by_hand(a, b)` returning `(p_o, p_e, kappa)`, and compare with scikit-learn.

# %%
def kappa_by_hand(a, b) -> tuple[float, float, float]:
    # BEGIN SOLUTION
    a, b = np.asarray(a), np.asarray(b)
    p_o = float(np.mean(a == b))
    cats = sorted(set(a) | set(b))
    p_e = float(sum(np.mean(a == k) * np.mean(b == k) for k in cats))
    return p_o, p_e, (p_o - p_e) / (1 - p_e)
    # END SOLUTION


try:
    p_o, p_e, k = kappa_by_hand(a, b)
except NotImplementedError:
    p_o, p_e = float(np.mean(np.asarray(a) == np.asarray(b))), None
    k = cohen_kappa_score(a, b)
print(f"percent agreement {p_o:.3f} | chance {p_e if p_e is None else round(p_e, 3)} | kappa {k:.3f}")
U.check(abs(k - cohen_kappa_score(a, b)) < 1e-9, "kappa matches scikit-learn")
print(pd.crosstab(pd.Series(a, name="coder A"), pd.Series(b, name="coder B")))

# %% [markdown]
# 🔍 **Look at** the off-diagonal cells. Which pair of categories do the two of you confuse? Find the line of the
# codebook that should have decided it.

# %% [markdown]
# ## 4 · The prevalence trap (5')
#
# The gold set has two coders on 300 complaints. ✏️ **Exercise** · For each category, turn both coders' labels into
# "this category or not" and compute percent agreement and kappa. Sort by the category's share. What happens to
# kappa for the rare categories while percent agreement stays high?

# %%
gold = U.gold()


def per_category(gold: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    rows = []
    for c in U.CATEGORIES:
        x, y = gold.coder_a == c, gold.coder_b == c
        rows.append({"category": c, "share": round(float((gold.gold == c).mean()), 3),
                     "agreement": round(float((x == y).mean()), 3), "kappa": round(float(cohen_kappa_score(x, y)), 3)})
    return pd.DataFrame(rows).sort_values("share")
    # END SOLUTION


cats = pd.DataFrame(U.attempt(lambda: per_category(gold).to_dict(orient="records"), "d2_per_category"))
print(cats.to_string(index=False))
overall = U.kappa(gold.coder_a, gold.coder_b)
print(f"\nthe two gold coders, all categories: agreement {np.mean(gold.coder_a == gold.coder_b):.3f}, kappa {overall:.3f}")
U.keep("d2_human_kappa", {"agreement": round(float(np.mean(gold.coder_a == gold.coder_b)), 3), "kappa": round(overall, 3)})
U.check(cats.agreement.min() > 0.9, "every category: agreement above 0.9")

# %% [markdown]
# ## ✱ Stretch · Krippendorff's alpha
#
# Alpha compares observed disagreement with the disagreement expected from all labels pooled, and works with any
# number of coders and missing labels. For two coders and nominal labels it is close to kappa. Compute it for the
# two gold coders.

# %%
def stretch():
    # BEGIN SOLUTION
    pairs = list(zip(gold.coder_a, gold.coder_b))
    values = [v for p in pairs for v in p]
    n = len(values)
    counts = pd.Series(values).value_counts()
    d_o = sum(2 * (x != y) for x, y in pairs) / n  # each unit with 2 values contributes 2 ordered pairs, divided by m-1 = 1
    d_e = (n * n - (counts ** 2).sum()) / (n * (n - 1))
    print(f"alpha {1 - d_o / d_e:.3f} against kappa {overall:.3f}")
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. Two coders agree on 92% of complaints. What else do you need before you call that good?
# 2. Why is the gold label adjudicated, rather than coder A's label?
# 3. Writing and piloting the codebook is not in this course. Where is it taught?
#
# <details><summary>Answers</summary>
#
# 1. Chance agreement: with one dominant category, 92% can be little above chance. Report kappa and the categories
#    where the disagreements sit.
# 2. Each coder makes errors; an adjudicated label resolves disagreements against the codebook, so the gold set is
#    the best reference available, not one person's view.
# 3. In DS-311 (labelling guidelines, pilots and adjudication). Here the codebook and the adjudicated gold are given.
# </details>
#
# **Carry forward.** The human pair's kappa on the gold set is the bar Fahim is compared with in Lab 3.4.
