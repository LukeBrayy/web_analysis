import os
import json
import requests
from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
import database_queries
from datetime import datetime, date, timedelta
import random
import time


def make_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox") # linux only
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    return driver



def carsales_results_scraper(driver):
    url = 'https://www.carsales.com.au/cars/?&q=(And.Service.Carsales._.Condition.Used._.(C.Make.Toyota._.(Or.Model.Landcruiser._.Model.Landcruiser%20Prado.)))'

    driver.get(url)
    print(driver.page_source)
    #listing_items = soup.find_all("div", _class="listing-item card showcase")




def gumtree_car_scraper(car_url, driver):
    car_dict = {}

    url = "https://www.gumtree.com.au" + car_url
    car_dict['url'] = url
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    title = soup.find('h1', class_="vip-ad-title__header").text
    car_dict['title'] = title
    price = soup.find('span', class_='user-ad-price__price').text
    car_dict['price'] = float(price.replace("$", "").replace(",", ""))
    location = soup.find('span', class_='vip-ad-title__location-address').text
    car_dict['location'] = location

    all_description = ""
    descriptions = soup.find_all("span", class_="vip-ad-description__content--wrapped")
    for desc in descriptions:
        all_description += desc.text + "\n"
    main_description = descriptions[0].text

    car_dict['main_description'] = main_description
    car_dict['full_description'] = all_description

    all_attributes = soup.find_all("li", class_="vip-ad-attributes__item")
    header_lookup = {"date listed": "date_listed", "last edited":"last_edited", "seller type":"seller_type", "drive train":"drive_train", "fuel type":"fuel_type", "air conditioning":"air_conditioning", "registration number":"registration_number", "body type":"body_type"}
    for attr in all_attributes:
        try:
            header = attr.find("span", class_="vip-ad-attributes__value").text[:-1]
            #print(header)
            try:
                value = attr.find("span", class_="vip-ad-attributes__name").text
            except:
                try:
                    value = attr.find("a", class_="vip-ad-attributes__name").text
                except:
                    print("attribute error")
            #vip-ad-attributes__name link link--base-color-primary link--hover-color-none
            if len(header.strip().split(" ")) == 1:
                formatted_header = header.lower()
                #print("|{}|".format(formatted_header))
            else:
                formatted_header = header_lookup.get(header.lower(), 0)
            if formatted_header==0:
                print("Warning header not found!! |{}| ".format(header))

            if formatted_header == "kilometres":
                car_dict[formatted_header] = int(value)
            elif formatted_header == "date_listed":
                if "hours" in value or "minutes" in value:
                    now = datetime.now()
                    car_dict[formatted_header] = now.strftime("%d/%m/%Y")
                elif "Yesterday" in value:
                    yesterday = date.today() - timedelta(days=1)
                    car_dict[formatted_header] = yesterday.strftime("%d/%m/%Y")
                else:
                    car_dict[formatted_header] = value
            else:
                car_dict[formatted_header] = value
                #print(header, value)
        except AttributeError:
            print("attribute error")


    #driver.get(url)
    #print("\n")

    #h1 = driver.find_element_by_class_name("vip-ad-image__main-image")

    #image_url = h1.get_attribute('src')
    image_url = ""

    car_dict['first_photo'] = image_url
    return car_dict



def gumtree_results_scraper(url):
    #url = "https://www.gumtree.com.au/s-cars-vans-utes/perth/carmake-toyota/carmodel-toyota_landcruiser/page-2/c18320l3008303"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    listings_container = 'user-ad-collection-new-design__wrapper--row'
    results_container = soup.find_all('div', class_=listings_container)

    links = []
    for result in results_container:
        all_car_containers = result.find_all("a")
        for car in all_car_containers:
            link = car['href']
            links.append(link)
    return links



