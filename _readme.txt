

- "parallel_URLs_collection.py":		collecting a parallel list of URLs of Italian and German laws from the LexBrowser database for subsequent text 
						scraping. A first filtering is carried out based on a blacklist of terms in the Italian law title.


- "LexScraper_IT.py":   	a scraper for law texts from the LexBrowser database.
   	 			Given a list of URLs, for each URL:
       					- parsing the HTML
        				- extracting law title, subtitle and body
        				- printing it to a .txt file
        				- creating a .csv report file.


- "LexScraper_DE.py":   	same as LexScraper_IT.py, there is just an additional filtering stage based on a blacklist of terms in the German law title.


- "unpaired_texts_filter.py":   given two directories of IT and DE scraped texts, filtering out unpaired bitexts (according to the ID number in their filename) to 					allow subsequent text alignment.


- "tmx_cleaner.py"		A toolkit for cleaning the parallel corpus in .tmx format (aligned with LF Aligner) and getting clean sentence-sentence
				translation units:
				- removing untranslated TUs
				- cleaning sentences from noise at the beginning and the end of the segment
				- removing TUs containing segments with only whitespaces
				- removing leading and trailing spaces
				- filtering, displaying and eliminating "bad" TUs with segments with different lenghts or wrong language

