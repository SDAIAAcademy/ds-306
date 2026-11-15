# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scikit-learn>=1.6", "python-dotenv>=1.0", "openai>=1.60", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 1.3 · Find near-duplicates
#
# Day 1 · Session 3 (Near-duplicates) · 25 min.
#
# Exact copies are easy. A citizen who adds "this is my second report" to the front, or 600 residents who paste
# the same message and change two words, are not. You compare complaints by their character shingles, find
# candidates fast with MinHash, group them, and write the keep rule Muhannad Al-Oqaili will apply before any count.
#
# **AI policy: AI-tutor.**
#
# **Reference state.** `data/complaints.csv.gz` and the course's reference `U.normalise()`. Nothing from Labs 1.1
# or 1.2.
#
# **Tasks**
# - [ ] 1 · Shingles and Jaccard on two complaints (5')
# - [ ] 2 · MinHash signatures for the corpus (7')
# - [ ] 3 · Bands: candidate pairs, then the true similarity (6')
# - [ ] 4 · Groups and the keep rule (7')
# - [ ] ✱ Stretch · Count the campaign as one issue: which district's count changes most?

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
import zlib
from collections import defaultdict

import numpy as np
import pandas as pd
import sada as U

U.banner("Lab 1.3")
c = U.complaints().sort_values(["received", "id"]).reset_index(drop=True)
if U.QUICK:
    c = c.sample(6000, random_state=306).sort_values(["received", "id"]).reset_index(drop=True)
OUT = U.lab_dir("day1")
print(len(c), "complaints")

# %% [markdown]
# ## 1 · Shingles and Jaccard on two complaints (5')
#
# A shingle is a run of `k` characters. Two texts that share most of their shingles say nearly the same thing in
# nearly the same words. Normalise first, and replace every long number (seven digits or more, with or without
# spaces) by `#`: a different phone number should not make two copies of one message look different. Short
# numbers stay: "Street 12" and "Street 46" are different places.
#
# ✏️ **Exercise** · Write `shingles(text, k=5)` (a set) and `jaccard(a, b)` (the size of the intersection over the
# size of the union).

# %%
def prepare(text: str) -> str:
    return re.sub(r"\+?\d[\d \-]{5,}\d", "#", U.normalise(text))


def shingles(text: str, k: int = 5) -> set[str]:
    # BEGIN SOLUTION
    t = prepare(text)
    return {t[i:i + k] for i in range(max(1, len(t) - k + 1))}
    # END SOLUTION


def jaccard(a: set, b: set) -> float:
    # BEGIN SOLUTION
    return len(a & b) / len(a | b) if a | b else 0.0
    # END SOLUTION


try:
    shingles("تجربة")
except NotImplementedError:
    print("↩️  Exercise not done yet: using the reference versions.")

    def shingles(text, k=5):
        t = prepare(text)
        return {t[i:i + k] for i in range(max(1, len(t) - k + 1))}

    def jaccard(a, b):
        return len(a & b) / len(a | b) if a | b else 0.0

naseem = c[(c.district == "al_naseem") & c.text.str.contains("شارع (?:12|١٢) (?:عند|جنب) المدرسة")].text.iloc[[0, 5]].tolist()
other = c.text.iloc[[10, 11]].tolist()
for a, b in [naseem, other]:
    print(round(jaccard(shingles(a), shingles(b)), 2), "|", a[:60], "||", b[:60])

# %% [markdown]
# ## 2 · MinHash signatures for the corpus (7')
#
# Comparing every pair of 20,000 complaints is 200 million comparisons. MinHash summarises each shingle set by 64
# numbers such that two signatures agree at a position with probability equal to the Jaccard similarity.
#
# ✏️ **Exercise** · Hash each shingle to an integer with `zlib.crc32`. For each of the 64 hash functions
# `(a * h + b) mod P`, keep the minimum over the document's shingles. Return an array of shape (documents, 64).

# %%
P = (1 << 31) - 1  # a prime: products stay inside 64-bit integers
rng = np.random.default_rng(306)
A = rng.integers(1, P, 64, dtype=np.int64)
B = rng.integers(0, P, 64, dtype=np.int64)
sets = [shingles(t) for t in c.text]


def minhash(sets) -> np.ndarray:
    # BEGIN SOLUTION
    sig = np.empty((len(sets), len(A)), dtype=np.int64)
    for i, s in enumerate(sets):
        h = np.fromiter((zlib.crc32(x.encode("utf-8")) % P for x in s), dtype=np.int64, count=len(s))
        sig[i] = ((np.outer(h, A) + B) % P).min(axis=0)
    return sig
    # END SOLUTION


try:
    sig = minhash(sets)
except NotImplementedError:
    print("↩️  Exercise not done yet: computing the reference signatures.")
    sig = np.empty((len(sets), 64), dtype=np.int64)
    for i, s in enumerate(sets):
        h = np.fromiter((zlib.crc32(x.encode("utf-8")) % P for x in s), dtype=np.int64, count=len(s))
        sig[i] = ((np.outer(h, A) + B) % P).min(axis=0)
i, j = c.index[c.text.isin(naseem)][:2]
print("estimated similarity of the two Al-Naseem messages:", round(float((sig[i] == sig[j]).mean()), 2))

