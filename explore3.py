# lgeorge zipfian project

from datetime import datetime
import sys
import pymysql 
import numpy as np
import pandas as pd
import pandas.io.sql as psql
import nltk
import re
from nltk.corpus import stopwords
from nltk import tokenize
from nltk.tokenize import wordpunct_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from replacers import RegexpReplacer   # contains custom text replacement strings

def read_db_pro(company_id=9):
    # not optimal having two separate functions for this, but ok for now

    conn=pymysql.connect(host="localhost", port=3306, db="glassdoor", user='root', passwd='passwd12')
    sql = "SELECT pro FROM review WHERE company_id = '%s'" % (company_id)   # can add 'LIMIT 5' for a test set
    df_pro  = psql.read_frame(sql, conn)
    conn.close()
    df_pro['label'] = 1
    df_pro.columns = ['text', 'label']
    #print "number of reviews:", len(df_pro)
    #print df_pro[0:9]
    return df_pro

def read_db_con(company_id=9):
    conn=pymysql.connect(host="localhost", port=3306, db="glassdoor", user='root', passwd='passwd12')
    sql = "SELECT con FROM review WHERE company_id = '%s'" % (company_id)
    df_con  = psql.read_frame(sql, conn)
    conn.close()
    df_con['label'] = 0
    df_con.columns = ['text', 'label']
    #print df_con[0:9]
    return df_con

def create_bag(df):
    replacer = RegexpReplacer()
    sentences = []
    for review in df['text']:
        tmp = replacer.replace(review)
        tmp1 = tmp.strip()
        sentences.append(sent_tokenize(tmp1))
    # extract nested list
    sentences = [ inner for sublist in sentences for inner in sublist ]
    #print "number of sentences across reviews:", len(sentences), '\n'
    return sentences

def tokenize_and_normalize(chunks):  # which in this case are sentences...
    wnl = nltk.WordNetLemmatizer()
    words = [ tokenize.word_tokenize(sent) for sent in tokenize.sent_tokenize("".join(chunks)) ]
    flatten = [ inner for sublist in words for inner in sublist ]
    stripped = [] 

    for word in flatten: 
        if word not in stopwords.words('english'):
            try:
                stripped.append(word.encode('latin-1').decode('utf8').lower())
            except:
                print "Cannot encode: " + word

    no_punks = [ word for word in stripped if len(word) > 1 ]  # this misses "", etc.
    return [wnl.lemmatize(t) for t in no_punks]

def process_sentences(sentences):
    processed_sentences = []
    tag_set = ['JJ','JJR','JJS','RB','RBR','RBS','VB','VBD','VBG','VBN','VBP','VBZ']

    for sentence in sentences:
        token_list = tokenize_and_normalize(sentence)
        processed_sentences.append(token_list)
    print "# of sentences:", len(processed_sentences)

    tagged_sentences = [[nltk.pos_tag([word])[0][0] for word in sentence if nltk.pos_tag([word])[0][1] in tag_set] for sentence in processed_sentences]
    #print "# of sentences:", len(tagged_sentences)
    #print "first 3:", tagged_sentences[0:3]

    sent_strings = [' '.join(sentence) for sentence in tagged_sentences]    
    #print "number of sentence strings:", len(sent_strings)
    #print "first 5:", sent_strings[0:5]
    return sent_strings

def get_top_sents(sent_strings, sentences, num=10):
    result_list = []

    # vectorize trimmed sentence elements (documents) x words (features)
    # the result is a sparse matrix with rows = documents, columns = features
    vec = TfidfVectorizer(min_df = 1)    
    pos_vec = vec.fit_transform(sent_strings) 
    names = vec.get_feature_names()
    #print "number of features:", len(names)

    # sum the weights of words in each sentence
    matrix_totals = pos_vec.sum(axis=1)
    sentence_totals = np.squeeze(np.asarray(matrix_totals)).argsort()
    sorted_sentence_totals = np.argsort(sentence_totals)
    #print sorted_sentence_totals
    for idx in sorted_sentence_totals[0:num]:
        result_list.append(sentences[idx])
    return result_list

def main():
    # read_db... takes company_id as argument: 
    print "Which company would you like to read about?"
    print "1 Accenture, 2 Google, 3 Hewlett-Packard, 4 Intuit, 5 Optimizely, 6 Salesforce.com,"
    print "7 SAP, 8 Splunk, 9 Twitter, 10 VMware, 11 Wikimedia Foundation, 12 Yelp"
    company_id = raw_input("Enter the company ID: ")
    try:
        company_id = int(company_id)
    except ValueError:
        print "not a number"
        company_id = 9

    if company_id > 12 or company_id < 1:
        print "invalid number"
    else:

        num_sents = raw_input("How many phrases would you like in your summary? (1-40) \n")
        try:
            num_sents = int(num_sents)
        except ValueError:
            print "not a number"
            company_id = 9

        if num_sents > 40:
            print "number too big"
        else:    
            # retrieve 'pro' phrases
            df_pro = read_db_pro(company_id)
            sents_pro = create_bag(df_pro)
            sent_strings_pro = process_sentences(sents_pro)
            sentences_pro = get_top_sents(sent_strings_pro, sents_pro, num_sents)
            print "\npros - summary:\n"
            for sentence in sentences_pro:
                print '++ ', sentence
            # retrieve "con" phrases
            df_con = read_db_con(company_id) 
            sents_con = create_bag(df_con)
            sent_strings_con = process_sentences(sents_con)
            sentences_con = get_top_sents(sent_strings_con, sents_con, num_sents)
            print "\ncons - summary:\n"
            for sentence in sentences_con:
                print '-- ', sentence

if __name__ == "__main__":
    main()