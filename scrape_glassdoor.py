from bs4 import BeautifulSoup
import requests
import time
import io
import csv
import os
import string

# This program crawls glassdoor.com, collecting company review text. 
# Note: there are two URL formats, one for the first URL for a company; the other for 2:n subsequent URLs.

# Input: file with base URLs, suffix, and number of secondary pages to retrieve

# Output:  
# - set of files containing text
# - log file

# Future: 
# - make this more flexible and interactive by acquiring all pages for a given company and (optional) location.
# - detect & handle end of review list. glassdoor returns the last page of reviews if we go beyond the available pages. 

logfile = open('scrape_log.txt', 'a')

with open('glassdoor_urls.csv') as f:
    url_list = [tuple(rec) for rec in csv.reader(f, delimiter='\t')]

def main():                                                    
    for (url, suffix, idx) in url_list: 
        idx = int(idx)
        trim_point = string.find(url, "-Reviews-")
        new_url = url[:trim_point]                       # set url to base form for 2:idx pages

        fname = new_url[33:55] + "_1.htm"                # create output filename for first page
        rqst = requests.get(url)                         # fetch first page
        logfile.write("Status = "+str(rqst.status_code)+" for "+url+'\n')
        with open(fname, 'w') as f:
            f.write(rqst.content)
        logfile.write("  Wrote "+fname+'\n')
        time.sleep(3)

        for pagenum in range(2, idx+1):                  # process remaining pages as specified in url_list
            this_url = url + "_" + str(pagenum) + ".htm" # construct secondary url from base form
            rqst = requests.get(this_url)
            logfile.write("status = "+str(rqst.status_code)+" for "+this_url+'\n')
            # Construct output filename using first 22 characters of company name and
            # location (in URL), then append page number and "htm".
            fname = new_url[33:55] + "_" + str(pagenum) + ".htm"
            with open(fname, 'w') as f:
                f.write(rqst.content)
            logfile.write("  Wrote "+fname+'\n')
            time.sleep(3)
    logfile.close()

if __name__ == "__main__":
    main()