# %% [markdown]
# ## 3 · Bands: candidate pairs, then the true similarity (6')
#
# Cut each signature into 16 bands of 4 rows. Two documents that agree on all four rows of any band become a
# candidate pair. Short complaints about the same thing are often worded alike ("the street lights on Street 12
# are off"), so text alone over-matches: block by district (only complaints from the same district can pair) and
# confirm a pair only when the true Jaccard similarity is 0.7 or more **and** the two arrived within 21 days.
#
# ✏️ **Exercise** · Fill `candidate_pairs(sig, block)`, where `block` is each row's district, and keep the
# confirmed pairs.

# %%
def candidate_pairs(sig: np.ndarray, block, bands: int = 16, rows: int = 4) -> set[tuple[int, int]]:
    # BEGIN SOLUTION
    pairs = set()
    for b in range(bands):
        buckets = defaultdict(list)
        for i, key in enumerate(map(tuple, sig[:, b * rows:(b + 1) * rows])):
            buckets[(block[i], key)].append(i)
        for members in buckets.values():
            for x in range(len(members)):
                for y in range(x + 1, len(members)):
                    pairs.add((members[x], members[y]))
    return pairs
    # END SOLUTION


try:
    cands = candidate_pairs(sig, c.district.to_numpy())
except NotImplementedError:
    cands = set()
    for b in range(16):
        buckets = defaultdict(list)
        for i, key in enumerate(map(tuple, sig[:, b * 4:(b + 1) * 4])):
            buckets[(c.district.iat[i], key)].append(i)
        for m in buckets.values():
            cands.update((m[x], m[y]) for x in range(len(m)) for y in range(x + 1, len(m)))
day = c.received.to_numpy().astype("datetime64[D]").astype(np.int64)
confirmed = [(i, j) for i, j in cands if abs(day[i] - day[j]) <= 21 and jaccard(sets[i], sets[j]) >= 0.7]
print(f"candidate pairs: {len(cands)}, confirmed at Jaccard 0.7 or more: {len(confirmed)}")
U.check(len(confirmed) > 0, "near-duplicate pairs found")

# %% [markdown]
# ## 4 · Groups and the keep rule (7')
#
# Pairs chain into groups: if A is like B and B is like C, all three are one group. ✏️ **Exercise** · Build the
# groups (a union-find is ten lines), then apply the keep rule:
#
# - a group of 20 or more is a **campaign**: keep every message, flag `campaign = True`, count the issue once;
# - a smaller group is one citizen writing again: keep the earliest message, mark the others `keep = False`.

# %%
def groups_and_keep(n: int, pairs) -> pd.DataFrame:
    # BEGIN SOLUTION
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, j in pairs:
        parent[find(i)] = find(j)
    root = [find(i) for i in range(n)]
    out = pd.DataFrame({"row": range(n), "group": root})
    size = out.group.map(out.group.value_counts())
    out["campaign"] = size >= 20
    first = ~out.duplicated("group", keep="first")  # rows are sorted by date: the first row is the earliest
    out["keep"] = out.campaign | first
    return out
    # END SOLUTION


try:
    g = groups_and_keep(len(c), confirmed)
except NotImplementedError:
    print("↩️  Exercise not done yet: the reference keep flags are loaded.")
    ref = pd.DataFrame(U.reference("d1_keep"))
    g = c[["id"]].merge(ref, on="id", how="left").fillna({"keep": True, "campaign": False})
    g["group"] = range(len(g))
c["keep"], c["campaign"], c["group"] = g["keep"].to_numpy(), g["campaign"].to_numpy(), g["group"].to_numpy()
sizes = c.groupby("group").size()
print("groups of 2 or more:", int((sizes >= 2).sum()), "| largest:", int(sizes.max()))
print("removed as copies:", int((~c.keep).sum()), "| campaign messages kept and flagged:", int(c.campaign.sum()))
print(c[c.campaign].district.value_counts().head(3).to_string())
U.keep("d1_keep", c.loc[~c.keep | c.campaign, ["id", "keep", "campaign"]].to_dict(orient="records"))
c[["id", "keep", "campaign"]].to_csv(OUT / "keep_flags.csv", index=False)
U.check(c.campaign.sum() >= U.pick(500, 100), "the campaign is found")

# %% [markdown]
# 🔍 **Look at** three removed messages next to the message they copy. Is "keep the earliest" right for each?

# %% [markdown]
# ## ✱ Stretch · The campaign as one issue
#
# Count complaints per district twice: every kept message, and campaign messages counted once. Which district
# changes most?

# %%
def stretch():
    # BEGIN SOLUTION
    kept = c[c.keep]
    per_message = kept.district.value_counts()
    per_issue = kept[~kept.campaign].district.value_counts().add(
        kept[kept.campaign].groupby("district").group.nunique(), fill_value=0)
    change = (per_message - per_issue).sort_values(ascending=False)
    print(change.head(3).to_string())
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. Why are digits replaced by `#` before shingling?
# 2. Two complaints have a Jaccard similarity of 0.65. Are they duplicates?
# 3. Why does the keep rule keep every campaign message instead of the first?
#
# <details><summary>Answers</summary>
#
# 1. The copies differ in phone numbers and street numbers; without the mask those digits make copies look
#    different (and they are personal data the comparison does not need).
# 2. The threshold is a decision, not a fact: read a sample of pairs around 0.7 and set it where reading says
#    "same message".
# 3. Each message is a resident who complained. The rate question decides whether to count messages or issues;
#    the flag lets both counts be made.
# </details>
#
# **Carry forward.** `artifacts/day1/keep_flags.csv`. Lab 4.4 uses the reference flags if yours are missing.
