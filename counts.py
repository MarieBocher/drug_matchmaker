import pandas as pd

def get_percent(num1, num2):
    percent = (num1/num2)*100
    return percent


def get_count_dataframe(source_count_dict):
    '''
    Does necessary counts for clinical trials graph on dash.
    Counts % of disease trials to all trials at that year.
    '''
    
    all_years = {2017: 74290, 2015: 74481, 2010: 60554, 2014: 69950, 2019: 77051, 2009: 62768,
            2012: 64626, 2016: 79349, 2018: 75459, 2005: 52721, 2006: 41029, 2013: 65434,
            2002: 6553, 2003: 7123, 2007: 50337, 2008: 61088, 2011: 62613, 2020: 35745, 
            1999: 10972, 2000: 6472, 2004: 7167, 2001: 5013}
    
    dis_counts = pd.DataFrame(columns = ['year', 'count', 'total_count', 'percentage'])
    dis_counts['year'] = [i for i in range(1999,2021)]
    dis_counts['total_count'] = [all_years[i] for i in range(1999, 2021)]
    
    temp = {key: 0 for key in range(1999, 2021)}
    for i in source_count_dict:
        temp[int(i)] = source_count_dict[i]
    dis_counts['count'] = [temp[i] for i in range(1999,2021)]
    dis_counts = dis_counts.fillna(0)
    dis_counts['percentage'] = dis_counts.apply(lambda row: get_percent(row['count'], row['total_count']), axis=1)
    
    
    return dis_counts



def get_count_abstracts(source_dict):
    
    all_years = {2013: 848250, 2009: 659800, 2016: 952159, 2010: 694295, 2012: 805028, 2019: 1154895,
                 2011: 741366, 2014: 891503, 2015: 925105, 2017: 967534, 2018: 1023659, 2020: 16711}
    
    
    dis_counts = pd.DataFrame(columns = ['year', 'count', 'total_count', 'percentage'])
    dis_counts['year'] = [i for i in range(2009,2021)]
    dis_counts['total_count'] = [all_years[i] for i in range(2009, 2021)]
    dis_counts['count'] = [source_dict[i] for i in range(2009, 2021)]
    dis_counts['percentage'] = dis_counts.apply(lambda row: get_percent(row['count'], row['total_count']), axis=1)
    
    return dis_counts
    
    
    
    
    
    
    