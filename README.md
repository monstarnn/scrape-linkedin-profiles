# Scrape Linkedin profiles

## Preinstall Selenium

### Local testing environment

It's required to have installed local browsers and have WebDriver for browsers, for example:
* [ChromeDriver - WebDriver for Chrome](https://sites.google.com/a/chromium.org/chromedriver/)
* [WebDriver for Firefox](https://github.com/mozilla/geckodriver/releases)

After downloading suitable WebDriver it should be started, for example ChromeDriver can be ran on port 4444 by:
```bash
./chromedriver --port=4444 --url-base="wd/hub" --whitelisted-ips=""
```

During the tests WebDriver will open new browser session and run the tests in this browser's session.
After tests completion this just opened browser's session will be closed.

### Docker testing environment

NOTE: this method is not implemented yet, use previous method. 

It's available to run WebDriver in docker container.
Required containers can be found in [Selenium Docker project](https://github.com/SeleniumHQ/docker-selenium)

For example, to run WebDriver for Chrome on default port 4444, the following command should be executed:
```bash
docker run -d -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome
```
Note: mounting `-v /dev/shm:/dev/shm` or using the flag `--shm-size=2g` is required to use the host's shared memory
for Chrome or Firefox.

WebDriver can be checked by opening [http://localhost:4444/wd/hub](http://localhost:4444/wd/hub)

## Install required Python 3 packages 

```bash
pip3 install selenium  
```

## Scrape

### Prepare existing data
```bash
python prepare.py source-filename.csv [first-name-col last-name-col position-col company-col additional-cols...]
```
For example, without additional columns:
```bash
python3 prepare.py source-filename.csv 1 3 0
```
With additional columns:
```bash
python3 prepare.py source-filename.csv 1 3 0 '2:Email' '5:Engagement Type' '6:Stage'
```
This script prepares source CSV to required format with at least 3 columns with header:
`First and Last Name`, `Position` and `Company`. This data will record to `./data.csv`

### Scrape LinkedIn profiles
```bash
python scrape.py linkedin-email linkedin-password
```
This script logins browser session to LinkedIn as user with specified user's email and password.
If login succeeded it searches for LinkedIn users from `./data.csv` using LinkegIn's search form
and scrapes user's info from their profiles. So existing information is complemented by the following fields:
* `LinkedIn` - URL to LinkedIn's profile (empty if user has not been found)
* `Image` - URL to user's avatar image (empty if absent)
* `Positions` - "|"-separated user's last jobs positions (related with companies)
* `Companies` - "|"-separated user's last jobs companies (related with positions)
* `Links` - "|"-separated user's links (Twitter, sites, etc...)

Scrapped info stores to `./data.linkedin.scraped.csv`

You can interrupt execution at any time and run script again, it will continue scrapping from the last position.

### Save to dataset
```bash
python make.py save-to-dir
```
This script downloads photos and metadata to `save-to-dir` directory.
Photo saves as `linkedin.jpg`, metadata saves to `meta.json`.

If additional columns exists in scraped data, these columns headers must be set as arguments, for example:
```bash
python make.py ./data2 Email "Engagement Type" Stage
```
