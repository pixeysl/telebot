import jsonutil
from requests_html import HTMLSession
from datetime import date

# flyer page url
BASE_URL = 'https://promotions.fairprice.com.sg'
URL =  'https://www.fairprice.com.sg/weekly-promotions/'
# company id
COM_ID = 'ntuc'
# list of promo title to match and ignore the rest
FILTER_TITLE = ['Celebrate', '4 Days Only!', 'Must Buy', 'Weekly Savers', 'Fresh Picks', 'Fresh Buys', 'Neighbourhood', 'Specials']

DBG_FILENAME = 'index.html'
DBG_URL = 'http://localhost:80/'
# DBG_URL = 'https://www.fairprice.com.sg/store-weekly-ads/weekly-saver/'

glblsession = None


def toFile(filename, content):
    filename = jsonutil.WORKING_DIR + '\\' + filename
    with open(filename, 'wb') as f:
        f.write(content)

def fromFile(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    return content


def getHTMLSession():
    global glblsession
    if glblsession == None:
        glblsession = HTMLSession()
    return glblsession

def closeHTMLSession():
    global glblsession
    if glblsession:
        glblsession.close()


def getImageUrl(response):
    # expect only 1 main page
    main_image = response.html.xpath('//div[@id="print_current_page"]', first=True)
    if main_image:
        # locate image container
        images = main_image.xpath('//img')
        if len(images) == 1:
            return images[0].attrs['src']
        raise Exception('unexpected image list length, please check')


def parsePromoPage(response, title, past_url_list):
# <div id="print_current_page" class="single">
#     <img src="/91990/1694121/pages/85db28e0-ca52-41cf-a22b-2648bbe718a1-at600.jpg">
# </div>

# <div class="chrome">
#   <a id="next_slide" class="navButton" aria-label="Next page" role="button" href="https://promotions.fairprice.com.sg/price-drop-buy-now-must-buy/page/2" tabindex="0" aria-hidden="false"></a>
#   <div id="progress_indicator"><a href="" class="first-page disabled" aria-label="Skip to the first page" tabindex="-1" aria-hidden="true"></a>
#   <span class="current-page" aria-label="Current page position is 1 of 2"><span class="page-numbers">1</span><span class="separator">/</span>
#   <span class="total">2</span></span><a href="" class="last-page" aria-label="Skip to the last page" tabindex="0" aria-hidden="false"></a>
# </div><div class="current_page_label" aria-live="assertive">Price Drop Buy Now - Must Buy - page 1</div></div>

# <div class="chrome">
#   <a id="next_slide" class="navButton disabled" aria-label="Next page" role="button" href="" tabindex="-1" aria-hidden="true"></a>
#   <div id="progress_indicator"><a href="" class="first-page" aria-label="Skip to the first page" tabindex="0" aria-hidden="false"></a>
#   <span class="current-page" aria-label="Current page position is 2 of 2"><span class="page-numbers">2</span><span class="separator">/</span>
#   <span class="total">2</span></span><a href="" class="last-page disabled" aria-label="Skip to the last page" tabindex="-1" aria-hidden="true"></a>
# </div><div class="current_page_label" aria-live="assertive">Price Drop Buy Now - Must Buy - page 2</div></div>

    promo_page_dict = {}
    image_list = []

    while True:
        image_url = getImageUrl(response)
        if image_url != "":
            # replace with higher res image url
            image_url = image_url.replace("-at600", "-at1000")
            image_list.append(image_url)

        # check if there's a next page
        next_page = response.html.find('#next_slide', first=True)
        next_page_url = next_page.attrs['href']
        if next_page_url != "":
            session = getHTMLSession()
            response = session.get(next_page_url)
            response.html.render() # render .js
        else:
            break

    # filter past urls
    try:
        filtered = [BASE_URL + image_url for image_url in image_list if BASE_URL + image_url not in past_url_list]
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
        # locate promo container
        container = response.html.xpath('//ul[@class="sc-e79d1db7-0 eqfXC"]', first=True)
        # locate promo pages
        promos = container.xpath('//li[@class="sc-70112128-0 iRgrLZ"]')
        # get individual promo page
        for promo in promos:
            # only interested in last link
            links = promo.find('a', first=True)
            if links:
                link = links.attrs['href']
            else:
                continue
            # print(links.attrs['href'])

            titles = promo.find('p')
            title = titles[0].text + '\n' + titles[1].text
            # print(title)

            # filter uninterested page
            filtered = next((link for keyword in FILTER_TITLE if keyword in title), None)
            if filtered != None:
                promo_page_dict[title] = filtered

    except Exception as ex:
        print('Exception in parsing main page')
        raise ex

    return promo_page_dict


def getNTUCPromos():

    json_data = None

    try:
        promo_dict = {}
        past_url_list = []
        
        # retrieve last broadcasted data
        past_url_list = jsonutil.readLastUrl(COM_ID)

        session = getHTMLSession()
        response = session.get(URL)
        response.html.render() # render .js

        # toFile(DBG_FILENAME, response.content)
        # return

        promo_pages = parseMainPage(response)
        for key in promo_pages.keys():
            response = session.get(promo_pages[key])
            response.html.render() # render .js
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
        closeHTMLSession()

    return promo_dict


if __name__ == "__main__":
    getNTUCPromos()