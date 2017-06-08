# The class to login and get information as well as pictures
import os, re, time, requests
import cookielib
import urllib2
import pixiv_urls
import Queue
import json
from bs4 import BeautifulSoup

class Pixiv:
    def __init__(self, cookie_path = './cookie.txt'):
        while not os.path.exists(cookie_path):
            cookie_path = raw_input("Enter cookie path")
        self.request_count = 0
        cookie_jar = cookielib.MozillaCookieJar()
        cookies = open(cookie_path).read()
        for cookie in json.loads(cookies):
            cookie_jar.set_cookie(
                cookielib.Cookie(
                    version=0, name=cookie['name'],
                    value=cookie['value'], port=None,
                    port_specified=False, domain=cookie['domain'],
                    domain_specified=False, domain_initial_dot=False,
                    path=cookie['path'], path_specified=True,
                    secure=cookie['secure'], expires=None,
                    discard=True, comment=None, comment_url=None,
                    rest={'HttpOnly': None}, rfc2109=False
                )
            )
        self.cookies = cookie_jar
        self.artist_hash = {}
        self.page = 1
        self.headers = ({
            'Referer': 'http://www.pixiv.net/',
            'User-Agent': pixiv_urls.User_Agent
        })
        self.user_ids = []
        self.curr_user = None

    def friendly_wait(self, request_limit=20):
        self.request_count += 1
        if self.request_count > request_limit:
            time.sleep(30) # sleep 30s
            self.request_count = 0

    def get_user_ids(self, page = 1):
        url = pixiv_urls.Daily_Url
        res = requests.get(url=url + '&p=' + str(page), cookies=self.cookies, headers=self.headers)
        self.friendly_wait()

        # get user ids from the page
        content = res.text.encode('utf-8')
        pattern = re.compile('(?<=member.php\?id=)\d*(?=&)')
        user_ids = re.findall(pattern, content)
        self.user_ids.extend(user_ids)

    def find_next_artist(self):
        found = False
        limit = 100
        count = 0
        self.curr_user = None
        while not found and count < limit:
            while len(self.user_ids) == 0 and count < limit:
                self.get_user_ids()
                count += 1
            self.curr_user = {}
            self.curr_user["id"] = self.user_ids[0]
            self.curr_user["follower_page"] = 1
            self.curr_user["follower_ids"] = []
            self.user_ids = self.user_ids[1: ]
            found = True
        if self.curr_user is not None:
            # find an artist
            print 'Getting the information of user: ' + str(self.curr_user["id"])
        return self.user_ids

    def get_followed(self):
        # try to get the users that followed by curr user
        if self.curr_user is None:
            return
        while True:
            url = pixiv_urls.Follower_List_Url
            print url + str(self.curr_user["id"]) + "&p=" + str(self.curr_user["follower_page"])
            res = requests.get(url=url + str(self.curr_user["id"]) + "&p=" + str(self.curr_user["follower_page"]),\
                               cookies=self.cookies, headers=self.headers)
            self.friendly_wait()
            self.curr_user["follower_page"] += 1

            # get followers list
            content = res.text.encode('utf-8')
            soup = BeautifulSoup(content, 'lxml')
            question = soup.find_all('div', {'class': 'members'})
            pattern = re.compile('(?<=member.php\?id=)\d*(?=\")')
            followers = re.findall(pattern, str(question))
            for follower in followers:
                if follower != self.curr_user["id"] and follower not in self.curr_user["follower_ids"]:
                    self.curr_user["follower_ids"].append(follower)
                    print follower
            print self.curr_user["follower_ids"]


    def get_favours(self):
        # try to get the users that
        pass

    def get_commentators(self):
        pass

    def collect_images(self, id):
        page = 1
        if type(id) != str:
            id = str(id)
        self._save_path = './' + id
        url = pixiv_urls.get_gallery_url(id, page)
        res = requests.get(url=url, cookies=self.cookies, headers=self.headers)
        # find name
        content = res.text.encode('utf-8')
        soup = BeautifulSoup(content, 'lxml')
        username = soup.find_all('h1', {'class': 'user'})[0]
        print unicode('Collecting User: ') + unicode(username.string)
        self._save_path = unicode(self._save_path + '_') + unicode(username.string)
        if not os.path.exists(self._save_path):
            os.mkdir(self._save_path)
        else:
            return

        while True:
            url = pixiv_urls.get_gallery_url(id, page)
            res = requests.get(url=url, cookies=self.cookies, headers=self.headers)
            # find images
            content = res.text.encode('utf-8')
            soup = BeautifulSoup(content, 'lxml')
            image_items = soup.find_all('li', {'class': 'image-item'})
            if len(image_items) == 0:
                break
            
            # download images
            pattern = re.compile('href="\S*"')
            for image_item in image_items:
                urls = re.findall(pattern, str(image_item))
                if len(urls) > 0:
                    url = urls[0][6: -1]
                    self.download_image(pixiv_urls.Pixiv + url)
                    self.friendly_wait()
            print page, ' ', res.status_code
            self.friendly_wait()
            page += 1

    def download_image(self, url):
        res = requests.get(url=url, cookies=self.cookies, headers=self.headers)
        content = res.text.encode('utf-8')
        soup = BeautifulSoup(content, 'lxml')
        origin = soup.find_all('img', {'class': 'original-image'})

        if len(origin) == 0:
            print 'It might be a manga. Will not download ' + url[55:]
            return
        pattern = re.compile('data-src="\S*"')
        urls = re.findall(pattern, str(origin))
        if len(urls) == 0:
            print 'Fail to find image url ' + url[55:]
            return
        url = urls[0][10: -1]
        file_name = str(url).split('/')[-1]
        print file_name
        if not os.path.exists(self._save_path):
            os.mkdir(self._save_path)
        self.save_image(os.path.join(self._save_path, file_name), url)
        
    def get_file(self, url):  
        try:  
            cj=cookielib.LWPCookieJar()  
            opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))  
            urllib2.install_opener(opener)  
              
            req=urllib2.Request(url, headers=self.headers)  
            operate=opener.open(req)  
            data=operate.read()  
            return data  
        except BaseException, e:  
            print e  
            return None  

    def save_file(self, file_name, data):  
        if data == None:  
            return  
           
        file=open(file_name, "wb")  
        file.write(data)  
        file.flush()  
        file.close()  

    def save_image(self, filename, url):  
        self.save_file(filename, self.get_file(url))

if __name__ == "__main__":
    pixiv = Pixiv()
    # pixiv.collect_images(660788)
    # pixiv.collect_images(2309638)
    ids = pixiv.find_next_artist()
    for id in ids:
        pixiv.collect_images(id)
        

