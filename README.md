## WorkVibes

Zipfian project: Summarize company reviews from Glassdoor.com.

This project has four components:

1 - Acquire company names (approx. 40,000 U.S. IT/software companies) from Glassdoor.com.

2 - Download html pages for bay area companies. Parse html, store text in MySQL database.

3 - Preprocess, vectorize, and curate a user-specified number of reviews for a specified company.

workvibes.py (3) and replacers.py (regex preprocessing) are currently in the repo; other code will be added soon. 
