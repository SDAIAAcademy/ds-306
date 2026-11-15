# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scikit-learn>=1.6", "python-dotenv>=1.0", "openai>=1.60", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 1.1 · Profile the corpus
#
# Day 1 · Session 1 (Text as a data source) · 25 min.
#
# Sada Citizen Voice Centre received 20,000 complaints in the first ten months of 2026. Before anyone trains a
# model on them, Dr. Ebtisam Al-Dhafiri wants to know what arrived: in which languages, through which channels, how
# long, and how many twice. You build the profile table that the cleaning report of this day opens with.
#
# **AI policy: AI-tutor.** Hints, not solutions.
#
# **Reference state.** `data/complaints.csv.gz` as received. Nothing from another lab.
#
# **Tasks**
# - [ ] 1 · Load the complaints and count what arrived (4')
# - [ ] 2 · Language from the script against the form field (6')
# - [ ] 3 · Length by language and channel (5')
# - [ ] 4 · The exact duplicate rate (5')
# - [ ] 5 · The profile table, saved for the report (5')
# - [ ] ✱ Stretch · Complaints per week and channel: find the week that does not look like the others

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
import re

import numpy as np
import pandas as pd
import sada as U

U.banner("Lab 1.1")
OUT = U.lab_dir("day1")

# %% [markdown]
# ## 1 · Load the complaints and count what arrived (4')
#
# Each row is one message as the centre stored it. `form_lang` is the language the citizen's form was set to, not
# a judgement about the text. Read five rows before you count anything.

# %%
c = U.complaints()
print(len(c), "complaints;", c.received.min().date(), "to", c.received.max().date())
print(c.sample(5, random_state=1)[["id", "channel", "form_lang", "district", "text"]].to_string(max_colwidth=90))
print(c.channel.value_counts().to_string())
U.check(len(c) == 20_000, "20,000 complaints loaded")

# %% [markdown]
# ## 2 · Language from the script against the form field (6')
#
# ✏️ **Exercise** · Write `script_language(text)`: the share of letters that are Arabic (U+0600 to U+06FF, and the
# presentation forms U+FB50 to U+FEFF). Return `"ar"` at 0.8 or more, `"en"` at 0.2 or less, `"mixed"` between.
# Then compare it with `form_lang`. How often does the form field disagree with the text?

# %%
def script_language(text: str) -> str:
    # BEGIN SOLUTION
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return "none"
    arabic = sum("؀" <= ch <= "ۿ" or "ﭐ" <= ch <= "﻿" for ch in letters) / len(letters)
    return "ar" if arabic >= 0.8 else "en" if arabic <= 0.2 else "mixed"
    # END SOLUTION


try:
    c["script"] = c.text.map(script_language)
except NotImplementedError:
    print("↩️  Exercise not done yet: using the course's reference function.")
    c["script"] = c.text.map(U.script_language)
table = pd.crosstab(c.form_lang, c.script, margins=True)
print(table)
wrong = ((c.form_lang == "en") & (c.script == "ar")) | ((c.form_lang == "ar") & (c.script == "en"))
print(f"form field contradicts the script: {wrong.sum()} complaints ({wrong.mean():.1%})")
print("by channel:", (wrong.groupby(c.channel).mean() * 100).round(1).to_dict())
U.check(wrong.mean() > 0.03, "the form field is not a language label")

# %% [markdown]
# 🔍 **Look at** the channel where the form field is wrong most often. Who set that field: the citizen or the app?

# %% [markdown]
# ## 3 · Length by language and channel (5')
#
# ✏️ **Exercise** · Add `chars` (characters) and `words` (whitespace-separated tokens). Then the median of each by
# `script` and `channel`. Which channel writes the shortest complaints, and in which script?

