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

It's available to run WebDriver in docker container.
Required containers can be found in [Selenium Docker project](https://github.com/SeleniumHQ/docker-selenium)

For example, to run WebDriver for Chrome on default port 4444, the following command should be executed:
```
docker run -d -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome
```
Note: mounting `-v /dev/shm:/dev/shm` or using the flag `--shm-size=2g` is required to use the host's shared memory
for Chrome or Firefox.

WebDriver can be checked by opening [http://localhost:4444/wd/hub](http://localhost:4444/wd/hub)

NOTE: this method not works with Google scanning that shows kaptcha for more than 100 queries.

## Install required Python 3 packages 

```
pip3 install selenium  
```

## Scrape

### Prepare existing data

```
python 1.prepare.py
```
This script prepares source CSV to required format with 3 fields: name, position and company.
This data will record to `./data.csv`

### Get LinkedIn URLs
```
python 2.add_linkedin.py
```

This script uses Google search with Selenium browser to get LinkedIn URLs by name, position and company.
Source file is `./data.csv`, target - `./data.linkedin.csv`

If process interrupted tne next execution will continue from last scanned person. 

Note: if you have a lot of users, many requests will make. Every 100 requests Google returns kaptha,
so executing will be paused until YOU will pass this kaptcha.

### Scan LinkedIn profiles
```
python 3.scrape_linkedin.py <linkerid-email> <linkedin-password>
```
