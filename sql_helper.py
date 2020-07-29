'''
Given target name, connects to the SQLite database and pulls frequencies necessary for ranking.
The main function, get_rankings, returns a database with disease name and rankings.
Requires ranking module in same dir.
'''

import sqlite3
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine

import ranking

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import ast
from collections import Counter


#Lookup functions: names and ids

def get_disease_name(disease_id, engine):
    with engine.connect() as con:
        rs = con.execute(f"""
        SELECT Disease
        FROM malacard
        WHERE Disease_ID = {disease_id}
        """)
        counts = rs.fetchall()
    name = counts[0][0]
    
    return name

def find_similar(targ_abbr, engine):
    '''
    Gets 5 top matches to the term from target list.
    
    Arguments:
        targ_abbr: target abbreviation, search term
        engine: connection to SQLite database
    
    Returns:
        clean_matches: list of 5 top matches to the target
    '''
    with engine.connect() as con:
        rs = con.execute("""
        SELECT targ_abbr
        FROM targets
        """)
        counts = rs.fetchall()
        targ_abbrs = [i[0] for i in counts]
        matches = process.extract(targ_abbr, targ_abbrs, limit = 5)
        #print(targ_abbrs)
        #matches = [i for i in targ_abbrs if fuzz.ratio(targ_name, i) >40]
        
        clean_matches = [i[0] for i in matches]
        
        return clean_matches   


def get_dis_year(dis_id, engine):
    '''
    Get number of publications per year for a given disease_id.
    
    Arguments:
        dis_id: disease_id
        engine: connection to SQLite database
    
    Returns:
        dataframe with pmid, disease_id, year
    '''
    with engine.connect() as con:
        df = pd.read_sql_query(
                f"""
            SELECT disease_pubmed.pmid, disease_id, pubmed.year
            FROM disease_pubmed
            JOIN pubmed ON pubmed.pmid = disease_pubmed.pmid
            WHERE disease_id = {dis_id}
            """, con)
            #counts = rs.fetchall()
            #info = counts#[0]
            
        return df

def get_dis_id(dis_name, engine):
    '''
    Get disease id based on name.
    Arguments:
        dis_name: disease name from table. This lookup can be avoided if the whole ranking dataframe is saved
        engine: connection to SQLite
    Returns:
        info: disease id from malacard table
    '''
    with engine.connect() as con:
        try:
            rs = con.execute("""
            SELECT Disease_id
            FROM malacard
            WHERE Disease = ?
            """, (dis_name,))
            counts = rs.fetchall()
            info = counts[0][0]
            
            return info
        
        except: 
            return 'NaN'

def get_target_id(target_name, engine):
    '''
    Takes the target name and returns it's id.
    
    Arguments:
        target_name: target name (only abbreviation for now).
        engine: sqlalchemy engine, connected to the database
    Returns:
        name: integer, target id based on DB
    
    '''
    with engine.connect() as con:
        try:
            rs = con.execute("""
            SELECT target_id, targ_abbr, targ_name
            FROM targets
            WHERE (targ_name = ?1 OR targ_abbr = ?2)
            """, (target_name, target_name))
            counts = rs.fetchall()
            info = counts[0]
            
            return info
        
        except: 
            return 'NaN'
        
def get_target_name(target_id, engine):
    '''
    Takes target id and returns name abbreviation
    '''
    with engine.connect() as con: 
        rs = con.execute(f"""
        SELECT targ_abbr
        FROM targets
        WHERE target_id = {target_id}
        """)
        counts = rs.fetchall()
        name = counts[0][0]
    return name
        
#Lookup for clinical trials


def get_pubmed_year(disease_id, engine):
    '''
    Get number of publications per year for a given disease_id.
    
    Arguments:
        dis_id: malacard disease_id
        engine: connection to SQLite database
    
    Returns:
        yr_counts: dictionary with counts of how many publications we found for given disease per year
    '''
    
    with engine.connect() as con:
        rs = con.execute("""
            SELECT *
            FROM pubmed_disease_frequencies
            WHERE disease_id = ?
        """,(disease_id,))
        counts = rs.fetchall()
        yrs = list(range(2009,2021))
        yr_counts = {}
        for i in yrs:
            yr_counts[i] = counts[0][yrs.index(i)+1]
    
    return yr_counts

