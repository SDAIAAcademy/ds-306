# Text and Unstructured Data for Data Science: labs

## Quick start

- Google Colab: open a notebook from the course page; its first cell clones this repository.
- Locally: clone the repository, then open the notebooks in `labs/` with Jupyter.

| Unit | Session | Notebook |
|---|---|---|
| Day 1 | Session 1 · Text as a data source | [`D1_1_profile_corpus_language.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D1_1_profile_corpus_language.ipynb) |
| Day 1 | Session 2 · Preparing Arabic text | [`D1_2_normalise_letter_variants.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D1_2_normalise_letter_variants.ipynb) |
| Day 1 | Session 3 · Near-duplicates | [`D1_3_find_near_duplicate.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D1_3_find_near_duplicate.ipynb) |
| Day 1 | Session 4 · Redacting personal data | [`D1_4_mask_phone_numbers.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D1_4_mask_phone_numbers.ipynb) |
| Day 2 | Session 1 · Gold sets and agreement | [`D2_1_label_40_complaints.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D2_1_label_40_complaints.ipynb) |
| Day 2 | Session 2 · Sparse baselines | [`D2_2_train_character_n.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D2_2_train_character_n.ipynb) |
| Day 2 | Session 3 · Embeddings as features | [`D2_3_train_embedding_classifier.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D2_3_train_embedding_classifier.ipynb) |
| Day 2 | Session 4 · Comparing classifiers fairly | [`D2_4_compare_two_classifiers.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D2_4_compare_two_classifiers.ipynb) |
| Day 3 | Session 1 · Prompted classification | [`D3_1_classify_gold_set.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D3_1_classify_gold_set.ipynb) |
| Day 3 | Session 2 · Ask it twice | [`D3_2_repeat_one_prompt.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D3_2_repeat_one_prompt.ipynb) |
| Day 3 | Session 3 · Dialect gaps | [`D3_3_measure_agreement_modern.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D3_3_measure_agreement_modern.ipynb) |
| Day 3 | Session 4 · Is the model a good annotator | [`D3_4_decide_whether_model.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D3_4_decide_whether_model.ipynb) |
| Day 4 | Session 1 · Schema-constrained extraction | [`D4_1_extract_six_fields.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D4_1_extract_six_fields.ipynb) |
| Day 4 | Session 2 · Field-level validation | [`D4_2_compute_per_field.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D4_2_compute_per_field.ipynb) |
| Day 4 | Session 3 · Structure in text | [`D4_3_cluster_complaint_embeddings.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D4_3_cluster_complaint_embeddings.ipynb) |
| Day 4 | Session 4 · Errors downstream | [`D4_4_correct_model_label.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-306/blob/main/labs/D4_4_correct_model_label.ipynb) |

The notebooks are generated from the percent-format sources in `labs/_src/` by `labs/_tools/py2nb.py` (`uv run python _tools/py2nb.py` from `labs/`), which also writes the solutions to `labs/solutions/`. Edit the sources, not the notebooks.
