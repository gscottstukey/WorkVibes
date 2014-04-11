from bs4 import BeautifulSoup
import requests
import urllib2
import re
import random
import time
from sys import argv
import os

# Collect names of companies classified as software/IT on Glassdoor.

# User specifies:
# - number of pages (10 companies per page)
# - starting index to append to URL.

# Output: 
# - company names are stored in myfile, separated by commas
# - index numbers of pages processed are stored in logfile

def fetch(index=1, count = 1):
    '''
    access urls that have a sequential order as part of the url
    input: 
        - starting index (int)
        - number of urls to fetch (int)
    output:
        - company names appended to rslt.txt file
        - running list of page indexes appended to log.txt file
    '''

    myfile  = open('rslt.txt', 'a')
    logfile = open('fetch_log.txt',  'a')                        # log which pages were scraped
    url_list = random.sample(xrange(index, index+count), count)  # generate randomized list of indexes

    done_list = []          

    try:
        for idx in url_list:
            if idx in done_list:
                print "skipping duplicate", idx
            else:
                # returns reviews for IT companies; this could be generalized.
                url = "http://www.glassdoor.com/Reviews/information-technology-company-reviews-SRCH_II10013.0,22_IP%d.htm" % (idx)
                rqst = requests.get(url)
                soup = BeautifulSoup(rqst.content)
                
                for row in soup.findAll('h3'):
                    company = row.text.encode('utf-8').strip()
                    if company != 'Companies by Industry' and company != 'Jobs by Company' and company != 'Additional Resources':
                        #print company, ',',
                        myfile.write(company)
                        myfile.write(',')  
            
                logfile.write(str(idx)+' ') 
                time.sleep(2)  # add delay between each request

    except urllib2.HTTPError, e:
        print '*** HTTPError = ' + str(e.code)
    except urllib2.URLError, e:
        print '*** URLError = ' + str(e.reason)
    except Exception:
        print "*** unknown error"

    finally:
        myfile.close()
        logfile.write('\n\n')
        logfile.close()

def main():

    print "\nThis program retrieves names of IT companies from Glassdoor.com, 10 per page.\n"
    idx = raw_input("Enter starting URL page index:   ")
    try:
        idx = int(idx)
    except ValueError:
        print "not a number"

    if idx > 500 or idx < 1:
        print "Invalid number, must be between 1 and 500"
    else:
        num_urls = raw_input("How many pages would you like to retrieve? (recommend < 500)   ")
        try:
            num_urls = int(num_urls)
        except ValueError:
            print "not a number"

        t1 = time.clock()
        fetch(idx, num_urls) 
        print "elapsed time:", (time.clock() - t1)

if __name__ == "__main__":
    main()