# custom_MT
## Python scripts for corpus scraping and cleaning

- `parallel_URLs_collection.py`:		collecting a parallel list of URLs of Italian and German laws from the LexBrowser database for subsequent text 
						scraping. A first filtering is carried out based on a blacklist of terms in the Italian law title.


- `LexScraper_IT.py`:   	a scraper for law texts from the LexBrowser database.
   	 			Given a list of URLs, for each URL:
  - parsing the HTML
  - extracting law title, subtitle and body and printing to a .txt file
  - creating a .csv report file


- `LexScraper_DE.py`:   	same as LexScraper_IT.py, there is just an additional filtering stage based on a blacklist of terms in the German law title.


- `unpaired_texts_filter.py`:   given two directories of IT and DE scraped texts, filtering out unpaired bitexts (according to the ID number in their filename) to 					allow subsequent text alignment.


- `tmx_cleaner.py`:		a toolkit for cleaning the parallel corpus in .tmx format (aligned with LF Aligner) and getting clean sentence-sentence
				translation units:
  - `remove_untranslated()`:    removes TUs with identical source and target
  - `remove_art_and_co()`:      a first TU cleaning. Noise at sentence beginning is removed ("Art. 1"). TUs with segments containing only non-relevant noise (such as ""Art. 1". "(1)", "1." "1bis.") are removed from the TM.
  - `remove_punctuation_numeral_segments()`: removes TUs with at least one segment containing only punctuation and/or numbers.
  - `noise_cleaning()`:     extensive segment cleaning
    - removes noise at the beginning of segments: “(1)", "1.", "a.", "1)", "a)", "1.1", "1.1)", “(1/bis)”, "A 1)", "I.A.", "I.1)", "1.1.1", "1.1.1.1", "I.", "I)", "a1)", "a1.", "A)", "(A)", "•", ".", "-"
    - removes noise at the end of segments: ">", " *)", “1)”, “(1)”
    - removes other noise: single/double quotes if both at the beginning and the end of segments only; single/double quotes if only at the beginning or the end of segments
  - `remove_blank_units()`:     removes half-empty TUs and TUs containing segments with only whitespaces.
  - `remove_whitespaces()`:     removes leading and trailing whitespaces.
  - `select_TUs_with_wrong_lang()`:     allows manual selection (delete or retain) of TUs containing segments whose detected language does not match the default it/de language.
  - `select_TUs_with_different_lenght()`:    allows automatic or manual selection (delete or retain) of TUs whose length difference ratio is higher than a given threshold (indicating possible misalignment).
