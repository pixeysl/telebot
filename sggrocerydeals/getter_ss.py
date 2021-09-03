# import requests
from requests import NullHandler
from requests_html import HTMLSession

URL =  'https://corporate.shengsiong.com.sg/category/promotions/'

DBG_FILENAME = 'index.html'
DBG_FILENAME2 = 'index1.html'
DBG_URL = 'http://localhost:80/'

def toFile(filename, content):
    with open(filename, 'wb') as f:
        f.write(content)

def fromFile(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    return content

def parsePromoPage(response):
# <div class="wp-block-image">
#     <figure class="aligncenter size-large">
#         <img alt="" data-src="https://shengsiongcontent.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2021/07/12174027/7M21Booklet-F-02-1024x727.jpg" class="wp-image-6395 lazyloaded" src="https://shengsiongcontent.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2021/07/12174027/7M21Booklet-F-02-1024x727.jpg">
#             <noscript>
#                 <img src="https://shengsiongcontent.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2021/07/12174027/7M21Booklet-F-02-1024x727.jpg" alt="" class="wp-image-6395"/>
#             </noscript>
#         </figure>
#     </div>
    try:

        print(response.html.find('title', first=True).text)

        main = response.html.find('.td-ss-main-content')
        if main:    
            # expect only 1 main frame
            blocks = main[0].xpath('//div[@class="wp-block-image"]')
            # get all the promo image
            for block in blocks:
                images = block.xpath('//img')
                # only interested in last link
                link = images[-1]
                if link:
                    print(link.attrs['src'])
            

    except Exception as ex:
        print('Exception in parsing promo page')
        print(str(ex))

def parseMainPage(response):
    promos_dict = {}

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

        print(response.html.find('title', first=True).text)
        
        main = response.html.find('.td-ss-main-content')
        if main:    
            # expect only 1 main frame
            promos = main[0].xpath('//div[@class="td-block-span4"]')
            # get all the promos
            for promo in promos:
                links = promo.find('a')
                # only interested in last link
                link = links[-1]
                if link:
                    # add to dictionary with format {title:link}
                    promos_dict[link.text] = link.attrs['href']

    except Exception as ex:
        print('Exception in parsing main page')
        raise ex
    
    return promos_dict

def main():

    session = None

    try:
        session = HTMLSession()
        response = session.get(DBG_URL)
        
        # toFile(DBG_FILENAME, req.content)
        # content = fromFile(DBG_FILENAME)
        # allpromos = parseMainPage(response)

        # for key in allpromos:
            # print(key + ':  ' + allpromos[key])
            # response = session.get(allpromos[key])

        # toFile(DBG_FILENAME2, response.content)
        parsePromoPage(response)

    except Exception as ex:
        print(str(ex))
    finally:
        if session:
            session.close()

if __name__ == "__main__":
    main()