<!-- academy:title -->
# Text and Unstructured Data for Data Science

النصوص والبيانات غير المهيكلة في علم البيانات

Data Science Track · SDAIA Academy · DS-306 · Level 300

Turn Arabic and English text into measurements you can defend: clean and redact a corpus, score sparse, embedding and prompted classifiers on one gold set, test a language model as an annotator and correct the estimates its labels feed

Participants turn text into measurements they can defend. For the Sada Citizen Voice Centre, a fictional agency receiving complaints in Arabic and English, they normalise Arabic script and dialect spellings, redact personal data, build sparse and embedding-based classifiers, classify and extract fields with a prompted open-weight language model, and treat every model-made label as a measurement: agreement with a human gold set, stability across runs and prompts, gaps between dialects and the bias it carries into estimates. Writing labelling guidelines and adjudication are in DS-311.

**Format:** Intensive: 4 teaching days of four sessions and a capstone day, with guided pre-work and a tracked follow-up task

**Course page:** https://sdaiaacademy.github.io/ds-306/
<!-- /academy:title -->

## Outcomes

| | Outcomes | Level | Evidence |
|---|---|---|---|
| LO1 | Prepare a bilingual corpus by normalising script, removing near-duplicates and redacting personal data, given 20,000 raw complaints with mixed scripts and embedded phone numbers | Applied | a cleaning script and a profile report with the redaction miss rate |
| LO2 | Implement sparse, embedding-based and prompted classifiers and score them on one held-out gold set, given a training pool and a fixed budget of model calls | Applied | results with intervals by language and cost per thousand documents |
| LO3 | Implement schema-constrained field extraction and measure field-level precision and recall, given 500 synthetic inspection reports with reference extractions | Applied | an extraction script and a per-field validation report |
| LO4 | Compute a district complaint rate from model labels corrected with a human-labelled sample and compare it with the uncorrected rate, given model labels for all complaints and a 300-document human gold set with measured agreement | Applied | a table of naive and corrected rates with intervals |
| LO5 | Evaluate a language model as an annotator and decide whether its labels can feed a downstream estimate, given labels from two prompts and three runs over the gold set | Performance | a reliability memo on agreement, stability, dialect gaps and the decision |
| LO6 | Design a text-measurement pipeline for a stakeholder question and defend each measurement choice, given a supplied corpus and a written brief | Performance | a repository and report defended live |

<!-- academy:units -->
## Units

| Unit | Title | Sessions | Slides |
|---|---|---|---|
| Day 1 | Text into clean data | Text as a data source; Preparing Arabic text; Near-duplicates; Redacting personal data | [`slides/day1.html`](slides/day1.html) |
| Day 2 | Labels you can trust | Gold sets and agreement; Sparse baselines; Embeddings as features; Comparing classifiers fairly | [`slides/day2.html`](slides/day2.html) |
| Day 3 | Language models as instruments | Prompted classification; Ask it twice; Dialect gaps; Is the model a good annotator | [`slides/day3.html`](slides/day3.html) |
| Day 4 | From documents to tables | Schema-constrained extraction; Field-level validation; Structure in text; Errors downstream | [`slides/day4.html`](slides/day4.html) |
| Capstone | Capstone: a text measurement defended live |  | [`slides/capstone.html`](slides/capstone.html) |
<!-- /academy:units -->

## Case study

**Sada Citizen Voice Centre (مركز صدى لصوت المواطن)** is a fictional government centre that receives complaints about municipal services in Modern Standard Arabic, Gulf dialect and English. Every lab works on its synthetic data, written by `labs/prepare_data.py` with a fixed seed:

| Data | What it holds | Used in |
|---|---|---|
| 20,000 complaints | As received, with personal data: 12 districts, five channels, three language varieties, copies and one campaign | Day 1, Lab 4.4 |
| A redaction audit | 500 complaints whose personal data a person marked | Lab 1.4 |
| A codebook and a gold set | Eight categories; 300 redacted complaints coded by two people, with the adjudicated label | Days 2 to 4 |
| A training pool | 3,000 redacted complaints with the intake team's routing labels (not checked) | Labs 2.2, 2.3 |
| Recorded runs of Fahim | The centre's prompted labelling instruction on an open-weight model: two prompts by three runs on the gold set, one run on all complaints | Days 3 and 4 |
| 500 inspection reports | Arabic and English, with reference extractions of six fields and one recorded extraction run | Labs 4.1, 4.2 |
| Two capstone corpora | Nadwa Public Libraries Network and Raafid Social Support Office: documents, a gold set, recorded runs, a codebook and a brief | Capstone |

The recorded model runs are synthetic too: they imitate behaviours the course measures (a dialect gap, unstable answers on two-topic complaints, invented deadlines). With a free key, the labs' live cells call a hosted model and the results can be compared with the recorded runs. Without a key, a scripted stand-in replays the recorded runs and says so on screen.

## How the course runs

