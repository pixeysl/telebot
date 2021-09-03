import telegram.bot
import credential
import getter_ss as ss
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  

def test(bot):
    bot.send_message(chat_id=credential.CHAT_ID, text='Hello world')

def dispatch_SS_promos(bot, promo_list):
    '''
    promo_list -- list of promos on the main page
    bot --
    update --
    '''

    for promo_pages in promo_list:
        # in every promo page
        for promo_page in promo_pages.keys():            
            # send the tile and the flyer url
            bot.send_message(chat_id=credential.CHAT_ID, text=promo_page)
            for img_url in promo_pages[promo_page]:
                bot.send_photo(chat_id=credential.CHAT_ID, photo=img_url)

def main():
    # query all the promos
    promo_list = ss.getSSPromos()

    # get the bot instance
    bot = telegram.bot(token=credential.TOKEN_KEY)

    # how to find channel-id https://gist.github.com/mraaroncruz/e76d19f7d61d59419002db54030ebe35
    # test()
    dispatch_SS_promos(bot, promo_list)

if __name__ == "__main__":
    main()