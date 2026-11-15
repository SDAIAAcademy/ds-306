# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scikit-learn>=1.6", "python-dotenv>=1.0", "openai>=1.60", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 1.2 · Normalise Arabic text
#
# Day 1 · Session 2 (Preparing Arabic text) · 25 min.
#
# The same word reaches Sada in several spellings: with or without hamza on the alef, with a final ة or ه, with
# marks, stretched with tatweel, typed on a Persian keyboard, or pasted from a PDF as presentation forms. You write
# the normalisation in named layers and measure what each layer does to the vocabulary, so that every rule in the
# cleaning script has a number and a reason next to it.
#
# **AI policy: AI-tutor.**
#
# **Reference state.** `data/complaints.csv.gz` and `data/dialect_map.csv`. Nothing from Lab 1.1.
#
# **Tasks**
# - [ ] 1 · Find the variants: forms, marks, letters, digits (5')
# - [ ] 2 · Write `normalise()` in layers (8')
# - [ ] 3 · The vocabulary change of each layer (7')
# - [ ] 4 · Gulf spellings from the supplied map (5')
# - [ ] ✱ Stretch · Find two different words that one rule merges into one

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
import unicodedata
from collections import Counter

import pandas as pd
import sada as U

U.banner("Lab 1.2")
c = U.complaints()
arabic = c[c.text.map(U.script_language).isin(["ar", "mixed"])].reset_index(drop=True)
print(len(arabic), "complaints in Arabic script (or mixed)")

# %% [markdown]
# ## 1 · Find the variants (5')
#
# Each pattern below is one kind of variation. Count the complaints that contain at least one match. Then look at
# one example of each: what would a person see, and what would a computer see?

# %%
PATTERNS = {
    "presentation forms (U+FB50 to U+FEFF)": "[ﭐ-﻿]",
    "Persian yeh or kaf (ی ک)": "[یک]",
    "tatweel (ـ)": "ـ",
    "diacritics (harakat)": "[ً-ْ]",
    "hamza on alef (أ إ آ)": "[أإآ]",
    "alef maqsura (ى)": "ى",
    "teh marbuta (ة)": "ة",
    "Arabic-Indic digits": "[٠-٩]",
}
found = pd.DataFrame([{"variant": k, "complaints": int(arabic.text.str.contains(v, regex=True).sum())}
                      for k, v in PATTERNS.items()])
found["share"] = (found.complaints / len(arabic)).round(3)
print(found.to_string(index=False))
example = arabic[arabic.text.str.contains("[ﭐ-﻿]")].text.iloc[0]
print("\nLooks like:", example[:80])
print("Code points:", [hex(ord(ch)) for ch in example[:6]])

# %% [markdown]
# ## 2 · Write `normalise()` in layers (8')
#
# ✏️ **Exercise** · Apply only the layers named in `layers`, in this order:
#
# | Layer | Rule |
# |---|---|
# | `unicode` | `unicodedata.normalize("NFKC", t)`: presentation forms back to letters |
# | `persian` | ی to ي, ک to ك |
# | `marks` | remove diacritics U+064B to U+0652, the dagger alef U+0670, and tatweel U+0640 |
# | `alef` | أ إ آ ٱ to ا |
# | `yeh_teh` | ى to ي, ة to ه |
# | `digits` | Arabic-Indic and Persian digits to 0 to 9 |
#
# Collapse whitespace at the end. The rules mirror CAMeL Tools' `normalize_unicode`, `normalize_alef_ar`,
# `normalize_alef_maksura_ar` and `normalize_teh_marbuta_ar`.

# %%
LAYERS = ["unicode", "persian", "marks", "alef", "yeh_teh", "digits"]


def normalise(text: str, layers=LAYERS) -> str:
    # BEGIN SOLUTION
    t = text
    if "unicode" in layers:
        t = unicodedata.normalize("NFKC", t)
    if "persian" in layers:
        t = t.replace("ی", "ي").replace("ک", "ك")
    if "marks" in layers:
        t = re.sub("[ً-ْٰـ]", "", t)
    if "alef" in layers:
        t = re.sub("[أإآٱ]", "ا", t)
    if "yeh_teh" in layers:
        t = t.replace("ى", "ي").replace("ة", "ه")
    if "digits" in layers:
        t = t.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789"))
    return re.sub(r"\s+", " ", t).strip()
    # END SOLUTION


try:
    normalise("تجربة")
except NotImplementedError:
    print("↩️  Exercise not done yet: using the course's reference normalise().")
    normalise = U.normalise
