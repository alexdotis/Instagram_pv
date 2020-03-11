import string
import requests
import os
import time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import sys
from multiprocessing.dummy import Pool
import random
import urllib.parse
import argparse
import threading

LINKS = []
PICTURES = []
VIDEO = []


class Errors:
    """Checking Instagram Profiles"""

    def __init__(self, link, cookies=None):
        self.link = urllib.parse.urljoin(link, "?__a=1")
        self.cookies = cookies
        if self.cookies is not None:
            self.cookies = cookies

    def availability(self):
        search = requests.get(self.link, self.cookies)
        if search.status_code == 404:
            return "Sorry, this page isn't available."
        elif search.json()["graphql"]["user"]["is_private"] is True:
            return "This Account is Private"
        else:
            return True


class fetch_urls(threading.Thread):

    def __init__(self, url, cookies=None):
        threading.Thread.__init__(self)
        self.cookies = cookies
        if self.cookies is not None:
            self.cookies = cookies
        self.url = url

    def run(self):
        """Extract Images and Videos"""
        logging_page_id = requests.get(self.url.split()[0], cookies=COOKIES).json()
        try:
            for i in range(len(logging_page_id['graphql']['shortcode_media']['edge_sidecar_to_children']['edges'])):
                video = \
                    logging_page_id['graphql']['shortcode_media']['edge_sidecar_to_children']['edges'][i]['node'][
                        "is_video"]
                if video is True:
                    video_url = \
                        logging_page_id['graphql']['shortcode_media']['edge_sidecar_to_children']['edges'][i][
                            'node'][
                            "video_url"]
                    if video_url not in VIDEO:
                        VIDEO.append(video_url)

                else:
                    image = \
                        logging_page_id['graphql']['shortcode_media']['edge_sidecar_to_children']['edges'][i][
                            'node'][
                            'display_url']
                    if image not in PICTURES:
                        PICTURES.append(image)
        except KeyError:
            image = logging_page_id['graphql']['shortcode_media']['display_url']
            if image not in PICTURES:
                PICTURES.append(image)

            if logging_page_id['graphql']['shortcode_media']["is_video"] is True:
                videos = logging_page_id['graphql']['shortcode_media']["video_url"]
                if videos not in VIDEO:
                    VIDEO.append(videos)


class Instagram_pv:

    def close(self):
        self.driver.close()

    def __init__(self, username, password, folder, name):
        self.username = username
        self.password = password
        self.folder = folder
        self.name = name
        
        try:
            self.driver = webdriver.Chrome() # or you can pass \path\to\chromedriver.exe
        except WebDriverException as e:
            print(str(e))
            sys.exit(1)

    def control(self):
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
        else:
            self.close()
            raise FileExistsError("[*] Alredy Exists This Folder")

    def login(self):
        self.driver.get("https://www.instagram.com/accounts/login")
        time.sleep(3)
        self.driver.find_element_by_name('username').send_keys(self.username)
        self.driver.find_element_by_name('password').send_keys(self.password)
        submit = self.driver.find_element_by_tag_name('form')
        submit.submit()
        time.sleep(3)
        try:
            var_error = self.driver.find_element_by_class_name("eiCW-").text
            if len(var_error) > 0:
                print(var_error)
                sys.exit(1)
        except WebDriverException:
            pass

        try:
            self.driver.find_element_by_xpath('//button[text()="Not Now"]').click()
        except WebDriverException:
            pass
        time.sleep(2)
        """Taking Cookies for requests json"""
        cookies = self.driver.get_cookies()
        needed_cookies = ['csrftoken', 'ds_user_id', 'ig_did', 'mid', 'sessionid']
        global COOKIES
        COOKIES = {cookies[i]['name']: cookies[i]['value'] for i in range(len(cookies)) if
                   cookies[i]['name'] in needed_cookies}

        self.driver.get("https://www.instagram.com/{name}/".format(name=self.name))

        error = Errors("https://www.instagram.com/{name}/".format(name=self.name), COOKIES).availability()
        if error is not True:
            print(error)
            self.close()
            sys.exit(1)
        else:
            self._scroll_down()

    def _get_href(self):
        elements = self.driver.find_elements_by_xpath("//a[@href]")
        for elem in elements:
            urls = elem.get_attribute("href")
            if "p" in urls.split("/"):
                LINKS.append(urls)

    def _scroll_down(self):
        """Taking hrefs while scrolling down"""
        end_scroll = []
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            self._get_href()
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            end_scroll.append(new_height)
            if end_scroll.count(end_scroll[-1]) > 4:
                self.close()
                self.extraction_url()
                break

    def extraction_url(self):
        links = list(set(LINKS))
        print("[!] Ready for video - images".title())
        print("[*] extracting {links} posts , please wait...".format(links=len(links)).title())
        for url in LINKS:
            new_link = urllib.parse.urljoin(url, '?__a=1')
            fetch_urls(new_link).start()
        for thread in threading.enumerate():
            if thread is not threading.currentThread():
                thread.join()

    def content_of_url(self, url):
        re = requests.get(url)
        return re.content

    def _download_video(self, new_videos):
        with open(
                os.path.join(self.folder, "Video{}.mp4").format(
                    "".join([random.choice(string.digits) for i in range(20)])),
                "wb") as f:
            content_of_video = self.content_of_url(new_videos)
            f.write(content_of_video)

    def _images_download(self, new_pictures):
        with open(
                os.path.join(self.folder, "Image{}.jpg").format(
                    "".join([random.choice(string.digits) for i in range(20)])),
                "wb") as f:
            content_of_picture = self.content_of_url(new_pictures)
            f.write(content_of_picture)

    def downloading_video_images(self):
        print("[*] ready for saving images and videos!".title())
        new_pictures = list(set(PICTURES))
        new_videos = list(set(VIDEO))
        pool = Pool(8)
        pool.map(self._images_download, new_pictures)
        pool.map(self._download_video, new_videos)
        print("[+] done".title())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--username", help='Username or your email of your account', action="store",
                        required=True)
    parser.add_argument("-p", "--password", help='Password of your account', action="store", required=True)
    parser.add_argument("-f", "--filename", help='Filename for storing data', action="store", required=True)
    parser.add_argument("-n", "--name", help='Name to search', action="store", required=True)
    args = parser.parse_args()

    ipv = Instagram_pv(args.username, args.password, args.filename, args.name)
    ipv.control()
    ipv.login()
    ipv.downloading_video_images()