def loop_gumtree(driver):
    #url = "https://www.gumtree.com.au/s-cars-vans-utes/perth/carmake-toyota/carmodel-toyota_landcruiser/c18320l3008303"
    base_url = 'https://www.gumtree.com.au/s-cars-vans-utes/perth/carmake-toyota/carmodel-toyota_landcruiser/page-{}/c18320l3008303'

    searches = {
        "navara":"https://www.gumtree.com.au/s-cars-vans-utes/perth/carmake-nissan/carmodel-nissan_navara/drivetrain-4x4/page-{}/c18320l3008303?price=__30000.00",
        "patrol":"https://www.gumtree.com.au/s-cars-vans-utes/perth/carmake-nissan/carmodel-nissan_patrol/drivetrain-4x4/page-{}/c18320l3008303?price=__40000.00",
        "prado":"https://www.gumtree.com.au/s-cars-vans-utes/perth/carmake-toyota/carmodel-toyota_landcruiserprado/page-{}/c18320l3008303?price=__30000.00",
        "landcruiser":"https://www.gumtree.com.au/s-cars-vans-utes/perth/carmake-toyota/carmodel-toyota_landcruiser/page-{}/c18320l3008303?price=__35000.00",
        "hilux":"https://www.gumtree.com.au/s-cars-vans-utes/wa/carmake-toyota/carmodel-toyota_hilux/page-{}/c18320l3008845?price=__35000.00",
        "jimny":"https://www.gumtree.com.au/s-cars-vans-utes/perth/carmake-suzuki/carmodel-suzuki_jimny/page-{}/c18320l3008303?price=__35000.00",
        "triton":"https://www.gumtree.com.au/s-cars-vans-utes/wa/carmake-mitsubishi/carmodel-mitsubishi_triton/drivetrain-4x4/page-{}/c18320l3008845?price=__35000.00",
        "pajero":"https://www.gumtree.com.au/s-cars-vans-utes/wa/carmake-mitsubishi/carmodel-mitsubishi_pajero/page-{}/c18320l3008845?price=__35000.00",
        "colorado":"https://www.gumtree.com.au/s-cars-vans-utes/wa/carmake-holden/carmodel-holden_colorado/drivetrain-4x4/page-{}/c18320l3008845?price=__35000.00",
        "liberty_3":"https://www.gumtree.com.au/s-cars-vans-utes/wa/carmake-subaru/carmodel-subaru_liberty/page-{}/c18320l3008845?price=__35000.00",
        "liberty_3r":"https://www.gumtree.com.au/s-cars-vans-utes/wa/carmake-subaru/carmodel-subaru_liberty/variant-3.0R/page-{}/c18320l3008845?price=__35000.00",
        "amarok":"https://www.gumtree.com.au/s-cars-vans-utes/perth/carmake-volkswagen/carmodel-volkswagen_amarok/drivetrain-4x4/page-{}/c18320l3008845?price=__35000.00",
        "ranger": "https://www.gumtree.com.au/s-cars-vans-utes/wa/carmake-ford/carmodel-ford_ranger/drivetrain-4x4/page-{}/c18320l3008845?price=__35000.00",
        "mx5": "https://www.gumtree.com.au/s-cars-vans-utes/wa/carmake-mazda/carmodel-mazda_mx5/page-{}/c18320l3008845",
        "fj_cruiser": "https://www.gumtree.com.au/s-cars-vans-utes/wa/carmake-toyota/carmodel-toyota_fjcruiser/c18320l3008845",
        "dmax": "https://www.gumtree.com.au/s-cars-vans-utes/wa/carmake-isuzu/carmodel-isuzu_dmax/drivetrain-4x4/page-{}/c18320l3008845",
        "mux": "https://www.gumtree.com.au/s-cars-vans-utes/wa/carmake-isuzu/carmodel-isuzu_mux/drivetrain-4x4/page-{}/c18320l3008845",
        "wrangler": "https://www.gumtree.com.au/s-cars-vans-utes/wa/carmake-jeep/carmodel-jeep_wrangler/drivetrain-4x4/page-{}/c18320l3008845",
        "challenger": "https://www.gumtree.com.au/s-cars-vans-utes/wa/carmake-mitsubishi/carmodel-mitsubishi_challenger/drivetrain-4x4/page-{}/c18320l3008845",
        "defender": "https://www.gumtree.com.au/s-cars-vans-utes/wa/carmake-landrover/carmodel-landrover_defender/drivetrain-4x4/page-{}/c18320l3008845"
    }

    for search_name in searches:
        base_url = searches[search_name]
        for page in range(1, 11):
            url = base_url.format(page)
            car_urls = gumtree_results_scraper(url)
            for car_url in car_urls:
                time_delay = random.randint(100, 3000)
                #time.sleep(time_delay/1000)
                if not database_queries.check_if_inserted("https://www.gumtree.com.au" + car_url):
                    print("Trying", car_url)
                    try:
                        car_dict = gumtree_car_scraper(car_url, driver)
                    except Exception as E:
                        with open("broken_links.txt", "a") as file:
                            file.write(car_url + ", " + str(E) + "\n")
                    car_dict["search_name"] = search_name
                    database_queries.insert_gumtree(car_dict)
                    print("Completed url", car_url)



def test_gumtree_car(driver):
    car_url = '/s-ad/waikiki/cars-vans-utes/2007-volkswagen-mk5-golf-gti/1258933907'
    car_dict = gumtree_car_scraper(car_url, driver)
    database_queries.insert_gumtree(car_dict)
    for item in car_dict:
        print('{} : {}\n'.format(item, car_dict[item]))


if __name__ == '__main__':
    driver = False
    loop_gumtree(driver)
    database_queries.export_csv()
