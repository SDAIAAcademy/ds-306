---
course: "Text and Unstructured Data for Data Science"
code: "DS-306"
version: "2027.1.0"
scope: "course"
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-306/"
---

# Text and Unstructured Data for Data Science

Turn Arabic and English text into measurements you can defend: clean and redact a corpus, score sparse, embedding and prompted classifiers on one gold set, test a language model as an annotator and correct the estimates its labels feed

Participants turn text into measurements they can defend. For the Sada Citizen Voice Centre, a fictional agency receiving complaints in Arabic and English, they normalise Arabic script and dialect spellings, redact personal data, build sparse and embedding-based classifiers, classify and extract fields with a prompted open-weight language model, and treat every model-made label as a measurement: agreement with a human gold set, stability across runs and prompts, gaps between dialects and the bias it carries into estimates. Writing labelling guidelines and adjudication are in DS-311.

- **Audience:** Specialists. Analysts and data scientists who have completed the level 200 set or can show equivalent work: an analysis or model they built, validated and can explain.
- **Prerequisites:** DS-202 Data Acquisition, Preparation and Quality; DS-204 Machine Learning for Tabular Data: Baselines and Validation; Calls a web API from Python and parses JSON
- **Case study:** Sada Citizen Voice Centre: Sada Citizen Voice Centre is a fictional government centre that receives complaints about municipal services in Modern Standard Arabic, Gulf dialect and English. Participants work on 20,000 synthetic complaints from 12 districts, a 300-document gold set coded by two people, 500 inspection reports and the recorded runs of Fahim, the centre's prompted labelling instruction on an open-weight model: they clean and redact the corpus, compare three classifiers, measure Fahim as an instrument and correct the district complaint rates its labels produce. All data are synthetic and written with a fixed seed; the recorded model runs are synthetic too.

## Outcomes

- LO1 (Applied): Prepare a bilingual corpus by normalising script, removing near-duplicates and redacting personal data, given 20,000 raw complaints with mixed scripts and embedded phone numbers
- LO2 (Applied): Implement sparse, embedding-based and prompted classifiers and score them on one held-out gold set, given a training pool and a fixed budget of model calls
- LO3 (Applied): Implement schema-constrained field extraction and measure field-level precision and recall, given 500 synthetic inspection reports with reference extractions
- LO4 (Applied): Compute a district complaint rate from model labels corrected with a human-labelled sample and compare it with the uncorrected rate, given model labels for all complaints and a 300-document human gold set with measured agreement
- LO5 (Performance): Evaluate a language model as an annotator and decide whether its labels can feed a downstream estimate, given labels from two prompts and three runs over the gold set
- LO6 (Performance): Design a text-measurement pipeline for a stakeholder question and defend each measurement choice, given a supplied corpus and a written brief

## Day 1: Text into clean data

Profile, normalise, deduplicate and redact 20,000 complaints before any model reads them

#### [day1#title] Text into clean data

*SDAIA Academy · Text and Unstructured Data for Data Science*

Day 1: Profile, normalise, deduplicate and redact 20,000 complaints before any model reads them

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-306

#### [day1#agenda] Text into clean data

*Today*

- **Session 1 · Text as a data source**: Who writes to the centre, through which channel and in which language: a profile before any model
- **Session 2 · Preparing Arabic text**: Script variants, marks, digits and dialect spellings, and what each normalisation rule costs
- **Session 3 · Near-duplicates**: Shingles, Jaccard similarity and MinHash, and a keep rule that the count can defend
- **Session 4 · Redacting personal data**: Personal data in free text: patterns, cue words and a miss rate measured on an audited sample

#### [day1#the-case] Sada Citizen Voice Centre wants numbers it can defend

*The case for the week*

- **20,000 complaints** from 12 districts, in formal Arabic, Gulf dialect and English
- **Fahim** (فهيم): the centre's labelling prompt on an open-weight model
- **500 inspection reports** whose fields go into a table
- By Day 4: sewage complaints per 10,000 residents, by district

- **The people.** Dr. Ebtisam Al-Dhafiri, director. Muhannad Al-Oqaili, intake and the codebook. Ashwaq Al-Jabr, data protection. You are Fatin Al-Muqbel, junior data scientist.

> **All synthetic.** Every complaint, name and number, and every recorded model run, is generated with a fixed seed.

### Session 1: Text as a data source

#### [day1#s1] Text as a data source

*Session 1*

- Describe how a complaint corpus samples the people affected
- Profile a corpus by language, length and channel
- Measure the exact duplicate rate and say what it does to a count

#### [day1#who-writes] Complaints sample the people who write, not the people who are affected

*A corpus is a sample*

- **Who writes.** Residents with the app, time and confidence to complain. A street with older residents may suffer more and write less.
- **How they write.** The channel shapes the text: a call-centre transcript, a form field, a social post, an email pasted from a PDF.
- **What it can answer.** "What do complaints say?" directly. "Where are services worst?" only with a check against something else, such as inspections.

> **What goes wrong.** A rate of complaints is read as a rate of problems. It is a rate of people who wrote.

#### [day1#three-units] Message, complaint and issue are three different units

*What is one row?*

| Unit | What it is | Counted when you ask |
| --- | --- | --- |
| **Message** | One row as stored, copies included | How much work arrived at intake? |
| **Complaint** | One citizen's report of one problem, copies removed | How many residents complained? |
| **Issue** | One problem in the world, however many reported it | How many problems need a crew? |

A campaign of 600 messages about one overflowing sewer is 600 messages, about 600 complaints and one issue.

#### [day1#channels] Five channels deliver the corpus, and each leaves its mark on the text

*Lab 1.1, the channels*

| Item | Value |
| --- | --- |
| Web form | 30.9% |
| App | 27.1% |
| Call centre | 23.5% |
| Social media | 9.7% |
| Email | 8.8% |

Call-centre transcripts carry more Gulf dialect; app text arrives with a Persian keyboard layout; emails carry letters pasted from PDF files.

#### [day1#form-field] The form's language field is wrong for about one complaint in eleven

*Lab 1.1, metadata*

**8.8%** of complaints: the form field contradicts the script of the text

| Channel | Field contradicts the text |
| --- | --- |
| App | 25.1% |
| Social media | 4.8% |
| Web form | 2.7% |
| Call centre | 2.0% |
| Email | 1.8% |

> **What goes wrong.** A dashboard reports "English complaints" from the field. A quarter of the app's "English" rows are Arabic.

#### [day1#profile-first] A profile is the first table of every text project

*Before any model*

1. **Count** Rows, dates, channels, districts
2. **Language** From the text, compared with the fields
3. **Length** By language and channel
4. **Copies** Exact first, near next

The profile is saved as a file and opens the cleaning report: anyone who reruns the script can compare their numbers with it.

#### [day1#lengths] English complaints are longer in characters and words than Arabic ones

*Lab 1.1, length*

| Script | Median characters | Median words |
| --- | --- | --- |
| Arabic | 126 | 22 |
| English | 164 | 29 |
| Mixed | 98 | 14 |

- Length differs by language, hardly by channel
- A word count is not a token count: models split Arabic into more pieces per word
- Cost per document, on Day 3, depends on both

#### [day1#exact-copies] One message in thirty is an exact copy of an earlier one

*Lab 1.1, copies*

**3.2%** 639 exact copies after whitespace is collapsed

- Most copies arrive through the app (4.7%) and the web form (4.0%): a second press of "send"
- Copies inflate every count by district
- A copy in the training data and its twin in the test data flatter every score

#### [day1#check-form-field] Which split of the corpus by language can you defend?

*Checkpoint*

**Question:** Muhannad needs the complaints split into Arabic and English for two review teams. The form records a language for every complaint. What do you use?

- A. The form's language field, since every row has one
- B. The channel, since the call centre serves Arabic speakers
- C. The script of the text itself, checked against the form field on a sample
- D. A person reading every complaint and tagging it

#### [day1#lab-1-1] Profile the corpus

Lab 1.1 · 25 min

Profile the corpus by language, length, channel and duplicate rate, and test the form's language field against the text itself.

[D1_1_profile.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D1_1_profile.ipynb)

- [ ] Load the complaints and count what arrived (4 min)
- [ ] Language from the script against the form field (6 min)
- [ ] Length by language and channel (5 min)
- [ ] The exact duplicate rate (5 min)
- [ ] The profile table, saved for the report (5 min)
- [ ] ✱ Stretch: Complaints per week and channel: find the week that does not look like the others

### Session 2: Preparing Arabic text

#### [day1#s2] Preparing Arabic text

*Session 2*

- Identify the script variants in an Arabic corpus
- Write a normalisation function in named layers
- Measure the vocabulary change of each layer and name what it merges

#### [day1#recap-ds202] You already repair encodings and build matching keys; today the goal is measurement

*Recap from DS-202*

- **In DS-202.** Encoding repair (Windows-1256 read as UTF-8) and a normalised name key for matching records, kept beside the stored name.
- **Here.** Normalising whole texts for counting and classifying: which rules, in which order, and what each does to the vocabulary a model sees.

#### [day1#same-word-many-codes] Text pasted from a PDF looks Arabic and is made of different characters

*What a computer sees*

```python
# file: lab 1.2
"تحية"  →  U+062A U+062D U+064A U+0629      # letters
"ﺕحﻱة"  →  U+FE95 U+062D U+FEF1 U+0629      # presentation forms

unicodedata.normalize("NFKC", "ﺕحﻱة") == "تحية"   # True
```

- Presentation forms are the shapes a PDF stores; NFKC folds them back into letters
- To a classifier, the two spellings are two unrelated words

