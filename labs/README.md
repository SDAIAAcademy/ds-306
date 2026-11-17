# Text and Unstructured Data for Data Science: labs

Hands-on notebooks for the SDAIA Academy course **DS-306 Text and Unstructured Data for Data Science**. Every lab
works on the text of **Sada Citizen Voice Centre (مركز صدى لصوت المواطن)**, a fictional municipal complaints
centre that receives complaints in formal Arabic, Gulf dialect and English, and on its labelling instruction
**Fahim (فهيم)**, a prompt for an open-weight language model. Each lab starts from a supplied reference state, so
none depends on an earlier one.

All labs use **free hosted models over an API**, and only for a few requests each. Nothing downloads or runs a model
on your machine: a laptop processor or a Colab CPU runtime is enough. **Without a key every lab still runs**: a
scripted stand-in replays the course's recorded runs and says so in the banner of every notebook.

## Quick start

**1 · Optional: a free OpenRouter key.** Create one at <https://openrouter.ai/keys>. Free models (IDs ending in
`:free`) allow 20 requests a minute and 50 a day; a one-time purchase of 10 credits raises that to 1,000 a day.
Identical requests are replayed from `labs/cache/`, so running a cell again costs nothing.

**2a · Google Colab**
1. Open a notebook from the [course page](https://sdaiaacademy.github.io/ds-306/), or directly:
   `https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/<notebook>.ipynb`.
2. If you have a key, add `OPENROUTER_API_KEY` in the 🔑 **Secrets** panel and turn on notebook access.
3. Run the first cell. It clones this repository and installs `requirements-colab.txt`.

**2b · Local**
```bash
git clone https://github.com/SDAIAAcademy/ds-306
cd ds-306/labs
cp .env.example .env           # optional: paste your key into .env
uv sync                        # creates the environment from pyproject.toml (uv.lock pins every version)
uv run jupyter lab
```
Run `00_setup_check.ipynb` once before Day 1. Pre-work is `00_prework_metrics.ipynb` (about two hours).

**Windows and long folder paths.** If an import fails with "The filename or extension is too long", keep the
environment in a short folder: set `UV_PROJECT_ENVIRONMENT` to a short path (for example a folder at the root of
your drive) before `uv sync`, and set `PYTHONUTF8=1` if Arabic text prints as question marks in a terminal.

## Models and the stand-in

| Setting (`.env`) | Default | Notes |
|---|---|---|
| `SADA_MODEL` | `google/gemma-4-31b-it:free` | the chat model behind Fahim and the extraction prompt |
| `SADA_FALLBACKS` | `google/gemma-4-26b-a4b-it:free` | tried when the first model does not answer |
| `SADA_EMBED_MODEL` | `nvidia/nemotron-3.5-embed-1b:free` | embeddings for Labs 2.3 and 4.3 |
| `LLM_BASE_URL`, `LLM_API_KEY` | OpenRouter | any OpenAI-compatible endpoint: llama.cpp or Ollama serving an Arabic-capable model such as ALLaM 7B |
| `SADA_CACHE` | `1` | `0` sends every request again |
| `SADA_QUICK` | `0` | `1` shrinks samples and bootstrap rounds |
| `SADA_STANDIN` | `0` | `1` uses the stand-in even with a key |

**The stand-in is not a model.** When no key is set, or the endpoint refuses the key, `sada.py` switches to a
scripted stand-in and prints a warning:

- for Fahim's two prompts it replays the **recorded runs** in `data/model_runs_gold.csv` and
  `data/model_labels_all.csv.gz`;
- for the extraction prompt it replays `data/inspection_runs.jsonl`;
- for embeddings it returns hashed character n-grams of the normalised text: vectors that see wording, not meaning.

**The recorded runs are synthetic.** `prepare_data.py` wrote them with the behaviour the course measures (a lower
accuracy on Gulf dialect, run-to-run variation, invented deadlines), so that every number in the decks can be
reproduced without a key. A trainer with a working key can record real runs with the same notebooks and compare;
the labs say where a live call would change a result.

## Notebooks

| Day | Session | Notebook | Model requests with a key |
|---|---|---|---|
| 0 | Setup check | [`00_setup_check.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/00_setup_check.ipynb) | 2 |
| 0 | Pre-work: classification metrics | [`00_prework_metrics.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/00_prework_metrics.ipynb) | 0 |
| 1 | Profile the corpus | [`D1_1_profile.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D1_1_profile.ipynb) | 0 |
| 1 | Normalise Arabic text | [`D1_2_normalise.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D1_2_normalise.ipynb) | 0 |
| 1 | Find near-duplicates | [`D1_3_near_duplicates.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D1_3_near_duplicates.ipynb) | 0 |
| 1 | Redact and measure misses | [`D1_4_redaction.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D1_4_redaction.ipynb) | 0 |
| 2 | Agreement with a partner | [`D2_1_agreement.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D2_1_agreement.ipynb) | 0 |
| 2 | A character n-gram classifier | [`D2_2_sparse.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D2_2_sparse.ipynb) | 0 |
| 2 | An embedding classifier | [`D2_3_embeddings.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D2_3_embeddings.ipynb) | 25 (embeddings) |
| 2 | Compare classifiers fairly | [`D2_4_paired_bootstrap.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D2_4_paired_bootstrap.ipynb) | 0 |
| 3 | Prompted classification | [`D3_1_prompted.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D3_1_prompted.ipynb) | 1, stretch 10 |
| 3 | Ask it twice | [`D3_2_stability.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D3_2_stability.ipynb) | stretch 6 |
| 3 | Dialect gaps | [`D3_3_dialect_gaps.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D3_3_dialect_gaps.ipynb) | 0 |
| 3 | A good annotator? | [`D3_4_annotator.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D3_4_annotator.ipynb) | 0 |
| 4 | Six fields, validated | [`D4_1_extraction.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D4_1_extraction.ipynb) | about 16, stretch 12 |
| 4 | Field-level validation | [`D4_2_field_validation.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D4_2_field_validation.ipynb) | 0 |
| 4 | Structure in text | [`D4_3_clusters.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D4_3_clusters.ipynb) | 16 (embeddings) |
| 4 | Corrected rates | [`D4_4_corrected_rates.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D4_4_corrected_rates.ipynb) | 0 |

The busiest day stays under the free limit of 50 requests. Exercises are marked **✏️ Exercise** and raise
`NotImplementedError` until you fill them in; a safety net then loads the course's reference result from
`data/reference/`, so the cells below still run. Complete versions are in `solutions/`. Cells marked **✱ Stretch**
are optional. Self-checks print ✅ or ❌.

The notebooks are generated from the percent-format sources in `_src/` by `_tools/py2nb.py`
(`uv run python _tools/py2nb.py` from `labs/`), which also writes the solutions. Edit the sources, not the
notebooks. Labs write their outputs to `artifacts/`; delete `artifacts/` and `cache/` before running the course's
`academy check`.

## The case study: Sada Citizen Voice Centre

Synthetic and deterministic (`prepare_data.py`, fixed seed 306), dated January to September 2026. The personal data
in the complaints are invented: names, phone numbers, identity numbers and email addresses that belong to nobody.

| Data | File | Contents |
|---|---|---|
| Complaints | `data/complaints.csv.gz` | 20,000 complaints as received, with personal data: channel, the form's language field, district, text in formal Arabic, Gulf dialect or English, with script noise |
| Districts | `data/districts.csv` | 12 districts with Arabic and English names and population |
| Codebook and prompts | `data/codebook.md`, `data/prompts/` | the codebook (version 3), Fahim's prompts 1 and 2, the extraction prompt |
| Dialect map | `data/dialect_map.csv` | Gulf spelling variants and their canonical forms (Lab 1.2) |
| Redaction audit | `data/redaction_audit.csv` | 500 complaints with every personal value marked (Lab 1.4) |
| Gold set | `data/gold.csv` | 300 redacted complaints: variety, two coders and the adjudicated label |
| Partner sample | `data/pair40.csv` | 40 redacted complaints with two reference coders (Lab 2.1) |
| Training pool | `data/pool.csv` | 3,000 redacted complaints with the intake team's routing labels (noisy) |
| Recorded model runs | `data/model_runs_gold.csv`, `data/model_labels_all.csv.gz` | Fahim on the gold set (two prompts, three runs) and on all complaints (**synthetic**) |
| Inspection reports | `data/inspections.jsonl`, `data/inspections_reference.jsonl`, `data/inspection_runs.jsonl` | 500 reports in Arabic and English, their reference fields and a recorded extraction run (**synthetic**) |
| Reference results | `data/reference/` | the results the safety nets load, and the paid prices of the default model read on 2026-11-15 |
| Capstone corpora | `data/capstone/nadwa/`, `data/capstone/raafid/` | two corpora of 2,575 documents each with a brief, a codebook, a 200-document gold set and recorded runs |

`sada.py` holds the repeated parts: loading the data, the course's normalisation rules, scores with bootstrap
intervals, one cached call to a chat or embedding model with the stand-in, and the reference schema of Lab 4.1.

## Helpers: `sada.py`

| Helper | What it does |
|---|---|
| `complaints()`, `gold()`, `pool()`, `runs_gold()`, `labels_all()`, `jsonl(name)` | load the case data |
| `normalise(text, layers)`, `dialect(text)` | the course's Arabic normalisation rules and the Gulf spelling map |
| `guess_variety(text)` | English by script, Gulf by marker words, else formal Arabic: measured in Lab 3.3 |
| `misses(redacted, pii)` | the marked personal values still readable after redaction |
| `boot_ci(y, p, metric, groups)` | a metric with a 95% bootstrap interval, overall and per group |
| `chat(messages, ...)`, `embed(texts)` | one cached, paced, retried request; the stand-in when no key works |
| `parse_labels(text, ids)` | labels from Fahim's reply; anything outside the codebook becomes `None` |
| `prices()`, `cost_per_1000(...)` | the paid endpoint's price per token and the cost of 1,000 documents |

## Follow-up

`followup/README.md`: the audit of one labelling process, due four weeks after the course.
