from shibboleth.shibboleth import Shibboleth
from shibboleth.credentials import Idp, CredentialManager
from http.cookiejar import MozillaCookieJar
import logging

def login():
    start_url = 'https://www.moodle.tum.de/Shibboleth.sso/Login?providerId=https%3A%2F%2Ftumidp.lrz.de%2Fidp%2Fshibboleth&target=https%3A%2F%2Fwww.moodle.tum.de%2Fauth%2Fshibboleth%2Findex.php'

    c = CredentialManager()
    idp = Idp()
    jar = MozillaCookieJar()
    logging.basicConfig(level=logging.DEBUG)
    shib = Shibboleth(idp, c, jar)
    shib.openurl('https://www.moodle.tum.de')
    shib.initurl(start_url)
    return shib
