# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scikit-learn>=1.6", "python-dotenv>=1.0", "openai>=1.60", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 3.1 · Prompted classification
#
# Day 3 · Session 1 (Prompted classification) · 25 min.
#
# Fahim is the centre's labelling instruction: the codebook turned into a prompt for an open-weight model that has
# never seen Sada's training data. You send it ten gold complaints, parse every reply, then score its full recorded
# run on the gold set by language and work out what labelling a thousand complaints costs.
#
# **AI policy: models are measured here.** The labels come from the model; the judgement is yours.
#
# **Model access.** With a free key in `labs/.env`, task 2 calls `google/gemma-4-31b-it:free` on OpenRouter (one
# request). Without one, the scripted stand-in replays the course's **recorded run**, which is synthetic: it was
# written by `prepare_data.py` to imitate the behaviour this day measures. The banner says which answered.
#
# **Reference state.** `data/gold.csv`, `data/prompts/fahim_p1.md`, `data/model_runs_gold.csv`. Nothing from Day 2.
#
# **Tasks**
# - [ ] 1 · The prompt: codebook, labels, JSON (6')
# - [ ] 2 · Classify a batch of ten (5')
# - [ ] 3 · Load the recorded run and its version record (4')
# - [ ] 4 · Score it on the gold set by language (6')
# - [ ] 5 · Cost per thousand documents (4')
# - [ ] ✱ Stretch · One document per call against batches of ten: do the labels change?

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

import json
from datetime import date

import pandas as pd
import sada as U

U.banner("Lab 3.1")
OUT = U.lab_dir("day3")
gold = U.gold()

# %% [markdown]
# ## 1 · The prompt: codebook, labels, JSON (6')
#
# Read prompt 1. It names the eight codes exactly, defines each in one line, says what to do with the redaction
# tags and fixes the output format. ✏️ **Exercise** · Write `messages(prompt_text, docs)`: a system message with the
# prompt and a user message with one line per complaint, `id: text` (`U.batch_message(docs)` builds those lines).
# Then fill the version record that will travel with every label.

# %%
P1 = U.prompt("P1")
print(P1)


def messages(prompt_text: str, docs: pd.DataFrame) -> list[dict]:
    # BEGIN SOLUTION
    return [{"role": "system", "content": prompt_text}, {"role": "user", "content": U.batch_message(docs)}]
    # END SOLUTION


try:
    messages(P1, gold.head(1))
except NotImplementedError:
    print("↩️  Exercise not done yet: using the reference message builder.")

    def messages(prompt_text, docs):
        return [{"role": "system", "content": prompt_text}, {"role": "user", "content": U.batch_message(docs)}]

VERSION = {"model": U.CHAT_MODEL, "prompt": "P1", "prompt_sha": U.sha(P1), "temperature": 0.7, "batch_size": 10,
           "date": date.today().isoformat()}
print(VERSION)

# %% [markdown]
# ## 2 · Classify a batch of ten (5')
#
# ✏️ **Exercise** · Send the first ten gold complaints with `U.chat(messages(...), temperature=0.7)`. Parse the
# reply with `U.parse_labels(reply["text"], ids)`: an id that is missing, or a label outside the codebook, becomes
# `None`, never a guess. How many of the ten came back usable, and how many are right?

# %%
batch = gold.head(10)


def classify(docs: pd.DataFrame, sample: int = 0) -> tuple[dict, dict]:
    # BEGIN SOLUTION
    reply = U.chat(messages(P1, docs), temperature=0.7, sample=sample)
    return reply, U.parse_labels(reply["text"], docs.id.tolist())
    # END SOLUTION


try:
    reply, labels = classify(batch)
except NotImplementedError:
    reply = U.chat(messages(P1, batch), temperature=0.7)
    labels = U.parse_labels(reply["text"], batch.id.tolist())
print("answered by:", "stand-in (recorded, synthetic)" if reply["standin"] else reply["model"])
live = batch.assign(label=batch.id.map(labels))
print(live[["id", "variety", "gold", "label"]].to_string(index=False))
print(f"usable {live.label.notna().sum()} of 10 | right {int((live.label == live.gold).sum())} | tokens in {reply['prompt_tokens']}, out {reply['completion_tokens']}")
U.check(live.label.notna().sum() >= 9, "at least nine usable labels")

