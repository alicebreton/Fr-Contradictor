# Fr-Contradictor: A Toolkit for Generating Contradictions of French Sentences

**Fr-Contradictor** is a Python toolkit designed to create contradictions of French sentences. This repository is aimed at researchers building datasets for misinformation studies, enabling controlled generation of contradictory statements from original sentences.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Repository Structure

### 1. **./scripts**

- **`contradictor.py`**Applies various techniques to generate contradictions of French sentences:

  - **Negation**: Introduces negations to sentences.
  - **Antonym Replacement**: Replaces verbs or adjectives with their antonyms while preserving grammatical congruence.
  - **GPT Contradictions**: In the last case that no Roots to be contradicted, this script uses OpenAI GPT to propose nuanced contradictions.
    **Input**: Text files with one sentence per line.
    **Output**: Contradicted sentences in different formats.
- **`extract_verb_adj_root.py`**Extracts root verbs and adjectives from input sentences to aid in constructing antonym dictionaries.
- **`spacy_analytics.py`**
  Annotates sentences with syntactic details using SpaCy’s French transformer model (`fr_dep_news_trf`). The output includes token-level information such as lemma, part-of-speech (POS), dependency labels, morphological features, and head. This annotation also aid in constructing the antonym dictionaries.

### 2. **Dictionaries**

- **`adj_antonyme.txt`**: Adjective-antonym pairs.
- **`verbe_antonyme.txt`**: Verb-antonym pairs.

### 3. **Input/Output**

- **Input Files**: Text files with sentences to process.
- **Output Files**: Contradicted sentences or syntactic analysis results.

---

## Installation

### Prerequisites

```bash
   pip install -r requirements.txt
   python -m spacy download fr_dep_news_trf
```

Make sure you have your OpenAI key stored at line 31 of `./script/contradictor.py`. You do not have the enter a key for the script to work.

## Usage

### Make contradictions

Make sure your reference sentences are stored in `./input` and make sure there is one sentence per line.

To build the contradiction dataset use this command:

```
python ./scripts/contradictor.py
```

You should get a new file in the `./output` folder with the contradictions.

### Build your Antonym dictionaries

In the `./dictionaries` folder, you can see two different dictionaries containing the antonyms of various verbs and adjectives. You can extract all the verb and adj roots from your reference file using this command:

```
python ./scripts/extract_verb_adj_root.py
```

You will get a list of all the verbs and the adj that needs to be in both of the dictionaries. You should follow this syntax inside both of the dictionaries:

```
réchauffer:refroidir
prendre:lâcher
aider:nuire
```

It can bu useful to extract various syntactical information with Spacy to improve the dictionaries. To do so, use this command:

```
python ./scripts/spacy_analytics.py
```

## Limitation

The contradiction output should be reviewed. Some mistakes might occur where, for example, the difference between a transitive and a intransitive verb is not made.
