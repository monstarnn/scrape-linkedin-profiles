# Scrape Linkedin profiles

## Preinstall Selenium

### Local testing environment

It's required to have installed local browsers and have WebDriver for browsers, for example:
* [ChromeDriver - WebDriver for Chrome](https://sites.google.com/a/chromium.org/chromedriver/)
* [WebDriver for Firefox](https://github.com/mozilla/geckodriver/releases)

After downloading suitable WebDriver it should be started, for example ChromeDriver can be ran on port 4444 by:
```
./chromedriver --port=4444 --url-base="wd/hub" --whitelisted-ips=""
```

During the tests WebDriver will open new browser session and run the tests in this browser's session.
After tests completion this just opened browser's session will be closed.

### Docker testing environment

NOTE: this method is not implemented yet, use previous method. 

It's available to run WebDriver in docker container.
Required containers can be found in [Selenium Docker project](https://github.com/SeleniumHQ/docker-selenium)

For example, to run WebDriver for Chrome on default port 4444, the following command should be executed:
```
docker run -d -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome
```
Note: mounting `-v /dev/shm:/dev/shm` or using the flag `--shm-size=2g` is required to use the host's shared memory
for Chrome or Firefox.

WebDriver can be checked by opening [http://localhost:4444/wd/hub](http://localhost:4444/wd/hub)

## Install required Python 3 packages 

```
pip3 install selenium  
```

## Scrape

### Prepare existing data
```
python prepare.py <source-filename>
```
This script prepares source CSV to required format with 3 columns with header:
`First and Last Name`, `Position` and `Company`. This data will record to `./data.csv`

### Scrape LinkedIn profiles
```
python scrape.py <linkerid-email> <linkedin-password>
```
This script logins browser session to LinkedIn as user with specified user's email and password.
If login succedeed it searches for LinkedIn users from `./data.csv` using LinkegIn's search form
and scrapes user's info from their profiles. So existing information is complemented by the following fields:
* `LinkedIn` - URL to LinkedIn's profile (empty if user has not been found)
* `Image` - URL to user's avatar image (empty if absent)
* `Positions` - "|"-separated user's last jobs positions (related with companies)
* `Companies` - "|"-separated user's last jobs companies (related with positions)
* `Links` - "|"-separated user's links (Twitter, sites, etc...)

Scrapped info stores to `./data.linkedin.scraped.csv`

You can interrupt execution at any time and run script again, it will continue scrapping from the last position.