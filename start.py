# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template

from collections import OrderedDict
import datetime
import gevent
from gevent import monkey, Timeout
import json
import urllib.request

monkey.patch_all()

user_token = '6988be7b0f62a2dbd97c71cd59a5406ecd02c431'
user_password = 'x-oauth-basic'

app = Flask(__name__)
app.debug = True

url_list_commits = 'https://api.github.com/repositories/596892/commits?page={0}'
urls = list()
result = dict()


def download(url):
    req = urllib.request
    auth_handler = req.HTTPBasicAuthHandler()
    auth_handler.add_password(
        realm=None,
        uri='https://api.github.com/',
        user=user_token,
        passwd=user_password
        )
    opener = req.build_opener(auth_handler)
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    req.install_opener(opener)
    try:
        response = req.urlopen(url)
        gevent.sleep(0)
        response_code = (response.getcode())
        data = json.loads(response.read().decode('utf8'))
    except urllib.error.HTTPError as ex:
        response_code, data = ex.code, None

    result[url] = [response_code, data]


@app.route('/')
def get_commits():
    print('Start - {0}'.format(datetime.datetime.now()))
    timeout = Timeout(10)
    timeout.start()
    try:
        job_stack = [gevent.spawn(download(url)) for url in urls]
        gevent.joinall(job_stack)
    except Timeout:
        pass
    finally:
        timeout.cancel()
    cntx = OrderedDict(sorted(result.items()))
    return render_template('start.html', cntx=cntx)
    print('End - {0}'.format(datetime.datetime.now()))


if __name__ == '__main__':

    for i in range(1, 70):
        urls.append(url_list_commits.format(i))
        result[url_list_commits.format(i)] = ['dont get', 'emtpy']
    app.run(debug=True)
