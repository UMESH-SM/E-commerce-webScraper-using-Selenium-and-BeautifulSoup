from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from flask import Flask, render_template, request
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('webScraper.html')

options = Options()
options.add_argument("--headless")  # To run chrome in headless mode
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('start-maximized')
options.add_argument('disable-infobars')
options.add_argument("--disable-extensions")

imaStudent_Url = "https://www.imastudent.com/search?query={}"

# create url as per needs


def getUrl(search_Term):

    search_Term = search_Term.strip()
    search_Term = search_Term.replace(' ', '%20')
    url = imaStudent_Url.replace('{}', search_Term)

    return url


# scrape data from target site

def reqData(url):

    titles = []
    descriptions = []
    prices = []
    images = []
    buy_Links = []

    try:
        # path to chrome executable file
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        driver.get(url)     # fetch data
    except:
        driver.quit()
        return render_template("webScraper.html", not_found_msg="No products were found that matched your criteria.")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        empty = soup.find_all("div", class_="ais-hits ais-hits__empty")
        if len(empty) == 1:     # if no results found
            return render_template("webScraper.html", not_found_msg="No products were found that matched your criteria.")
        results = soup.find_all("div", class_="ais-hits--item item-box")
    except:
        driver.quit()
        return render_template("webScraper.html", not_found_msg="No products were found that matched your criteria.")
    for item in results:
        titles.append(item.h2.a.text.strip())
        descriptions.append(
            item.find("div", class_="description").text.strip())
        prices.append(
            item.find("span", class_="price actual-price").text.strip())
        images.append(item.img.get("src"))
        small_Link = item.h2.a.get("href").strip()
        buy_Links.append("https://www.imastudent.com" + small_Link)

    num = len(titles)
    driver.quit()

    return render_template("webScraper.html", **locals())


@app.route('/webScraper.html/search', methods=['POST', 'GET'])
def pass_check():
    if request.method == 'POST':
        search_input = request.form['search_input']
    base_Url = getUrl(search_input)
    return reqData(base_Url)
