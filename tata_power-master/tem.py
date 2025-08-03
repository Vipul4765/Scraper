
import requests

import lxml.html

URL = 'https://store.steampowered.com/explore/new/'

getHtml = requests.get(URL)

docContent = lxml.html.fromstring(getHtml.content)
xpathComplete = docContent.xpath('//div[@id="tab_newreleases_content"]')[0]