#### [day1#variants-found] Every Arabic complaint carries at least one spelling choice

*Lab 1.2, step 1*

| Variant | Arabic complaints with it | Where it comes from |
| --- | --- | --- |
| Teh marbuta (ة) | 90.0% | Spelling, written either ة or ه |
| Hamza on alef (أ إ آ) | 69.3% | Spelling, often typed without hamza |
| Alef maqsura (ى) | 43.8% | Spelling, often confused with ي |
| Arabic-Indic digits | 28.8% | Keyboard |
| Diacritics | 14.8% | Emphasis or habit |
| Tatweel (ـ) | 9.8% | Stretching a word for emphasis |
| Persian yeh or kaf | 6.5% | Keyboard layout, mostly the app |
| Presentation forms | 2.8% | Pasted from PDF files, the email channel |

#### [day1#layers] Write normalisation as layers you can switch on and measure one by one

*One function, named layers*

| Layer | Rule | Mirrors in CAMeL Tools |
| --- | --- | --- |
| `unicode` | NFKC: presentation forms to letters | `normalize_unicode` |
| `persian` | ی to ي, ک to ك |  |
| `marks` | Remove diacritics and tatweel |  |
| `alef` | أ إ آ ٱ to ا | `normalize_alef_ar` |
| `yeh_teh` | ى to ي, ة to ه | `normalize_alef_maksura_ar`, `normalize_teh_marbuta_ar` |
| `digits` | Arabic-Indic and Persian digits to 0 to 9 |  |

The course uses its own rules: CAMeL Tools 1.6 installs a deep learning framework that these labs do not need.

#### [day1#vocab-drop] Three layers do almost all the work: forms, marks and digits

*Lab 1.2, step 3*

| Item | Value |
| --- | --- |
| unicode | −2,935 |
| persian | −346 |
| marks | −2,488 |
| alef | −33 |
| yeh_teh | −68 |
| digits | −1,018 |

Distinct tokens over the Arabic complaints: 14,158 raw, 7,270 after all six layers.

#### [day1#rules-cost] A normalisation rule removes noise and, sometimes, a difference that mattered

*Every rule is a decision*

- **ة to ه** merges a feminine ending with a pronoun suffix
- **Digits** merge ٢٣ and 23, which is right for counting streets
- **Marks** remove emphasis the writer chose
- 53 normalised tokens in this corpus came from both a final ة and a final ه

- **The habit.** Keep the raw text in its own column. Write each rule with its layer name. Rerun with a layer off when a result surprises you.

> **What goes wrong.** Normalised text overwrites the raw text, and a rule that turns out wrong cannot be undone.

#### [day1#dialect-spellings] Dialect spellings are normalised as spellings, not translated into formal Arabic

*Gulf dialect*

| Written | Normalised to | Meaning |
| --- | --- | --- |
| اللحين, الحينه | الحين | now |
| ماحد | محد | nobody |
| شنو, ويش | وش | what |
| واااايد | وايد | a lot (letters repeated three times or more) |

Lab 1.2: the stretched letters fired in 872 complaints; the map took the vocabulary from 7,270 to 7,211.

> **Why not translate?** وايد is not an error. Turning Gulf text into formal Arabic hides the variety that Day 3 measures.

#### [day1#check-normalise] Which normalisation choice keeps the evidence?

*Checkpoint*

**Question:** A colleague's script applies NFKC, removes marks, maps ة to ه and writes the result over the `text` column. A reviewer asks how many complaints had presentation forms. What should the script have done?

- A. Written the normalised text to a new column and kept the raw text
- B. Applied NFKC only and skipped the other rules
- C. Logged the rules it applied in a comment
- D. Applied the rules in the reverse order

#### [day1#lab-1-2] Normalise Arabic text

Lab 1.2 · 25 min

Normalise letter variants and diacritics in named layers, measure the vocabulary change of each, and apply the course's Gulf spelling rules.

[D1_2_normalise.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D1_2_normalise.ipynb)

- [ ] Find the variants: forms, marks, letters, digits (5 min)
- [ ] Write normalise() in layers (8 min)
- [ ] The vocabulary change of each layer (7 min)
- [ ] Gulf spellings from the supplied map (5 min)
- [ ] ✱ Stretch: Find two different words that one rule merges into one

### Session 3: Near-duplicates

#### [day1#s3] Near-duplicates

*Session 3*

- Compute the Jaccard similarity of two texts from character shingles
- Find near-duplicate candidates with MinHash and banding
- Write a keep rule that separates resubmissions from a campaign

#### [day1#three-kinds] A copy, a resubmission and a campaign need three different decisions

*Not all copies are the same*

- **Exact copy.** The same text twice within days. One citizen pressed send twice. Keep the first.
- **Resubmission.** The same complaint with a sentence added: "this is my second report". One citizen, one complaint. Keep the first, note the repeat.
- **Campaign.** Many residents paste one message and change a few words. Many complaints, one issue. Keep all, flag them.

#### [day1#shingles] Shingles turn a text into a set of overlapping five-character pieces

*Comparing texts*

`المجا` `لمجار` `مجاري` `جاري ` `اري ط` `ري طا` `ي طاف` ` طافح`

- Normalise first, so spelling variants share shingles
- Mask long numbers: two copies with different phone numbers should still match
- Keep short numbers: Street 12 and Street 46 are different places

#### [day1#jaccard] Jaccard similarity is the shared shingles over all the shingles of the two texts

*One number for overlap*

**|A ∩ B| / |A ∪ B|** 1 for identical sets, 0 for nothing shared

- Two campaign messages written in different words: **0.21**
- Two unrelated complaints: **0.03**
- A resubmission and its original: usually above 0.7

> **Same issue, different words.** Jaccard finds copied wording, not the same problem described twice. The campaign is found as several groups, one per template.

#### [day1#minhash] MinHash compares 20,000 complaints without comparing every pair

*Fast candidates*

1. **Signature** 64 minimum hash values per complaint
2. **Agreement** The share of equal positions estimates Jaccard
3. **Bands** 16 bands of 4: equal in one band makes a candidate
4. **Confirm** The true Jaccard on candidates only

All pairs would be about 200 million comparisons. The bands leave about 103,000 candidates.

#### [day1#blocking] Short complaints look alike, so district and date join the rule

*Lab 1.3, step 3*

- "The street lights on Street 12 are off" is written by many residents, independently
- **Block** by district: only complaints from the same district can pair
- **Window**: confirm a pair only within 21 days
- **Threshold**: Jaccard of 0.7 or more

| Step | Pairs |
| --- | --- |
| Candidates from the bands | 103,238 |
| Confirmed | 11,031 |

#### [day1#keep-rule] The keep rule removes 998 messages and flags 576 as one campaign

*Lab 1.3, step 4*

| Group | Rule | Messages |
| --- | --- | --- |
| Fewer than 20 members | Keep the earliest; the others are copies | 998 removed |
| 20 members or more | Keep all, flag `campaign` | 576 flagged |

All 576 flagged messages are from Al-Naseem, sent in ten days of June, about one sewer on Street 12.

#### [day1#threshold-tradeoff] A threshold trades copies missed against real complaints dropped

*What the answer key shows*

| Jaccard threshold | Messages removed | Of them, true copies | True copies found |
| --- | --- | --- | --- |
| 0.6 | 1,247 | 839 | 91% |
| 0.7 | 998 | 810 | 88% |
| 0.8 | 758 | 626 | 68% |

924 messages are true copies or resubmissions. Synthetic data has an answer key; real data has a sample you read.

#### [day1#check-near-dups] What do you do with 576 near-identical messages?

*Checkpoint*

**Question:** The keep rule finds 576 near-identical messages from one district in ten days, all about one sewer. Dr. Ebtisam asks for the number of sewage complaints per district. What does the cleaning script do with them?

- A. Keep the earliest message and drop the other 575
- B. Drop all 576 as an organised campaign
- C. Keep all 576 with no flag, since they are complaints
- D. Keep all 576, flag them, and report the count with and without the campaign

#### [day1#lab-1-3] Find near-duplicates

Lab 1.3 · 25 min

Find near-duplicate complaints with character shingles and MinHash, group them, and decide which to keep and which to flag as a campaign.

[D1_3_near_duplicates.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D1_3_near_duplicates.ipynb)

- [ ] Shingles and Jaccard on two complaints (5 min)
- [ ] MinHash signatures for the corpus (7 min)
- [ ] Bands: candidate pairs, then the true similarity (6 min)
- [ ] Groups and the keep rule (7 min)
- [ ] ✱ Stretch: Count the campaign as one issue: which district's count changes most?

### Session 4: Redacting personal data

#### [day1#s4] Redacting personal data

*Session 4*

- Explain why identifiers are removed before text reaches a hosted model
- Write patterns for phone and identity numbers in both digit systems
- Measure a redaction miss rate by type and language on an audited sample

#### [day1#redact-before] Identifiers come out before any text goes to a model

*Why first*

- The Data Classification Policy has four levels: Top Secret, Secret, Restricted, Public
- The Generative AI Guideline for government asks employees not to enter data classified Restricted or higher into generative AI tools
- It limits their use, and data analysis with them, to data classified Public
- Complaints with names and numbers are not Public

- **At Sada.** Redacted text is classified again by Ashwaq. Text that stays above Public goes to a locally served model (llama.cpp, Ollama), never to a free hosted one.

#### [day1#what-is-there] A person marked 339 personal values in 500 complaints

*The audited sample*

| Item | Value |
| --- | --- |
| Phone numbers | 160 |
| Names | 122 |
| Identity numbers | 38 |
| Emails | 19 |

