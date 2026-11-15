# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scikit-learn>=1.6", "python-dotenv>=1.0", "openai>=1.60", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 4.3 · Structure in text
#
# Day 4 · Session 3 (Structure in text) · 25 min.
#
# Dr. Ebtisam asks a different question: "What are people writing about that our eight categories do not show?"
# Clustering answers it without a codebook. You cluster complaint vectors, choose a number of clusters, name five
# from their terms and examples, and compare them with the categories. A cluster is a way to look at a corpus, not
# a label.
#
# **AI policy: models are measured here.** The vectors come from a model; the names are yours.
#
# **Model access.** With a free key, the vectors come from `nvidia/nemotron-3.5-embed-1b:free` on OpenRouter
# (16 requests of 64 complaints). Without one, the lexical stand-in from Lab 2.3 makes them (hashed character
# n-grams): the clusters are then about shared wording, not meaning. The banner says which.
#
# **Reference state.** `data/pool.csv` (3,000 redacted complaints with routing labels) and the keep flags of Lab 1.3
# (`data/reference/d1_keep.json`). Only redacted text is sent to the hosted model.
#
# **Tasks**
# - [ ] 1 · Vectors for a sample of complaints (5')
# - [ ] 2 · k-means for several k, with silhouette (6')
# - [ ] 3 · Five clusters: terms and examples (7')
# - [ ] 4 · Name them and compare with the categories (7')
# - [ ] ✱ Stretch · Find the campaign: which cluster is it, and what would it do to a topic count?

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

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import adjusted_rand_score, silhouette_score
import sada as U

U.banner("Lab 4.3")
OUT = U.lab_dir("day4")
pool = U.pool()
sample = pool.sample(U.pick(1000, 400), random_state=306).reset_index(drop=True)
print(len(sample), "redacted complaints;", sample.routing_label.value_counts().to_dict())

# %% [markdown]
# ## 1 · Vectors for a sample of complaints (5')
#
# ✏️ **Exercise** · Embed the sample with `U.embed(texts)`. The vectors come back with length one, so a dot product
# is a cosine similarity. Check the shape and that two complaints with the same routing label are, on average, closer
# than two with different labels.

# %%
def vectors() -> np.ndarray:
    # BEGIN SOLUTION
    return U.embed(sample.text.tolist())
    # END SOLUTION


try:
    X = vectors()
except NotImplementedError:
    print("↩️  Exercise not done yet: using U.embed directly.")
    X = U.embed(sample.text.tolist())
print("vectors:", X.shape, "| calls:", U.CALLS["embed"], "| stand-in:", U.standin())
S = X @ X.T
same_label = sample.routing_label.to_numpy()[:, None] == sample.routing_label.to_numpy()[None, :]
off = ~np.eye(len(X), dtype=bool)
print(f"mean cosine, same label {S[same_label & off].mean():.3f} | different labels {S[~same_label].mean():.3f}")
U.check(S[same_label & off].mean() > S[~same_label].mean(), "same-label complaints sit closer")

# %% [markdown]
# ## 2 · k-means for several k, with silhouette (6')
#
# The silhouette of a complaint compares its distance to its own cluster with its distance to the nearest other
# cluster: near 1 is well placed, near 0 is on a border. ✏️ **Exercise** · Fit k-means for k = 3 to 12 (`n_init=10`,
# `random_state=306`) and compute the mean silhouette (cosine) for each. Which k is best, and how much better is it
# than k = 5?

# %%
KS = list(range(3, 13))


def silhouettes() -> dict:
    # BEGIN SOLUTION
    return {k: round(float(silhouette_score(X, KMeans(k, n_init=10, random_state=306).fit_predict(X), metric="cosine")), 3)
            for k in KS}
    # END SOLUTION


sil = {int(k): v for k, v in U.attempt(silhouettes, "d4_silhouette").items()}
print(sil)
best = max(sil, key=sil.get)
print(f"best k by silhouette: {best} ({sil[best]}) | k = 5: {sil[5]}")

# %% [markdown]
# 🔍 **Look at** the size of the silhouettes. Below about 0.25, the clusters overlap: the corpus has no sharp
# borders, which is normal for complaints. Silhouette advises; the number of clusters you can read and name decides.

# %% [markdown]
# ## 3 · Five clusters: terms and examples (7')
#
# ✏️ **Exercise** · Fit k = 5. For each cluster: its size, the six words most **distinctive** of it (mean TF-IDF in
# the cluster minus the mean overall, on normalised text), and the three complaints nearest its centre.

# %%
km = KMeans(5, n_init=10, random_state=306).fit(X)
sample["cluster"] = km.labels_
tf = TfidfVectorizer(preprocessor=lambda t: U.dialect(U.normalise(t)).lower(), token_pattern=r"[\w؀-ۿ]{3,}", min_df=3)
T = tf.fit_transform(sample.text)
vocab = np.array(tf.get_feature_names_out())


