# LEXB_mt
## Scripts for the creation and cleaning of the LEXB_mt corpus

The LEXB_mt corpus is the version of the LEXB corpus used for machine translation training. 
Texts are scraped and aligned using LF Aligner; the corpus in .tmx format is then cleaned up and filtered.


- `LexScraper_tm.py`:   	a scraper for texts from the LexBrowser database.
   	 			Given a list of URLs, for each URL:
  - parsing the HTML
  - filtering according to blacklisted terms in titles
  - extracting law title, subtitle and body and printing to a .txt file
  - creating a .csv report file


- `tmx_cleaner.py`:		a toolkit for cleaning and filtering the parallel corpus in .tmx format and getting clean sentence-sentence
				translation units:
  - `remove_untranslated()`:    filters out TUs with identical or almost identical source and target sentences
  - `punct_digit_filter()`: filters out TUs with at least one segment containing punctuation and/or numbers only.
  - `noise_cleaning()`:     extensive cleaning at sentence level
    - removes noise at the beginning of segments: “(1)", "1.", "a.", "1)", "a)", "1.1", "1.1)", “(1/bis)”, "A 1)", "I.A.", "I.1)", "1.1.1", "1.1.1.1", "I.", "I)", "a1)", "a1.", "A)", "(A)", "•", ".", "-"
    - removes noise at the end of segments: ">", " *)", "1)", "(1)"
    - removes other noise: single/double quotes if both at the beginning and the end of segments only; single/double quotes if only at the beginning or the end of segments
  - `non_alphabetical_ratio_filter()`:     filters out sentence pairs with segments having a number-punctuation/letters ratio higher than 0.6
  - `remove_blank_units()`:     filters out half-empty TUs and TUs containing segments with only whitespaces.
  - `dehyphenation()`:	normalizes erroneously hyphenated words using a vocabulary-based approach
  - `remove_whitespaces()`:     removes leading and trailing whitespaces.
  - `language_filter()`:     filters out sentence pairs whose detected languages are not it-de.
  - `length_ratio_filter()`:    filters out sentence pairs whose length ratio is higher than a given threshold.
  - `filter_per_token()`:	filters out very long and very short segments according to number of tokens.	


- `dataset_splitting_dedupe.py`:	a script for dataset splitting between training set and test set. Test set contains 2000 random sentences between 10-20 words. Before dataset splitting, a more advanced deduplication operation (based on the approach of Pinnis et al. 2018) is carried out in order to avoid overlapping of almost duplicates between training set and test set.

- `evaluation_metrics.py`:	generating automatic evaluation scores (BLEU, chrF3). A .tsv file with scores at segment level is also created, for more granular and score-based manual evaluation.

- `removing_test-set_from_training-set.py`:	to be used to deduplicate sentence pairs between training/test when adding new data to the training set.




