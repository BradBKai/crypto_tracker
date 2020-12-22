'''
Crypto tracker Version 1

Webscrapes crypto market capitalization site with beautiful soup then sends out notices in IFTTT via webhooks and sms notification apps.
Notifications occur in mobile phone.  Notifications require installation of IFTTT app on the mobile phone.

Future improvements:
Sort values from highest to lowest

By: Brad Kai

'''

import requests
from bs4 import BeautifulSoup
import json
import time

# initialize variables
# soup_tasting() variables
website_request = ''
soup = ''
data = ''
raw_data = ''
coin_data = ''

# message(), ifttt_notice() varibles
prime_list = []
five_less_list = []
five_greater_list = []
crypto_info = []
crypto_stats = {}

# placeholders for previous iteration of lists in ifttt_notice(), requires one iteration before comparison kicks in
previous_prime = []
previous_greater = []
previous_less = []

# boolean used for toggling whether to post a notice
big_change = False

# boolean used to toggle to sleep longer
sleep_longer = False

# beautiful soup webscraping
def soup_tasting():

    # grab website data
    website_request = requests.get("https://coinmarketcap.com/")

    # scrape website
    soup = BeautifulSoup(website_request.text,'lxml')
    raw_data = soup.find("script",id = "__NEXT_DATA__",type = "application/json")
    coin_data = json.loads(raw_data.contents[0])

    # scrape the websites
    crypto_info = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']

    # for loop to pick the data of the crypto coins
    for item in crypto_info:
        crypto_stats[item['slug']] = [item['name'],item['symbol'],item['quote']['USD']['price'],item['quote']['USD']['percent_change_1h'],item['quote']['USD']['percent_change_24h']]

# identify particular coins or large changes in percent then format message
def message():

    global big_change
    # for loop to cycle throught the key/value in crypto_stats dictionary
    for key, value in crypto_stats.items():

        # key is bitcoin
        if key == 'bitcoin':

            # round values primarily due to IFTTT mobile notifications display length restrictions
            price = round(value[2],2)
            percent_1h = round(value[3],2)
            percent_24h = round(value[4],2)
            bit_msg = value[0] + " (" + value[1] +  ") is $" + str(price) + ". 1 hour: " + str(percent_1h) +"%, " + " 24 hour: " + str(percent_24h) +"%."
            prime_list.append(bit_msg)

        # key is ethereum
        elif key == 'ethereum':

            # round values primarily due to IFTTT mobile notifications display length restrictions
            price = round(value[2],2)
            percent_1h = round(value[3],2)
            percent_24h = round(value[4],2)
            eth_msg = value[0] + " (" + value[1] +  ") is $" + str(price) + ". 1 hour: " + str(percent_1h) +"%, " + " 24 hour: " + str(percent_24h) +"%."
            prime_list.append(eth_msg)

        # any coin with an absolute value greater/equal to 1 but not greater/equal to 5 in the past hour
        elif abs(value[3]) >= 1 and not key == 'bitcoin' or not key == 'ethereum':

            # compare absolute values of 1 hour to 24 hour percent changes
            if abs(value[3]) < 5:

                # round values primarily due to IFTTT mobile notifications display length restrictions
                price = round(value[2],4)
                percent_1h = round(value[3],2)
                percent_24h = round(value[4],2)
                five_less_msg = value[1] + " is $" + str(price) + ". 1 hr: " + str(percent_1h) +"%, " + " 24 hr: " + str(percent_24h) +"%."
                five_less_list.append(five_less_msg)

                # set to True since a percent change meeting notice criteria was met for IFTTT_notice()
                big_change = True

            # any coin greater than 5 percent change in the past hour
            elif abs(value[3]) >= 5 and not key == 'bitcoin' or not key == 'ethereum':

                # round values primarily due to IFTTT mobile notifications display length restrictions
                price = round(value[2],4)
                percent_1h = round(value[3],2)
                percent_24h = round(value[4],2)
                five_greater_msg = value[1] + " is $" + str(price) + ". 1 hr: " + str(percent_1h) +"%, " + " 24 hr: " + str(percent_24h) +"%."
                five_greater_list.append(five_greater_msg)

                # set to True since a percent change meeting notice criteria was met for IFTTT_notice()
                big_change = True

            # continue for loop since criteria was not met
            else:
                continue

        # continue for loop since criteria was not met
        else:
            continue

# ifttt webhook      
def ifttt_notice():
    global sleep_longer
    global previous_prime
    global previous_greater
    global previous_less
    print(previous_prime)

    # variable for ifttt webhook
    ifttt_webhook_url = 'https://maker.ifttt.com/trigger/crypto_tracker/with/key/f1wDWGuolNmEfdJtok_ko'

    # uses existing variables and assigns to ifttt variables
    #data = {'value1' : prime_list, 'value2' : five_greater_list, 'value3' : five_less_list}

    # using two values to post bitcoin, eth and large percentage changes
    data = {'value1' : prime_list, 'value2' : five_greater_list}

    # posts data and starts up webhook to notify
    print('post ifttt')
    requests.post(ifttt_webhook_url,data=data)
    
    # logic states to compare len of assigned variables in previous iteration to current values
    print('len comparison')
    print(sleep_longer)

    # if False then assign current to holder variables for next loop
    if len(previous_prime) == len(prime_list) or len(previous_greater) == len(five_greater_list) or len(previous_less) == len(five_less_list):

       # assign placeholder with current lists
        previous_prime = prime_list
        previous_greater = five_greater_list
        previous_less = five_less_list
        print(previous_prime)

        # clear lists so it doesn't infinitely append in while loop
        prime_list.clear()
        five_less_list.clear()
        five_greater_list.clear()
        print('cleared lists')

        # sleep boolean set to True since no difference when previous len iteration was compared to current list
        sleep_longer = True
        return sleep_longer
    else:
        # sleep boolean set to False since there was a difference in list len comparisons
        sleep_longer = False
        return sleep_longer

# main
def __main__():
    global big_change
    global sleep_longer
    print('main')
    print(sleep_longer)

    # while loop to have it keep checking every 60 seconds
    while True:
        # call functions
        soup_tasting()
        message()

        # condition checks for a change in bitcoin or ethereum then kicks off a notice then puts loop to sleep
        if abs(crypto_stats['bitcoin'][3]) >= 1 or abs(crypto_stats['ethereum'][3]) >= 1 or big_change == True:
            ifttt_notice()
            print('notice sent out')

            # set to False since 
            big_change = False
            print('if while sleeps for 300 seconds')

            # set to sleep for 5 minutes
            time.sleep(300)
        else:
            # sleep boolean True indicates no new coins so sleep longer
            if sleep_longer == True:
                print('else')
                print(sleep_longer)
                sleep_longer = False
                print('While loop sleeping for 360 seconds')

                # set to sleep for half hour
                time.sleep(1800)

            # sleep bolean == False so there were new coins with percent changes
            else:
                sleep_longer = False
                print('While loop sleeping for 60 seconds')

                # set to sleep for 1 hour
                time.sleep(3600)

if __name__ == "__main__":
    __main__()
