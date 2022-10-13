from bs4 import BeautifulSoup
from requests import get
from json import loads, dump

req = get("https://zangakbookstore.am/grqer", "html")
src = req.text

soup = BeautifulSoup(src, "lxml")
# json_file = {}


def alpha(sym):
    tmp = ""
    for i in sym:
        if i.isalpha() or i == ' ':
            tmp += i
    return tmp


def creating_category():
    for i in soup.find_all("div", class_="category-name-box"):
        if i.find("div", class_="collapse sub-category"):
            continue
        print(i.find("a", class_="category-name").text)
        print(alpha(i.find("a", class_="category-name").text))
        if alpha(i.find("a", class_="category-name").text) in ["Գրքեր", "Բեսթսելլեր", "Նոր տեսականի", "Zangak Store"]:
            continue
        if alpha(i.find("a", class_="category-name").text) == "Գրենական պիտույքներ":
            break
        json_file[i.find("a", class_="category-name").text] = i.find('a', class_="category-name").get('href') + "?page=1"
        print(json_file)


# json_file["Գեղարվեստական"] = {'https://zangakbookstore.am/gekharvestakan?page=1'}
# json_file["Ոչ գեղարվեստական"] = {'https://zangakbookstore.am/voch-gegharvestakan?page=1'}
# json_file["Մանկական"] = {'https://zangakbookstore.am/mankakan?page=1'}
# json_file["Կոմիքսներ"] = {'https://zangakbookstore.am/komiqsner-ev-grafikakan-veper?page=1'}
# json_file["Պատանեկան"] = {'https://zangakbookstore.am/patanekan?page=1'}
# json_file["Ուսումնական"] = {'https://zangakbookstore.am/usumnakan?page=1'}
# json_file["Մատենաշարեր"] = {'https://zangakbookstore.am/matenasharer?page=1'}


def book_items():
    json_book = {}
    count = 0
    for category_name, books_url in json_file.items():
        json_book[category_name] = {}
        print(len(books_url))
        try:
            for book_url in books_url:
                book_soup = BeautifulSoup(get(book_url, "html").text, "lxml")
                book_name = book_soup.find("h1").text
                json_book[category_name][book_name] = {}
                need_info = book_soup.find("a", class_="nav-link active").text
                rows = book_soup.find_all("div", class_="form-row")
                web_row = book_soup.find("div", class_="tab-pane fade show active")
                if need_info == "Մանրամասներ":
                    for i in rows:
                        if i.find("label").text == 'Կոդ':
                            continue
                        for tmp in i.find_all("div", class_="col-6"):
                            value = tmp.text
                        json_book[category_name][book_name][i.find("label").text] = value
                elif need_info == "Նկարագրություն":
                    json_book[category_name][book_name][need_info] = web_row.find("div", class_="col-md-10").text
                    for i in rows:
                        if i.find("label").text == 'Կոդ':
                            continue
                        for tmp in i.find_all("div", class_="col-6"):
                            value = tmp.text
                        json_book[category_name][book_name][i.find("label").text] = value
                count += 1
                print(count)
        except:
            continue
        print(book_name)
    with open("scraped_data.json", "w") as new_file:
        dump(json_book, new_file, ensure_ascii=False)


with open("category_books.json", "r") as file:
    src = loads(file.read())

json_file = src
book_items()


def books_scraping():
    for category_name, category_link in json_file.items():
        page_count = 1
        tmp_url = ''.join([x for x in category_link][0])
        json_file[category_name] = {}
        try:
            while True:
                req = get(tmp_url, "html").text
                book_soup = BeautifulSoup(req, "lxml")
                if category_name == "Գեղարվեստական" and page_count == 408:
                    break
                elif category_name == "Ոչ գեղարվեստական" and page_count == 265:
                    break
                elif category_name == "Մանկական" and page_count == 134:
                    break
                elif category_name == "Կոմիքսներ" and page_count == 35:
                    break
                elif category_name == "Պատանեկան" and page_count == 43:
                    break
                elif category_name == "Ուսումնական" and page_count == 46:
                    break
                elif category_name == "Մատենաշարեր" and page_count == 29:
                    break
                # books_url = book_soup.find("div", class_="row no-gutters product-items-list items-list-container")
                # if books_url == None:
                #     break
                books_url = book_soup.find_all("div", class_="col-6 col-md-4 col-lg-6 col-xl-4 col-xxl-3 mb-5 list-item")
                for take_books in books_url:
                    new_url = take_books.find("div", class_="mb-3").find("a").get("href")
                    json_file[category_name][new_url] = {}
                page_count += 1

                if page_count < 11:
                    tmp_url = tmp_url[:-1] + str(page_count)
                elif 10 < page_count < 101:
                    tmp_url = tmp_url[:-2] + str(page_count)
                elif 100 < page_count < 1001:
                    tmp_url = tmp_url[:-3] + str(page_count)
                elif 1000 < page_count < 10001:
                    tmp_url = tmp_url[:-4] + str(page_count)
                print(page_count)
            print(json_file)
        except:
            continue
    with open("js_zangak.json", "w") as file:
        dump(json_file, file, ensure_ascii=False)

# with open("data.json", "r") as file:
#     src = loads(file.read())


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
