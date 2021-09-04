import jsonutil
from requests_html import HTMLSession
from datetime import date

# flyer page url
URL =  'https://corporate.shengsiong.com.sg/category/promotions/'
# company id
COM_ID = 'ss'
# list of promo title to match and ignore the rest
FILTER_TITLE = ['special', 'fair']

DBG_FILENAME = 'index.html'
DBG_FILENAME2 = 'index1.html'
DBG_URL = 'http://localhost:80/'

def toFile(filename, content):
    filename = jsonutil.WORKING_DIR + filename
    with open(filename, 'wb') as f:
        f.write(content)

def fromFile(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    return content


def parsePromoPage(response, past_url_list):
# <div class="wp-block-image">
#     <figure class="aligncenter size-large">
#         <img alt="" data-src="https://shengsiongcontent.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2021/07/12174027/7M21Booklet-F-02-1024x727.jpg" class="wp-image-6395 lazyloaded" src="https://shengsiongcontent.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2021/07/12174027/7M21Booklet-F-02-1024x727.jpg">
#             <noscript>
#                 <img src="https://shengsiongcontent.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2021/07/12174027/7M21Booklet-F-02-1024x727.jpg" alt="" class="wp-image-6395"/>
#             </noscript>
#         </figure>
#     </div>
    promo_page_dict = {}
    img_url_list = []

    try:

        title = response.html.find('title', first=True).text

        # expect only 1 main frame
        main = response.html.find('.td-ss-main-content', first=True)
        if main:    
            # locate image container
            blocks = main.xpath('//div[@class="wp-block-image"]')
            # get all the promo image
            for block in blocks:
                images = block.xpath('//img')
                # only interested in last link
                image = images[-1]
                if image:
                    img_url_list.append(image.attrs['src'])

        # filter past urls
        filtered = [img_url for img_url in img_url_list if img_url not in past_url_list]
        if filtered != []:
            # add to dictionary with format {title:[img_urls]}
            promo_page_dict[title] = img_url_list

    except Exception as ex:
        print('Exception in parsing promo page')
        print(str(ex))
    
    return promo_page_dict


def parseMainPage(response):
    promo_pages_list = []

# <div class="td-block-span4">
#     <div class="td_module_1 td_module_wrap td-animation-stack">
#         <div class="td-module-image">
#             <div class="td-module-thumb">
#                 <a href="https://corporate.shengsiong.com.sg/baby-fair-03-sept-2021-16-sept-2021/" rel="bookmark" class="td-image-wrap" title="Baby Fair 03 Sept 2021 – 16 Sept 2021" data-wpel-link="internal">
#                     <img alt="" title="Baby Fair 03 Sept 2021 – 16 Sept 2021" data-src="https://shengsiongcontent.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2021/09/02144442/BABY-FAIR-324x160.jpg" class="entry-thumb lazyloaded" src="https://shengsiongcontent.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2021/09/02144442/BABY-FAIR-324x160.jpg" width="324" height="160">
#                         <noscript>
#                             <img width="324" height="160" class="entry-thumb" src="https://shengsiongcontent.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2021/09/02144442/BABY-FAIR-324x160.jpg" alt="" title="Baby Fair 03 Sept 2021 &#8211; 16 Sept 2021"/>
#                         </noscript>
#                     </a>
#                 </div>
#             </div>
#             <h3 class="entry-title td-module-title">
#                 <a href="https://corporate.shengsiong.com.sg/baby-fair-03-sept-2021-16-sept-2021/" rel="bookmark" title="Baby Fair 03 Sept 2021 – 16 Sept 2021" data-wpel-link="internal">Baby Fair 03 Sept 2021 – 16 Sept 2021</a>
#             </h3>
#             <div class="td-module-meta-info">
#                 <span class="td-post-date">
#                     <time class="entry-date updated td-module-date" datetime="2021-09-03T00:00:00+00:00">September 3, 2021</time>
#                 </span>
#             </div>
#         </div>
#     </div>

    try:

        # print(response.html.find('title', first=True).text)
        
        # expect only 1 main frame
        main = response.html.find('.td-ss-main-content', first=True)
        if main:    
            # locate promos container 
            promos = main.xpath('//div[@class="td-block-span4"]')
            # get all the promo pages
            for promo in promos:
                # only interested in last link
                link = promo.find('a')[-1]
                # filter uninterested page
                filtered = next((link.attrs['href'] for keyword in FILTER_TITLE if keyword in link.text.lower()), None)
                if filtered != None:
                    promo_pages_list.append(filtered)

    except Exception as ex:
        print('Exception in parsing main page')
        raise ex

    return promo_pages_list


def getSSPromos():

    session = None
    json_data = None

    try:
        session = HTMLSession()
        response = session.get(URL)

        promo_dict = {}
        past_url_list = []
        
        # toFile(DBG_FILENAME, req.content)
        # return 

        # retrieve last broadcasted data
        past_url_list = jsonutil.readLastUrl(COM_ID)

        promo_pages = parseMainPage(response)
        for page_url in promo_pages:
            response = session.get(page_url)
            url_dict = parsePromoPage(response, past_url_list)
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
    getSSPromos()