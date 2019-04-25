import csv
import re
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

source_data_file_name = 'data.csv'
target_data_file_name = 'data.linkedin.scraped.csv'


def main():
    if len(sys.argv) < 3:
        print("usage: %s <linkedin-email> <linkedin-password>" % sys.argv[0])
        exit(1)

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

    # login to linkedin
    driver.get('https://www.linkedin.com/uas/login')
    username = driver.find_element_by_id('username')
    username.send_keys(sys.argv[1])
    password = driver.find_element_by_id('password')
    password.send_keys(sys.argv[2])
    sign_in_button = driver.find_element_by_xpath('//*[@type="submit"]')
    sign_in_button.click()

    feed_url = 'https://www.linkedin.com/feed/'
    if not driver.current_url.startswith(feed_url):
        print("LinkedIn login error, you've been redirected to '%s', not to %s. "
              "Probably email/pass are wrong?" % (driver.current_url, feed_url))
        exit(1)

    persons, prev = 0, 0
    with open(source_data_file_name, mode='r') as source:
        with open(target_data_file_name, mode=mode) as target:
            csv_reader = csv.reader(source, delimiter=';')
            data_writer = csv.writer(target, delimiter=';')
            header = next(csv_reader)
            if write_header:
                header.append("LinkedIn")
                header.append("Image")
                header.append("Positions")
                header.append("Companies")
                header.append("Links")
                data_writer.writerow(header)

            for row in csv_reader:

                persons += 1
                row_exists = False
                exists_name = ""
                for e in exists:
                    # name, position and company are the same
                    #  OR linkedin profile is the same (if exists)
                    if e[0] == row[0] and e[1] == row[1] and e[2] == row[2] \
                            or len(e) >= 4 and len(row) >= 4 and e[3] == row[3]:
                        row_exists = True
                        exists_name = e[0]
                        break
                if row_exists:
                    print("%s: already exists" % exists_name)
                    prev += 1
                    continue

                scraped_row = row[:3]
                by_link = True
                scrapped = {}
                res = "not found"

                linkedin_url = row[3] if len(row) >= 4 else ''
                if linkedin_url == '':
                    by_link = False
                    search_args = []
                    for f in row:
                        if f != "":
                            search_args.append(f)
                    linkedin_url = search_and_follow_linkedin_profile(driver, " ".join(search_args))
                else:
                    driver.get(linkedin_url)

                if linkedin_url != "":
                    scrapped, errors = parse_linkedin_page(driver, by_link)
                    res = ", ".join(errors) if len(errors) > 0 else "done"

                if by_link:
                    if scraped_row[0] == '':
                        scraped_row[0] = scrapped['name'] if 'name' in scrapped else ''
                    if scraped_row[1] == '':
                        scraped_row[1] = scrapped['position'] if 'position' in scrapped else ''
                    if scraped_row[2] == '':
                        scraped_row[2] = scrapped['company'] if 'company' in scrapped else ''

                scraped_row.append(linkedin_url)
                scraped_row.append(scrapped["avatar"] if "avatar" in scrapped else "")
                scraped_row.append("|".join(scrapped["positions"]) if "positions" in scrapped else "")
                scraped_row.append("|".join(scrapped["companies"]) if "companies" in scrapped else "")
                scraped_row.append("|".join(scrapped["links"]) if "links" in scrapped else "")
                data_writer.writerow(scraped_row)
                print("%s: %s (%d[%d])" % (scraped_row[0], res, persons, prev))


def search_and_follow_linkedin_profile(driver, query):
    search_input = driver.find_element_by_css_selector('.nav-search-typeahead input')
    search_input.clear()
    search_input.send_keys(query)
    search_input.send_keys(Keys.RETURN)

    linkedin_urls = []
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "blended-srp-results-js")
            )
        )
        linkedin_urls = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".search-results__list a.search-result__result-link")
            )
        )
    except Exception:
        pass

    linkedin_url = ""
    if len(linkedin_urls) > 0:
        linkedin_url = linkedin_urls[0].get_attribute("href")
        driver.execute_script("arguments[0].click();", linkedin_urls[0])

    return linkedin_url


def parse_linkedin_page(driver, by_link=False):
    ret = {}
    errors = []

    # get current name
    if by_link:
        name_h1 = driver.find_elements_by_css_selector('h1.pv-top-card-section__name')
        if len(name_h1) > 0:
            ret['name'] = name_h1[0].text

    # get image url
    try:
        avatar = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".presence-entity__image.pv-top-card-section__photo")
            )
        )
        avatar_style = driver.execute_script("""
            var element = arguments[0], style = element.currentStyle || window.getComputedStyle(element, false);
            return style['background-image'];
        """, avatar)
        avatar_re = re.search('url\(\"(.*)\"\)', avatar_style)
        if avatar_re:
            avatar_image = avatar_re.group(1).strip()
            if "static.licdn.com" not in avatar_image:
                ret["avatar"] = avatar_re.group(1).strip()
    except Exception:
        errors.append("get avatar error")

    # get companies and positions
    try:
        element = False
        for i in range(3):
            try:
                driver.execute_script("window.scrollTo(0, 250);")
                element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located(
                        (By.ID, "experience-section")
                    )
                )
            except:
                pass
            else:
                break

        if element:
            driver.execute_script("arguments[0].scrollIntoView();", element)
            positions_selector = WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "#experience-section div.pv-entity__summary-info h3.t-16")
                )
            )
            positions = [pos.text.replace("|", " ").strip() for pos in positions_selector]
            companies_selector = driver.find_elements_by_css_selector(
                '#experience-section span.pv-entity__secondary-title')
            companies = [cmp.text.replace("|", " ").strip() for cmp in companies_selector]
            if len(positions) > 0 and len(companies) > 0:
                ret["positions"] = positions
                ret["companies"] = companies
                if by_link:
                    ret['position'] = positions[0]
                    ret['company'] = companies[0]
    except Exception:
        errors.append("get companies and positions error")

    # get links
    try:
        see_links = driver.find_element_by_css_selector('a.pv-top-card-v2-section__link--contact-info')
        driver.execute_script("arguments[0].click();", see_links)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".pv-profile-section.pv-contact-info.pv-contact-info--for-top-card-v2")
            )
        )
        see_links_a = driver.find_elements_by_css_selector(
            'section.pv-profile-section.pv-contact-info.pv-contact-info--for-top-card-v2 a.pv-contact-info__contact-link')
        links = [a.get_attribute('href').replace("|", " ").strip() for a in see_links_a]
        if len(links) > 0:
            ret["links"] = links
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    except Exception:
        errors.append("get links error")

    return ret, errors


if __name__ == '__main__':
    main()