The marking is the reference. Without it, a redaction can only report what it found, never what it missed.

#### [day1#naive-pattern] "05 and eight digits" misses four phone numbers in five

*Lab 1.4, step 1*

**80.6%** of marked phone numbers missed by `05\d{8}`

- ٠٥٥ ٩٥٠ ٨٤١٤: Arabic-Indic digits, with spaces
- `+966 59 158 0751`: international form
- `059-386-9528`: dashes

#### [day1#one-pattern] One pattern covers both digit systems, the country code and the separators

*Lab 1.4, step 2*

```python
# file: redact.py
D = "[0-9٠-٩]"
PHONE = rf"(?:\+?(?:966|٩٦٦)[\s\-]?|[0٠])?[5٥]{D}(?:[\s\-]?{D}){{7}}(?!{D})"
ID    = rf"(?<!{D})[12١٢]{D}{{9}}(?!{D})"
EMAIL = r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"
```

- The digit class keeps the citizen's text as written: no translation before masking
- Phones first, then emails, then identity numbers

#### [day1#names-cues] Names have no shape, so the pattern looks for the words that introduce them

*Lab 1.4, step 4*

| Cue | Example after masking |
| --- | --- |
| اسمي | اسمي [NAME]، جوالي [PHONE] |
| معك, انا | معك [NAME]. |
| My name is, Regards, | My name is [NAME]. Call me on [PHONE]. |
| *No cue* | *Badr Al-Mutairi, phone [PHONE]* |

> **What goes wrong.** A name written with no cue word passes untouched. Patterns reach their limit here.

#### [day1#miss-rate] The redaction misses 7.7% of personal values, all of them names

*Lab 1.4, step 5*

| Type | Missed |
| --- | --- |
| Phone numbers | 0 of 160 |
| Identity numbers | 0 of 38 |
| Emails | 0 of 19 |
| Names | 26 of 122 (21.3%) |

- Arabic-script complaints: 5.7% missed
- English complaints: 15.1% missed
- The interval on 26 of 122 runs from about 15% to 29%

#### [day1#zero-matches] Zero matches is a statement about the pattern, not about the text

*The rule of the session*

1. **Sample** Draw complaints at random
2. **Mark** A person marks every personal value
3. **Redact** Run the script on the sample
4. **Count misses** By type and language, with an interval

The profile report carries the miss rate next to the profile: `artifacts/day1/profile_report.md`.

#### [day1#check-redaction] What does Ashwaq need to approve the redaction?

*Checkpoint*

**Question:** Your script masked 7,400 values in the corpus. Ashwaq Al-Jabr must decide whether the redacted text may leave the centre's servers. Which number answers her?

- A. The 7,400 values the script masked
- B. The share of values a person marked in a random sample that the script left readable
- C. The time the script takes on the whole corpus
- D. The six test numbers that all passed

#### [day1#lab-1-4] Redact and measure misses

Lab 1.4 · 25 min

Mask phone numbers, identity numbers, emails and names, measure the misses on 500 audited complaints, and write the profile report.

[D1_4_redaction.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D1_4_redaction.ipynb)

- [ ] Read what leaks in the audited sample (4 min)
- [ ] Phone numbers in every format (7 min)
- [ ] Identity numbers and emails (4 min)
- [ ] Names after cue words (5 min)
- [ ] The miss rate and the profile report (5 min)
- [ ] ✱ Stretch: Names with no cue word: how many are there, and what would catch them?

#### [day1#wrap-up] Three things to keep

*Day 1 · wrap-up*

- **Profile first.** Language from the text, not the form; copies counted; the profile saved as a file.
- **Rules are decisions.** Each normalisation layer and each keep rule has a name, a number and a reason. The raw text stays.
- **Measure misses.** A redaction is reported with its miss rate on a human-marked sample, by type and language.

#### [day1#next] Day 2: Labels you can trust

*Next*

Bring a partner for the first lab: you will label 40 complaints together, without AI. Read the codebook in labs/data/codebook.md tonight.

## Day 2: Labels you can trust

A gold set, chance-corrected agreement and two classifiers compared on the same documents

#### [day2#title] Labels you can trust

*SDAIA Academy · Text and Unstructured Data for Data Science*

Day 2: A gold set, chance-corrected agreement and two classifiers compared on the same documents

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-306

#### [day2#agenda] Labels you can trust

*Today*

- **Session 1 · Gold sets and agreement**: A gold set from a codebook, and agreement that is corrected for chance
- **Session 2 · Sparse baselines**: Character n-grams and a linear model: the baseline every other classifier must beat
- **Session 3 · Embeddings as features**: Vectors from a hosted embedding model as features, within a budget of calls
- **Session 4 · Comparing classifiers fairly**: Two classifiers on the same 300 documents: a paired bootstrap by language and a decision with its cost

#### [day2#review-day1] What does the redaction miss rate tell Ashwaq?

*Review of Day 1*

**Question:** The redaction left 26 of 122 marked names readable in the audited sample, and no phone or identity number. What follows for the release of redacted text?

- A. Phone numbers are proven absent from the redacted corpus
- B. About one name in five survives: a name rule or a review is needed before release
- C. The overall miss rate of 7.7% is low enough to release
- D. The audited sample must be re-marked before anything is decided

### Session 1: Gold sets and agreement

#### [day2#s1] Gold sets and agreement

*Session 1*

- Label complaints from a codebook without AI help
- Compute percent agreement and Cohen's kappa from a confusion table
- Explain why a rare category can show high agreement and low kappa

#### [day2#why-gold] Every score this week is a comparison with labels people made

*The measuring stick*

1. **Codebook** Categories, what each includes and excludes
2. **Random sample** 300 complaints from the cleaned corpus
3. **Two coders** Independently, AI-off
4. **Adjudication** Disagreements resolved against the codebook

At Sada the codebook and the adjudicated gold set are supplied. Writing a labelling guideline and running adjudication are taught in DS-311.

#### [day2#codebook-boundary] Most disagreements live in the "does not include" column

*The codebook*

| Code | Includes | Does not include |
| --- | --- | --- |
| `water_sewage` | A street flooded by sewage or a burst pipe | Rain on a damaged road, no pipe named (`roads`) |
| `permits` | Applications, renewals, rejections | Rude staff at a permits counter (`staff_service`) |
| `lighting` | Street lights and poles | Lighting inside a park (`parks`) |

One rule decides complaints with two problems: the main one is described first and at more length.

#### [day2#gold-sample] The gold set is a random sample, so it carries the corpus's mix of varieties

*Who is in the gold set*

| Item | Value |
| --- | --- |
| Gulf dialect | 120 |
| Modern Standard Arabic | 114 |
| English | 66 |

- Random: on Day 4 its errors can be carried to the whole corpus
- Small groups get wide intervals: 66 English complaints is the limit of what it can say about English

#### [day2#percent-agreement] Two careful coders agree on three complaints in four

*Lab 2.1, the reference pair*

**0.750** percent agreement of the two reference coders on the 40 complaints

- Two-problem complaints cause most disagreements
- Some agreement happens by chance: two coders who both say `roads` often agree without reading
- Percent agreement cannot tell the two apart

#### [day2#kappa] Kappa is the agreement beyond chance, as a share of what was possible beyond chance

*Correcting for chance*

**(po − pe) / (1 − pe)** pe: the sum over categories of each coder's share in it, multiplied

| Reference pair | Value |
| --- | --- |
| Observed agreement po | 0.750 |
| Chance agreement pe | 0.144 |
| Cohen's kappa | 0.708 |

#### [day2#prevalence-trap] For a rare category, high agreement can hide a weak kappa

*Lab 2.1, step 4*

| "This category or not" | Share | Agreement | Kappa |
| --- | --- | --- | --- |
| Parks | 4.7% | 0.957 | 0.644 |
| Street lighting | 7.7% | 0.970 | 0.775 |
| Waste | 15.3% | 0.977 | 0.911 |
| Water and sewage | 21.3% | 0.967 | 0.900 |

Gold set, two coders, 300 complaints. Over all eight categories: agreement 0.853, kappa 0.829.

#### [day2#labelling-bias] Two coders can agree and both be wrong in the same way

*What agreement cannot show*

- Kappa measures consistency, not correctness
- Coders trained together share their blind spots
- SDAIA's AI Bias Reference Guide names this **labelling bias**: labels shaped by the annotators' own interpretations

- **What the guide recommends.** Clear, objective criteria; annotators of diverse backgrounds; several annotators per item with disagreements resolved by consensus or expert review.

#### [day2#check-kappa] Which pair of coders is more reliable?

*Checkpoint*

**Question:** Pair A agrees on 94% of complaints for "staff conduct or not", with kappa 0.52. Pair B agrees on 88% for "water and sewage or not", with kappa 0.71. Staff conduct is rare. Which statement holds?

- A. Pair A, since they agree more often
- B. Pair B labels water and sewage more correctly
- C. They cannot be compared at all
- D. Pair B agrees more beyond chance; Pair A's 94% is mostly agreement on "no"

#### [day2#lab-2-1] Agreement with a partner

Lab 2.1 · 25 min

Label 40 complaints with a partner from the supplied codebook, compute percent agreement and Cohen's kappa by hand, and meet the prevalence trap.

[D2_1_agreement.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D2_1_agreement.ipynb)

- [ ] Read the codebook (5 min)
- [ ] Label 40 complaints with a partner (AI-off) (10 min)
- [ ] Percent agreement and kappa by hand (5 min)
- [ ] The prevalence trap (5 min)
- [ ] ✱ Stretch: Krippendorff's alpha for you, your partner and the two reference coders

