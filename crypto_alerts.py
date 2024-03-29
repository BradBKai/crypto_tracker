'''
Crypto tracker Version 1.4.5

Webscrapes crypto market capitalization site with beautiful soup then sends out notices in IFTTT via webhooks and sms notification apps.
Notifications occur in mobile phone.  Notifications require installation of IFTTT app on the mobile phone.

Update for 1.4.5  Added Algorand. Removed Value 3.

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
url = 'https://coinmarketcap.com/'

# message(), ifttt_notice() varibles
prime_list = []
five_less_list = []
five_greater_list = []
crypto_info = []
crypto_stats = {}

# beautiful soup webscraping
def soup_tasting():

    # grab website data
    for page in range(1, 3):
        website_request = requests.get(url + '?page=' + str(page))

        # scrape website
        soup = BeautifulSoup(website_request.text,'lxml')
        raw_data = soup.find("script",id = "__NEXT_DATA__",type = "application/json")
        coin_data = json.loads(raw_data.contents[0])
        crypto_info = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
        #print(crypto_info)

        # for loop to pick the data of the crypto coins
        for item in crypto_info:
            crypto_stats[item['slug']] = {'name':item['name'],'symbol':item['symbol'],'price':item['quote']['USD']['price'],'1_hour_percent':item['quote']['USD']['percentChange1h'],'24_hour_percent':item['quote']['USD']['percentChange24h']}

def process_message(key):
    # round values primarily due to IFTTT mobile notifications display length restrictions
    #crypto_name = key
    crypto_symbol = crypto_stats[key]['symbol']
    price = round(crypto_stats[key]['price'],3)
    percent_1h = round(crypto_stats[key]['1_hour_percent'],3)
    percent_24h = round(crypto_stats[key]['24_hour_percent'],3)
    return str(crypto_symbol) + " is $" + str(price) + ", 1 hour: " + str(percent_1h) +"%," + " 24 hour: " + str(percent_24h) +"%."

# identify particular coins or large changes in percent then format message
def create_message(dict):

    # for loop to cycle throught the key/value in crypto_stats dictionary
    for key, value in dict.items():

        # key is bitcoin
        if key == 'bitcoin':

            # round values primarily due to IFTTT mobile notifications display length restrictions
            btc_msg = process_message(key)
            prime_list.append(btc_msg)

        # key is ethereum
        elif key == 'ethereum':

            # round values primarily due to IFTTT mobile notifications display length restrictions
            eth_msg = process_message(key)
            prime_list.append(eth_msg)

        # key is cardano
        elif key == 'cardano':

            # round values primarily due to IFTTT mobile notifications display length restrictions
            ada_msg = process_message(key)
            prime_list.append(ada_msg)
        
        # key is polkadot-new
        elif key == 'polkadot-new':

            # round values primarily due to IFTTT mobile notifications display length restrictions
            dot_msg = process_message(key)
            prime_list.append(dot_msg)

        # key is loopring
        elif key == 'loopring':

            # round values primarily due to IFTTT mobile notifications display length restrictions
            lrc_msg = process_message(key)
            prime_list.append(lrc_msg)

        # key is stacks
        elif key == 'stacks':

            # round values primarily due to IFTTT mobile notifications display length restrictions
            stx_msg = process_message(key)
            prime_list.append(stx_msg)

        # key is vechain
        elif key == 'vechain':

            # round values primarily due to IFTTT mobile notifications display length restrictions
            vet_msg = process_message(key)
            prime_list.append(vet_msg)

        # key is algorand
        elif key == 'algorand':

            # round values primarily due to IFTTT mobile notifications display length restricdtions
            algo_msg = process_message(key)
            prime_list.append(algo_msg)

        # any coin with an absolute value greater/equal to 1 but not greater/equal to 5 in the past hour
        elif abs(crypto_stats[key]['1_hour_percent']) >= 1 and not key == 'bitcoin' or not key == 'ethereum' and not key == 'cardano' and not key == 'polkadot-new' and not key == 'loopring' and not key == 'stacks' and not key == 'vechain' and not key == 'algorand':

            # compare absolute values of 1 hour to 24 hour percent changes
            if abs(crypto_stats[key]['1_hour_percent']) <= 5:

                # round values primarily due to IFTTT mobile notifications display length restrictions
                five_less_msg = process_message(key)
                five_less_list.append(five_less_msg)

            # any coin greater than 5 percent change in the past hour
            elif abs(crypto_stats[key]['1_hour_percent']) > 5 and not key == 'bitcoin' or not key == 'ethereum' and not key == 'cardano' and not key == 'polkadot-new' and not key == 'loopring' and not key == 'stacks' and not key == 'vechain' and not key == 'algorand':

                # round values primarily due to IFTTT mobile notifications display length restrictions
                five_greater_msg = process_message(key)
                five_greater_list.append(five_greater_msg)

            # continue for loop since criteria was not met
            else:
                continue

        # continue for loop since criteria was not met
        else:
            continue

# ifttt webhook      
def ifttt_notice():

    # variable for ifttt webhook
    ifttt_webhook_url = 'https://maker.ifttt.com/trigger/crypto_tracker/with/key/f1wDWGuolNmEfdJtok_ko'

    # lists assigned to data values
    data = {'value1' : prime_list, 'value2' : five_greater_list}

    # posts data and starts up webhook to notify
    print('post ifttt')
    requests.post(ifttt_webhook_url,data=data)

    # clear lists so it doesn't infinitely append in while loop
    prime_list.clear()
    five_less_list.clear()
    five_greater_list.clear()

# main
def __main__():

    # while loop to have it keep checking
    while True:

        # call functions
        soup_tasting()
        create_message(crypto_stats)

        # condition checks for a change in bitcoin, cardano or ethereum then kicks off a notice then puts loop to sleep
        if abs(crypto_stats['bitcoin']['1_hour_percent']) >= 1 or abs(crypto_stats['ethereum']['1_hour_percent']) >= 1 or abs(crypto_stats['cardano']['1_hour_percent']) >= 1 or abs(crypto_stats['polkadot-new']['1_hour_percent']) or abs(crypto_stats['loopring']['1_hour_percent']) >= 1 or abs(crypto_stats['stacks']['1_hour_percent']) >= 1 or abs(crypto_stats['algorand']['1_hour_percent']) >= 1:
            
            # post notice in IFTTT
            ifttt_notice()
            print('btc/eth/ada/dot/lrc/stx/algo notice sent out')

            # sleep while loop for 60 seconds
            print('sleep 5 mins/300 seconds')
            time.sleep(300)

        else:
            
            #post notice in IFTTT 
            ifttt_notice()

            # sleep while loop for 1 hour
            print('if while sleeps for 1 hour/3600 seconds')
            time.sleep(3600)

if __name__ == "__main__":
    __main__()