# %% [markdown]
# ## 3 · Load the recorded run and its version record (4')
#
# The full run of prompt 1 over the 300 gold complaints was recorded once, in batches of ten, with its version
# record in every row. Labelling the gold set again would cost 30 requests, more than half of a free day.

# %%
runs = U.runs_gold()
run1 = runs[(runs.prompt == "P1") & (runs.run == 1)].merge(gold[["id", "variety", "gold"]], on="id")
print(run1[["model", "prompt", "run", "temperature", "batch_size", "recorded"]].drop_duplicates().to_string(index=False))
U.check(len(run1) == 300 and run1.label.notna().all(), "300 recorded labels, none missing")

# %% [markdown]
# ## 4 · Score it on the gold set by language (6')
#
# ✏️ **Exercise** · Accuracy with bootstrap intervals by variety (`U.boot_ci`), and macro F1 overall. Put the
# numbers next to the sparse classifier's from Day 2 (0.930 overall in the course's run). Which variety is weakest?

# %%
def score():
    # BEGIN SOLUTION
    ci = U.boot_ci(run1.gold, run1.label, U.accuracy, groups=run1.variety)
    return ci, round(U.macro_f1(run1.gold, run1.label), 3)
    # END SOLUTION


try:
    ci, f1 = score()
except NotImplementedError:
    ci, f1 = U.boot_ci(run1.gold, run1.label, U.accuracy, groups=run1.variety), round(U.macro_f1(run1.gold, run1.label), 3)
print(ci.to_string(index=False), "\nmacro F1:", f1)
U.keep("d3_prompted_ci", ci.to_dict(orient="records"))
U.check(ci.set_index("group").loc["gulf", "value"] < ci.set_index("group").loc["msa", "value"], "Gulf complaints score lower than MSA")

# %% [markdown]
# ## 5 · Cost per thousand documents (4')
#
# The free endpoint costs no money but limits requests. At volume, the paid endpoint of the same model charges per
# token (`U.prices()`, read from OpenRouter's public list on 2026-11-15). ✏️ **Exercise** · From the recorded
# tokens per complaint, compute for 1,000 complaints: requests at ten a batch, days on a free account without
# credits (50 requests a day), and dollars on the paid endpoint.

# %%
def cost() -> dict:
    # BEGIN SOLUTION
    p_in, p_out = run1.prompt_tokens.mean(), run1.completion_tokens.mean()
    requests = 1000 / 10
    return {"tokens_in_per_doc": round(p_in, 1), "tokens_out_per_doc": round(p_out, 1), "requests": requests,
            "free_days_without_credits": requests / 50, "usd_paid_endpoint": U.cost_per_1000(p_in, p_out)}
    # END SOLUTION


c = U.attempt(cost, "d3_cost")
print(json.dumps(c, indent=1))
(OUT / "version_P1.json").write_text(json.dumps({**VERSION, "cost_per_1000": c}, indent=1), encoding="utf-8")

# %% [markdown]
# 🔍 **Look at** the tokens in per complaint: most of them are the prompt, shared by the ten complaints of a
# batch. What happens to the cost with batches of one?

# %% [markdown]
# ## ✱ Stretch · One complaint per call
#
# Send the same ten complaints one per call and compare the labels with the batch. With the stand-in both replay the
# same recorded run, so the stretch only shows something with a working key: say so if that is your case.

# %%
def stretch():
    # BEGIN SOLUTION
    single = {}
    for _, row in batch.iterrows():
        r = U.chat(messages(P1, batch[batch.id == row.id]), temperature=0.7)
        single.update(U.parse_labels(r["text"], [row.id]))
    same = sum(single[i] == labels[i] for i in batch.id)
    print(f"same label in {same} of 10" + (" (stand-in: replayed, not measured)" if U.standin() else ""))
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. Why does the parser return `None` instead of the nearest category for a label outside the codebook?
# 2. Which fields of the version record would you need to reproduce a label set a year from now?
# 3. Fahim scores below the sparse classifier. Name one situation where it would still be the better choice.
#
# <details><summary>Answers</summary>
#
# 1. A guessed label would be counted as the model's answer; `None` keeps the failure visible and countable.
# 2. The model identifier, the prompt text (or its hash), the settings (temperature, batch size) and the date: the
#    same model name can change behind an endpoint.
# 3. A new category, a new corpus or a capstone with no training labels: Fahim needs a codebook, not 3,000 labelled
#    complaints.
# </details>
#
# **Carry forward.** `artifacts/day3/version_P1.json`, the version record with the cost.
