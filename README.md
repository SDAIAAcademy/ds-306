<!-- academy:title -->
# Text and Unstructured Data for Data Science

النصوص والبيانات غير المهيكلة في علم البيانات

Data Science Track · SDAIA Academy · DS-306 · Level 300

REPLACE: one line under the title: what participants can do after the course

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
| Capstone | Capstone project presentations |  | [`slides/capstone.html`](slides/capstone.html) |
<!-- /academy:units -->

## Case study

**REPLACE: the name of the fictional organisation every lab works on.** REPLACE: two sentences on the case study and its synthetic data

<!-- academy:labs -->
## Labs

Every lab is a notebook in `labs/`. Open it in Google Colab from the course page, or run it locally with `uv`. Exercises raise `NotImplementedError` until they are done; the reference versions are in `labs/solutions/`.

| | Session | Lab | File |
|---|---|---|---|
| 1.1 | Day 1 · Session 1 | Profile the corpus by language, length, channel and duplicate rate | [`D1_1_profile_corpus_language.ipynb`](labs/D1_1_profile_corpus_language.ipynb) |
| 1.2 | Day 1 · Session 2 | Normalise letter variants and diacritics and measure the vocabulary change | [`D1_2_normalise_letter_variants.ipynb`](labs/D1_2_normalise_letter_variants.ipynb) |
| 1.3 | Day 1 · Session 3 | Find near-duplicate complaints with character shingles and decide which to keep | [`D1_3_find_near_duplicate.ipynb`](labs/D1_3_find_near_duplicate.ipynb) |
| 1.4 | Day 1 · Session 4 | Mask phone numbers, identity numbers and names and measure misses | [`D1_4_mask_phone_numbers.ipynb`](labs/D1_4_mask_phone_numbers.ipynb) |
| 2.1 | Day 2 · Session 1 | Label 40 complaints with a partner from the supplied codebook and compute chance-corrected agreement | [`D2_1_label_40_complaints.ipynb`](labs/D2_1_label_40_complaints.ipynb) |
| 2.2 | Day 2 · Session 2 | Train a character n-gram classifier and score it on the gold set | [`D2_2_train_character_n.ipynb`](labs/D2_2_train_character_n.ipynb) |
| 2.3 | Day 2 · Session 3 | Train an embedding classifier and score it per language | [`D2_3_train_embedding_classifier.ipynb`](labs/D2_3_train_embedding_classifier.ipynb) |
| 2.4 | Day 2 · Session 4 | Compare the two classifiers on the gold set with paired bootstrap intervals by language | [`D2_4_compare_two_classifiers.ipynb`](labs/D2_4_compare_two_classifiers.ipynb) |
| 3.1 | Day 3 · Session 1 | Classify the gold set with a prompted open-weight model | [`D3_1_classify_gold_set.ipynb`](labs/D3_1_classify_gold_set.ipynb) |
| 3.2 | Day 3 · Session 2 | Repeat one prompt three times, reword it once and measure label stability | [`D3_2_repeat_one_prompt.ipynb`](labs/D3_2_repeat_one_prompt.ipynb) |
| 3.3 | Day 3 · Session 3 | Measure agreement on Modern Standard Arabic, Gulf dialect and English subsets | [`D3_3_measure_agreement_modern.ipynb`](labs/D3_3_measure_agreement_modern.ipynb) |
| 3.4 | Day 3 · Session 4 | Decide whether model labels can replace a second human coder | [`D3_4_decide_whether_model.ipynb`](labs/D3_4_decide_whether_model.ipynb) |
| 4.1 | Day 4 · Session 1 | Extract six fields from inspection reports into a validated schema | [`D4_1_extract_six_fields.ipynb`](labs/D4_1_extract_six_fields.ipynb) |
| 4.2 | Day 4 · Session 2 | Compute per-field precision and recall and list the commonest errors | [`D4_2_compute_per_field.ipynb`](labs/D4_2_compute_per_field.ipynb) |
| 4.3 | Day 4 · Session 3 | Cluster complaint embeddings and label five clusters | [`D4_3_cluster_complaint_embeddings.ipynb`](labs/D4_3_cluster_complaint_embeddings.ipynb) |
| 4.4 | Day 4 · Session 4 | Correct model-label complaint rates with the human sample and choose the capstone corpus | [`D4_4_correct_model_label.ipynb`](labs/D4_4_correct_model_label.ipynb) |
<!-- /academy:labs -->

## Capstone

A text-measurement project on a supplied or public corpus, in a public repository whose README reports the gold set, agreement, model and extraction results and a reliability memo; eight-minute defence plus questions

**Submission:** REPLACE: what participants submit and how: a public repository link, or a shared folder for a course without code

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

- REPLACE: every source the course cites, with its address, in course.json under "sources"; this list is written from there
<!-- /academy:sources -->

### National references

- Personal Data Protection Law and its implementing regulations: REPLACE: the address of the official text
- NDMO Data Classification Policy: REPLACE: the address of the official text
- SDAIA Generative AI Guidelines: REPLACE: the address of the official text
- SDAIA AI Bias Reference Guide: REPLACE: the address of the official text