def get_ct_year(dis_name, engine):
    '''
    Get number of clinical trial per year for a given disease_name.
    TODO change to id
    
    Arguments:
        dis_name: disease_name
        engine: connection to SQLite database
    
    Returns:
        counts: dictionary with counts of how many clinical trials we found for given disease per year
    '''
    with engine.connect() as con:
        with engine.connect() as con:
            rs = con.execute("""
                SELECT CT_trial_years
                FROM ct_diseases
                WHERE Disease = ?
            """,(dis_name,))
            counts = rs.fetchall()
            if counts == []:
                yr_counts = []
                return yr_counts
            else:
                info = counts[0][0]
                years = ast.literal_eval(info)
                yr_counts = dict(Counter(years))
            
                return yr_counts

def get_drug_info(target_id, engine):
    '''
    Takes target id and checks the DB for all the drugs that are in work related to the target.
    Based on the TTD data http://db.idrblab.net/ttd/.
    Arguments:
        target_id: int, target id based on malacard table in DB
        engine: DB connection
    Returns:
        df_sql: dataframe with drug names and their statuses
    '''
    
    with engine.connect() as con:
        df_sql = pd.read_sql_query(f"""
        SELECT Drug_name, Drug_status, INDICATI
        FROM drug_target_indication
        WHERE target_id = {target_id}
        """, con)
        
        return df_sql            

def ct_forecast(dis_id, engine):
    '''
    Gets data with timeseries forecast for number of trials for a given disease.
    The forecast has been done for the full year of 2020 and 2021.
    When there was not enough data for a prediction and there is nothing in the table, 
    will return a [0,0] prediction.
    '''
    with engine.connect() as con:
        rs = con.execute(f"""
            SELECT *
            FROM ct_forecast
            WHERE disease_id = {dis_id}
        """)
        counts = rs.fetchall()
        try:
            predictions = [counts[0][1], counts[0][2]]
        except:
            #When there was not enough data
            predictions = [0,0]
    
    return predictions
            
#Counting functions for ranking table

def tg_count(target_id, engine):
    '''
    Connects to a SQLite DB and counts in how many articles is the given target mentioned.
    This count is defined as n2 in metrics.
    
    Arguments:
        target_id: target id (as defined by ids in the "targets" table).
        engine: sqlalchemy engine, connected to the database
    Returns:
        num_tg: integer, number of articles that mention a given target.
    '''
    with engine.connect() as con:
        rs = con.execute(f"""
        SELECT COUNT(*)
        FROM target_pubmed
        WHERE target_id = {target_id}
        """)
        counts = rs.fetchall()
    num_tg = counts[0][0]
    
    return num_tg


def tg_dis_counts(target_id, engine):
    '''
    Connects to a SQLite DB and counts mentions of each disease together with a given target
    in the abstracts.
    This contributes to counting n0 (disease + target mentions) and n3 (disease mentions) in metrics.
    
    Arguments:
        target_id: target id (as defined by Malacard ids in the DB, defined in "targets" table)
        engine: sqlalchemy engine, connected to the database
    Returns:
        target_disease_counts: dictionary. Contains pairs 'disease_id' vs number of mentions with the given target
    '''
    
    with engine.connect() as con:
        df_sql = pd.read_sql_query(f"""
        SELECT disease_pubmed.pmid, target_id, disease_pubmed.disease_id  FROM target_pubmed
        JOIN disease_pubmed ON target_pubmed.pmid = disease_pubmed.pmid
        WHERE target_id = {target_id}

        """, con)
    con.close()
    #df_sql
    target_disease_counts = df_sql.groupby('disease_id').size().to_dict()
    
    return target_disease_counts


