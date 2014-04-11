from bs4 import BeautifulSoup
import os
from datetime import datetime
import pymysql 

# Use BeautifulSoup to parse html for Glassdoor company review text.
# Store data in MySQL.
# Writes status to stdout. 
# Assumes program runs in data directory.
# Future: Check for additional special encoding/decoding issues. 

def open_conn():
    db=pymysql.connect(host="localhost", port=3306, db="glassdoor2", user='root', passwd='passwd12')
    c=db.cursor()
    c.execute("""USE glassdoor2;""")
    c.close()
    return db

def get_company_id(company_name, db):
    company_id = []
    try:
        c = db.cursor()
        sql = "SELECT company_id FROM company WHERE company_name = '%s'" % (company_name)
        c.execute(sql)
        results = c.fetchall()
        for row in results:
            company_id = row[0]
    except db.Error, e:
        print "--- Error in get_company_id(39) %d: %s" % (e.args[0], e.args[1])
    c.close()
    return company_id

def get_location_id(city, company_id, db):
    location_id = []
    try:
        c = db.cursor()
        sql = "SELECT location_id FROM location WHERE city = '%s' AND company_id = '%s' LIMIT 1" % (city, company_id)
        c.execute(sql)
        results = c.fetchall()
        for row in results:
            location_id = row[0]
    except db.Error, e:
        print "--- Error %d: %s" % (e.args[0], e.args[1])
        # Rollback in case there is any error
    c.close()
    return location_id

def parse_company(soup, db):
    h1tag = soup.find('div', class_ = "h1")

    company_name = h1tag.find('tt', class_ = "i-emp").text
    #print company_name,

    eis = soup.find('div', id="EI-Srch")
    global_rating = eis.find('span', class_ = "rating").text   # rating is out of 5 total
    #print global_rating

    hq_location = eis.find('span', class_ = "i-loc").text.strip()
    hq_location = hq_location.split(",")
    hq_city = hq_location[0]
    #print hq_city,

    hq_statecountry = hq_location[1].strip()
    #print hq_statecountry

    # Insert company into the database if it's not already there
    sql = "SELECT company_name FROM company WHERE company_name = '%s' LIMIT 1" % (company_name)
    try:
        c = db.cursor()
        c.execute(sql)
        results = c.fetchall()
    except db.Error, e:
        print "--- Error in parse_company(85), %d: %s" % (e.args[0], e.args[1])
    c.close()

    if len(results) == 0:   # new company name, add to db
        try:
            c = db.cursor()
            c.execute(u"""
                INSERT INTO company (company_name, global_rating, hq_city, hq_statecountry) 
                VALUES(%s,%s,%s,%s) """, 
                (company_name, global_rating, hq_city, hq_statecountry))
            db.commit()
            print "+++ Inserted", company_name 
        except db.Error, e:
                print "Error in parse_company(105), %d: %s" % (e.args[0], e.args[1])
                db.rollback()
                return -1
        c.close()
    return company_name

def parse_location(soup, company_name, db):
    main_col = soup.find('div', id="MainCol")

    local_rating = main_col.find('span', class_ = "rating").text
    #print local_rating

    review_location = main_col.find('span', class_ = "nonSoloLocFilter").text
    review_location = review_location.split(",")

    city = review_location[0][3:]
    #print "location:", city

    state = review_location[1].strip()
    #print state

    company_id = get_company_id(company_name, db)

    #print '---in parse_location(126):', company_name, city, company_id

    # See if location-company combo is already in the db - if not, insert it. 
    sql = "SELECT location_id FROM location WHERE company_id = '%s' and city = '%s' LIMIT 1" % (company_id, city)
    try:
        c = db.cursor()
        c.execute(sql)
        results = c.fetchall()
        #for row in results:
        #    print row
        c.close()   
    except db.Error, e:
        print "--- Error in parse_location, %d: %s" % (e.args[0], e.args[1])
        c.close()

    #print "name/city/state/id/rating:", company_name, city, state, company_id, local_rating

    if len(results) == 0:    # add new company-location pair
        try:
            c = db.cursor()
            c.execute(u"""
                INSERT INTO location (city, state, company_id, local_rating) 
                VALUES(%s,%s,%s,%s) """, 
                (city, state, company_id, local_rating))
            db.commit()
            print "+++ Inserted", city
            c.close()
            
        except db.Error, e:
            print "--- Error in parse_location(157), %d: %s" % (e.args[0], e.args[1])
            db.rollback()
            c.close()
            return -1
    return city

