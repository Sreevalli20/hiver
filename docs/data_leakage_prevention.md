# Data Leakage Prevention

## Overview

This document describes the data separation strategy to prevent leakage between training/development data and the golden evaluation set.

## Data Sources

### 1. Training/Development Data
- **Location:** `data/processed/`
- **Files:** 
  - `{brand}_train.csv` - 70% of conversations for training
  - `{brand}_dev.csv` - 15% of conversations for development/validation
  - `{brand}_test.csv` - 15% of conversations for testing (NOT used for evaluation)
  - `{brand}_retrieval_corpus.csv` - Combined train+dev for retrieval indexing
- **Source:** Real AmazonHelp Twitter conversations from Kaggle dataset
- **Size:** ~4,631 conversations (after filtering for AmazonHelp brand)
- **Labels:** Heuristically generated using keyword matching rules

### 2. Golden Evaluation Set
- **Location:** `golden/`
- **Files:**
  - `golden_200.csv` - Original heuristic-labeled set (200 examples)
  - `golden_annotation.csv` - Human annotation workflow file (200 examples)
- **Source:** Real AmazonHelp Twitter conversations (sampled from the same dataset)
- **Size:** 200 examples
- **Labels:** 
  - Initially: Heuristically generated (keyword matching)
  - Final: Human-labeled (after manual annotation workflow)
- **Sampling:** Stratified across 10 intents to ensure coverage

## Data Separation Rules

### ✅ ALLOWED (No Leakage)

1. **Training data usage:**
   - Classifier training: `{brand}_train.csv`
   - Retrieval corpus: `{brand}_retrieval_corpus.csv` (train+dev only)
   - Hyperparameter tuning: `{brand}_dev.csv`
   - Model selection: Based on dev set performance

2. **Golden set usage:**
   - Final evaluation only: `golden_annotation.csv` (human-labeled)
   - Never used for: training, tuning, retrieval indexing, model selection

### ❌ FORBIDDEN (Leakage)

1. **Golden set in training:**
   - Never add golden examples to `{brand}_train.csv`
   - Never use golden examples for classifier training
   - Never use golden examples for retrieval corpus

2. **Golden set in development:**
   - Never use golden examples for hyperparameter tuning
   - Never use golden examples for model selection
   - Never use golden examples for threshold tuning

3. **Circular evaluation:**
   - The previous heuristic-labeled evaluation used the same keyword rules for both training labels and test labels
   - This created circular evaluation that inflated metrics
   - Human-labeled evaluation breaks this circular dependency

## Pipeline Audit

### Current Implementation

#### Data Preparation (`scripts/prepare_data.py`)
- Loads raw Twitter dataset
- Filters for AmazonHelp brand
- Builds conversation threads
- Creates 70/15/15 train/dev/test split
- **Status:** ✅ Golden set is NOT included in this pipeline

#### Model Training (`scripts/train.py`)
- Trains classifier on `{brand}_train.csv`
- Builds retrieval index from `{brand}_retrieval_corpus.csv`
- **Status:** ✅ Golden set is NOT used for training

#### Evaluation (`evaluation/run_evaluation.py`)
- Loads golden set from `golden/golden_200.csv` or `golden/golden_annotation.csv`
- **Current behavior:** Uses heuristic labels if human labels not available
- **Status:** ⚠️ Needs update to prefer human labels when available

#### Retrieval System
- Indexes `{brand}_retrieval_corpus.csv` (train+dev only)
- **Status:** ✅ Golden set is NOT in retrieval corpus

## Required Changes

### 1. Update Evaluation Script
Modify `evaluation/run_evaluation.py` to:
- Check for human labels first (`human_intent` column)
- Fall back to heuristic labels only if human labels not available
- Clearly label which labels were used in results

### 2. Update Documentation
- Clearly document train/test separation in README.md
- Update REPORT.md to explain the heuristic vs human label distinction
- Remove any estimated performance claims

### 3. Add Validation
- Add script to verify no overlap between training conversations and golden set
- Check conversation IDs to ensure complete separation

## Verification Checklist

- [ ] Golden set conversation IDs are not in training data
- [ ] Golden set is not in retrieval corpus
- [ ] Evaluation script uses human labels when available
- [ ] Documentation clearly explains data separation
- [ ] No estimated performance claims in documentation
- [ ] Headline metrics only from human-labeled evaluation

## Sampling Methodology for Golden Set

The 200-example golden set was sampled as follows:

1. **Source:** Real AmazonHelp conversations from the same Kaggle dataset
2. **Stratification:** Sampled to ensure coverage of all 10 intents
3. **Exclusion:** Conversations used in train/dev/test splits were excluded
4. **Size:** 200 examples (within Hiver's 150-250 requirement)
5. **Initial labeling:** Heuristic keyword matching (for suggestion only)
6. **Final labeling:** Human annotation via web interface

## Important Notes

1. **Heuristic labels are NOT ground truth:** The initial labels in `golden_200.csv` are heuristic suggestions only. They must be verified by human annotation.

2. **Human labels are required:** For valid evaluation, all 200 examples must be human-labeled via the annotation workflow at `/golden` in the UI.

3. **No circular evaluation:** Human labels provide independent verification, breaking the circular dependency of heuristic evaluation.

4. **Separation maintained:** The golden set is sampled from the same dataset but from different conversations than the training data, ensuring no overlap.
