# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scikit-learn>=1.6", "pydantic>=2.8", "python-dotenv>=1.0", "openai>=1.60"]
# ///
# %% [markdown]
# # Setup check
#
# Run this notebook once before Day 1. It checks Python and the packages, the course data, your OpenRouter key with
# one chat request and one embedding request, and the cache. It takes about a minute and uses two free requests.
#
# Nothing here downloads or runs a model on your machine. Without a key, every lab still runs: the scripted stand-in
# replays the course's recorded runs (which are synthetic) and says so.

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
        os.chdir("..")
sys.path.insert(0, os.getcwd())

# %% [markdown]
# ## 1 · Python and packages

# %%
import importlib

print("Python", sys.version.split()[0])
ok_python = sys.version_info >= (3, 11)
missing = []
for name in ("numpy", "pandas", "scipy", "sklearn", "pydantic", "openai", "dotenv", "matplotlib"):
    try:
        mod = importlib.import_module(name)
        print(f"  {name:<10} {getattr(mod, '__version__', '')}")
    except ImportError:
        missing.append(name)
import sada as U

U.check(ok_python, "Python 3.11 or newer")
U.check(not missing, "packages installed" + (f" (missing: {', '.join(missing)})" if missing else ""))

# %% [markdown]
# ## 2 · The course data
#
# The data are synthetic and committed with the repository; `prepare_data.py` rebuilds them with a fixed seed.

# %%
files = ["complaints.csv.gz", "districts.csv", "gold.csv", "pool.csv", "pair40.csv", "redaction_audit.csv",
         "model_runs_gold.csv", "model_labels_all.csv.gz", "inspections.jsonl", "inspections_reference.jsonl",
         "inspection_runs.jsonl", "codebook.md", "prompts/fahim_p1.md", "prompts/extract_v1.md"]
absent = [f for f in files if not (U.DATA / f).exists()]
U.check(not absent, "course data present" + (f" (missing: {', '.join(absent)})" if absent else ""))
c = U.complaints()
U.check(len(c) == 20000, f"{len(c):,} complaints load")
print("first complaint:", c.text.iloc[0][:120])

# %% [markdown]
# ## 3 · Your key: one chat request and one embedding request
#
# Put `OPENROUTER_API_KEY` in `labs/.env` (copy `.env.example`), or in Colab's Secrets panel. Free models allow 20
# requests a minute and 50 a day; a one-time purchase of 10 credits raises that to 1,000 a day.

# %%
U.banner("Setup check")
reply = U.chat([{"role": "system", "content": "Reply with JSON only."},
                {"role": "user", "content": 'Return {"ok": true, "word": "<the Arabic word for water>"}'}], temperature=0)
print("chat:", "stand-in" if reply["standin"] else reply["model"], "·", reply["text"][:120])
vec = U.embed(["ضغط المياه ضعيف", "low water pressure"])
print("embeddings:", vec.shape, "· cosine of the two phrases:", round(float(vec[0] @ vec[1]), 3))
if U.standin():
    print("ℹ️  No hosted model answered: the labs will use the scripted stand-in, which is enough for the course.")
else:
    U.check(True, "a hosted model answered")

# %% [markdown]
# ## 4 · Cache
#
# Identical requests are answered from `labs/cache/`, so running a cell again costs no request. Delete the folder to
# ask the model again.

# %%
print("cache folder:", U.CACHE, "| exists:", U.CACHE.exists())
print("calls this session:", U.CALLS)
print("\nSetup check finished.")
