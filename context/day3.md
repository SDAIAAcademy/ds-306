---
course: "Text and Unstructured Data for Data Science"
code: "DS-306"
version: "2027.1.0"
deck: "day3"
day: 3
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-306/slides/day3.html"
---

# Text and Unstructured Data for Data Science

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
