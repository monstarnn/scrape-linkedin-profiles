import csv
import re
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

source_data_file_name = 'data.linkedin.csv'
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
    driver.get('https://www.linkedin.com')
    username = driver.find_element_by_class_name('login-email')
    username.send_keys(sys.argv[1])
    password = driver.find_element_by_class_name('login-password')
    password.send_keys(sys.argv[2])
    sign_in_button = driver.find_element_by_xpath('//*[@type="submit"]')
    sign_in_button.click()

    if driver.current_url != 'https://www.linkedin.com/feed/':
        print("Linkedin login error, email/pass are wrong?")
        exit(1)

    persons, prev = 0, 0
    with open(source_data_file_name, mode='r') as source:
        with open(target_data_file_name, mode=mode) as target:
            csv_reader = csv.reader(source, delimiter=';')
            data_writer = csv.writer(target, delimiter=';')
            header = next(csv_reader)
            if write_header:
                header.append("Image")
                header.append("Positions")
                header.append("Compaties")
                header.append("Links")
                data_writer.writerow(header)

            for row in csv_reader:
                if row[3] == "":
                    continue

                persons += 1
                row_exists = False
                for e in exists:
                    if e[0] == row[0] and e[1] == row[1] and e[2] == row[2]:
                        row_exists = True
                        break
                if row_exists:
                    print("%s: already exists" % row[0])
                    prev += 1
                    continue

                scrapped = parse_linkedin_page(driver, row[3])

                row.append(scrapped["avatar"] if "avatar" in scrapped else "")
                row.append("|".join(scrapped["positions"]) if "positions" in scrapped else "")
                row.append("|".join(scrapped["companies"]) if "companies" in scrapped else "")
                row.append("|".join(scrapped["links"]) if "links" in scrapped else "")

                data_writer.writerow(row)


def parse_linkedin_page(driver, url):
    driver.get(url)

    ret = {}

    # get image url
    avatar = driver.find_element_by_css_selector('.presence-entity__image.pv-top-card-section__photo')
    avatar_style = driver.execute_script("""
        var element = arguments[0], style = element.currentStyle || window.getComputedStyle(element, false);
        return style['background-image'];
    """, avatar)
    avatar_re = re.search('url\(\"(.*)\"\)', avatar_style)
    if avatar_re:
        avatar_image = avatar_re.group(1).strip()
        if "static.licdn.com" not in avatar_image:
            ret["avatar"] = avatar_re.group(1).strip()

    # get companies and positions
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.ID, "experience-section")
            )
        )
        positions_selector = driver.find_elements_by_css_selector(
            '#experience-section div.pv-entity__summary-info h3.t-16')
        positions = [pos.text.replace("|", " ").strip() for pos in positions_selector]
        companies_selector = driver.find_elements_by_css_selector('#experience-section span.pv-entity__secondary-title')
        companies = [cmp.text.replace("|", " ").strip() for cmp in companies_selector]
        if len(positions) > 0 and len(companies) > 0:
            ret["positions"] = positions
            ret["companies"] = companies
    except Exception as e:
        print("get companies and positions: ", e)
        pass

    # get links
    see_links = driver.find_element_by_css_selector('a.pv-top-card-v2-section__link--contact-info')
    try:
        see_links.click()
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
    except Exception as e:
        print("get links error: ", e)
        pass

    return ret


if __name__ == '__main__':
    main()
