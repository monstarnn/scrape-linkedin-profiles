import csv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

source_data_file_name = 'data.csv'
target_data_file_name = 'data.linkedin.csv'


def main():
    exists = []
    mode = "w"
    write_header = True
    try:
        with open(target_data_file_name, mode='r') as source:
            csv_reader = csv.reader(source, delimiter=';')
            next(source)
            for row in csv_reader:
                exists.append(row)
    except Exception:
        print("data from %s has not been read" % target_data_file_name)
    else:
        mode = "a"
        write_header = False
        print("data from %s has been read" % target_data_file_name)

    driver = webdriver.Chrome('./chromedriver')
    driver.get('https://www.google.com')

    persons, prev, has_li = 0, 0, 0
    with open(source_data_file_name, mode='r') as source:
        with open(target_data_file_name, mode=mode) as target:
            csv_reader = csv.reader(source, delimiter=';')
            data_writer = csv.writer(target, delimiter=';')
            header = next(csv_reader)
            if write_header:
                header.append("LinkedIn")
                data_writer.writerow(header)

            for row in csv_reader:

                persons += 1
                row_exists = False
                for e in exists:
                    if e[0] == row[0] and e[1] == row[1] and e[2] == row[2]:
                        row_exists = True
                        if e[3] != "":
                            has_li += 1
                        break
                if row_exists:
                    print("%s: already exists" % row[0])
                    prev += 1
                    continue

                search_args = []
                for f in row:
                    if f != "":
                        search_args.append(f)

                linkedin_url = ""
                search_query = driver.find_element_by_name('q')
                search_query.clear()
                query_string = 'site:linkedin.com/in/ AND "' + '" AND "'.join(search_args) + '"'
                search_query.send_keys(query_string)
                search_query.send_keys(Keys.RETURN)

                kaptcha = True
                while kaptcha:
                    try:
                        driver.find_element_by_id("captcha-form")
                    except Exception:
                        kaptcha = False
                    else:
                        input("Kaptcha detected, pass it and press Enter to continue...")

                linkedin_urls = driver.find_elements_by_class_name('iUh30')
                linkedin_urls = [url.text for url in linkedin_urls]

                res = ""
                if len(linkedin_urls) > 0:
                    linkedin_url = linkedin_urls[0]
                    res = "got linkedin: %s" % linkedin_url
                    has_li += 1
                else:
                    res = "no linkedin"

                print("%s: %s (%d[%d]/%d)" % (row[0], res, persons, prev, has_li))

                row.append(linkedin_url.strip())
                data_writer.writerow(row)

    print("Scanned %d persons, found LinkedIn for only for %d of them" % (persons, has_li))


if __name__ == '__main__':
    main()
