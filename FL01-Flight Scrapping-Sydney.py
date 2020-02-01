
# Link to tutorial
# https://dzone.com/articles/make-python-surf-the-web-for-you-and-send-best-fli

# Importing Selenium (for accessing websites and automation testing):
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ChromeOptions

# importing time and randint to create delays between operations
import time
from random import randint
# importing datetime to access current date and time information
import datetime

# importing pandas to store scrapped data into dataframe format
import pandas as pd


# Connect with webbrowser and setting up preferences

# service_args = ['--vrbose','--log-path=/path/to/hromedriver.log']
executable_path="C:/Users/user/chromedriver.exe"

# create user preference object
prefs = {'profile':{}}

# setup user preference to block popups
# 1=Allow popups, 2=Block popups
prefs['profile']['default_content_setting_values']={"popups":2}

# Set exceptions for popups
#prefs['profile']['content_settings']={'exceptions':{"popups":{"a.com":{"setting":2},
                                                             # "b.com,*":{"setting":1}
                                                             # }}}

# Create ChromeOptions oject
chromeOptions = ChromeOptions()
# Adding user preference to ChromeOptions oject
chromeOptions.add_experimental_option("prefs",prefs)
# Chrome to ignore certificate errors
chromeOptions.add_argument('--ignore-certificate-errors')
chromeOptions.add_argument('--ignore-ssl-errors')

browser = webdriver.Chrome(executable_path=executable_path, options=chromeOptions)#,service_args=service_args)

# Setting ticket types xpaths
one_way_ticket = "//label[@id='flight-type-one-way-label-hp-flight']"


# Define function to choose ticket type: Mutli,one-way or roundtrip
def ticket_chooser(ticket):
    try:
        ticket_type = browser.find_element_by_xpath(ticket)
        ticket_type.click()
    except Exception as e:
        pass

# Define function to choose departure country:
def dep_country_chooser(dep_country):
    fly_from = browser.find_element_by_xpath("//input[@id='flight-origin-hp-flight']")
    time.sleep(randint(1,5))
    fly_from.clear()
    time.sleep(randint(1,5))
    fly_from.send_keys('  ' + dep_country)
    time.sleep(randint(1,5))
    first_item = browser.find_element_by_xpath("//a[@id='aria-option-0']")
    time.sleep(randint(1,5))
    first_item.click()

# Define function to choose departure country:
def arrival_country_chooser(arrival_country):
    fly_to = browser.find_element_by_xpath("//input[@id='flight-destination-hp-flight']")
    time.sleep(randint(1,5))
    fly_to.clear()
    time.sleep(randint(1,5))
    fly_to.send_keys('  ' + arrival_country)
    time.sleep(randint(1,5))
    first_item = browser.find_element_by_xpath("//a[@id='aria-option-0']")
    time.sleep(randint(1,5))
    first_item.click()

# Define function to select departure date:
def dep_date_chooser(day, month, year):
    dep_date_button = browser.find_element_by_xpath("//input[@id='flight-departing-single-hp-flight']")
    dep_date_button.clear()
    dep_date_button.send_keys(day + '/' + month + '/' + year)
    datepicker_button=browser.find_element_by_xpath("//button[@class='datepicker-close-btn close btn-text']")
    datepicker_button.click()

# Define defintion to access search results
def search():
    search = browser.find_element_by_xpath("//button[@class='btn-primary btn-action gcw-submit']")
    search.click()
    time.sleep(randint(30,50))
    print('Results ready!')


