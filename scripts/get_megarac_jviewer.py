import pathlib
import re
import requests

SERVER = ""
USERNAME = "admin"
PASSWORD = "admin"

SESSION = requests.session()


def login():
    resp = SESSION.post(f"http://{SERVER}/rpc/WEBSES/create.asp", headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62",
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Origin": f"http://{SERVER}",
        "Referer": f"http://{SERVER}/page/login.html",
        "Accept-Encoding": "gzip, deflate"
    }, data=f"WEBVAR_USERNAME={USERNAME}&WEBVAR_PASSWORD={PASSWORD}")
    cookie = re.findall(" { 'SESSION_COOKIE' : '(.+?)' }", resp.text)[0]
    print(cookie)
    SESSION.cookies.set("SessionCookie", cookie)


def get_jviewer_jnlp():
    resp = SESSION.get(f"http://{SERVER}/Java/jviewer.jnlp?EXTRNIP={SERVER}&JNLPSTR=JViewer")
    jnlp_text = resp.text
    jnlp_text = jnlp_text.replace("https", "http")
    print(jnlp_text)
    return jnlp_text


if __name__ == '__main__':
    login()
    pathlib.Path("./jviewer.jnlp").write_text(get_jviewer_jnlp())
