---
course: "Text and Unstructured Data for Data Science"
code: "DS-306"
version: "2027.1.0"
deck: "day4"
day: 4
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-306/slides/day4.html"
---

# Text and Unstructured Data for Data Science

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
