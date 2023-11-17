import jsonutil
from requests_html import HTMLSession
from datetime import date

# flyer page url
BASE_URL = 'https://www.fairprice.com.sg'
URL =  BASE_URL + '/store-weekly-ads/'
# company id
COM_ID = 'ntuc'
# list of promo title to match and ignore the rest
FILTER_TITLE = ['4 Days Only!', 'Must Buy', 'Weekly Savers', 'Fresh Picks', 'Fresh Buys', 'Neighbourhood']

DBG_FILENAME = 'index.html'
DBG_URL = 'http://localhost:80/'
# DBG_URL = 'https://www.fairprice.com.sg/store-weekly-ads/weekly-saver/'

def toFile(filename, content):
    filename = jsonutil.WORKING_DIR + '\\' + filename
    with open(filename, 'wb') as f:
        f.write(content)

def fromFile(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    return content


def parsePromoPage(response, title, past_url_list):
# <div class="wp-block-image">
#     <figure class="aligncenter size-large">
#         <img alt="" data-src="https://shengsiongcontent.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2021/07/12174027/7M21Booklet-F-02-1024x727.jpg" class="wp-image-6395 lazyloaded" src="https://shengsiongcontent.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2021/07/12174027/7M21Booklet-F-02-1024x727.jpg">
#             <noscript>
#                 <img src="https://shengsiongcontent.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2021/07/12174027/7M21Booklet-F-02-1024x727.jpg" alt="" class="wp-image-6395"/>
#             </noscript>
#         </figure>
#     </div>
    promo_page_dict = {}

    try:

        # expect only 1 main frame
        main = response.html.find('.tp-summary-info', first=True)
        if main:    
            # locate image container
            images = main.xpath('//img')
            # filter past urls
            filtered = [image.attrs['src'] for image in images if image.attrs['src'] not in past_url_list]
            if filtered != []:
                # add to dictionary with format {title:[img_urls]}
                promo_page_dict[title] = filtered

    except Exception as ex:
        print('Exception in parsing promo page')
        print(str(ex))
    
    return promo_page_dict


def parseMainPage(response):
    promo_page_dict = {}

    try:

        containers = response.html.xpath('//div[@class="vc_row wpb_row vc_row-fluid vc_row-o-equal-height vc_row-flex"]')
        for container in containers[:3]:
            # locate promo container
            promos = container.xpath('//div[@class="wpb_column vc_column_container vc_col-sm-3 vc_col-lg-3 vc_col-md-6 vc_col-xs-6"]')
            # get all the promo pages
            for promo in promos:
                # only interested in last link
                links = promo.find('a')
                if links:
                    link = links[-1]
                else:
                    continue
                rel_link = link.attrs['href'].replace(BASE_URL, '')
                # print(link.attrs['href'])

                # title = promo.find('strong', first=True)
                title = promo.find('p', first=True)
                # print(title.text)

                # filter uninterested page
                filtered = next((BASE_URL + rel_link for keyword in FILTER_TITLE if keyword in title.text), None)
                if filtered != None:
                    promo_page_dict[title.text] = filtered

    except Exception as ex:
        print('Exception in parsing main page')
        raise ex

    return promo_page_dict


def getNTUCPromos():

    session = None
    json_data = None

    try:
        promo_dict = {}
        past_url_list = []
        
        # retrieve last broadcasted data
        past_url_list = jsonutil.readLastUrl(COM_ID)

        session = HTMLSession()
        response = session.get(URL)

        # toFile(DBG_FILENAME, response.content)
        # return

        promo_pages = parseMainPage(response)
        for key in promo_pages.keys():
            response = session.get(promo_pages[key])
            url_dict = parsePromoPage(response, key, past_url_list)
            if url_dict != {}:
                promo_dict.update(url_dict)

        # promo = parsePromoPage(response)
        # promo_list.append(promo)

        # don't care about page title, flatten the urls
        flat_list = [url for urls in list(promo_dict.values()) for url in urls]
        # save data to prevent re-broadcast if promo has not been updated
        if flat_list != []:
            jsonutil.saveTodayUrl(date.today(), COM_ID, flat_list)

    except Exception as ex:
        print(str(ex))
    finally:
        if session:
            session.close()

    return promo_dict


if __name__ == "__main__":
    getNTUCPromos()