from bs4 import BeautifulSoup
import requests
import urllib2
import re
import random
import time
from sys import argv
import os

def fetch(index=1, count = 1):
    '''Fetch names of IT companies from glassdoor.com.
    The site lists one to ten companies on each IT review summary page. 

    Input: 
        - Starting url index (int)
        - Number of urls to fetch (int)
    
    Output:
        - Company names appended to myfile
        - List of url indexes and elapsed time appended to logfile 
    '''

    myfile  = open('rslt.txt', 'a')
    logfile = open('fetch_log.txt',  'a')
    t1 = time.clock()
    url_list = random.sample(xrange(index, index+count), count)  # randomize
    done_list = []          
    try:
        for idx in url_list:
            if idx in done_list:
                print "Skipping duplicate: ", idx
            else:
                url = "http://www.glassdoor.com/Reviews/information-technology- \
                    company-reviews-SRCH_II10013.0,22_IP%d.htm" % (idx)
                rqst = requests.get(url)
                soup = BeautifulSoup(rqst.content)
                
                for row in soup.findAll('h3'):
                    company = row.text.encode('utf-8').strip()
                    if company != 'Companies by Industry' and \
                        company != 'Jobs by Company' and \
                        company != 'Additional Resources':
                        myfile.write(company.split('    ')[0])
                        myfile.write(',')  
            
                logfile.write("Wrote URL index"+str(idx)+' \n') 
                time.sleep(2)  # include a polite delay between each request

    except urllib2.HTTPError, e:
        print '*** HTTPError = ' + str(e.code)
    except urllib2.URLError, e:
        print '*** URLError = ' + str(e.reason)
    except Exception:
        print "*** unknown error"
    finally:
        logfile.write("Elapsed time:" + str(time.clock() - t1))
        myfile.close()
        logfile.write('\n\n')
        logfile.close()

def main():
    ''' Fetch names of companies classified as software/IT on Glassdoor.

    Input:
    - number of pages (10 companies per page)
    - starting index to append to URL.

    Output: 
    - Company names are stored in myfile, separated by commas.
    - Index numbers of pages processed are stored in logfile
    '''

    print "\nThis program fetches names of IT companies."
    print "Each page has from one to ten company names.\n"
    idx = raw_input("Enter starting page (greater than or equal to 1):  ")
    try:
        idx = int(idx)
    except ValueError:
        print "Error: Not a number."

    if idx > 500 or idx < 1:
        print "Invalid number, must be between 1 and 500"
    else:
        num_urls = raw_input("How many pages would you like to retrieve?  ")
        try:
            num_urls = int(num_urls)
        except ValueError:
            print "Error: Number of pages should be a positive integer. "
        fetch(idx, num_urls) 

if __name__ == "__main__":
    main()