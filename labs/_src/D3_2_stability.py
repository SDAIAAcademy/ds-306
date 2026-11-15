# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scikit-learn>=1.6", "python-dotenv>=1.0", "openai>=1.60", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 3.2 · Ask it twice
#
# Day 3 · Session 2 (Ask it twice) · 25 min.
#
# An instrument that gives a different reading each time you use it is measuring something besides the thing you
# care about. You measure how often Fahim changes its label between three runs of one prompt, and how far a
# reworded prompt moves the labels, then find out which complaints move.
#
# **AI policy: models are measured here.**
#
# **Reference state.** `data/model_runs_gold.csv`: prompt 1 and prompt 2, three runs each, over the 300 gold
# complaints (recorded; synthetic). `data/gold.csv`. Nothing from Lab 3.1.
#
# **Tasks**
# - [ ] 1 · Three runs of one prompt: the flip rate (6')
# - [ ] 2 · Kappa between runs (5')
# - [ ] 3 · The reworded prompt: the shift (6')
# - [ ] 4 · Which documents move (5')
# - [ ] 5 · The majority of three runs (3')
# - [ ] ✱ Stretch · Run twenty complaints three times live and compare with the recorded runs

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
    except Exception:  # noqa: BLE001
        pass
else:
    while not Path("sada.py").exists() and Path.cwd() != Path.cwd().parent:
        os.chdir("..")  # solutions/ notebooks run from labs/
sys.path.insert(0, os.getcwd())

import itertools

import pandas as pd
import sada as U

U.banner("Lab 3.2")
gold = U.gold()
runs = U.runs_gold()
wide = runs.pivot_table(index="id", columns=["prompt", "run"], values="label", aggfunc="first")
wide.columns = [f"{p}_r{r}" for p, r in wide.columns]
wide = gold.set_index("id")[["variety", "gold", "coder_a", "coder_b"]].join(wide)
print(wide.head(3).to_string())

# %% [markdown]
# ## 1 · Three runs of one prompt: the flip rate (6')
#
# ✏️ **Exercise** · For each prompt, the share of complaints whose three runs do **not** all give the same label.
# Then the accuracy of each run on its own: do the three runs score the same?

# %%
def flip_rate(w: pd.DataFrame, p: str) -> float:
    # BEGIN SOLUTION
    same = (w[f"{p}_r1"] == w[f"{p}_r2"]) & (w[f"{p}_r1"] == w[f"{p}_r3"])
    return round(float(1 - same.mean()), 3)
    # END SOLUTION


flips = U.attempt(lambda: {"P1": flip_rate(wide, "P1"), "P2": flip_rate(wide, "P2")}, "d3_flips")
print("complaints whose label changes between runs:", flips)
for r in (1, 2, 3):
    print(f"P1 run {r}: accuracy {U.accuracy(wide.gold, wide[f'P1_r{r}']):.3f}")
U.check(0 < flips["P1"] < 0.5, "Fahim is neither fixed nor random")

# %% [markdown]
# ## 2 · Kappa between runs (5')
#
# Treat two runs as two coders. ✏️ **Exercise** · Compute kappa for each pair of prompt-1 runs and compare it with
# the kappa of the two human coders (0.829 in Lab 2.1).

# %%
def run_kappas(w: pd.DataFrame, p: str) -> dict:
    # BEGIN SOLUTION
    return {f"r{a}-r{b}": round(U.kappa(w[f"{p}_r{a}"], w[f"{p}_r{b}"]), 3) for a, b in itertools.combinations((1, 2, 3), 2)}
    # END SOLUTION


rk = U.attempt(lambda: run_kappas(wide, "P1"), "d3_run_kappas")
print("prompt 1, run against run:", rk, "| two human coders:", round(U.kappa(wide.coder_a, wide.coder_b), 3))

# %% [markdown]
# ## 3 · The reworded prompt: the shift (6')
#
# Prompt 2 says the same thing in other words and adds a rule for complaints with two problems. ✏️ **Exercise** ·
# Compare prompt 1 run 1 with prompt 2 run 1: the share of complaints whose label changes, and the accuracy of each.
# Is the shift between prompts larger than the shift between runs of one prompt?

# %%
print(U.prompt("P2"))


