#! /usr/bin/env python3
# -*- coding:utf-8 -*-
"""
A tool to collect subdomains using the Bing search engine.
'Created on Tues June 5 17:31:12 2023'
__author__ = 'Af10wer'
"""

import sys,time,random,argparse,textwrap
import http.cookiejar
from tqdm import tqdm
from urllib import request,parse,error
from bs4 import BeautifulSoup


def load_cookie(req,cookie_filename):
        cookie = http.cookiejar.MozillaCookieJar()
        cookie.load(cookie_filename)
        cookieStr = ''
        for item in cookie:
                cookieStr = cookieStr + item.name + '=' + item.value + ';'
        return cookieStr

def save_cookie(req,cookie_filename):
        cookie = http.cookiejar.MozillaCookieJar(cookie_filename)
        opener = request.build_opener(request.HTTPCookieProcessor(cookie))
        response = opener.open(req)
        cookie.save()

def subdomain_collect_by_bing(domain,pages,file_path):
        subdomain = []
        cookie_filename = 'cookies.txt'
        headers={
                'User-Agent':'Mozilla/5.4 (Windows NT 11.0; Win64; x64) AppleWebKit/538.29 (KHTML, like Gecko) Chrome/100.1.2.3 Safari/526.33',
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Referer':'https://cn.bing.com/',
        }

        for page in tqdm(range(0,pages)):
                url = "https://cn.bing.com/search?"+parse.urlencode({'q':domain,'search':'','first':str(page*10+1),'FORM':'PERE','ensearch':'1'})
                #print(url)
                req = request.Request(url=url,headers=headers)
                save_cookie(req,cookie_filename)
                if 'Cookie' not in req.headers.keys():
                        req.add_header('Cookie',load_cookie(req,cookie_filename))

                response = request.urlopen(req)
                soup = BeautifulSoup(response.read(),'lxml')
                tags = soup.select('h2 > a[href]')
                for tag in tags:
                        tag_url = tag.get('href')
                        collect_domain = parse.urlparse(tag_url).netloc
                        complete_domain = parse.urlparse(tag_url).scheme + "://" + collect_domain
                        if (complete_domain in subdomain) or (domain not in collect_domain):
                                pass
                        else:
                                subdomain.append(complete_domain)
                time.sleep(random.randint(1,2))
        if file_path:
                with open(file_path,'a') as f:
                        for i in range(len(subdomain)):
                                f.write(subdomain[i]+'\n')
        else:
                for i in range(len(subdomain)):
                        print(subdomain[i])

if __name__ == '__main__':
        parser = argparse.ArgumentParser(
                description = 'Subdomain collection',
                formatter_class = argparse.RawDescriptionHelpFormatter,
                epilog = textwrap.dedent('''Example:
            subdomain_collect_bing.py baidu.com [-p 20] [-f result.txt]
            ''')
        )
        parser.add_argument('domain',help='Type the domain.')
        parser.add_argument('-p','--pages',type=int,default=20,help='Specifies the number of pages to crawl.')
        parser.add_argument('-f','--filepath',help='Specify the local file stored in the collected subdomains.')
        args = parser.parse_args()
        try:
                subdomain_collect_by_bing(args.domain,args.pages,args.filepath)
        except error.URLError as e:
                print('An error occurred：',e.reason)
