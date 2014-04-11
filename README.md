## WorkVibes: Summarize company reviews from Glassdoor.com.

### Components

fetch_company_names.py: Acquire company names (approx. 40,000 U.S. IT/software companies) from Glassdoor.com

scrape_glassdoor.py: Download html pages for bay area companies

parse_glassdoor_html.py:  Parse html; store text in MySQL database

WorkVibes.py:  Preprocess, vectorize, and curate a user-specified number of reviews for a specified company

replacers.py: regex preprocessing

MySQL_create_db.mysql: script for creating database and tables






