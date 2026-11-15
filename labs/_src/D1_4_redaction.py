# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scikit-learn>=1.6", "python-dotenv>=1.0", "openai>=1.60", "tabulate>=0.9"]
# ///
# %% [markdown]
# # Lab 1.4 · Redact and measure misses
#
# Day 1 · Session 4 (Redacting personal data) · 25 min.
#
# Before a complaint reaches a hosted model, or a colleague's laptop, its phone numbers, identity numbers, emails
# and names are masked. Ashwaq Al-Jabr, the centre's data protection officer, will not accept "we ran a regex":
# she wants the share of personal data the regex **missed**, measured on 500 complaints a person marked by hand.
#
# **AI policy: AI-tutor.**
#
# **Reference state.** `data/redaction_audit.csv` (500 complaints, each with the personal data a person marked)
# and, for the report, `artifacts/day1/profile.json` from Lab 1.1 or the reference profile.
#
# **Tasks**
# - [ ] 1 · Read what leaks in the audited sample (4')
# - [ ] 2 · Phone numbers in every format (7')
# - [ ] 3 · Identity numbers and emails (4')
# - [ ] 4 · Names after cue words (5')
# - [ ] 5 · The miss rate and the profile report (5')
# - [ ] ✱ Stretch · Names with no cue word: how many are there, and what would catch them?

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

import pandas as pd
import sada as U

U.banner("Lab 1.4")
OUT = U.lab_dir("day1")
audit = U.redaction_audit()
marked = [p for ps in audit.pii for p in ps]
print(len(audit), "audited complaints;", len(marked), "marked values:", pd.Series([p["type"] for p in marked]).value_counts().to_dict())


def miss_table(redact) -> pd.DataFrame:
    """Marked values still readable after `redact`, by type."""
    rows = []
    for text, pii in zip(audit.text, audit.pii):
        missed = U.misses(redact(text), pii)
        rows += [{"type": p["type"], "script": U.script_language(text), "missed": p in missed} for p in pii]
    return pd.DataFrame(rows)


# %% [markdown]
# ## 1 · Read what leaks in the audited sample (4')
#
# A first attempt that many teams ship: Saudi mobile numbers as `05` followed by eight digits. Run it and read the
# miss rate, then read five of the numbers it missed. What do they have in common?

# %%
def naive(text: str) -> str:
    return re.sub(r"05\d{8}", "[PHONE]", text)


t = miss_table(naive)
phones = t[t.type == "phone"]
print(f"naive pattern: {phones.missed.mean():.1%} of phone numbers missed")
missed_examples = [p["value"] for text, pii in zip(audit.text, audit.pii)
                   for p in U.misses(naive(text), pii) if p["type"] == "phone"][:5]
print(missed_examples)

# %% [markdown]
# ## 2 · Phone numbers in every format (7')
#
# ✏️ **Exercise** · Write `redact_phones(text)`. One pattern must catch: `0551234567`, `+966 55 123 4567`,
# `966551234567`, `055-123-4567`, `055 123 4567`, and the same in Arabic-Indic digits (٠٥٥١٢٣٤٥٦٧). Use a digit
# class that holds both systems, `[0-9٠-٩]`, rather than translating the text: the redacted text must stay as the
# citizen wrote it.

# %%
D = "[0-9٠-٩]"


def redact_phones(text: str) -> str:
    # BEGIN SOLUTION
    pattern = rf"(?:\+?(?:966|٩٦٦)[\s\-]?|[0٠])?[5٥]{D}(?:[\s\-]?{D}){{7}}(?!{D})"
    return re.sub(pattern, "[PHONE]", text)
    # END SOLUTION


try:
    redact_phones("0551234567")
except NotImplementedError:
    print("↩️  Exercise not done yet: using a reference pattern.")

    def redact_phones(text):
        return re.sub(rf"(?:\+?(?:966|٩٦٦)[\s\-]?|[0٠])?[5٥]{D}(?:[\s\-]?{D}){{7}}(?!{D})", "[PHONE]", text)

for s in ["0551234567", "+966 55 123 4567", "966551234567", "055-123-4567", "055 123 4567", "٠٥٥١٢٣٤٥٦٧"]:
    U.check(redact_phones(f"x {s} y") == "x [PHONE] y", s)

# %% [markdown]
# ## 3 · Identity numbers and emails (4')
#
# A national identity number or a resident's number has ten digits and starts with 1 or 2. ✏️ **Exercise** · Write
# `redact_ids_emails(text)`. Run it **after** the phone pattern: think about which order avoids a phone number being
# half-masked as an identity number.

# %%
def redact_ids_emails(text: str) -> str:
    # BEGIN SOLUTION
    text = re.sub(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "[EMAIL]", text)
    return re.sub(rf"(?<!{D})[12١٢]{D}{{9}}(?!{D})", "[ID]", text)
    # END SOLUTION


try:
    redact_ids_emails("x")
except NotImplementedError:
    def redact_ids_emails(text):
        text = re.sub(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "[EMAIL]", text)
        return re.sub(rf"(?<!{D})[12١٢]{D}{{9}}(?!{D})", "[ID]", text)
U.check(redact_ids_emails("ID number 1234567890, sara.12@mail.example") == "ID number [ID], [EMAIL]", "identity number and email")

