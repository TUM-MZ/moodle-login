import argparse
import json
import logging
import re
from http.cookiejar import MozillaCookieJar

import sys

from shibboleth.credentials import Idp, SimpleCredentialManager
from shibboleth.shibboleth import Shibboleth


def read_login_data():
    try:
        cfg = json.load(open('./login_data.json'))
    except IOError:
        print('Please create `login_data.json` with the following format:')
        print('''{
    "login": "<your-lrz-login>",
    "password": "<your-lrz-password"
}''')
        sys.exit(1)
    else:
        return cfg['login'], cfg['password']


def login():
    start_url = 'https://www.moodle.tum.de/Shibboleth.sso/Login?providerId=https%3A%2F%2Ftumidp.lrz.de%2Fidp%2Fshibboleth&target=https%3A%2F%2Fwww.moodle.tum.de%2Fauth%2Fshibboleth%2Findex.php'

    login, password = read_login_data()
    c = SimpleCredentialManager(login, password)
    idp = Idp()
    jar = MozillaCookieJar()
    logging.basicConfig(level=logging.INFO)
    shib = Shibboleth(idp, c, jar)
    shib.readurl('https://www.moodle.tum.de')
    shib.initurl(start_url)
    return shib


def get_quiz_answers(shib, quiz_url):
    quiz_id_match = re.findall(r'https://www.moodle.tum.de/mod/quiz/view.php\?id=(\d+)', quiz_url)
    if not quiz_id_match:
        raise RuntimeError('Invalid quiz url')
    quiz_id = quiz_id_match[0]

    quiz_report_url = 'https://www.moodle.tum.de/mod/quiz/report.php?id={quiz_id}&mode=responses'.format(
        quiz_id=quiz_id)
    csv_url_pattern = ('https://www.moodle.tum.de/mod/quiz/report.php?sesskey={sesskey}&'
                       'download=csv&id={quiz_id}&mode=responses&attempts=enrolled_with&'
                       'onlygraded=&qtext=&resp=1&right=')

    report_page = shib.readurl(quiz_report_url)
    cfg = json.loads(re.findall(r'M\.cfg = (\{.*?\});', report_page)[0])
    sesskey = cfg['sesskey']
    csv = shib.readurl(csv_url_pattern.format(sesskey=sesskey, quiz_id=quiz_id))
    return csv


def main():
    parser = argparse.ArgumentParser(description='Download moodle quiz results')
    parser.add_argument('url', type=str, help='Moodle Quiz URL')
    args = parser.parse_args()
    quiz_url = args.url
    print(get_quiz_answers(login(), quiz_url))


if __name__ == "__main__":
    main()
