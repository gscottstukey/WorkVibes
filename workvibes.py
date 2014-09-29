# lgeorge Zipfian Capstone Project

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
from replacers import RegexpReplacer 

def read_db(company_id=1, positive = True):
    '''Retrieve review text from glassdoor database.
       (Edit user and password as needed.)

    Input:
    - Int: Company number
    - Boolean: whether to retrieve positive or negative content
    
    Output:
    - Pandas dataframe containing reviews for the specified company. 
      Each review is one row. 
    '''
    conn=pymysql.connect(host="localhost", port=3306, db="glassdoor", 
        user='root', passwd='xxxx')
    if positive == True:
        sql = "SELECT pro FROM review WHERE company_id = '%s'" % (company_id)
    else:
        sql = "SELECT con FROM review WHERE company_id = '%s'" % (company_id)
    df_result  = psql.read_frame(sql, conn)
    conn.close()
    df_result.columns = ['text']
    return df_result

def create_bag(df):
    '''Create a "bag of words" from the review text.

    Input:
    - Pandas dataframe containing review text. 
    Output:
    - List of sentences.
    '''
    replacer = RegexpReplacer()
    sentences = []
    for review in df['text']:
        tmp = replacer.replace(review)
        tmp1 = tmp.strip()
        sentences.append(sent_tokenize(tmp1))
    sentences = [ inner for sublist in sentences for inner in sublist ]
    return sentences

def tokenize_and_normalize(chunks): 
    ''' Transform each sentence into a set of tokens, using their base
        form (lemmatization) and removing short common words (a, the, etc.).
    '''
    wnl = nltk.WordNetLemmatizer()
    words = [ tokenize.word_tokenize(sent) for sent in tokenize.sent_tokenize("".join(chunks)) ]
    flatten = [ inner for sublist in words for inner in sublist ]
    stripped = [] 

    for word in flatten: 
        if word not in stopwords.words('english'):
            try:
                stripped.append(word.encode('latin-1').decode('utf8').lower())
            except:
                print "Warning: unrecognizable word: couldn't encode."

    no_punks = [ word for word in stripped if len(word) > 1 ] 
    return [wnl.lemmatize(t) for t in no_punks]

def process_sentences(sentences):
    '''Associate part of speech (noun, verb, etc.) with each word in
       each sentence. 
    '''
    processed_sentences = []
    tag_set = ['JJ','JJR','JJS','RB','RBR','RBS','VB','VBD','VBG','VBN','VBP','VBZ']

    for sentence in sentences:
        token_list = tokenize_and_normalize(sentence)
        processed_sentences.append(token_list)

    tagged_sentences = [[nltk.pos_tag([word])[0][0] for word in sentence if nltk.pos_tag([word])[0][1] in tag_set] for sentence in processed_sentences]
    sent_strings = [' '.join(sentence) for sentence in tagged_sentences]    
    return sent_strings

def get_top_sents(sent_strings, sentences, num=10):
    '''
    Vectorize trimmed sentence elements (documents) x features (words).

    Input: 
    - sent_strings: processed/trimmed sentences
    - sentences: original (whole) sentences
    - num: number of phrases requested by the user

    Output:
    - result_list: list of curated phrases
    '''
    result_list = []

    # Vectorize trimmed sentence elements (documents) x words (features)
    # The result is a sparse matrix with rows = documents, columns = features
    vec = TfidfVectorizer(min_df = 1)    
    pos_vec = vec.fit_transform(sent_strings) 
    names = vec.get_feature_names()

    # Sum the weights of words in each sentence
    matrix_totals = pos_vec.sum(axis=1)
    sentence_totals = np.squeeze(np.asarray(matrix_totals)).argsort()
    sorted_sentence_totals = np.argsort(sentence_totals)
    for idx in sorted_sentence_totals[0:num]:
        result_list.append(sentences[idx])
    return result_list

def main():
    '''
    Input: company ID, number of sentences to return
    Output: Two lists: positive and negative sentences deemed relevant within the body of reviews for the specified company_id

    Future work: 
    - refine trim/filter sequence to optimize POS classification
    - experiment with other stemming/lemmatization techniques
    '''

    print "\n~ ~ ~ Welcome to the WorkVibes prototype! ~ ~ ~\n"
    print "Which company would you like to read about?"
    print "1 Accenture, 2 Google, 3 Hewlett-Packard, 4 Intuit, 5 Optimizely, 6 Salesforce.com,"
    print "7 SAP, 8 Splunk, 9 Twitter, 10 VMware, 11 Wikimedia Foundation, 12 Yelp"
    company_id = raw_input("Enter the company ID: ")
    try:
        company_id = int(company_id)
    except ValueError:
        print "Company ID should be a number.\n"
        return()

    if company_id > 12 or company_id < 1:
        print "Error: Company number should be between 1 and 12. "
    else:

        num_sents = raw_input("How many phrases would you like to read? (1-40)\n")
        num_sents = int(num_sents)
        if num_sents < 1 or num_sents > 40:
            print "Number of sentences should be between 1 and 40."
            return()
        else:    
            # Retrieve distinctive positive phrases
            df_pro = read_db(company_id, True)
            sents_pro = create_bag(df_pro)
            sent_strings_pro = process_sentences(sents_pro)
            sentences_pro = get_top_sents(sent_strings_pro, sents_pro, num_sents)
            print "\nPros - summary:\n"
            for sentence in sentences_pro:
                print '++ ', sentence

            # Retrieve distinctive negative phrases
            df_con = read_db(company_id, False) 
            sents_con = create_bag(df_con)
            sent_strings_con = process_sentences(sents_con)
            sentences_con = get_top_sents(sent_strings_con, sents_con, num_sents)
            print "\nCons - summary:\n"
            for sentence in sentences_con:
                print '-- ', sentence

if __name__ == "__main__":
    main()