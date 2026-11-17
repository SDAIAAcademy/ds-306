---
course: "Text and Unstructured Data for Data Science"
code: "DS-306"
version: "2027.1.0"
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-306/index.html"
---

# Text and Unstructured Data for Data Science

النصوص والبيانات غير المهيكلة في علم البيانات

Data Science Track · 4 teaching days + capstone day · 26 hours · Level 300

Turn Arabic and English text into measurements you can defend: clean and redact a corpus, score sparse, embedding and prompted classifiers on one gold set, test a language model as an annotator and correct the estimates its labels feed

Participants turn text into measurements they can defend. For the Sada Citizen Voice Centre, a fictional agency receiving complaints in Arabic and English, they normalise Arabic script and dialect spellings, redact personal data, build sparse and embedding-based classifiers, classify and extract fields with a prompted open-weight language model, and treat every model-made label as a measurement: agreement with a human gold set, stability across runs and prompts, gaps between dialects and the bias it carries into estimates. Writing labelling guidelines and adjudication are in DS-311.

**Who it is for:** Specialists. Analysts and data scientists who have completed the level 200 set or can show equivalent work: an analysis or model they built, validated and can explain.

**Format:** Intensive: 4 teaching days of four sessions and a capstone day, with guided pre-work and a tracked follow-up task

## The case study

**Sada Citizen Voice Centre.** Sada Citizen Voice Centre is a fictional government centre that receives complaints about municipal services in Modern Standard Arabic, Gulf dialect and English. Participants work on 20,000 synthetic complaints from 12 districts, a 300-document gold set coded by two people, 500 inspection reports and the recorded runs of Fahim, the centre's prompted labelling instruction on an open-weight model: they clean and redact the corpus, compare three classifiers, measure Fahim as an instrument and correct the district complaint rates its labels produce. All data are synthetic and written with a fixed seed; the recorded model runs are synthetic too.

## The course

### Day 1: Text into clean data

Slides: https://sdaiaacademy.github.io/ds-306/slides/day1.md