# %% [markdown]
# ## 4 · Names after cue words (5')
#
# A name has no fixed shape, but citizens introduce it: اسمي, أنا, معك, مقدم البلاغ, "My name is", "Regards,".
# ✏️ **Exercise** · Write `redact_names(text)`: after a cue word, mask the next two words (Arabic letters, or two
# capitalised Latin words). Keep the cue word: it tells a reader that a name was there.

# %%
AR_WORD = "[ء-ي٠-٩]+"
CUES_AR = ["اسمي", "أنا المواطن", "انا المواطن", "أنا", "انا", "معك", "مقدم البلاغ:"]
CUES_EN = ["My name is", "Regards,"]


def redact_names(text: str) -> str:
    # BEGIN SOLUTION
    for cue in CUES_AR:
        text = re.sub(rf"({re.escape(cue)}) {AR_WORD} {AR_WORD}", r"\1 [NAME]", text)
    for cue in CUES_EN:
        text = re.sub(rf"({re.escape(cue)}) [A-Z][a-z]+ [A-Z][\w\-]+", r"\1 [NAME]", text)
    return text
    # END SOLUTION


def redact(text: str) -> str:
    try:
        return redact_names(redact_ids_emails(redact_phones(text)))
    except NotImplementedError:
        return U_redact(text)


def U_redact(text: str) -> str:
    text = redact_ids_emails(redact_phones(text))
    for cue in CUES_AR:
        text = re.sub(rf"({re.escape(cue)}) {AR_WORD} {AR_WORD}", r"\1 [NAME]", text)
    for cue in CUES_EN:
        text = re.sub(rf"({re.escape(cue)}) [A-Z][a-z]+ [A-Z][\w\-]+", r"\1 [NAME]", text)
    return text


print(redact("السلام عليكم، اسمي سارة الشهري، جوالي ٠٥٥١٢٣٤٥٦٧"))
print(redact("My name is Fahad Al-Harbi. Call me on +966 55 123 4567."))

# %% [markdown]
# ## 5 · The miss rate and the profile report (5')
#
# ✏️ **Exercise** · Measure the misses of the full `redact` on the audited sample: overall, by type and by script.
# Then write `artifacts/day1/profile_report.md`: the profile from Lab 1.1 and the miss rates. This file is the
# evidence of the day's cleaning script.

# %%
def miss_summary() -> dict:
    # BEGIN SOLUTION
    t = miss_table(redact)
    return {"marked": int(len(t)), "missed": int(t.missed.sum()), "miss_rate": round(float(t.missed.mean()), 4),
            "by_type": t.groupby("type").missed.mean().round(4).to_dict(),
            "by_script": t.groupby("script").missed.mean().round(4).to_dict()}
    # END SOLUTION


summary = U.attempt(miss_summary, "d1_misses")
print(json.dumps(summary, indent=1))
try:
    profile = json.loads((OUT / "profile.json").read_text(encoding="utf-8"))
except FileNotFoundError:
    profile = U.reference("profile")
lines = ["# Complaint corpus: profile and redaction", "", "## Profile", ""]
lines += [f"- {k}: {v}" for k, v in profile.items()]
lines += ["", "## Redaction", "", f"Audited sample: 500 complaints, {summary['marked']} marked values.",
          f"Missed after redaction: {summary['missed']} ({summary['miss_rate']:.1%}).", ""]
lines += [f"- {k}: {v:.1%} missed" for k, v in summary["by_type"].items()]
(OUT / "profile_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
U.check(summary["by_type"]["phone"] < 0.02, "fewer than 2% of phone numbers missed")
U.check(summary["miss_rate"] < phones.missed.mean(), "the full redaction misses less than the naive pattern")

# %% [markdown]
# 🔍 **Look at** the type with the highest miss rate. Is it a pattern you can still fix, or the limit of patterns?

# %% [markdown]
# ## ✱ Stretch · Names with no cue word
#
# List the names still visible after `redact`. How do they appear in the text? Name one method that would catch
# them and the cost it brings (a list of common names, a named-entity model, a person).

# %%
def stretch():
    # BEGIN SOLUTION
    left = [(p["value"], text[:70]) for text, pii in zip(audit.text, audit.pii)
            for p in U.misses(redact(text), pii) if p["type"] == "name"]
    print(len(left), "names left, for example:")
    for v, t in left[:5]:
        print(" ", v, "|", t)
    # END SOLUTION


try:
    stretch()
except NotImplementedError:
    print("Stretch not attempted.")

# %% [markdown]
# ## Checkpoint
#
# 1. The regex found no phone number in a complaint. Does the complaint hold none?
# 2. Why measure misses on a sample a person marked, instead of counting the matches?
# 3. The complaint text is classified Restricted. Can the redacted text go to a free hosted model?
#
# <details><summary>Answers</summary>
#
# 1. No: zero matches is a statement about the pattern, not about the text. Only the audited sample says how much
#    the pattern misses.
# 2. Matches count what the pattern recognises; the misses are what it does not, and only a person's marking shows
#    them.
# 3. Not by itself: the classification of the redacted text must be decided again (redaction can lower the level),
#    and the Generative AI Guidelines for government limit hosted tools to data classified Public. Otherwise use a
#    locally served model.
# </details>
#
# **Carry forward.** Every labelled file from Day 2 on is redacted text: `[PHONE]`, `[ID]`, `[EMAIL]`, `[NAME]`.