### Session 2: Sparse baselines

#### [day2#s2] Sparse baselines

*Session 2*

- Build character n-gram features for Arabic and English text
- Train a linear classifier on a noisy training pool
- Score it on the gold set with bootstrap intervals by language

#### [day2#baseline-first] A sparse baseline sets the bar every other classifier must clear

*The first rung*

- **Cheap.** Trains and predicts in seconds on a laptop processor.
- **Local.** No text leaves the computer: no classification question to settle.
- **Readable.** Each weight belongs to a piece of text you can print.

#### [day2#char-ngrams] Character n-grams let different forms of one Arabic word share evidence

*Features*

`الحديقه` `حديق` `ديقه` `حديقتنا` `حديق` `ديقت`

- The article ال and suffixes such as نا change the word but keep most of its pieces
- `char_wb`: n-grams inside word boundaries, 2 to 5 characters
- Normalisation and the dialect map from Day 1 run first, so spelling variants collapse

#### [day2#tfidf] TF-IDF weights a piece by how often it appears here and how rare it is elsewhere

*Weights*

```python
# file: lab 2.2
vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5),
                      min_df=2, sublinear_tf=True)
X_pool = vec.fit_transform(prep(pool.text))   # fit on the pool only
X_gold = vec.transform(prep(gold.text))
model = LogisticRegression(max_iter=2000, C=5).fit(X_pool, pool.routing_label)
```

8,566 features; trained and scored in 6.4 seconds on a laptop.

#### [day2#noisy-pool] The pool's labels are the intake team's routing, fast and unchecked

*The training labels*

- 3,000 redacted complaints, each routed once by intake
- Some routing is wrong, and not at random: permits and staff conduct trade places, so do waste and parks
- A model trained on them learns the habits too

- **The rule.** Train on the noisy labels, score on the gold set. Never score on the labels you trained on.

#### [day2#sparse-results] The character n-gram classifier is right on 93% of the gold set

*Lab 2.2, the scores*

| Gold complaints | n | Accuracy | 95% interval |
| --- | --- | --- | --- |
| All | 300 | 0.930 | 0.900 to 0.957 |
| Modern Standard Arabic | 114 | 0.921 | 0.868 to 0.965 |
| Gulf dialect | 120 | 0.942 | 0.900 to 0.983 |
| English | 66 | 0.924 | 0.848 to 0.985 |

Macro F1 over the eight categories: 0.917.

#### [day2#interval-width] The interval for English is twice as wide because it rests on 66 complaints

*Reading an interval*

- Bootstrap: resample the gold complaints with replacement, recompute, repeat 2,000 times
- The middle 95% of the results is the interval
- Width shrinks with the square root of n: four times the complaints halves it

> **What goes wrong.** "English is 0.924 and Arabic 0.921, so they are equal." The intervals say the gold set cannot tell.

#### [day2#word-vs-char] Word n-grams lose most on formal Arabic, where words carry prefixes and suffixes

*Lab 2.2, stretch*

| Accuracy | Characters | Words |
| --- | --- | --- |
| Modern Standard Arabic | 0.921 | 0.886 |
| Gulf dialect | 0.942 | 0.925 |
| English | 0.924 | 0.955 |

Differences of this size sit inside the intervals: a direction to check, not a finding.

#### [day2#check-sparse] Where should the classifier be scored?

*Checkpoint*

**Question:** A colleague reports 0.97 accuracy for the n-gram classifier, measured on a random fifth of the 3,000 pool complaints held out from training. What is wrong with the number?

- A. It is scored against routing labels nobody checked, which share the model's own training habits
- B. 600 complaints are too few to score on
- C. The held-out complaints leaked into training
- D. Accuracy should have been macro F1

#### [day2#lab-2-2] A character n-gram classifier

Lab 2.2 · 25 min

Train a character n-gram classifier on the 3,000-document pool and score it on the 300-document gold set, with intervals by language.

[D2_2_sparse.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D2_2_sparse.ipynb)

- [ ] Load the pool and the gold set (3 min)
- [ ] Character n-grams with TF-IDF (6 min)
- [ ] A logistic classifier (5 min)
- [ ] Macro F1 and accuracy on the gold set (5 min)
- [ ] Bootstrap intervals by language (6 min)
- [ ] ✱ Stretch: Word n-grams instead: which language loses most?

### Session 3: Embeddings as features

#### [day2#s3] Embeddings as features

*Session 3*

- Explain what an embedding vector keeps and loses
- Train a classifier on embeddings fetched within a call budget
- Report scores per language with the cost of the vectors

#### [day2#what-a-vector-is] An embedding places texts so that similar meanings sit close together

*Embeddings*

- A model reads the text and returns a fixed-length vector
- Close vectors: complaints about the same thing, even in different words or languages
- A simple classifier on top learns the categories from a few examples each

- **What it loses.** Which words carried the decision. A wrong label is harder to explain than with n-gram weights.

#### [day2#hosted-embeddings] A free hosted embedding model, within a budget of requests

*The tool slot*

| Setting | Value, checked this month |
| --- | --- |
| Default model | `nvidia/nemotron-3.5-embed-1b:free` on OpenRouter |
| Free requests | 20 a minute; 50 a day, or 1,000 a day after a one-time purchase of 10 credits |
| Texts per request | Up to 64 in the labs, cached on disk |
| Paid endpoint of this model | None listed |

Other examples for the same slot: sentence-transformers models served elsewhere, or a commercial embedding API.

#### [day2#call-budget] A budget of 25 requests buys 1,280 training complaints and the gold set

*Lab 2.3, step 1*

1. **Gold first** 300 complaints: 5 requests of 64
2. **The rest** 20 requests: 1,280 pool complaints
3. **Stratified** Sampled by routing label, so every category is there

Every vector is cached: a rerun of the notebook costs no request.

#### [day2#standin-honesty] Without a working key, the lab says so on every number it prints

*When no key works*

- The stand-in hashes character pieces into 384 numbers
- It is lexical, like the sparse model: it measures the lab's code, not an embedding model
- The course's own run used it: no key that worked was available

> **What goes wrong.** A stand-in score is quoted as "the embedding model". Every table from such a run carries the words "stand-in".

#### [day2#embed-results] The stand-in classifier is right on 89% of the gold set

*Lab 2.3, the scores (stand-in vectors)*

| Gold complaints | n | Accuracy | 95% interval |
| --- | --- | --- | --- |
| All | 300 | 0.893 | 0.857 to 0.927 |
| Modern Standard Arabic | 114 | 0.886 | 0.825 to 0.939 |
| Gulf dialect | 120 | 0.908 | 0.858 to 0.958 |
| English | 66 | 0.879 | 0.788 to 0.955 |

Trained on 1,280 pool complaints, a little under half the sparse model's 3,000.

#### [day2#embed-cost] Free is not free: requests, waiting and text that leaves the building

*Lab 2.3, step 4*

| Per 1,000 complaints | Value |
| --- | --- |
| Requests | 15.8 |
| Money on the free endpoint | 0 |
| Days to embed all 20,000 at 50 requests a day | 6.2 |

> **And the data.** Each request sends redacted complaints to a third party. The classification of that text decides whether this lab is allowed at all with real data.

#### [day2#check-embeddings] What can you report from a stand-in run?

*Checkpoint*

**Question:** Your key failed and Lab 2.3 ran on the stand-in vectors, with 0.893 gold accuracy. Dr. Ebtisam asks whether embeddings beat the n-gram baseline. What do you answer?

- A. "No: embeddings reach 0.893 against 0.930"
- B. "Yes: embeddings usually beat n-grams"
- C. "Not measured yet: the code works, the comparison needs a run with the hosted model"
- D. "Embeddings cannot be used at the centre"

#### [day2#lab-2-3] An embedding classifier

Lab 2.3 · 25 min

Embed the pool and the gold set with a free hosted model within a call budget, train a classifier on the vectors and score it per language.

[D2_3_embeddings.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D2_3_embeddings.ipynb)

- [ ] Embed the pool and the gold set within the budget (7 min)
- [ ] A logistic head on the vectors (5 min)
- [ ] Scores per language with intervals (7 min)
- [ ] Calls, seconds and cost per thousand documents (6 min)
- [ ] ✱ Stretch: Join the sparse and the embedding features: does the union beat both?

### Session 4: Comparing classifiers fairly

#### [day2#s4] Comparing classifiers fairly

*Session 4*

- Explain why scores on the same documents are compared in pairs
- Compute a paired bootstrap interval for a difference in accuracy
- Decide between classifiers by language with cost in view

#### [day2#recap-pairing] In DS-204 you paired models by fold; here you pair them by document

*Recap from DS-204*

- **DS-204.** Champion and challenger scored on the same five folds: five paired differences, an interval on their mean.
- **Here.** Both classifiers labelled the same 300 gold complaints: 300 paired differences of right minus right.

#### [day2#two-by-two] Only 33 of the 300 complaints decide the comparison

*Lab 2.4, step 2*

|  | Embedding right | Embedding wrong |
| --- | --- | --- |
| Sparse right | 257 | 22 |
| Sparse wrong | 11 | 10 |

Where both are right or both wrong, the difference is zero. The 22 and the 11 are the evidence.

#### [day2#paired-bootstrap] A paired bootstrap resamples complaints, keeping each pair together

*Lab 2.4, step 3*

```python
# file: lab 2.4
diff = ok_sparse - ok_embed            # one value per complaint: -1, 0 or 1
means = [diff[rng.integers(0, 300, 300)].mean() for _ in range(2000)]
low, high = np.percentile(means, [2.5, 97.5])
```