# %%
def lengths(df: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    df = df.assign(chars=df.text.str.len(), words=df.text.str.split().str.len())
    return df.groupby(["script", "channel"])[["chars", "words"]].median().round(0).reset_index()
    # END SOLUTION


try:
    by_length = lengths(c)
except NotImplementedError:
    by_length = pd.DataFrame(U.reference("d1_lengths"))
U.keep("d1_lengths", by_length.to_dict(orient="records"))
print(by_length.to_string(index=False))

# %% [markdown]
# ## 4 · The exact duplicate rate (5')
#
# A citizen who presses "send" twice creates two rows. ✏️ **Exercise** · Write `exact_key(text)`: the text with
# runs of whitespace collapsed and the ends stripped. Count the rows whose key already appeared earlier, and the
# share of the corpus they are.

# %%
def exact_key(text: str) -> str:
    # BEGIN SOLUTION
    return re.sub(r"\s+", " ", text).strip()
    # END SOLUTION


try:
    c["key"] = c.text.map(exact_key)
except NotImplementedError:
    c["key"] = c.text.str.replace(r"\s+", " ", regex=True).str.strip()
c = c.sort_values(["received", "id"])
c["exact_copy"] = c.duplicated("key", keep="first")
rate = c.exact_copy.mean()
print(f"exact copies: {c.exact_copy.sum()} ({rate:.1%}); distinct texts: {c.key.nunique()}")
print("copies by channel (%):", (c.groupby("channel").exact_copy.mean() * 100).round(1).to_dict())
U.check(0.02 < rate < 0.05, "an exact duplicate rate between 2% and 5%")

# %% [markdown]
# ## 5 · The profile table, saved for the report (5')
#
# ✏️ **Exercise** · Fill `profile` with: rows, distinct texts, the exact duplicate rate, the share of each script,
# the share of each channel, the form-field disagreement rate, and the median length in characters. Session 4 adds
# the redaction miss rate to the same report.

# %%
def make_profile(df: pd.DataFrame) -> dict:
    # BEGIN SOLUTION
    return {
        "rows": int(len(df)),
        "distinct_texts": int(df.key.nunique()),
        "exact_duplicate_rate": round(float(df.exact_copy.mean()), 4),
        "script_share": df.script.value_counts(normalize=True).round(4).to_dict(),
        "channel_share": df.channel.value_counts(normalize=True).round(4).to_dict(),
        "form_field_wrong_rate": round(float(wrong.mean()), 4),
        "median_chars": int(df.text.str.len().median()),
    }
    # END SOLUTION


profile = U.attempt(lambda: make_profile(c), "profile")
(OUT / "profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(profile, ensure_ascii=False, indent=1))
U.check(profile["rows"] == 20_000 and "mixed" in profile["script_share"], "profile saved to artifacts/day1/profile.json")

# %% [markdown]
# ## ✱ Stretch · The week that does not look like the others
#
# Count complaints per ISO week and channel. One week in June stands out. Which district, which channel? Session 3
# finds out whether it is many people or one message copied many times.

# %%
def stretch():
    # BEGIN SOLUTION
    weekly = c.groupby([c.received.dt.isocalendar().week, "channel"]).size().unstack(fill_value=0)
    peak = weekly.sum(axis=1).idxmax()
    print("busiest week:", peak, "| complaints:", int(weekly.sum(axis=1).max()), "| median week:", int(weekly.sum(axis=1).median()))
    print(c[c.received.dt.isocalendar().week == peak].district.value_counts().head(3).to_string())
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. A dashboard counts complaints "in English" from `form_lang`. What does it over-count, and why?
# 2. Why is the exact duplicate rate computed before any model is trained?
# 3. Name one group of people the complaint corpus under-represents, and one way to check.
#
# <details><summary>Answers</summary>
#
# 1. Arabic complaints sent from the app with an English form setting: the field records the form, not the text.
# 2. Copies inflate counts and can sit on both sides of a train and test split, which flatters every score.
# 3. Residents who do not write to the centre (older people, people without the app); compare complaint counts per
#    district with the population and with field inspection findings.
# </details>
#
# **Carry forward.** `artifacts/day1/profile.json` opens the profile report of Lab 1.4. If it is missing, Lab 1.4
# uses the reference profile.
