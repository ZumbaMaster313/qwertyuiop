from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup as bs
from requests import get
import requests
import os 
import webbrowser
import shutil
import json 
import urllib3

webserver = Flask(__name__)

sep = '/'
final = ""
myString = ""
newString = ""
link = "./templates/result.html"


@webserver.route("/")
def home():
    return render_template("index.html"), 200

@webserver.route('/go', methods=['POST'])
def go():
    myString = request.form['ecid']

    try:
        try:
            r = requests.get(myString)
        except requests.ConnectionError:
            errorString = "Your supposed to input a valid url..."
            sHelp = "* couldn't render *"
            return render_template("error.html", error=errorString, help=sHelp), 200
        txt = r.text
        
        newTxt = txt.replace('%','')

        ar = myString.split(sep, 3)
        newAr = [ar[0], ar[1], ar[2]]
        newString = sep.join(newAr)

        writeHtml(newString, newTxt)
        
        return render_template("result.html"), 200

    except Exception:
        return render_template("error.html", error="Hey mate, your supposed to input a url...", help="* https://idiot.com *"), 200

@webserver.route('/go', defaults={'path': ''})
@webserver.route('/go/<path:path>')
def proxy(path):
    r = requests.get(path)
    txt = r.text
        
    newTxt = txt.replace('%','')

    ar = path.split(sep, 3)
    newAr = [ar[0], ar[1], ar[2]]
    newString = sep.join(newAr)

    writeHtml(newString, newTxt)

    return render_template("result.html"), 200


def writeHtml(nString, txt):
    final = txt.replace('"/', '"'+nString+'/')

    soup = bs(final, 'html.parser')

    url = soup.find_all('a')
    urlList = []
    for u in url:
        tmp = u.get('href')
        urlList.append(tmp)

    emptyList = list(filter(None, urlList))
    newList = list(set(emptyList))
        
    while True:
        try:
            newList.remove(nString+'/')
        except ValueError:
            break

    for i in newList:
        final = final.replace(i, 'go/'+i)
    
    n = 0
    replaceString = '"go/'
    while n <= 100:
        replaceString += 'go/'
        final = final.replace(replaceString, '"go/')
        n += 1
    

    s = final.encode('utf-8', 'ignore')
    with open(link, 'wb') as f:
        f.write(s)
        f.close

if (__name__ == "__main__"):
    webserver.run(debug=True, port=5055, host='0.0.0.0')