- **Session 1: Text as a data source**
  - Describe how a complaint corpus samples the people affected
  - Profile a corpus by language, length and channel
  - Measure the exact duplicate rate and say what it does to a count
  - [Lab 1.1: Profile the corpus (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D1_1_profile.ipynb)
- **Session 2: Preparing Arabic text**
  - Identify the script variants in an Arabic corpus
  - Write a normalisation function in named layers
  - Measure the vocabulary change of each layer and name what it merges
  - [Lab 1.2: Normalise Arabic text (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D1_2_normalise.ipynb)
- **Session 3: Near-duplicates**
  - Compute the Jaccard similarity of two texts from character shingles
  - Find near-duplicate candidates with MinHash and banding
  - Write a keep rule that separates resubmissions from a campaign
  - [Lab 1.3: Find near-duplicates (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D1_3_near_duplicates.ipynb)
- **Session 4: Redacting personal data**
  - Explain why identifiers are removed before text reaches a hosted model
  - Write patterns for phone and identity numbers in both digit systems
  - Measure a redaction miss rate by type and language on an audited sample
  - [Lab 1.4: Redact and measure misses (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D1_4_redaction.ipynb)

### Day 2: Labels you can trust

Slides: https://sdaiaacademy.github.io/ds-306/slides/day2.md

- **Session 1: Gold sets and agreement**
  - Label complaints from a codebook without AI help
  - Compute percent agreement and Cohen's kappa from a confusion table
  - Explain why a rare category can show high agreement and low kappa
  - [Lab 2.1: Agreement with a partner (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D2_1_agreement.ipynb)
- **Session 2: Sparse baselines**
  - Build character n-gram features for Arabic and English text
  - Train a linear classifier on a noisy training pool
  - Score it on the gold set with bootstrap intervals by language
  - [Lab 2.2: A character n-gram classifier (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D2_2_sparse.ipynb)
- **Session 3: Embeddings as features**
  - Explain what an embedding vector keeps and loses
  - Train a classifier on embeddings fetched within a call budget
  - Report scores per language with the cost of the vectors
  - [Lab 2.3: An embedding classifier (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D2_3_embeddings.ipynb)
- **Session 4: Comparing classifiers fairly**
  - Explain why scores on the same documents are compared in pairs
  - Compute a paired bootstrap interval for a difference in accuracy
  - Decide between classifiers by language with cost in view
  - [Lab 2.4: Compare classifiers fairly (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D2_4_paired_bootstrap.ipynb)

### Day 3: Language models as instruments

Slides: https://sdaiaacademy.github.io/ds-306/slides/day3.md

- **Session 1: Prompted classification**
  - Write a classification prompt from a codebook with a fixed output format
  - Classify documents in batches within a call budget and parse every reply
  - Record model, prompt version and settings with every label set
  - [Lab 3.1: Prompted classification (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D3_1_prompted.ipynb)
- **Session 2: Ask it twice**
  - Measure how often labels change between runs of one prompt
  - Measure the shift caused by rewording a prompt
  - Name the documents that move and why
  - [Lab 3.2: Ask it twice (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D3_2_stability.ipynb)
- **Session 3: Dialect gaps**
  - Measure agreement by language variety with intervals
  - Find the confusion that drives a dialect gap
  - Estimate how a gap under-counts a category in some districts
  - [Lab 3.3: Dialect gaps (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D3_3_dialect_gaps.ipynb)
- **Session 4: Is the model a good annotator**
  - Compare model-human agreement with human-human agreement
  - Set decision criteria before reading the results
  - Write a reliability memo with a decision and its limits
  - [Lab 3.4: A good annotator? (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D3_4_annotator.ipynb)

### Day 4: From documents to tables

Slides: https://sdaiaacademy.github.io/ds-306/slides/day4.md

- **Session 1: Schema-constrained extraction**
  - Define a schema with types, ranges and allowed values for six fields
  - Request schema-constrained output and validate every reply
  - Return a null for a field the text does not state
  - [Lab 4.1: Six fields, validated (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D4_1_extraction.ipynb)
- **Session 2: Field-level validation**
  - Define precision and recall for a field that may be empty
  - Compute them per field over 500 reports
  - List the commonest errors per field and the rule that would catch each
  - [Lab 4.2: Field-level validation (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D4_2_field_validation.ipynb)
- **Session 3: Structure in text**
  - Cluster document vectors and choose a number of clusters
  - Name clusters from their terms and examples
  - Compare clusters with codebook categories and say what each shows
  - [Lab 4.3: Structure in text (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D4_3_clusters.ipynb)
- **Session 4: Errors downstream**
  - Compute a naive district rate from model labels
  - Correct it with the gold set, stratified by language
  - Report naive and corrected rates with intervals and a version record
  - [Lab 4.4: Corrected rates (25 min)](https://sdaiaacademy.github.io/ds-306/labs/D4_4_corrected_rates.ipynb)

### Capstone: Capstone: a text measurement defended live

Slides: https://sdaiaacademy.github.io/ds-306/slides/capstone.md

## Capstone

A text-measurement project on a supplied or public corpus, in a public repository whose README reports the gold set, agreement, model and extraction results and a reliability memo; eight-minute defence plus questions

**What you submit:** A link to a public GitHub repository: the cleaning and redaction script with its miss rate, the gold set and agreement, the classifier and extraction results with model and prompt versions, the saved model outputs and run logs, the corrected estimate and the reliability memo, with a lock file and a README that reports all of them; prompts and agent transcripts are committed with it

**Rubric:**

- Preparation and redaction: 25%
- Gold set and agreement: 20%
- Models and extraction: 20%
- Reliability memo: 25%
- Reproducibility: 10%

## Outcomes

- **LO1** Prepare a bilingual corpus by normalising script, removing near-duplicates and redacting personal data, given 20,000 raw complaints with mixed scripts and embedded phone numbers (Applied) Evidence: a cleaning script and a profile report with the redaction miss rate
- **LO2** Implement sparse, embedding-based and prompted classifiers and score them on one held-out gold set, given a training pool and a fixed budget of model calls (Applied) Evidence: results with intervals by language and cost per thousand documents
- **LO3** Implement schema-constrained field extraction and measure field-level precision and recall, given 500 synthetic inspection reports with reference extractions (Applied) Evidence: an extraction script and a per-field validation report
- **LO4** Compute a district complaint rate from model labels corrected with a human-labelled sample and compare it with the uncorrected rate, given model labels for all complaints and a 300-document human gold set with measured agreement (Applied) Evidence: a table of naive and corrected rates with intervals
- **LO5** Evaluate a language model as an annotator and decide whether its labels can feed a downstream estimate, given labels from two prompts and three runs over the gold set (Performance) Evidence: a reliability memo on agreement, stability, dialect gaps and the decision
- **LO6** Design a text-measurement pipeline for a stakeholder question and defend each measurement choice, given a supplied corpus and a written brief (Performance) Evidence: a repository and report defended live

## Tools

- **Language model through a chat-completions style endpoint:** a locally served Arabic-capable open-weight model such as ALLaM 7B, a free hosted open-weight model, any commercial API
- **Local model serving:** llama.cpp, Ollama
- **Arabic text processing:** CAMeL Tools, course-provided normalisation rules
- **Embeddings, classifiers and clustering:** sentence-transformers, scikit-learn, BERTopic
- **Schema validation for extracted fields:** Pydantic, JSON Schema
- **Annotation:** Label Studio, doccano

## Prerequisites

- DS-202 Data Acquisition, Preparation and Quality
- DS-204 Machine Learning for Tabular Data: Baselines and Validation
- Calls a web API from Python and parses JSON

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

---

SDAIA Academy · Data Science Track · Text and Unstructured Data for Data Science

Course version 2027.1.0 · engine 1.0.0 · built 2026-11-15 · commit b4603d2
