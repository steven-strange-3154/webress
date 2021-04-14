"""Simple image extractor from web pages"""

__name__ = "images"
__author__ = "Steven Strange"
__email__ = "stevenstrange31545nk74@gmail.com"
__version__ = "1.0"
__status__ = "Testing"

from urllib.request import Request, URLError, HTTPError, urlopen
from bs4 import BeautifulSoup as BS
import os, re
#import PIL.Image
#import io, imageio

def is_bw(data):
    """Checks if the image is in grayscale mode"""
    dat = io.BytesIO(data)
    dat = PIL.Image.open(data).convert('RGB')
    width, height = dat.size
    for i in range(width):
        for j in range(height):
            R, G, B = dat.getpixel((i, j))
            if R != G != B: return False
    return True

def file_name(url, data=None):
    """Returns file name from url"""
    index = url.rfind('/')
    name, ext = None, None
    if index == -1: name = url
    else: name = url[index+1:]
    #index = name.rfind('.')
    #if index == -1: ext = name
    #else: ext = name[index+1:]
    #if not ext or ext == name: ext = data.format.lower()
    return (name, ext)

#def verify(link, con):
    #"""Verification function (Disabled)"""
    #image_name, image_data = None, None
    #try:
        #req = Request(link['link'], None, con.user_agent)
        #image_data = urlopen(req)
    #except (URLError, HTTPError) as e: return False
    #else:
        #image_data = image_data.read()
        #if con.image_min_size and (len(image_data) < con.image_min_size): return False
        #if con.image_max_size and (len(image_data) > con.image_max_size): return False

        #image_data = imageio.imread(image_data)
        #image_data = io.BytesIO(image_data.tobytes())
        #try:
            #image_data = PIL.Image.open(image_data)
            #image_name = file_name(link['link'], image_data)

            #if con.image_types and (image_name[1] not in con.fetcher.image_types): return False
            #if con.image_min_width and (image_data.size[0] < con.image_mim_width): return False
            #if con.image_max_width and (image_data.size[0] > con.image_max_width): return False
            #if con.image_min_height and (image_data.size[1] < con.image_min_height): return False
            #if con.image_max_height and (image_data.size[1] > con.image_max_height): return False
            #if not (con.image_color and is_bw(image_data)): return False
            #return {'name': image_name[0], 'ext': image_name[1], 'link': link['link'], 'alt': link['alt']}
        #except Exception: return False

class Fetcher(object):
    """Holds important image properties"""
    def __init__(self):
        self.user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'}
        self.image_types = []
        self.image_min_size = None
        self.image_min_height = None
        self.image_min_width = None
        self.image_max_size = None
        self.image_max_height = None
        self.image_max_width = None
        self.image_color = True

class Links(object):
    """An object containing all collected links of images"""
    def __init__(self, res_location):
        """Object constructor"""
        self.res_loc = res_location
        self.data = None
        self.fetcher = Fetcher()
        #self.verify_object = False
        self.all_links = []

    def read_data(self):
        """Loads data from a local webpage document file or url"""
        ptn_weblink = re.compile('^(https?://)?\w+(\.\w+)+/?')
        if ptn_weblink.match(self.res_loc):
            try:
                req = Request(self.res_loc, None, self.fetcher.user_agent)
                loaded = urlopen(req)
            except (URLError, HTTPError) as e:
                err = e
                self.all_links.append(lambda: ("error happened while opening resource", self.res_loc, err))
            else: self.data = loaded.read().decode('utf-8')
        else:
            try: fp = open(self.res_loc, 'r')
            except Exception as e:
                err = e
                self.all_links.append(lambda: ("error happened while opening resource", self.res_loc, err))
            else: self.data = fp.read().decode('utf-8')

    def extract(self):
        """Extracts image links from loaded data"""
        ptn_weblink = re.compile('^(https?://)?\w+(\.\w+)+/?') # web link validator
        img_tags = BS(self.data, 'html.parser').findAll('img') # parsing document
        images, links = [], [] # containers

        for tag in img_tags:
            img = {}
            if tag['alt'].strip(): img.update({'alt': tag['alt'].strip()}) # alt text of image
            if tag['src'].strip(): img.update({'src': tag['src'].strip()}) # url of image
            if img: images.append(img)

        for image in images:
            # image link generator
            link = ptn_weblink.match(image['src'])
            if link: link = image['src']
            else:
                base = self.res_loc.split('/')
                base = base[0] + '//' + base[2]
                if image['src'].startswith('/'): image['src'] = image['src'][1:]
                link = '/'.join([base, image['src']]) 
            link = {'link': link}
            if image['alt']: link.update({'alt': image['alt']})
            links.append(link)

        #if self.fetcher.image_max_count:
           #if self.fetcher.image_max_count < len(links): links = links[:self.image_max_count]

        for link in links:
            #if self.verify_object:
                #image = verify(link, self.fetcher)
                #if image: self.all_links.append(image)
            #else: self.all_links.append(link)
            self.all_links.append(link)

    # verification disabled by default for a bug
    def enable_verification(self): self.verify_object = True # enables verification
    def disable_verification(self): self.verify_object = False # disables verification

    def get(self):
        """Loads a web page and extracts image link from loaded page source and returns as a list (returns a callable error function in case of failure)"""
        if not self.all_links:
            self.read_data() # load data
            self.extract() # extract links
        if type(self.all_links).__name__ == 'function': return self.all_links[0]
        else:
            links = [x['link'] for x in self.all_links] # extract pure links
            return links

    def save(self, path):
        """Saves all images to path in a folder as domain name"""
        if not self.all_links: self.get()

        base = self.res_loc.split('/')[2]
        try: os.mkdir(f"{path}{base}")
        except FileExistsError: pass

        for link in self.all_links:
            wlink = file_name(link['link'])
            try:
                req = Request(link['link'], None, self.fetcher.user_agent)
                loaded = urlopen(req)
            except (URLError, HTTPError) as e: continue
            else:
                loaded = loaded.read()
                with open(f"{path}{base}/{wlink[0]}", 'wb') as f:
                    f.write(loaded)
                    f.close()
        