def dis_count(disease_id, engine):
    '''
    Connects to a SQLite DB and counts in how many articles is the given disease mentioned.
    This function copies the tg_count and can be reduced later.
    This count is defined as n3 in metrics.
    
    Arguments:
        disease_id: disease id (as defined by Malacard ids in the DB, defined in "diseases" table).
        engine: sqlalchemy engine, connected to the database
    Returns:
        num_dis: integer, number of articles that mention a given target.
    '''
    with engine.connect() as con:
        rs = con.execute(f"""
        SELECT COUNT(*)
        FROM disease_pubmed
        WHERE disease_id = {disease_id}
        """)
        counts = rs.fetchall()
    num_dis = counts[0][0]
    
    return num_dis


def tg_per_disease(target_disease_count, engine):
    '''
    Takes in the resulting dictionary from tg_dis_counts (disease_id vs no of mentions together with target)
    and expands by adding counts of overall articles mentioning each disease. 
    The target id is not passed, it is a global variable, not used here.
    
    Arguments:
        target_disease_counts: dictionary, containing disease_id and count of mentions together with a target.
        engine: sqlalchemy engine, connected to the database
    Returns:
        diasease_dict: dictionary that has disease id, no of times mentioned with target, no mentioned alltogether.
        
    '''
    
    disease_dict = {}
    
    for key, val in target_disease_count.items():
        separate = dis_count(key, engine)
        local_dict = {'joined': val, 'separate': separate}
        disease_dict[key] = local_dict
        
    return disease_dict


def get_rankings(target_id, engine, fast=True, full=False):
    '''
    Overarching function that combines all the functions in this module.
    Takes target id and returns a dataframe with 4 metrics for each disease associated with target in articles.
    
    Arguments:
        target_id: target id (as defined by Malacard ids in the DB, defined in "targets" table)
        engine: sqlalchemy engine, connected to the database
        full: boolean.
            True: dataframe will be returned containing all columns
            False: default. Dataframe will be returned only containing columns with disease name and rankings
        fast:
            True: takes precomputed values
            Fast: checks DB and computes at the background. Tends to get slow on weak computers.
    
    Returns:
        df_counts: dataframe with rankings for diseases
    '''
    
    if fast:
        
        with engine.connect() as con:

            df_sql = pd.read_sql_query(f"""
            SELECT *
            FROM target_disease
            WHERE target_id = {target_id}
            """, con)
        df_sql['disease'] = df_sql.apply(lambda row: get_disease_name(row['disease_id'], engine), axis=1)
        df_sql = df_sql[['disease', 'f0', 'f1', 'f2', 'pmi']]
        df_sql = df_sql.round(4)
    
        return df_sql.sort_values(by='pmi', ascending = False)
          
    else:
        n1 = 9680305 #Number of all articles in the DB. Computing separately takes more time. 
        n2 = tg_count(target_id, engine)

        target_disease = tg_dis_counts(target_id, engine)
        taget_disease_count = tg_per_disease(target_disease, engine)

        df_counts = pd.DataFrame.from_dict(taget_disease_count, orient='index')
        df_counts = df_counts.reset_index().rename(columns = {'index': 'disease_id'})

        df_counts['disease'] = df_counts.apply(lambda row: get_disease_name(row['disease_id'], engine), axis=1)
        df_counts['f0'] = df_counts.apply(lambda row: ranking.f0(n0=row['joined'], n1=n1, r=True), axis=1)
        df_counts['f1'] = df_counts.apply(lambda row: ranking.f1(n0=row['joined'], n2=n2, r=True), axis=1)
        df_counts['f2'] = df_counts.apply(lambda row: ranking.f2(n0=row['joined'], n3=row['separate'], r=True), axis=1)
        df_counts['pmi'] = df_counts.apply(lambda row: ranking.pmi(n0=row['joined'], n1=n1, n2=n2, n3=row['separate'], r=True), axis=1)

        if full:
            return df_counts.sort_values(by='pmi', ascending = False)
        else:
            return df_counts[['disease', 'f0', 'f1', 'f2', 'pmi']].sort_values(by='pmi', ascending = False)
    
    
    
if __name__ == '__main__':

    engine = create_engine('sqlite:///./data/20200723pubmed.db', echo=False)
    con = engine.connect()


    rankings = get_rankings(15, engine)
    print(rankings)