# Define function to extract flights data from each search page
def compile_data():
    global df
    global dep_times_list
    global arr_times_list
    global airlines_list
    global price_list
    global durations_list
    global stops_list
    global layovers_list
    global current_date

    #Initialise dataframe df
    df = pd.DataFrame()
    #departure times
    dep_times = browser.find_elements_by_xpath("//span[@data-test-id='departure-time']")
    dep_times_list = [value.text for value in dep_times if value.text]
    #arrival times
    arr_times = browser.find_elements_by_xpath("//span[@data-test-id='arrival-time']")
    arr_times_list = [value.text for value in arr_times if value.text]
    #airline name
    airlines = browser.find_elements_by_xpath("//span[@data-test-id='airline-name']")
    airlines_list = [value.text for value in airlines if value.text]
    #prices
    prices = browser.find_elements_by_xpath("//span[@data-test-id='listing-price-dollars']")
    price_list = [value.text for value in prices if value.text]
    #durations
    durations = browser.find_elements_by_xpath("//span[@data-test-id='duration']")
    durations_list = [value.text for value in durations if value.text]
    #stops
    stops = browser.find_elements_by_xpath("//span[@class='number-stops']")
    stops_list = [value.text for value in stops if value.text]
    #layovers
    layovers = browser.find_elements_by_xpath("//span[@data-test-id='layover-airport-stops']")
    layovers_list = [value.text for value in layovers if value.text]
    now = datetime.datetime.now()
    current_date = str(now.day) + '-' + str(now.month) + '-' + str(now.year)
    #current_time = (str(now.hour) + ':' + str(now.minute))

    for i in range(len(dep_times_list)):
        try:
            df.loc[i, 'Search Date'] = current_date
        except Exception as e:
            pass
        try:
            df.loc[i, 'Departure Time'] = dep_times_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'Arrival Time'] = arr_times_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'Airline'] = airlines_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'Duration'] = durations_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'Stops'] = stops_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'Layovers'] = layovers_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'Current Price AUD'] = price_list[i]
        except Exception as e:
            pass





# Define function to change departure date on search date
def new_search(mm,dd,yyyy):
    dep_date_button = browser.find_element_by_xpath("//input[@id='departure-date-1']")
    for i in range(11):
        dep_date_button.send_keys(Keys.BACKSPACE)
    dep_date_button.send_keys(mm + '/' + dd + '/' + yyyy)
    search_button = browser.find_element_by_xpath("//button[@class='btn-secondary btn-sub-action']")
    search_button.click()
    time.sleep(randint(30,50))


# Generate list of departure dates to search flights for
date1 = '2020-02-15'
date2 = '2020-03-17'
mydates = pd.date_range(date1, date2).tolist()
mydates=[date.strftime('%d-%m-%Y') for date in mydates]



# Scrape flights results, store in dataframe, append to master dataframe and export to csv
def flight_scrapper(mydates,destination):

    global master_df
    master_df=pd.DataFrame()

    # Launch website on Chrome
    link = 'https://www.expedia.com.au/'
    browser.get(link)
    browser.implicitly_wait(30)


    #choose flights only tab
    flights_only = browser.find_element_by_xpath("//button[@id='tab-flight-tab-hp']")
    flights_only.click()

    # Create query
    ticket_chooser(one_way_ticket)
    dep_country_chooser('Mahebourg, Mauritius')
    arrival_country_chooser(destination)
    dd,mm,yyyy=mydates[0].split('-')
    dep_date_chooser(dd,mm,yyyy)

    # Generate results per query
    search()

    # Scrape flights data for the 1st departure date and store in dataframe
    compile_data()


    # Add Departure Date column
    df.insert(loc=1,column='Departure Date',value=mydates[0])

    # Add Destination
    df['Destination']=destination

    # append dataframe to master dataframe
    master_df=master_df.append(df)

    # Loop over date list, scrape results and store in dataframe for each departure date in the dates list

    for i in range(1,len(mydates)):
        # splitting date into day, month and year and assign to relevant variable
        dd,mm,yyyy=mydates[i].split('-')
        # new_search functions taking the variables above as arguments
        new_search(dd,mm,yyyy)
        try:
            compile_data()
            df.insert(loc=1,column='Departure Date',value=mydates[i])
        except:
            new_search(dd,mm,yyyy)
            compile_data()
            df.insert(loc=1,column='Departure Date',value=mydates[i])
        # Add Destination
        df['Destination']=destination
        #browser.save_screenshot('screenshots/'+mydates[i]+'.png')
        master_df=master_df.append(df,sort=False)

    # Write df to csv
    return master_df.to_csv('csv/'+ current_date+' '+destination+' flights.csv',index=False)



# Scrape flight results for Sydney
flight_scrapper(mydates,'Sydney, Australia')
