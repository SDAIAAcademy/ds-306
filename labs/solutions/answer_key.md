# Answer key for trainers

The numbers the solution notebooks print on the full data with the stand-in (no model key), as quoted in the
decks. Quick mode (`SADA_QUICK=1`) samples and prints different numbers. With a working key, Labs 2.3, 3.1 (task
2), 4.1 and 4.3 call a model and their numbers will differ; every other lab reads recorded files and reproduces
exactly.

## Planted problems

What the data were built to contain, so that each lab has something to find. All of it is synthetic
(`prepare_data.py`, seed 306); `truth/complaints_truth.csv.gz` holds the hidden category, variety and kind of every
complaint.

| Where | Planted problem | Found in |
|---|---|---|
| complaints | The form's language field contradicts the text on 8.8% of complaints, 25.1% of app complaints | Lab 1.1 |
| complaints | Persian letter forms, diacritics, tatweel, Arabic-Indic digits, repeated letters, Gulf spellings | Lab 1.2 |
| complaints | 555 exact copies, 369 resubmissions with small edits, and a campaign of 600 near-identical sewage messages in Al-Naseem, 3 to 12 June 2026 | Lab 1.3 |
| complaints | Phone and identity numbers in both digit systems, with spaces and dashes; names written in running text | Lab 1.4 |
| gold set | A quarter of complaints are ambiguous (two problems); human agreement drops on them | Lab 2.1 |
| pool | 12% of routing labels are wrong, most of them to a neighbouring category | Lab 2.2 |
| recorded runs | Fahim is less accurate on Gulf dialect, varies between runs, and moves with the wording of the prompt | Labs 3.1 to 3.4 |
| recorded runs | Gulf sewage complaints about a flooded street read as roads | Lab 3.3 |
| extraction run | Invented deadlines (28% of reports without one), day and month swapped in dd/mm dates, "no risk" read as a risk, pothole and pavement confused, medium read as low in Arabic, district left empty for some spellings | Labs 4.1, 4.2 |
| all complaints | Sewage under-counted where Gulf dialect is common; the campaign inflates Al-Naseem | Lab 4.4 |

## Expected numbers

**Day 1**
- Lab 1.1: channels web 30.9%, app 27.1%, call centre 23.5%, social 9.7%, email 8.8%; language field wrong on
  1,750 complaints (8.8%); median length Arabic 126 characters, English 164.
- Lab 1.2: distinct tokens 14,158 raw, 7,270 normalised, 7,211 after the dialect map.
- Lab 1.3: exact copies 639 (more than the 555 planted: short template complaints sometimes coincide); 103,238 candidate pairs, 11,031 confirmed at Jaccard 0.7; 998 messages removed, 576
  kept and flagged as the campaign. Threshold table (21-day window, 924 true copies): 0.6 removes 1,247 (839 true),
  0.7 removes 998 (810), 0.8 removes 758 (626).
- Lab 1.4: 339 marked values in the audit sample; the naive pattern misses 80.6% of phone numbers; after redaction
  7.7% of values are missed, all names (26 of 122, about 15% to 29%).

**Day 2**
- Lab 2.1: reference coders on pair40, observed agreement 0.750, chance 0.144, kappa 0.708; gold coders kappa 0.829.
- Lab 2.2: accuracy 0.930 [0.900, 0.957], macro F1 0.917.
- Lab 2.3 (stand-in vectors): accuracy 0.893 [0.857, 0.927], 25 requests.
- Lab 2.4: paired difference +0.037 [−0.003, +0.073]; interval width unpaired 0.093, paired 0.077.

**Day 3**
- Lab 3.1: accuracy 0.810 [0.763, 0.853]; formal Arabic 0.868, Gulf 0.733, English 0.848; USD 0.027 per 1,000 on
  the paid endpoint.
- Lab 3.2: flip rate 0.197; run kappas 0.840, 0.864, 0.837; labels changing 13.7% between runs, 31.3% between
  prompts; majority of three 0.850.
- Lab 3.3: gap +0.135 [+0.025, +0.236]; 9 of 32 Gulf sewage complaints labelled roads; variety guess agrees on 95.7%;
  expected sewage recall from 0.752 (Al-Naseem) to 0.910 (Al-Khalij).
- Lab 3.4: Fahim fails on Gulf (shortfall 0.187), on stability (80.3%) and on the gap (0.135).

**Day 4**
- Lab 4.1: 47 of 177 reports without a deadline got one (26.6%); the grounding rule catches all 47; all six fields
  right in 8 of the 12 reports.
- Lab 4.2: pooled 94.0%; deadline precision 0.870 [0.834, 0.903], recall 0.972; hazard 0.908; district recall
  0.942; 17 swapped dates, all in dd/mm/yyyy.
- Lab 4.3 (stand-in vectors): silhouette about 0.10 for every k (best k = 10, 0.110); adjusted Rand 0.005 with the
  routing labels and 0.642 with the variety; all 26 campaign messages of the sample in one cluster.
- Lab 4.4: rectifiers formal Arabic −0.008, Gulf −0.093, English +0.030; Al-Naseem 47.0 naive, 57.1 corrected
  [50.2, 64.5], 55.7 true; Al-Naseem minus Al-Khalij 23.2 naive, 33.3 corrected, 32.6 true; all 12 intervals cover
  the true rate; with the campaign counted, Al-Naseem's naive rate is 98.8.

**Pre-work**: the keyword list scores 0.857 on the gold set, macro F1 0.827. It was written after reading the
templates of a synthetic corpus, so it is a strong baseline here; say so if participants ask why it beats Fahim.
