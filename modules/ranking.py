'''Contains functions to rank target vs disease relationships.'''

import math

def f0(n0, n1, r=False):
    '''
    Returns a metric for ranking disease-target associations, 
    based on ratio of joint occurrences to number of all abstracts. 
    Normalise by multiplying by 10^6. Interpret as metric per million.
    
    Arguments:
        n0: count of joint occurrences target + disease
        n1: number of all texts considered
        r: boolean. 
            True: round to 5 digits. 
            False: return as is.
        
    Returns:
        f0: ratio value
        'NaN' if error occured
    '''
    try:
        ratio = (int(n0)/int(n1))*(10**6) #in case counts are input as strings
        if r:
            f0 = round(ratio, 5)
        else:
            f0 = ratio
        return f0
    
    except:
        return 'NaN'



def f1(n0, n2, r=False):
    '''
    Returns a metric for ranking disease-target associations, 
    based on ratio of joint occurrences together to number of abstracts mentioning target.
    Shows importance of disease to a given target.
    
    Arguments:
        n0: count of joint occurrences target + disease
        n2: number of all texts that mention target
        r: boolean. True: round to 5 digits. False: return as is
        
    Returns:
        f1: ratio value
        'NaN' if error occured
    '''
    try:
        ratio = int(n0)/int(n2)
        if r:
            f1 = round(ratio, 5)
        else: 
            f1=ratio
            
        return f1
    
    except:
        return 'NaN'



def f2(n0, n3, r=False):
    '''
    Returns a metric for ranking disease-target associations, 
    based on ratio of joint occurrences together to number of abstracts mentioning disease.
    Shows importance of target to a given disease.
    
    Arguments:
        n0: count of joint occurrences target + disease
        n3: number of all texts that mention disease
        r: boolean. True: round to 5 digits. False: return as is
        
    Returns:
        f2: ratio value
        'NaN' if error occured
    '''
    try:
        ratio = int(n0)/int(n3)
        if r:
            f2 = round(ratio, 5)
        else:
            f2=ratio
            
        return f2
    
    except:
        return 'NaN'



def pmi(n0, n1, n2, n3, r=False):
    '''
    Returns a metric for ranking disease-target associations, 
    based on pointwise mutual information (PMI) as shown in Manning, Schuetze "Foundations of statistical NLP".
    PMI shows how bigger than random are the chances that the two items co-occur, 
    but tends to show high rank for rare items. 
    This metric is an adjusted version of the original and takes frequencies, not probabilities.
    
    Arguments:
        n0: count of joint occurrences target + disease
        n1: number of all texts
        n2: number of all texts that mention target
        n3: number of all texts that mention disease
        r: boolean. True: round to 5 digits. False: return as is.
        
    Returns:
        round_pmi: ratio value
        'NaN' if error occured.
    '''
    try:
        P_xy = int(n0)/int(n1) #These can be reviewed.
        P_x = int(n2)/int(n1)
        P_y = int(n3)/int(n1)
        
        ratio = math.log2(P_xy/(P_x*P_y))
        
        if r:
            pmi = round(ratio, 5)
        else:
            pmi = ratio
        
        return pmi
    
    except:
        return 'NaN'
        