#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import glob
from functools import reduce
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


# Import all csv files in working directory
csv_list=glob.glob(r"csv/*Sydney*.csv")

# Initialise as master dataframe
master_df=pd.DataFrame()

# Load each csv to master dataframe
for csv in csv_list:
    df=pd.read_csv(csv)
    master_df=master_df.append(df)

# Remove AU$, commma and convert to AUD  
master_df['Current Price AUD']= master_df['Current Price AUD'].apply(lambda x: x.strip('AU$')).apply(lambda x: x.replace(',','')).astype('int64')

# Remove brackets and leave only digits
master_df.Stops=master_df.Stops.str.replace(r'\D',r'',regex=True).astype('int64')

# Create a unique identifier for each flight
master_df['Dep-Arrival Time']=master_df['Departure Time']+'-'+master_df['Arrival Time']

# Create a new duration column showing time taken in net hours
master_df[['Duration-Hours','Duration-Minutes']]=master_df.Duration.str.split(expand=True)
master_df['Duration-Hours'].replace(regex=True, inplace=True, to_replace=r'\D', value=r'')
master_df['Duration-Minutes'].replace(regex=True, inplace=True, to_replace=r'\D', value=r'')
master_df['Duration-Hours']=master_df['Duration-Hours'].astype('float64')
master_df['Duration-Minutes']=master_df['Duration-Minutes'].astype('float64')
master_df['Duration-Net Hours']=master_df['Duration-Hours']+master_df['Duration-Minutes'].apply(lambda x: round(x/60,1))

# Create a flight identifier
master_df['Flight ID']=master_df['Airline'] + '-'+ master_df['Dep-Arrival Time']

# Create dictionary for flight paths
flight_dict={'Emirates-4:45 pm-10:30 pm':'Emirates MRU-DBX-SYD',
'Air Mauritius-10:15 pm-5:50 pm':'Air Mauritius MRU-PER-SYD option 1',
'Air Mauritius-10:15 pm-10:40 pm':'Air Mauritius MRU-PER-SYD option 2',
'Air Mauritius-8:40 pm-9:20 pm':'Air Mauritius MRU-SIN-SYD'}


# Flight Path
master_df['Flight Path']=master_df['Flight ID'].map(flight_dict).fillna('Other')


# Create copy of master_df
lean_master_df=master_df.copy()

# Selecting only required columns for analysis
lean_master_df=lean_master_df[['Search Date','Departure Date','Flight Path','Flight ID','Airline','Duration-Net Hours','Stops','Destination','Current Price AUD']]

# Only include prices no greater than AUD 3000

lean_master_df= lean_master_df[lean_master_df['Current Price AUD'] <= 3000]

# Only duration time less than 25 hours

lean_master_df= lean_master_df[lean_master_df['Duration-Net Hours'] < 25]


# Converting Search Date to a datetime object to enable sorting
lean_master_df['Search Date']=pd.to_datetime(lean_master_df['Search Date'],format='%d-%m-%Y').dt.date

# Sort search date in ascending order
lean_master_df.sort_values(by='Search Date',inplace=True)

# Convert back to string
lean_master_df['Search Date']=lean_master_df['Search Date'].astype(str)

def generate_df():
    return lean_master_df


# In[ ]:




