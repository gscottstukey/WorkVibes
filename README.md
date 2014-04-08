## WorkVibes

Zipfian project: Summarize company reviews from Glassdoor.com.

This project has four components:

- Acquire company names (IT, software) from Glassdoor.com

- Download html pages with company reviews, parse html, store text in MySQL database

- Preprocess, vectorize, and curate a user-specified number of reviews with high relevance across a set of reviews for a company.  The program accesses review text stored in MySQL tables. 

workvibes.py and replacers.py (regex preprocessing) are currently in the repo; other code will be added soon. 
