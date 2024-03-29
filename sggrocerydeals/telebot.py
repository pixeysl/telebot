import telegram
import credential
import getter_ss as ss
import getter_ntuc as ntuc
import logging
import time

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  

def test(bot):
    bot.send_message(chat_id=credential.CHAT_ID, text='Hello world')

def dispatch_promos(bot, promo_dict):
    '''
    bot -- telegram bot instance
    promo_dict -- dictionary of promos {title: [url]}
    '''

    # in every promo page
    for promo_page in promo_dict.keys():
        # send the tile and the flyer url
        bot.send_message(chat_id=credential.CHAT_ID, text=promo_page)
        # print(promo_dict[promo_page])
        # send all image url in page
        for img_url in promo_dict[promo_page]:
            # print(img_url)
            if img_url.endswith('pdf'):
                bot.send_message(chat_id=credential.CHAT_ID, text=img_url)
            else:
                try:
                    #img_url += "?&random=64" # https://stackoverflow.com/questions/49645510/telegram-bot-send-photo-by-url-returns-bad-request-wrong-file-identifier-http/62672868#62672868
                    bot.send_photo(chat_id=credential.CHAT_ID, photo=img_url)
                except Exception as ex:
                    print(str(ex))
            # delay before sending next
            time.sleep(1)

def main():
    # how to find channel-id https://gist.github.com/mraaroncruz/e76d19f7d61d59419002db54030ebe35

    # get the bot instance
    bot = telegram.Bot(token=credential.TOKEN_KEY)

    # test()

    # query all SS the promos
    promo_dict = ss.getSSPromos()
    dispatch_promos(bot, promo_dict)

    # query all NTUC the promos
    promo_dict = ntuc.getNTUCPromos()
    dispatch_promos(bot, promo_dict)


if __name__ == "__main__":
    main()