def parse_reviews(soup, city, company_id, db):
    location_id = get_location_id(city, company_id, db)

    for rev in soup.find('div', id="EmployerReviews").find_all('div', class_ = "employerReview"):
                
        for vals in rev.select('span.gdStars.med .rating .value-title'):
            review_rating = vals.attrs['title']
            #print review_rating

        # *** Some reviews have no bar for Culture & Values. Omitting them for now.
        # *** Would need to use 'subtle' div class. 

        review_summary = rev.find('span', class_ = 'summary').text
        #print review_summary
    
        job_status = rev.find('div', class_ = 'authorJobTitle').text   
        job_status_temp = job_status.split('(')
        job_title = job_status_temp[0]
        #print job_title,
        
        job_flag = job_status_temp[1][:-1]
        #print job_flag
        if job_flag == "Current Employee":
            job_status = 2
        else:
            if job_flag == "Former Employee":
                job_status = 1
            else:
                job_status = 0
        #print job_status,
        
        reviewer_location = rev.find('tt', class_ = "i-loc").text
        reviewer_temp = reviewer_location.split(',')
        reviewer_city = reviewer_temp[0].strip()
        #print reviewer_city,
        
        reviewer_state = reviewer_temp[1].strip()
        #print reviewer_state

        for element in rev.select('.description'):
            tenure = element.select('p')[0].text
            #print 'tenure', tenure, '\n'
            pro = element.select('p')[1].text[7:]
            #print 'pro', pro, '\n'
            con = element.select('p')[2].text[7:]
            #print 'con', con, '\n'
            advice = element.select('p')[3].text
            if advice[0:6] == "Advice":
                advice = advice[30:]
                #print 'advice', advice, '\n'
            else:
                advice = ""
                #print "no advice"

        revw_date = rev.find('span', class_ = 'dtreviewed').text
        revw_date = revw_date[:-3].strip()
        #print revw_date
        #print '--- in parse_reviews(206): city', city, 'co', company_id, 'locn', location_id
        
        try:
            c = db.cursor()
            c.execute(u"""
                INSERT INTO review (location_id, company_id, review_rating, review_summary, job_title, 
                    job_status, reviewer_city, reviewer_state, tenure, pro, con, advice, revw_date) 
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """, 
                (location_id, company_id, review_rating, review_summary, job_title, 
                    job_status, reviewer_city, reviewer_state, tenure, pro, con, advice, revw_date))
            db.commit()
            #print "+++ Inserted", review_summary
            c.close()
        except db.Error, e:
            print "--- Error %d: %s" % (e.args[0], e.args[1])
            db.rollback()            
            c.close()
            return -1
        except UnicodeDecodeError:
            print "--- Decoding issue on'", review_summary, "'"
        except UnicodeEncodeError:
            print "--- Encoding issue on'", review_summary, "'"
    return review_summary

def main():
    #print "working directory:", os.getcwd() 
    rootdir = os.getcwd()
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            try:
                if file[-4:] == ".htm":
                    print "\nFile:", file
                    with open(file, 'r') as infile:
                        html = infile.read()
                    # Filter out any strange characters in text
                    h = ''.join([i if ord(i) <= 256 else ' ' for i in html])
                    soup = BeautifulSoup(h)
                    db = open_conn()    # returns cursor to open db server connection
                    co = parse_company(soup, db)
                    if co != -1:
                        city = parse_location(soup, co, db)
                        if city != -1:
                            co_id = get_company_id(co, db)
                            if co_id != -1:
                                parse_reviews(soup, city, co_id, db)
            except:
                print "--- Failed on", file

    db.close()

if __name__ == "__main__":
    main()