def describe() -> pd.DataFrame:
    # BEGIN SOLUTION
    overall = np.asarray(T.mean(axis=0)).ravel()
    rows = []
    for c in range(5):
        idx = np.where(sample.cluster == c)[0]
        lift = np.asarray(T[idx].mean(axis=0)).ravel() - overall
        centre = km.cluster_centers_[c] / np.linalg.norm(km.cluster_centers_[c])
        near = idx[np.argsort(-(X[idx] @ centre))[:3]]
        rows.append({"cluster": c, "size": len(idx), "terms": ", ".join(vocab[np.argsort(-lift)[:6]]),
                     "examples": [sample.text[i][:110] for i in near]})
    return pd.DataFrame(rows)
    # END SOLUTION


try:
    clusters = describe()
except NotImplementedError:
    clusters = pd.DataFrame({"cluster": range(5), "size": sample.cluster.value_counts().sort_index().to_numpy(),
                             "terms": "(not computed)", "examples": [[] for _ in range(5)]})
for _, r in clusters.iterrows():
    print(f"\ncluster {r.cluster} · {r['size']} complaints · {r.terms}")
    for e in r.examples:
        print("   ·", e)

# %% [markdown]
# ## 4 · Name them and compare with the categories (7')
#
# ✏️ **Exercise** · Give each cluster a short name from its terms and examples (write them yourself: the terms are
# evidence, not a name). Then cross-tabulate cluster against routing label and against the guessed variety
# (`U.guess_variety`), and compute the adjusted Rand index of clusters and labels (0 is chance agreement, 1 is the
# same partition). Do the clusters follow topics, or something else?

# %%
sample["variety"] = sample.text.map(U.guess_variety)
by_label = pd.crosstab(sample.cluster, sample.routing_label)
by_variety = pd.crosstab(sample.cluster, sample.variety, normalize="index").round(2)


def names() -> dict:
    # BEGIN SOLUTION
    out = {}
    for c in range(5):
        v = by_variety.loc[c].idxmax()
        top = by_label.loc[c] / by_label.loc[c].sum()
        topic = top.idxmax() if top.max() >= 0.4 else "mixed topics"
        out[c] = f"{c}: {dict(msa='formal Arabic', gulf='Gulf dialect', en='English')[v]}, {topic}"
    return out
    # END SOLUTION


try:
    NAMES = names()
except NotImplementedError:
    NAMES = {c: f"cluster {c}" for c in range(5)}
print(by_label.rename(index=NAMES).to_string())
print()
print(by_variety.rename(index=NAMES).to_string())
ari = adjusted_rand_score(sample.routing_label, sample.cluster)
ari_v = adjusted_rand_score(sample.variety, sample.cluster)
purity = by_label.max(axis=1).sum() / by_label.to_numpy().sum()
print(f"\nadjusted Rand index with routing labels {ari:.3f} | with variety {ari_v:.3f} | label purity {purity:.3f}")
U.keep("d4_clusters", {"silhouette_k5": sil[5], "best_k": best, "ari_labels": round(ari, 3), "ari_variety": round(ari_v, 3),
                       "purity": round(purity, 3), "sizes": sample.cluster.value_counts().sort_index().tolist(),
                       "names": list(NAMES.values())})
sample.assign(name=sample.cluster.map(NAMES))[["id", "cluster", "name", "variety", "routing_label"]].to_csv(
    OUT / "clusters.csv", index=False)

# %% [markdown]
# 🔍 **Look at** the two Rand indices. With the stand-in's lexical vectors the clusters follow the language and the
# register (formal, Gulf, English, a recurring phrase) more than the topic: wording-based vectors see wording. One
# cluster is different: it gathers one sewage message written hundreds of times.

# %% [markdown]
# ## ✱ Stretch · Find the campaign
#
# Lab 1.3 flagged the campaign messages. Which cluster holds most of the ones in this sample, and what share of that
# cluster are they? If the cluster were reported as a topic, how much of its size would one organised campaign be?

# %%
def stretch():
    # BEGIN SOLUTION
    flags = pd.DataFrame(U.reference("d1_keep"))
    campaign = set(flags.loc[flags.campaign, "id"])
    sample["campaign"] = sample.id.isin(campaign)
    by = sample.groupby("cluster").campaign.agg(["sum", "size"])
    c = int(by["sum"].idxmax())
    print(f"{int(by['sum'].sum())} campaign messages in the sample; {int(by.loc[c, 'sum'])} in cluster {c} "
          f"({NAMES[c]}), {by.loc[c, 'sum'] / by.loc[c, 'size']:.0%} of it")
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. The silhouette is highest at another k than five. Why might you still read five clusters?
# 2. Why is a cluster not a category you can count and publish?
# 3. Clusters on the stand-in's vectors follow wording. What would you expect to change with a real embedding model?
#
# <details><summary>Answers</summary>
#
# 1. The clusters are for reading: five that a person can name and check beat twelve with a slightly better score.
# 2. Its borders move with the sample, the vectors and k; it has no definition and no measured agreement. A category
#    has a codebook, a gold set and an error rate.
# 3. Complaints about one problem written in different words, or in another language, should join; clusters by
#    greeting or channel should weaken.
# </details>
#
# **Carry forward.** `artifacts/day4/clusters.csv`.