tests = {"ﺍﻟﻤﺎﺀ": "الماء", "إنارة": "اناره", "الحـــديقة": "الحديقه", "شارع ٢٣": "شارع 23", "مُغلق": "مغلق", "کهربای": "كهرباي"}
for raw, want in tests.items():
    U.check(normalise(raw) == want, f"{raw} → {normalise(raw)}")

# %% [markdown]
# ## 3 · The vocabulary change of each layer (7')
#
# ✏️ **Exercise** · For each prefix of `LAYERS` (none, then `unicode`, then `unicode` + `persian`, and so on), count
# the distinct tokens (`U.tokens`) over the Arabic complaints. Report the count and the drop from the step before.
# Which layer removes most distinct tokens, and which removes almost none?

# %%
texts = arabic.text.tolist() if not U.QUICK else arabic.text.head(4000).tolist()


def vocabulary_by_layer(texts) -> list[dict]:
    # BEGIN SOLUTION
    rows, prev = [], None
    for k in range(len(LAYERS) + 1):
        used = LAYERS[:k]
        vocab = set()
        for t in texts:
            vocab.update(U.tokens(normalise(t, used)))
        rows.append({"layers": "+".join(used) or "none", "distinct_tokens": len(vocab),
                     "drop": 0 if prev is None else prev - len(vocab)})
        prev = len(vocab)
    return rows
    # END SOLUTION


vocab = pd.DataFrame(U.attempt(lambda: vocabulary_by_layer(texts), "d1_vocab"))
print(vocab.to_string(index=False))
U.check(vocab.distinct_tokens.iloc[-1] < vocab.distinct_tokens.iloc[0], "normalisation shrinks the vocabulary")

# %% [markdown]
# 🔍 **Look at** the `digits` row. A street number typed as ٢٣ and as 23 is one token after it. Is that always what
# you want for a classifier? For a redaction rule?

# %% [markdown]
# ## 4 · Gulf spellings from the supplied map (5')
#
# `data/dialect_map.csv` holds the course's spelling rules for Gulf dialect: the same word spelled several ways
# (اللحين, الحينه and الحين). They are spelling rules, not translation into Modern Standard Arabic.
#
# ✏️ **Exercise** · Apply `U.dialect()` after `normalise()` and count the distinct tokens again. How many tokens
# did the map remove, and which three rules fired most often?

# %%
rules = pd.read_csv(U.DATA / "dialect_map.csv")
print(rules.head(6).to_string(index=False))


def dialect_effect(texts) -> dict:
    # BEGIN SOLUTION
    before, after, fired = set(), set(), Counter()
    for t in texts:
        n = normalise(t)
        before.update(U.tokens(n))
        after.update(U.tokens(U.dialect(n, rules)))
        for v in rules.variant:
            if re.search(rf"(?<!\S){re.escape(U.normalise(v))}(?!\S)", n):
                fired[v] += 1
        fired["(letters repeated 3 times or more)"] += bool(re.search(r"(.)\1{2,}", n))
    return {"before": len(before), "after": len(after), "top_rules": fired.most_common(3)}
    # END SOLUTION


eff = U.attempt(lambda: dialect_effect(texts), "d1_dialect")
print(eff)
U.check(eff["after"] < eff["before"], "the spelling map removes variants")

# %% [markdown]
# ## ✱ Stretch · One rule, two words
#
# Find tokens that end in ه after normalisation but came from both a final ة and a final ه in the raw text. Is any
# of them two different words? (Hint: in Gulf dialect مره means "very".)

# %%
def stretch():
    # BEGIN SOLUTION
    sources = {}
    for t in texts:
        for w in U.tokens(normalise(t, ["unicode", "persian", "marks", "alef"])):
            if w.endswith(("ة", "ه")):
                sources.setdefault(w[:-1] + "ه", set()).add(w[-1])
    both = sorted(k for k, v in sources.items() if len(v) == 2)
    print(len(both), "normalised tokens came from both spellings, e.g.", both[:12])
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. Which layer would you never apply before redaction, and why?
# 2. The `yeh_teh` layer merges two letters that mean different things. When is that still the right choice?
# 3. Why does the cleaning script keep the raw text in its own column?
#
# <details><summary>Answers</summary>
#
# 1. None has to wait, but `digits` must run before (or inside) the phone pattern: a pattern for 0 to 9 misses
#    numbers typed in Arabic-Indic digits.
# 2. When the task is counting or classifying topics: the merge removes spelling noise much more often than it
#    confuses two words. For a model that generates text, or for names, keep the letters.
# 3. Every rule loses information on purpose. The raw text is the evidence, and a rule can be changed and rerun.
# </details>
#
# **Carry forward.** `U.normalise()` and `U.dialect()` are the course's reference versions of this lab; later labs
# use them.
