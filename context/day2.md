---
course: "Text and Unstructured Data for Data Science"
code: "DS-306"
version: "2027.1.0"
deck: "day2"
day: 2
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-306/slides/day2.html"
---

# Text and Unstructured Data for Data Science

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
