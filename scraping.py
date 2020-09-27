from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

def scrape_all():
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_p = mars_news(browser)
    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemisphere_data": hemisphere_data(browser),
        "last_modified": dt.datetime.now()
    }
    browser.quit()
    return data

def mars_news(browser):

    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        news_title = slide_elem.find("div", class_="content_title").get_text()
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def hemisphere_data(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    hemisphere_image_urls = []
    html = browser.html
    hemisphere_soup = soup(html, 'html.parser')
    names = hemisphere_soup.find_all('h3')

    for name in names:
        hemisphere_name = name.text
        element = browser.is_element_present_by_text(hemisphere_name, wait_time=1)
        if element == True:
            element_link = browser.links.find_by_partial_text(hemisphere_name)
            element_link.click()
            html = browser.html
            img_soup = soup(html, 'html.parser')
            img_url = img_soup.select_one("ul li a").get("href")
            hemispheres = {'img_url':img_url,'title':hemisphere_name}
            hemisphere_image_urls.append(hemispheres)
        url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        browser.visit(url)
    return hemisphere_image_urls


def featured_image(browser):
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    full_image_elem = browser.find_by_id('full_image')[0]
    full_image_elem.click()
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    return img_url

def mars_facts():
    try:
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)
    return df.to_html(classes="table table-striped")

if __name__ == "__main__":
    print(scrape_all())