**+0.037** sparse minus embedding, 95% interval −0.003 to +0.073

#### [day2#paired-by-language] By language, every interval crosses zero

*Lab 2.4, step 4*

| Variety | n | Sparse minus embedding | 95% interval |
| --- | --- | --- | --- |
| Modern Standard Arabic | 114 | +0.035 | −0.026 to +0.096 |
| Gulf dialect | 120 | +0.033 | −0.017 to +0.092 |
| English | 66 | +0.045 | −0.030 to +0.121 |

The same direction in all three; no variety where the gold set can separate them.

#### [day2#paired-vs-unpaired] Pairing narrows the interval because hard complaints are hard for both

*Lab 2.4, stretch*

| Item | Value |
| --- | --- |
| Unpaired | 0.093 wide |
| Paired | 0.077 wide |

Resampling the two columns independently counts the shared difficulty of each complaint twice.

#### [day2#decision-cost] When the scores cannot separate two classifiers, cost and risk decide

*Lab 2.4, step 5*

|  | Character n-grams | Hosted embeddings |
| --- | --- | --- |
| Gold accuracy | 0.930 | 0.893 (stand-in) |
| Per 1,000 complaints | Seconds of laptop time | About 16 requests, a daily limit |
| Text leaves the centre | No | Yes, redacted |

> **The decision written in the lab.** Keep the n-gram classifier; rerun the comparison with the hosted model before it is final.

#### [day2#check-paired] How do you read +0.037 with an interval of −0.003 to +0.073?

*Checkpoint*

**Question:** The paired difference in gold accuracy, sparse minus embedding, is +0.037 with a 95% interval from −0.003 to +0.073. Which sentence belongs in the report?

- A. The two classifiers perform the same
- B. The sparse classifier is probably better by up to seven points, but a difference of zero cannot be ruled out
- C. The sparse classifier is 3.7 points better
- D. The embedding classifier may be the better one, since the interval is negative

#### [day2#lab-2-4] Compare classifiers fairly

Lab 2.4 · 25 min

Compare the sparse and embedding classifiers on the gold set with paired bootstrap intervals, overall and by language, and write the decision.

[D2_4_paired_bootstrap.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D2_4_paired_bootstrap.ipynb)

- [ ] Load both classifiers' predictions on the gold set (4 min)
- [ ] Paired differences per document (5 min)
- [ ] A paired bootstrap interval (7 min)
- [ ] The same, by language (5 min)
- [ ] The decision, with cost (4 min)
- [ ] ✱ Stretch: An unpaired bootstrap of the same difference: how much wider is it?

#### [day2#wrap-up] Three things to keep

*Day 2 · wrap-up*

- **Agreement beyond chance.** Kappa, by category, with the rare categories read carefully. It measures consistency, not truth.
- **Score on gold.** Train on the labels you have; score on the labels people checked, with intervals by language.
- **Pair the comparison.** Same documents, paired differences, an interval, then cost and risk.

#### [day2#next] Day 3: Language models as instruments

*Next*

Tomorrow Fahim, a prompted open-weight model, labels the gold set. Read data/prompts/fahim_p1.md and note one sentence you would change.

## Day 3: Language models as instruments

A prompted open-weight model measured like any other instrument: accuracy, stability, dialect gaps

#### [day3#title] Language models as instruments

*SDAIA Academy · Text and Unstructured Data for Data Science*

Day 3: A prompted open-weight model measured like any other instrument: accuracy, stability, dialect gaps

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-306

#### [day3#agenda] Language models as instruments

*Today*

- **Session 1 · Prompted classification**: A prompt is an instrument: codebook, label set, output format, batch and a version record
- **Session 2 · Ask it twice**: Run stability and prompt stability, measured as agreement of the model with itself
- **Session 3 · Dialect gaps**: Agreement by language variety, the confusions behind a gap, and what a gap does to a count
- **Session 4 · Is the model a good annotator**: A model as a second coder: criteria fixed before looking, evidence, and a written decision

#### [day3#review-day2] What did the paired comparison show?

*Review of Day 2*

**Question:** Sparse minus embedding accuracy on the same 300 gold complaints was +0.037, interval −0.003 to +0.073. Unpaired, the interval was 0.093 wide; paired, 0.077. What made the paired interval narrower?

- A. Pairing doubles the number of complaints
- B. The paired bootstrap used more resamples
- C. Complaints that are easy or hard for both classifiers cancel out in the difference
- D. Accuracy is less variable than macro F1

### Session 1: Prompted classification

#### [day3#s1] Prompted classification

*Session 1*

- Write a classification prompt from a codebook with a fixed output format
- Classify documents in batches within a call budget and parse every reply
- Record model, prompt version and settings with every label set

#### [day3#prompt-as-instrument] The codebook becomes a prompt with fixed labels and a fixed output format

*A prompt is an instrument*

Prompt for Fahim, prompt 1:

```text
You label citizen complaints for Sada Citizen Voice Centre.
Assign each complaint exactly one category: the main problem the citizen asks the centre to fix.
Categories: water_sewage, roads, waste, … each with one line of definition.
Reply with JSON only: {"labels": [{"id": …, "label": …}]}
```

Role · Unit and rule · Label set · Format

#### [day3#batch-and-budget] Ten complaints a request: the prompt is paid once per batch

*Within the budget*

- One request labels ten complaints, each line `id: text`
- The gold set is 30 requests; all 20,000 complaints are 2,000
- Free tier: 50 requests a day, 1,000 after a one-time 10 credits

> **A measurement choice.** Batching can change labels: a complaint is read next to nine others. The stretch of Lab 3.1 compares one-per-call with batches.

#### [day3#parse-never-guess] A reply that cannot be parsed is a missing label, never a guessed one

*Lab 3.1, step 2*

```python
# file: sada.py
def parse_labels(text, ids):
    data = json.loads(text[text.find("{"): text.rfind("}") + 1])
    got = {str(x.get("id")): x.get("label") for x in data.get("labels", [])}
    return {i: (got.get(i) if got.get(i) in CATEGORIES else None) for i in ids}
```

In the course's run all ten labels came back usable and eight were right.

#### [day3#version-record] Every label set travels with the model, the prompt and the settings that made it

*The version record*

| Field | Value in the recorded run |
| --- | --- |
| Model | `google/gemma-4-31b-it:free` |
| Prompt | P1 and the hash of its text |
| Temperature, batch size | 0.7, ten complaints |
| Date | The day of the run |

> **What goes wrong.** A model name stays while the weights behind an endpoint change. Without the date and the prompt hash, a published rate cannot be reproduced.

#### [day3#prompted-results] Fahim is right on 81% of the gold set, and on 73% of Gulf complaints

*Lab 3.1, the scores (recorded run)*

| Gold complaints | n | Accuracy | 95% interval |
| --- | --- | --- | --- |
| All | 300 | 0.810 | 0.763 to 0.853 |
| Modern Standard Arabic | 114 | 0.868 | 0.807 to 0.930 |
| Gulf dialect | 120 | 0.733 | 0.658 to 0.808 |
| English | 66 | 0.848 | 0.758 to 0.939 |

Macro F1 0.797. The sparse classifier of Day 2: 0.930, with no dialect gap.

#### [day3#prompted-cost] A thousand complaints cost 100 requests, or about three cents at volume

*Lab 3.1, step 5*

| Per 1,000 complaints | Value |
| --- | --- |
| Tokens in, per complaint (prompt shared by ten) | 106.9 |
| Tokens out, per complaint | 14.0 |
| Requests, ten a batch | 100 |
| Days on a free account without credits | 2 |
| USD on the paid endpoint of the same model | 0.027 |

#### [day3#check-prompted] Which classifier for a category that did not exist last month?

*Checkpoint*

**Question:** The centre adds a ninth category, "heat and cooling in public buildings", with no labelled examples yet. The sparse model scores 0.930 on the old eight; Fahim 0.810. What do you use for the first month?

- A. The sparse model, since it scores higher
- B. Fahim with the new category added to its prompt, checked on a small new gold sample
- C. Neither, until 3,000 new labels are collected
- D. The sparse model for the new category and Fahim for the old ones

#### [day3#lab-3-1] Prompted classification

Lab 3.1 · 25 min

Classify the gold set with Fahim, a prompted open-weight model: ten documents live, the full recorded run scored with intervals by language and costed.

[D3_1_prompted.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D3_1_prompted.ipynb)

- [ ] The prompt: codebook, labels, JSON (6 min)
- [ ] Classify a batch of ten (5 min)
- [ ] Load the recorded run and its version record (4 min)
- [ ] Score it on the gold set by language (6 min)
- [ ] Cost per thousand documents (4 min)
- [ ] ✱ Stretch: One document per call against batches of ten: do the labels change?

### Session 2: Ask it twice

#### [day3#s2] Ask it twice

*Session 2*

- Measure how often labels change between runs of one prompt
- Measure the shift caused by rewording a prompt
- Name the documents that move and why

#### [day3#two-kinds-of-instability] Two kinds of instability: the same prompt again, and the same request in other words

*Ask it twice*

- **Run stability.** Prompt 1, three runs at the same settings. Sampling makes the labels vary.
- **Prompt stability.** Prompt 2 says the same thing differently and adds a rule for two-problem complaints. Wording moves labels.

Both are part of the measurement error of one label. A single run shows neither.

#### [day3#flip-rate] One complaint in five gets a different label in one of three runs

*Lab 3.2, step 1*

**19.7%** of gold complaints: the three runs of prompt 1 do not all agree

