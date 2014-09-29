from bs4 import BeautifulSoup
import requests
import time
import io
import csv
import os
import string

def main():
    '''
    Crawl glassdoor.com, collecting company review text. 
    
    Note: there are two URL formats: one for the first URL for each company, 
        and one for for the 2nd through nth URLs.

    Input: 
    - .csv file with base URL, suffix, and number of pages to retrieve

    Output:  
    - One .htm file for each page of reviews
    - Log file with status of each request 
    '''

    logfile = open('scrape_log.txt', 'a')
    with open('glassdoor_urls.csv') as f:
        url_list = [tuple(rec) for rec in csv.reader(f, delimiter='\t')]

    for (url, suffix, idx) in url_list: 
        idx = int(idx)
        trim_point = string.find(url, "-Reviews-")
        # Set URL to base form for 2nd through idx pages
        new_url = url[:trim_point]

        # Create output filename for first page, then fetch the page
        fname = new_url[33:55] + "_1.htm"
        rqst = requests.get(url)
        logfile.write("Status = "+str(rqst.status_code)+" for "+url+'\n')
        with open(fname, 'w') as f:
            f.write(rqst.content)
        logfile.write("  Wrote "+fname+'\n')
        time.sleep(3)

        # Process remaining pages in url_list. Construct URLs from base form.
        for pagenum in range(2, idx+1): 
            this_url = url + "_" + str(pagenum) + ".htm"
            rqst = requests.get(this_url)
            logfile.write("status="+str(rqst.status_code)+" for "+this_url+'\n')

            # Build output filename using first 22 characters of company name
            # and location (in URL). Append page number and "htm".
            fname = new_url[33:55] + "_" + str(pagenum) + ".htm"
            with open(fname, 'w') as f:
                f.write(rqst.content)
            logfile.write("  Wrote "+fname+'\n')
            time.sleep(3)
    logfile.close()

if __name__ == "__main__":
    main()
