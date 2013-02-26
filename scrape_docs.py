"""
Attempt to scrape the v1.1 API docs and check if our allowed_params match
"""
import cookielib
import pickle
import re
import time
import urlparse
import urllib2
from BeautifulSoup import BeautifulSoup as BS

from tweepy import api

def get_docs(start='https://dev.twitter.com/docs/api/1.1'):
    try:
        return pickle.load(open('docs.pck'))
    except Exception:
        pass

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
    f = opener.open(urllib2.Request(start), timeout=5)
    doc = BS(f.read())
    subpages = []
    for a in doc.findAll('a'):
        if a.text.startswith('GET'):
            href = urlparse.urljoin(start, a['href'])
            method = '/' + a.text[4:]
            subpages.append((method, href))
    print "fetching", len(subpages), "subpages"

    docs = [] # [(method, href, html), ...]

    for i, (method, href) in enumerate(subpages):
        print i, "getting", href
        html = opener.open(urllib2.Request(href), timeout=5).read()
        time.sleep(3)
        docs.append((method, href, html))

    pickle.dump(docs, open('docs.pck', 'w+'))
    return docs

def main():
    docs = get_docs()

    api_methods = set()
    matched = set()
    for method, href, html in docs:
        for name, value in api.__class__.__dict__.items():
            try:
                ob = value.introspect
            except AttributeError:
                continue
            api_methods.add(ob.path)
            if ob.path.startswith(method):
                matched.add(ob.path)
                old = sorted(ob.allowed_param)
                new = sorted(params_from_html(html))
                if old != new:
                    print "Mismatch", ob.path
                    print "\texisting:", old
                    print "\tdocument:", new
                break
    print "examined %d methods" % (len(api_methods))
    print "these never matched an api call", sorted(api_methods - matched)

def params_from_html(html):
    doc = BS(html)
    # <span class="param">since_id <span>optional</span></span>
    params = []
    for span in doc.findAll("span", {'class': "param"}):
        params.append(str(re.sub('(required|(semi-)?optional)$', '', span.text)))
    return params

if __name__ == '__main__':
    main()