def prompt_shift(w: pd.DataFrame) -> dict:
    # BEGIN SOLUTION
    return {"between_prompts": round(float((w.P1_r1 != w.P2_r1).mean()), 3),
            "between_runs": round(float((w.P1_r1 != w.P1_r2).mean()), 3),
            "accuracy_P1": round(U.accuracy(w.gold, w.P1_r1), 3), "accuracy_P2": round(U.accuracy(w.gold, w.P2_r1), 3)}
    # END SOLUTION


shift = U.attempt(lambda: prompt_shift(wide), "d3_shift")
print(shift)

# %% [markdown]
# ## 4 · Which documents move (5')
#
# ✏️ **Exercise** · Mark a complaint `unstable` when its six labels (two prompts, three runs) are not all the same.
# Compare the share of unstable complaints where the two **human** coders agreed with the share where they
# disagreed. What does that tell you about the complaints Fahim cannot settle?

# %%
LABEL_COLS = [c for c in wide.columns if c.startswith("P")]


def who_moves(w: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    w = w.assign(unstable=w[LABEL_COLS].nunique(axis=1) > 1, humans_agree=w.coder_a == w.coder_b)
    return w.groupby("humans_agree").unstable.agg(["mean", "size"]).round(3).reset_index()
    # END SOLUTION


try:
    moves = who_moves(wide)
except NotImplementedError:
    moves = pd.DataFrame(U.reference("d3_moves"))
U.keep("d3_moves", moves.to_dict(orient="records"))
print(moves.to_string(index=False))
example = wide[wide[LABEL_COLS].nunique(axis=1) > 2].head(1)
if len(example):
    print("\nA complaint with three different labels:", gold.set_index("id").loc[example.index[0], "text"][:200])

# %% [markdown]
# ## 5 · The majority of three runs (3')
#
# ✏️ **Exercise** · Take the most frequent label of the three prompt-1 runs (run 1 when all three differ) and score
# it. Is the majority more accurate than a single run, and what does it cost?

# %%
def majority(w: pd.DataFrame) -> pd.Series:
    # BEGIN SOLUTION
    def vote(row):
        counts = pd.Series([row.P1_r1, row.P1_r2, row.P1_r3]).value_counts()
        return counts.index[0] if counts.iloc[0] > 1 else row.P1_r1
    return w.apply(vote, axis=1)
    # END SOLUTION


try:
    maj = majority(wide)
except NotImplementedError:
    maj = wide.P1_r1
print(f"majority of three: {U.accuracy(wide.gold, maj):.3f} | one run: {U.accuracy(wide.gold, wide.P1_r1):.3f} | cost: three times the requests")

# %% [markdown]
# ## ✱ Stretch · Twenty complaints, three times, live
#
# With a key, send twenty gold complaints three times (`sample=1, 2, 3` keeps the cache apart) and compute the flip
# rate. Compare it with the recorded flip rate. Without a key the stand-in replays the recorded runs: say so.

# %%
def stretch():
    # BEGIN SOLUTION
    docs = gold.head(20)

    def msgs(d):
        return [{"role": "system", "content": U.prompt("P1")}, {"role": "user", "content": U.batch_message(d)}]

    labels = []
    for s in (1, 2, 3):
        got = {}
        for k in range(0, 20, 10):
            r = U.chat(msgs(docs.iloc[k:k + 10]), temperature=0.7, sample=s)
            got.update(U.parse_labels(r["text"], docs.id.iloc[k:k + 10].tolist()))
        labels.append(got)
    flip = sum(len({lab[i] for lab in labels}) > 1 for i in docs.id) / 20
    print(f"live flip rate on 20: {flip:.2f}" + (" (stand-in: replayed recorded runs)" if U.standin() else ""))
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. Why is a model's agreement with itself an upper limit on its agreement with anyone else?
# 2. A team reports the accuracy of a single run. What is missing?
# 3. Would setting the temperature to 0 make the instability go away?
#
# <details><summary>Answers</summary>
#
# 1. The part of a label that changes from run to run is noise; noise cannot agree with the gold label more than
#    by chance.
# 2. How much that number moves between runs and prompts; a single run hides it.
# 3. It lowers it, but hosted endpoints do not promise identical outputs at temperature 0, and the prompt shift
#    stays. Measure it either way.
# </details>