| Prompt 1 | Accuracy |
| --- | --- |
| Run 1 | 0.810 |
| Run 2 | 0.793 |
| Run 3 | 0.817 |

#### [day3#run-kappa] Fahim agrees with itself about as well as two people agree with each other

*Lab 3.2, step 2*

| Item | Value |
| --- | --- |
| Run 1 and run 2 | 0.840 |
| Run 1 and run 3 | 0.864 |
| Run 2 and run 3 | 0.837 |
| Two human coders | 0.829 |

Kappa. Whatever changes between runs is noise that every single-run label set carries.

#### [day3#prompt-shift] Rewording the prompt moves twice as many labels as running it again

*Lab 3.2, step 3*

| Labels that change | Share of gold complaints |
| --- | --- |
| Prompt 1 run 1 against prompt 1 run 2 | 13.7% |
| Prompt 1 run 1 against prompt 2 run 1 | 31.3% |

Yet the accuracy barely moves: 0.810 with prompt 1, 0.797 with prompt 2. Different complaints are wrong.

#### [day3#who-moves] The complaints Fahim cannot settle are the ones people disagree on too

*Lab 3.2, step 4*

| The two human coders | Complaints | Unstable across six model labels |
| --- | --- | --- |
| Agreed | 256 | 43.4% |
| Disagreed | 44 | 72.7% |

Most of them name two problems. The codebook's rule for them is the weak point of both instruments.

#### [day3#majority-vote] The majority of three runs gains four points for three times the requests

*Lab 3.2, step 5*

**0.850** accuracy of the majority of three runs, against 0.810 for one run

- Votes cancel part of the run noise
- They do not cancel a systematic error: a Gulf word misread three times is misread
- Cost: 300 requests per 1,000 complaints

#### [day3#check-stability] Two prompts, the same accuracy: are their labels interchangeable?

*Checkpoint*

**Question:** Prompt 1 scores 0.810 on the gold set and prompt 2 scores 0.797. A colleague says the prompts are equivalent, so the published district counts do not depend on the choice. What do you check?

- A. Nothing: equal accuracy means equal counts
- B. The flip rate of prompt 1 alone
- C. Which prompt uses fewer tokens
- D. How many labels differ between the prompts, and the counts by category and district under each

#### [day3#lab-3-2] Ask it twice

Lab 3.2 · 25 min

Repeat one prompt three times, reword it once and measure label stability: flip rate, kappa between runs and the documents that move.

[D3_2_stability.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D3_2_stability.ipynb)

- [ ] Three runs of one prompt: the flip rate (6 min)
- [ ] Kappa between runs (5 min)
- [ ] The reworded prompt: the shift (6 min)
- [ ] Which documents move (5 min)
- [ ] The majority of three runs (3 min)
- [ ] ✱ Stretch: Run twenty complaints three times live and compare with the recorded runs

### Session 3: Dialect gaps

#### [day3#s3] Dialect gaps

*Session 3*

- Measure agreement by language variety with intervals
- Find the confusion that drives a dialect gap
- Estimate how a gap under-counts a category in some districts

#### [day3#gap-by-variety] Fahim falls short of the human coders on Gulf dialect, not elsewhere

*Lab 3.3, step 1*

| Variety | n | Kappa, Fahim against gold | Kappa, two humans |
| --- | --- | --- | --- |
| Modern Standard Arabic | 114 | 0.845 | 0.813 |
| Gulf dialect | 120 | 0.685 | 0.872 |
| English | 66 | 0.824 | 0.772 |

#### [day3#gulf-confusion] Gulf sewage complaints that mention a flooded street are read as road complaints

*Lab 3.3, step 2*

**9 of 32** Gulf gold `water_sewage` complaints labelled `roads`

**Complaint:** ترى المجاري طافحة عند الدوار … والشارع غرقان.

**Fahim (weak example):** roads

Gulf words such as غرقان and مويه ("flooded", "water") sit next to شارع ("street"). The prompt lists "flooding from sewage" under `water_sewage`, in formal words only.

#### [day3#gap-interval] The gap is 13.5 points, and its interval excludes zero

*Lab 3.3, step 3*

**+0.135** accuracy on formal Arabic minus Gulf; 95% interval +0.025 to +0.236

- Two groups, different complaints: resample within each group, nothing to pair
- Wide, because each group has about 120 complaints
- Prompt 2: +0.065, interval −0.046 to +0.167

#### [day3#variety-instrument] To carry the gap to districts, the variety of every complaint is guessed, and the guess is measured

*Lab 3.3, step 4*

- English: by script
- Gulf: when a Gulf marker word appears (وايد, الحين, محد, مويه …)
- Otherwise formal Arabic

**95.7%** agreement with the coders' variety on the gold set; 13 of 120 Gulf complaints guessed as formal

#### [day3#district-recall] Where most residents write in Gulf dialect, a quarter of sewage complaints are missed

*Lab 3.3, step 4*

| District | Gulf share | Expected recall of sewage complaints |
| --- | --- | --- |
| Al-Naseem | 60.5% | 0.752 |
| Al-Jazira | 55.1% | 0.767 |
| Al-Salam | 48.1% | 0.787 |
| Al-Shati | 17.5% | 0.892 |
| Al-Khalij | 12.8% | 0.910 |

#### [day3#check-dialect] What does the dialect gap do to the published rate?

*Checkpoint*

**Question:** Fahim misses more sewage complaints in Gulf dialect. Al-Naseem's complaints are 60% Gulf, Al-Khalij's 13%. The naive sewage rate is published for both. Which statement holds?

- A. Al-Naseem's rate is under-stated more than Al-Khalij's, so the gap between them looks smaller than it is
- B. Both are under-stated equally, so the comparison is fair
- C. Al-Naseem's rate is over-stated
- D. The rates are fine because overall accuracy is 0.81

#### [day3#lab-3-3] Dialect gaps

Lab 3.3 · 25 min

Measure Fahim's agreement on Modern Standard Arabic, Gulf dialect and English subsets, find the confusion behind the gap and its effect on a count.

[D3_3_dialect_gaps.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D3_3_dialect_gaps.ipynb)

- [ ] Agreement by variety with intervals (7 min)
- [ ] The confusion table of Gulf complaints (6 min)
- [ ] The gap with a bootstrap interval (6 min)
- [ ] What the gap does to a count (6 min)
- [ ] ✱ Stretch: Does the reworded prompt narrow the gap?

### Session 4: Is the model a good annotator

#### [day3#s4] Is the model a good annotator

*Session 4*

- Compare model-human agreement with human-human agreement
- Set decision criteria before reading the results
- Write a reliability memo with a decision and its limits

#### [day3#the-question] Can Fahim replace the second coder, and can its labels feed an estimate?

*The decision*

- **Replace a coder.** Each label is used as it is, complaint by complaint. The bar is what a second person adds.
- **Feed an estimate.** Labels are counted. Errors can be measured on a human sample and corrected in the count.

Two questions, two bars. A model can fail the first and pass the second.

#### [day3#criteria-first] Write the bar before you read the results

*Lab 3.4, step 3*

| Criterion, in every variety | The course's bar |
| --- | --- |
| Fahim's kappa below the human pair's, at most | 0.05 |
| Complaints whose three runs agree, at least | 90% |
| Accuracy gap between varieties, at most | 0.05 |

A criterion written after the results is a description of the results.

#### [day3#criteria-results] Fahim passes on formal Arabic and English, and fails on Gulf dialect and stability

*Lab 3.4, step 4*

| Test | Value | Result |
| --- | --- | --- |
| Kappa shortfall, Modern Standard Arabic | −0.032 | Pass |
| Kappa shortfall, Gulf dialect | 0.187 | Fail |
| Kappa shortfall, English | −0.052 | Pass |
| Three runs agree | 80.3% | Fail |
| Accuracy gap between varieties | 0.135 | Fail |

#### [day3#leave-one-out] Swapped in for either coder, Fahim agrees less with the other one than a person does

*Lab 3.4, stretch*

| Replace | The human's agreement with the other coder | Fahim's |
| --- | --- | --- |
| Coder A | 0.853 | 0.780 |
| Coder B | 0.853 | 0.750 |

#### [day3#reliability-memo] The reliability memo answers both questions in five short paragraphs

*Lab 3.4, step 5*

1. **Question** Replace the second coder? Feed the district rates?
2. **Evidence** Agreement, stability, gaps, each with its number
3. **Decision** Not as a coder; yes for counts with a correction
4. **Limits** Synthetic runs, small groups, versions to keep

#### [day3#check-annotator] What does the memo recommend?

*Checkpoint*

**Question:** Fahim fails the criteria on Gulf dialect and on stability, and passes on formal Arabic and English. Dr. Ebtisam wants one recommendation. Which one follows from the evidence?

- A. Replace the second coder, since overall kappa is 0.778
- B. Stop using Fahim for anything
- C. Keep both human coders; use Fahim's labels for counts only with a correction from the human sample, by variety
- D. Lower the stability criterion to 80% so that Fahim passes

#### [day3#lab-3-4] A good annotator?

Lab 3.4 · 25 min

Decide whether Fahim's labels can replace a second human coder, against criteria written first, and draft the reliability memo.

[D3_4_annotator.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D3_4_annotator.ipynb)

- [ ] Agreement between the two human coders (4 min)
- [ ] Fahim against each coder and the gold label (6 min)
- [ ] Write the criteria before looking (4 min)
- [ ] Apply them: agreement, stability, gaps (6 min)
- [ ] Draft the reliability memo (5 min)
- [ ] ✱ Stretch: Leave one coder out: how often does Fahim agree with the other coder as often as a human does?

