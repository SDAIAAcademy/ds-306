---
course: "Text and Unstructured Data for Data Science"
code: "DS-306"
version: "2027.1.0"
deck: "day1"
day: 1
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-306/slides/day1.html"
---

# Text and Unstructured Data for Data Science

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
