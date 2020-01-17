
import pandas as pd
import glob
import numpy as np


# Import all csv files in working directory
csv_list=[glob.glob(r"csv/*Sydney*.csv")]
csv_list.append(glob.glob(r"csv/*Brisbane*.csv"))

# Initialise empty dataframes for Syd and Bne
sydney_df=pd.DataFrame()
brisbane_df=pd.DataFrame()

# Load each csv to dataframe
def csv_to_df(list,location_df):
    for csv in list:
        search_date_df=pd.read_csv(csv)
        location_df=location_df.append(search_date_df)


    # Concat departure and arrival time
    location_df['Dep-Arrival Time']=location_df['Departure Time']+'-'+location_df['Arrival Time']
    # Create a flight identifier
    location_df['Flight ID']=location_df['Airline'] + '-'+ location_df['Dep-Arrival Time']

    return location_df

# generate sydney and brisbane dataframe
sydney_df=csv_to_df(csv_list[0],sydney_df)
brisbane_df=csv_to_df(csv_list[1],brisbane_df)


# Create dictionary for flight paths
flight_dict_sydney={'Emirates-4:45 pm-10:30 pm':'Emirates MRU-DBX-SYD',
'Air Mauritius-10:15 pm-5:50 pm':'Air Mauritius MRU-PER-SYD option 1',
'Air Mauritius-10:15 pm-10:40 pm':'Air Mauritius MRU-PER-SYD option 2',
'Air Mauritius-8:40 pm-9:20 pm':'Air Mauritius MRU-SIN-SYD'}

flight_dict_brisane={'Emirates-4:45 pm-10:40 pm':'Emirates MRU-DBX-BNE',
'Air Mauritius-10:15 pm-7:25 pm':'Air Mauritius MRU-PER-BNE option 1',
'Air Mauritius-10:15 pm-11:50 pm':'Air Mauritius MRU-PER-BNE option 2'}

# Map Flight Path based on Flight ID
sydney_df['Flight Path']=sydney_df['Flight ID'].map(flight_dict_sydney).fillna('Other-Sydney')
brisbane_df['Flight Path']=brisbane_df['Flight ID'].map(flight_dict_brisane).fillna('Other-Brisbane')


# Initialise as master dataframe
master_df=pd.concat([sydney_df,brisbane_df],ignore_index=True)

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

# Converting Search Date to a datetime object to enable sorting
master_df['Search Date']=pd.to_datetime(master_df['Search Date'],format='%d-%m-%Y').dt.date

# Sort search date in ascending order
master_df.sort_values(by='Search Date',inplace=True)

# Convert back to string
master_df['Search Date']=master_df['Search Date'].astype(str)

# Create copy of master_df
lean_master_df=master_df.copy()

# Selecting only required columns for analysis
lean_master_df=lean_master_df[['Search Date','Departure Date','Flight Path','Flight ID','Airline','Duration-Net Hours','Stops','Destination','Current Price AUD']]

# Only include prices no greater than AUD 3000

lean_master_df= lean_master_df[lean_master_df['Current Price AUD'] <= 3000]

# Only duration time less than 25 hours

lean_master_df= lean_master_df[lean_master_df['Duration-Net Hours'] < 25]


def generate_df():
    return lean_master_df

def generate_master_df_pivot():

	master_df_pivot=pd.pivot_table(master_df,index='Flight Path',columns='Search Date',values='Current Price AUD',aggfunc='count')
	master_df_pivot=master_df_pivot.stack().reset_index()
	master_df_pivot.columns=['Flight Path','Search Date','No of Flights']
	return master_df_pivot