#### [day3#wrap-up] Three things to keep

*Day 3 · wrap-up*

- **Version everything.** Model, prompt hash, settings and date travel with every label set.
- **Ask it twice.** Run and prompt stability are part of a label's error; a single run hides both.
- **Report by group.** A gap by variety turns into an under-count by district.

#### [day3#next] Day 4: From documents to tables

*Next*

Tomorrow: fields extracted from inspection reports, clusters, and the corrected district rates. Read the two capstone briefs in labs/data/capstone/.

## Day 4: From documents to tables

Validated extraction, field-level scores, clusters, and estimates corrected with the human sample

#### [day4#title] From documents to tables

*SDAIA Academy · Text and Unstructured Data for Data Science*

Day 4: Validated extraction, field-level scores, clusters, and estimates corrected with the human sample

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-306

#### [day4#agenda] From documents to tables

*Today*

- **Session 1 · Schema-constrained extraction**: A schema the model must fill, validation of every reply, and nulls instead of invented values
- **Session 2 · Field-level validation**: Precision and recall per field, with nulls counted correctly, and the commonest errors
- **Session 3 · Structure in text**: Clusters of embeddings as a way to see a corpus, and why a cluster is not a category
- **Session 4 · Errors downstream**: A complaint rate from model labels, corrected with the human sample, with intervals

#### [day4#review-day3] What did the criteria decide?

*Review of Day 3*

**Question:** Fahim failed the criteria on Gulf dialect (kappa 0.187 below the human pair) and on stability (80.3% of complaints with three agreeing runs). What did the reliability memo recommend?

- A. Stop using Fahim's labels altogether
- B. Keep the second coder; use Fahim's labels for counts, corrected with the gold set by variety
- C. Replace the coder with the majority of three runs
- D. Relax the stability criterion to 80%

### Session 1: Schema-constrained extraction

#### [day4#s1] Schema-constrained extraction

*Session 1*

- Define a schema with types, ranges and allowed values for six fields
- Request schema-constrained output and validate every reply
- Return a null for a field the text does not state

#### [day4#report-to-row] One report, six fields, each with a type and a rule

*From report to row*

**IR-0005:** تاريخ الزيارة: 19 سبتمبر 2026. الحي: المروة. لاحظ المفتش طفح مياه الصرف … الخلل جسيم. يشكل خطرا على المارة. يجب الإصلاح خلال 10 أيام.

| Field | Value |
| --- | --- |
| district | `al_marwa` |
| inspection_date | `2026-09-19` |
| defect_type | `sewage_overflow` |
| severity | `high` |
| hazard_to_public | `true` |
| repair_deadline_days | `10` |

#### [day4#schema] The schema says what a valid answer is before any model answers

*Lab 4.1, step 1*

```python
# file: D4_1_extraction.ipynb
class Inspection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    district: Optional[Literal[CODES]] = None
    inspection_date: Optional[date] = None      # and a 2026 check
    defect_type: Optional[Literal[DEFECTS]] = None
    severity: Optional[Literal["low", "medium", "high", "critical"]] = None
    hazard_to_public: Optional[bool] = None
    repair_deadline_days: Optional[int] = Field(None, ge=1, le=90)
```

#### [day4#validate-repair] JSON mode makes a reply parse; the schema makes it admissible

*Lab 4.1, step 3*

1. **1 · Ask** Prompt and report, JSON mode
2. **2 · Validate** "Al Marwa", "07/06/2026", "Minor": three errors
3. **3 · Repair once** Send the errors back; validate again

> **What goes wrong.** The repaired IR-0002 is valid and still wrong: no district, day and month swapped, a hazard the report denies.

#### [day4#null-not-invented] A deadline the report never gave looks exactly like data

*Lab 4.1, step 4*

**47 of 177** reports with no deadline got one in the recorded run (26.6%)

- The prompt says: never infer it from the severity
- The invented values match the severity table
- **Grounding rule**: keep a deadline only when the number of days is written in the text
- It catches all 47

#### [day4#check-extraction] What should come back for a field the report does not state?

*Checkpoint*

**Question:** A report reads "The repair date will be set later." The defect is serious. The schema allows `repair_deadline_days` from 1 to 90 or null. Which extraction is right?

- A. 7, the usual deadline for a serious defect
- B. 0, meaning no deadline
- C. "later"
- D. null

#### [day4#lab-4-1] Six fields, validated

Lab 4.1 · 25 min

Extract six fields from inspection reports into a validated schema, repair replies that fail and keep a null where the report states nothing.

[D4_1_extraction.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D4_1_extraction.ipynb)

- [ ] The schema with Pydantic (6 min)
- [ ] The prompt and three reports (6 min)
- [ ] Validate and repair (6 min)
- [ ] A null, not an invented value (4 min)
- [ ] Twelve reports, saved with the version (3 min)
- [ ] ✱ Stretch: Add a seventh field, the street number, and measure it on the twelve reports

### Session 2: Field-level validation

#### [day4#s2] Field-level validation

*Session 2*

- Define precision and recall for a field that may be empty
- Compute them per field over 500 reports
- List the commonest errors per field and the rule that would catch each

#### [day4#outcomes] A field that may be empty has five outcomes, not two

*Lab 4.2, step 2*

| Outcome | Reference | Extracted | Counts against |
| --- | --- | --- | --- |
| Right | a value | the same value |  |
| Wrong | a value | another value | precision and recall |
| Missed | a value | empty | recall |
| Invented | empty | a value | precision |
| Correctly empty | empty | empty |  |

#### [day4#field-scores] 94% of all values are right; the deadline's precision is 0.87

*Lab 4.2, step 3 (recorded run)*

| Field | Precision | Recall |
| --- | --- | --- |
| district | 1.000 | 0.942 |
| inspection_date | 0.966 | 0.966 |
| defect_type | 0.968 | 0.968 |
| severity | 0.968 | 0.968 |
| hazard_to_public | 0.908 | 0.908 |
| repair_deadline_days | 0.870 | 0.972 |

#### [day4#error-patterns] Each field fails in its own way, and most failures follow the text's form

*Lab 4.2, step 4*

| Field | Commonest error | n | Where |
| --- | --- | --- | --- |
| district | left empty for a spelling variant | 29 | Arabic 8% |
| inspection_date | day and month swapped | 17 | dd/mm/yyyy 15% |
| defect_type | damaged pavement read as pothole | 9 | English 4% |
| severity | medium read as low | 16 | Arabic 5% |
| hazard_to_public | "no risk" read as a risk | 46 | Arabic 9% |
| repair_deadline_days | empty filled with 14 | 18 | Arabic 12% |

#### [day4#rules-in-code] Most fixes are rules in code, not a better prompt

*Lab 4.2, step 5*

- Dates with slashes: parse in code, day first
- District: a list of spelling variants kept with the schema
- Hazard: check the negated phrase, override to false
- Deadline: keep it only when written in the text

- **The validation report.** One line per field: precision, recall, the commonest error and the rule that catches it. It goes to Khalaf with the table.

#### [day4#check-field] Which number tells Khalaf whether to trust the deadlines?

*Checkpoint*

**Question:** Khalaf will schedule repairs from `repair_deadline_days`. A wrong deadline sends a crew on the wrong day; a missing one is checked by phone. Which measure answers his question?

- A. The deadline field's precision, with the share of empty deadlines that stayed empty
- B. The accuracy pooled over all six fields
- C. The deadline field's recall
- D. The share of replies that passed the schema

#### [day4#lab-4-2] Field-level validation

Lab 4.2 · 25 min

Compute per-field precision and recall of the recorded extraction run over 500 reports, list the commonest errors and write the validation report.

[D4_2_field_validation.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D4_2_field_validation.ipynb)

- [ ] Load the run and the reference (3 min)
- [ ] Matching rules per field (5 min)
- [ ] Precision and recall per field (7 min)
- [ ] The commonest errors per field (6 min)
- [ ] The validation report (4 min)
- [ ] ✱ Stretch: An interval for the precision of the deadline field

### Session 3: Structure in text

#### [day4#s3] Structure in text

*Session 3*

- Cluster document vectors and choose a number of clusters
- Name clusters from their terms and examples
- Compare clusters with codebook categories and say what each shows

#### [day4#choosing-k] The silhouette barely moves with k: complaints have no sharp borders

*Lab 4.3, step 2*

| Item | Value |
| --- | --- |
| k = 3 | 0.100 |
| k = 5 | 0.101 |
| k = 8 | 0.102 |
| k = 10 | 0.110 |
| k = 12 | 0.086 |

Mean silhouette, cosine, 1,000 complaints. The silhouette advises; the number of clusters a person can read decides.

#### [day4#what-clusters-see] The five clusters follow the language, not the topic

*Lab 4.3, step 4*

| Agreement of the clusters with | Adjusted Rand |
| --- | --- |
| Routing labels (topic) | 0.005 |
| Guessed variety | 0.642 |

- One cluster is all English, one all formal Arabic
- Three are mostly Gulf dialect
- Wording-based vectors see wording

> **What goes wrong.** A team names the clusters "topics" and publishes their sizes. They were counting languages.

#### [day4#campaign-cluster] Every campaign message in the sample lands in one cluster

*Lab 4.3, stretch*

**26 of 26** campaign messages in the sample fall in one Gulf sewage cluster, a quarter of it

**Cluster 3, nearest the centre:** يا جماعة ترى المجاري طافحة عند مدخل الحي والريحة وايد قوية. الشارع غرقان مويه …