Four teaching days of four 50-minute sessions: about 20 to 25 minutes of ideas, a checkpoint, then a 25-minute lab. Every lab starts from a supplied file, so none depends on another lab of the same day. Pre-work (two hours) is the notebook `labs/00_prework_metrics.ipynb` on classification metrics, with an entry quiz on the practice page; the follow-up task is the audit of one labelling process (`labs/followup/README.md`).

**AI policy.** AI-off for the supervised checks and for the human gold labels (Lab 2.1). An AI tutor may hint at cleaning and classifier code without writing it. Language models are what the labs measure. AI is allowed in full in the capstone, which is defended live.

**Responsible use.** Identifiers are redacted before any text reaches a model; the classification of the data decides whether text may go to a hosted model at all (the labs only send synthetic text); dialect gaps are reported so that no group is under-counted; model and prompt versions are kept with every label set.

<!-- academy:labs -->
## Labs

Every lab is a notebook in `labs/`. Open it in Google Colab from the course page, or run it locally with `uv`. Exercises raise `NotImplementedError` until they are done; the reference versions are in `labs/solutions/`.

| | Session | Lab | File |
|---|---|---|---|
| 1.1 | Day 1 · Session 1 | Profile the corpus | [`D1_1_profile.ipynb`](labs/D1_1_profile.ipynb) |
| 1.2 | Day 1 · Session 2 | Normalise Arabic text | [`D1_2_normalise.ipynb`](labs/D1_2_normalise.ipynb) |
| 1.3 | Day 1 · Session 3 | Find near-duplicates | [`D1_3_near_duplicates.ipynb`](labs/D1_3_near_duplicates.ipynb) |
| 1.4 | Day 1 · Session 4 | Redact and measure misses | [`D1_4_redaction.ipynb`](labs/D1_4_redaction.ipynb) |
| 2.1 | Day 2 · Session 1 | Agreement with a partner | [`D2_1_agreement.ipynb`](labs/D2_1_agreement.ipynb) |
| 2.2 | Day 2 · Session 2 | A character n-gram classifier | [`D2_2_sparse.ipynb`](labs/D2_2_sparse.ipynb) |
| 2.3 | Day 2 · Session 3 | An embedding classifier | [`D2_3_embeddings.ipynb`](labs/D2_3_embeddings.ipynb) |
| 2.4 | Day 2 · Session 4 | Compare classifiers fairly | [`D2_4_paired_bootstrap.ipynb`](labs/D2_4_paired_bootstrap.ipynb) |
| 3.1 | Day 3 · Session 1 | Prompted classification | [`D3_1_prompted.ipynb`](labs/D3_1_prompted.ipynb) |
| 3.2 | Day 3 · Session 2 | Ask it twice | [`D3_2_stability.ipynb`](labs/D3_2_stability.ipynb) |
| 3.3 | Day 3 · Session 3 | Dialect gaps | [`D3_3_dialect_gaps.ipynb`](labs/D3_3_dialect_gaps.ipynb) |
| 3.4 | Day 3 · Session 4 | A good annotator? | [`D3_4_annotator.ipynb`](labs/D3_4_annotator.ipynb) |
| 4.1 | Day 4 · Session 1 | Six fields, validated | [`D4_1_extraction.ipynb`](labs/D4_1_extraction.ipynb) |
| 4.2 | Day 4 · Session 2 | Field-level validation | [`D4_2_field_validation.ipynb`](labs/D4_2_field_validation.ipynb) |
| 4.3 | Day 4 · Session 3 | Structure in text | [`D4_3_clusters.ipynb`](labs/D4_3_clusters.ipynb) |
| 4.4 | Day 4 · Session 4 | Corrected rates | [`D4_4_corrected_rates.ipynb`](labs/D4_4_corrected_rates.ipynb) |
<!-- /academy:labs -->

## Capstone

A text-measurement project on a supplied or public corpus, in a public repository whose README reports the gold set, agreement, model and extraction results and a reliability memo; eight-minute defence plus questions

**Submission:** a link to a public GitHub repository: the cleaning and redaction script with its miss rate, the gold set and agreement, the classifier and extraction results with model and prompt versions, the saved model outputs and run logs, the corrected estimate and the reliability memo, with a lock file and a README that reports all of them.

**Defence:** eight minutes, then seven minutes in which the assessor chooses ten documents for you to label live from your codebook and asks you to explain any disagreement with your gold set.

**Rubric:** preparation and redaction 25, gold set and agreement 20, models and extraction 20, reliability memo 25, reproducibility 10.

**Assessment:** AI-off entry and exit checks on agreement, representation choice and field validation (20%), the capstone rubric (60%) and the live defence (20%). Passing: 70% overall and at least 60% on both the capstone rubric and the supervised check.

## Prerequisites

- DS-202 Data Acquisition, Preparation and Quality
- DS-204 Machine Learning for Tabular Data: Baselines and Validation
- Calls a web API from Python and parses JSON

<!-- academy:tools -->
## Tools

