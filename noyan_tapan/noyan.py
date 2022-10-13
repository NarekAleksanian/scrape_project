from json import loads, dump
from requests import get
from bs4 import BeautifulSoup

url = "http://www.noyantapan.am/catalog/books/"
req = get(url, "html")
src = req.text
soup = BeautifulSoup(src, "lxml")


test_url = "http://www.noyantapan.am/catalog/books/mankakan/189232/"
req = get(test_url, "html").text
soup = BeautifulSoup(req, "lxml")
book_name = soup.find("h1", class_="changeName").text.strip()
print(book_name)


def alpha(sym):
    tmp = ""
    for i in sym:
        if i.isalpha() or i == ' ':
            tmp += i
    return tmp


def create_category():
    for i in soup.find_all("li", class_="c_left_item"):
        if alpha(i.find("a", class_="c_item_link").text) == 'Բեսթսելլեր':
            continue
        json_file[alpha(i.find("a", class_="c_item_link").text)] = \
            url[:-15] + i.find("a", class_="c_item_link").get("href")+"?PAGEN_1=1"


def scraping_all_books():
    for category_names, category_url in json_file.items():
        scrape_url = get(category_url, "html").text
        scrape_soup = BeautifulSoup(scrape_url, "lxml")
        pages_count = page_listing_and_count(scrape_soup)
        print(pages_count)
        json_file[category_names] = {}
        next_scrape_page = 1
        big_count = 0
        while next_scrape_page <= pages_count:
            count = 0
            books_item = scrape_soup.find("div", class_="items productList").find_all("div", class_="productColText")
            for tmp_book in books_item:
                tmp_book = "http://www.noyantapan.am" + tmp_book.find("a", class_="name").get("href")
                json_file[category_names][tmp_book] = {}
                count += 1
            big_count += count
            print("books count in one page: ", count)
            print("category count: ", big_count)
                # scrape_books()
            next_scrape_page += 1
            if next_scrape_page < 11:
                category_url = category_url[:-1] + str(next_scrape_page)
            elif 10 < next_scrape_page < 101:
                category_url = category_url[:-2] + str(next_scrape_page)
            elif 100 < next_scrape_page < 1001:
                category_url = category_url[:-3] + str(next_scrape_page)
            elif 1000 < next_scrape_page < 10001:
                category_url = category_url[:-4] + str(next_scrape_page)
            print(category_url)
            scrape_url = get(category_url).text
            scrape_soup = BeautifulSoup(scrape_url, "lxml")
        print(big_count)
        print(json_file)


def scrape_books():
    new_json = {}
    big_count = 0
    for category_name, category_links in json_file.items():
        count = 0
        new_json[category_name] = {}
        for link in category_links.keys():
            new_url = get(link, "html").text
            books_soup = BeautifulSoup(new_url, "lxml")
            try:
                book_name = books_soup.find("h1", class_="changeName").text.strip()
                new_json[category_name][book_name] = {}
                proper_name = books_soup.find_all("div", class_="propertyName")
                proper_value = books_soup.find_all("div", class_="propertyValue")
                new_json[category_name][book_name]["գին"] = books_soup.find("span", class_="priceVal").text
                for spec_name, spec_value in zip(proper_name, proper_value):
                    if spec_name.text == "Կոդ":
                        continue
                    else:
                        new_json[category_name][book_name][spec_name.text.strip()] = spec_value.text.strip()
            except:
                continue
            count += 1
            print(book_name)
            print(count)
        big_count += count
        print(new_json)

    with open("scraped_data.json", "w") as new_file:
        dump(new_json, new_file, ensure_ascii=False)


with open("category_books.json", "r") as file:
    src = loads(file.read())

json_file = src
scrape_books()


def page_listing_and_count(page_count_soup):
    try:
        tmp_count = [x.text for x in page_count_soup.find("div", class_="bx-pagination").find_all("span") if
                     x.text.isnumeric()]
        pages_count = 0
        for i in tmp_count:
            if i.isnumeric() and int(i) > pages_count:
                pages_count = int(i)
        return pages_count
    except:
        return 1