#### [day4#check-clusters] Can a cluster's size be published as a topic count?

*Checkpoint*

**Question:** A colleague proposes a new quarterly figure: the share of complaints in each of the five clusters, named from their top terms. What is the main problem?

- A. Five is the wrong number of clusters
- B. The silhouette is too low; a higher one would make the figure valid
- C. A cluster has no definition or measured error, and here it tracks language and a campaign more than topic
- D. The sample of 1,000 is too small

#### [day4#lab-4-3] Structure in text

Lab 4.3 · 25 min

Cluster complaint embeddings, name five clusters from their terms and examples, and compare them with the codebook categories.

[D4_3_clusters.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D4_3_clusters.ipynb)

- [ ] Vectors for a sample of complaints (5 min)
- [ ] k-means for several k, with silhouette (6 min)
- [ ] Five clusters: terms and examples (7 min)
- [ ] Name them and compare with the categories (7 min)
- [ ] ✱ Stretch: Find the campaign: which cluster is it, and what would it do to a topic count?

### Session 4: Errors downstream

#### [day4#s4] Errors downstream

*Session 4*

- Compute a naive district rate from model labels
- Correct it with the gold set, stratified by language
- Report naive and corrected rates with intervals and a version record

#### [day4#rectifier] The gold set measures how far the model's share is off, one variety at a time

*Lab 4.4, step 2*

| Guessed variety | Gold n | Model's share | True share | Rectifier |
| --- | --- | --- | --- | --- |
| Modern Standard Arabic | 127 | 0.197 | 0.205 | −0.008 |
| Gulf dialect | 107 | 0.187 | 0.280 | −0.093 |
| English | 66 | 0.152 | 0.121 | +0.030 |

Corrected count = model's count − complaints × rectifier, summed over varieties.

#### [day4#corrected-rates] The Gulf-speaking districts move up; Al-Khalij does not move

*Lab 4.4, steps 3 and 4*

| Per 10,000 residents | Gulf share | Naive | Corrected | 95% interval |
| --- | --- | --- | --- | --- |
| Al-Naseem | 57% | 47.0 | 57.1 | 50.2 to 64.5 |
| Al-Jazira | 55% | 38.5 | 47.9 | 41.4 to 54.9 |
| Al-Salam | 48% | 39.0 | 47.3 | 41.1 to 53.8 |
| Al-Shati | 18% | 21.5 | 22.7 | 17.2 to 27.0 |
| Al-Khalij | 13% | 23.8 | 23.8 | 18.2 to 28.1 |

#### [day4#against-truth] The correction restores the gap between districts, which is what the director compares

*Only in a course: the truth*

**23.2 → 33.3** Al-Naseem minus Al-Khalij, naive then corrected; the true gap is 32.6

- Average error per district: naive 2.7, corrected 2.6
- All 12 intervals contain the true rate
- The correction trades a hidden bias for a visible variance

#### [day4#campaign-rate] Counted message by message, one campaign would double Al-Naseem's rate

*Lab 4.4, stretch*

| Al-Naseem, per 10,000 | Naive | Corrected |
| --- | --- | --- |
| Campaign counted as one issue | 47.0 | 57.1 |
| Campaign's 576 messages counted | 98.8 | 113.3 |

Every choice from Day 1 reaches the published number: copies, the campaign rule, redaction, the variety guess.

#### [day4#check-corrected] Why stratify the correction by variety?

*Checkpoint*

**Question:** One rectifier for all complaints (−0.030) raises every district's rate by about the same amount, 5.4 to 5.8 per 10,000. The stratified rectifiers raise Al-Naseem by 10.1 and Al-Khalij by 0.0. Which reason justifies stratifying?

- A. It always gives narrower intervals
- B. It uses more gold complaints
- C. It makes all districts' rates rise equally
- D. The model's error differs by variety and districts differ in their variety mix

#### [day4#capstone-choice] Choose the corpus you will defend

*Lab 4.4, step 5*

- **Nadwa libraries.** Facilities feedback per branch, corrected, for the renovation budget. Six branches, 2,575 documents.
- **Raafid social support.** Late-payment enquiries per region and month, with intervals: national or regional?

Each has personal data to redact, a 200-document gold set with two coders, recorded runs and a brief. A public corpus needs the trainer's approval.

#### [day4#lab-4-4] Corrected rates

Lab 4.4 · 25 min

Correct model-label complaint rates with the human sample, compare naive and corrected rates by district with intervals, and choose the capstone corpus.

[D4_4_corrected_rates.ipynb](https://sdaiaacademy.github.io/ds-306/labs/D4_4_corrected_rates.ipynb)

- [ ] Naive rates per district from model labels (5 min)
- [ ] The correction from the gold set, by language (6 min)
- [ ] Corrected rates per district (6 min)
- [ ] Bootstrap intervals (5 min)
- [ ] Choose the capstone corpus (3 min)
- [ ] ✱ Stretch: What does the campaign do to Al-Naseem's rate, with and without it?

#### [day4#wrap-up] Three things to keep

*Day 4 · wrap-up*

- **Valid is not right.** A schema checks form; field-level precision and recall check truth.
- **A cluster is a lens.** It shows what the vectors see, here language and a campaign, not a category.
- **Correct, then compare.** A human sample turns a biased count into an estimate with an interval.

#### [day4#next] Capstone: a text measurement defended live

*Next*

Eight minutes to defend your pipeline, ten documents re-labelled live, then questions. Bring the corrected estimate, its interval and its version record.

## Capstone: Capstone: a text measurement defended live

Each participant defends a text-measurement pipeline in eight minutes, then re-labels ten documents chosen by the assessor and answers questions

#### [capstone#title] Capstone: a text measurement defended live

*SDAIA Academy · Text and Unstructured Data for Data Science*

Capstone: Each participant defends a text-measurement pipeline in eight minutes, then re-labels ten documents chosen by the assessor and answers questions

Data Science Track · 4 teaching days + capstone day · 8 min talk and demo · 7 min Q&A · DS-306

#### [capstone#agenda] How the defences run

*Capstone*

- **Expectations and final prep**: the rubric, what full marks look like, a last rehearsal
- **Defences**: eight minutes each, then seven minutes of live labelling and questions
- **Review and closing**: peer feedback, the trainer's review, what next

#### [capstone#the-task] One question, one corpus, one corrected number you can defend

*The task*

- The director's question from your brief, in one sentence
- The corpus prepared and redacted, with its miss rate
- A gold set with agreement, and a model scored on it
- Fields extracted and validated per field
- The corrected estimate with its interval
- The reliability memo and the version record

- **Corpora.** Nadwa libraries or Raafid social support (synthetic, in `labs/data/capstone/`), or a public corpus the trainer approved. Extraction uses the course's 500 inspection reports unless your corpus has its own fields.

#### [capstone#rubric] The rubric

*How the project is scored*

| Item | Value |
| --- | --- |
| Preparation and redaction | 25 |
| Gold set and agreement | 20 |
| Models and extraction | 20 |
| Reliability memo | 25 |
| Reproducibility | 10 |

> **Every claim carries a number from a run.** A claim without one is a plan, not a result.

#### [capstone#full-marks] Each criterion has one thing that separates a pass from full marks

*What full marks look like*

| Criterion | Full marks |
| --- | --- |
| Preparation and redaction | A near-duplicate rule justified by a threshold table; a redaction miss rate with its interval |
| Gold set and agreement | Kappa by group, and the disagreements read and explained |
| Models and extraction | Two methods compared on the same gold set, paired; precision and recall per field |
| Reliability memo | Criteria set before the results; separate answers for per-document and aggregate use |
| Reproducibility | Lock file, prompts, saved outputs and a version record for every label set |

#### [capstone#format] Eight minutes to defend, seven to label live and answer

*Format*

- **1 · The question.** Who asked, what decision it feeds. One slide.
- **2 · The pipeline.** Each measurement choice with the number that justified it.
- **3 · The estimate.** Naive and corrected, the interval, the limits, the memo's decision.

> **Then live.** The assessor picks ten documents; you label them from your codebook and explain any disagreement with your gold set.

#### [capstone#live-labelling] The ten documents test the codebook, not your memory

*The seven minutes after the talk*

1. **1 · Ten documents** The assessor picks them from your corpus, some from your gold set
2. **2 · Label** From your codebook, aloud, about two minutes
3. **3 · Explain** Where you differ from your gold label, say why

> **Assessor.** Pick at least two documents with two problems and one in each language variety.

#### [capstone#running-order] Who defends when

*Running order*

| # | Participant | Corpus and question |
| --- | --- | --- |
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |
| 4 |  |  |
| 5 |  |  |
| 6 |  |  |
| 7 |  |  |
| 8 |  |  |

#### [capstone#final-prep] Final prep · 20 minutes

*Before the first defence*

Rehearse once against the clock, check the repository link opens, keep your codebook at hand.

#### [capstone#now-presenting] Defence

*Now defending*

##### Ten documents and questions

#### [capstone#review] What the defences showed

*Trainer review*

- **Strongest patterns.** What several projects got right.
- **Common gaps.** What most projects would fix next.
- **One surprise.** Something nobody expected.

#### [capstone#what-next] Keep going

*After the course*

- **The follow-up task:** audit one labelling process, at your own organisation or in a published source, with the course's checks, due in four weeks (labs/followup/)
- **Your project stays yours:** keep it reproducible and add the next improvement you named today
- **Next Academy course:** DS-311, labelling guidelines, pilots and adjudication: building the gold set this course supplied

#### [capstone#thanks] Thank you

*SDAIA Academy*

Text and Unstructured Data for Data Science