Each line is a capability; the examples are interchangeable.

- **Language model through a chat-completions style endpoint:** a locally served Arabic-capable open-weight model such as ALLaM 7B, a free hosted open-weight model, any commercial API
- **Local model serving:** llama.cpp, Ollama
- **Arabic text processing:** CAMeL Tools, course-provided normalisation rules
- **Embeddings, classifiers and clustering:** sentence-transformers, scikit-learn, BERTopic
- **Schema validation for extracted fields:** Pydantic, JSON Schema
- **Annotation:** Label Studio, doccano
<!-- /academy:tools -->

<!-- academy:sources -->
## Sources

### National references

- [Personal Data Protection Law (SDAIA)](https://sdaia.gov.sa/en/SDAIA/about/Documents/PersonalDataProtectionLaw.pdf)
- [Implementing Regulation of the Personal Data Protection Law (SDAIA)](https://sdaia.gov.sa/en/SDAIA/about/Documents/ImplementingRegulationPersonalDataProtectionLaw.pdf)
- [Data Classification Policy (National Data Management Office, SDAIA)](https://sdaia.gov.sa/en/SDAIA/about/Documents/DataClassificationPolicy.pdf)
- [Generative AI Guideline for Government (SDAIA)](https://sdaia.gov.sa/en/SDAIA/about/Files/GenAIGuidelinesForGovernmentENCompressed.pdf)
- [Generative AI Guideline for Public (SDAIA)](https://sdaia.gov.sa/en/SDAIA/about/Files/GenerativeAIPublicEN.pdf)
- [AI Bias Reference Guide, first edition (SDAIA, May 2026)](https://sdaia.gov.sa/en/MediaCenter/KnowledgeCenter/ResearchLibrary/EN-AI-BIAS.pdf)

### Models and endpoints

- [OpenRouter: API rate limits, including free models](https://openrouter.ai/docs/api-reference/limits)
- [OpenRouter: Embeddings API](https://openrouter.ai/docs/api-reference/embeddings)
- [OpenRouter: Gemma 4 31B Instruct (Google), model page and prices](https://openrouter.ai/google/gemma-4-31b-it)
- [OpenRouter: list of embedding models](https://openrouter.ai/api/v1/embeddings/models)
- [ALLaM 7B Instruct (preview), model card on the Hugging Face Hub](https://huggingface.co/humain-ai/ALLaM-7B-Instruct-preview)
- [llama.cpp](https://github.com/ggml-org/llama.cpp)
- [Ollama](https://ollama.com/)

### Arabic text and near-duplicates

- [CAMeL Tools documentation: utils.normalize](https://camel-tools.readthedocs.io/en/latest/api/utils/normalize.html)
- [camel-tools on PyPI](https://pypi.org/project/camel-tools/)
- [Unicode Standard Annex 15: Unicode Normalization Forms](https://unicode.org/reports/tr15/)
- [Python documentation: unicodedata](https://docs.python.org/3/library/unicodedata.html)
- [Leskovec, Rajaraman and Ullman: Mining of Massive Datasets, chapter 3, Finding Similar Items](http://www.mmds.org/)

### Labels, classifiers and estimates

- [scikit-learn: cohen_kappa_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html)
- [scikit-learn: TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- [scikit-learn: clustering](https://scikit-learn.org/stable/modules/clustering.html)
- [Sentence Transformers documentation](https://www.sbert.net/)
- [BERTopic documentation](https://maartengr.github.io/BERTopic/)
- [Angelopoulos, Bates, Fannjiang, Jordan and Zrnic (2023): Prediction-Powered Inference](https://arxiv.org/abs/2301.09633)
- [Calderon, Reichart and Dror (2025): The Alternative Annotator Test for LLM-as-a-Judge](https://arxiv.org/abs/2501.10970)
- [Label Studio](https://labelstud.io/)
- [doccano](https://github.com/doccano/doccano)

### Extraction

- [Pydantic documentation: JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/)
- [JSON Schema](https://json-schema.org/)
<!-- /academy:sources -->

## National references

- Personal Data Protection Law and its implementing regulations: https://sdaia.gov.sa/en/SDAIA/about/Documents/PersonalDataProtectionLaw.pdf and https://sdaia.gov.sa/en/SDAIA/about/Documents/ImplementingRegulationPersonalDataProtectionLaw.pdf
- NDMO Data Classification Policy: https://sdaia.gov.sa/en/SDAIA/about/Documents/DataClassificationPolicy.pdf
- SDAIA Generative AI Guidelines: https://sdaia.gov.sa/en/SDAIA/about/Files/GenAIGuidelinesForGovernmentENCompressed.pdf (government) and https://sdaia.gov.sa/en/SDAIA/about/Files/GenerativeAIPublicEN.pdf (public)
- SDAIA AI Bias Reference Guide: https://sdaia.gov.sa/en/MediaCenter/KnowledgeCenter/ResearchLibrary/EN-AI-BIAS.pdf
