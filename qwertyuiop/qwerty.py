#!/usr/bin/python3.6

from flask import Flask, render_template, request, jsonify
from html5print import CSSBeautifier, HTMLBeautifier, JSBeautifier
from bs4 import BeautifulSoup as bs
from requests import get
import requests
import errno
import jsbeautifier
import os 
import webbrowser
import time
import shutil
import json 
import urllib3
import glob

webserver = Flask(__name__)

sep = '/'
myString = ""
newString = ""
link = "./templates/result.html"
test = "./templates/test.html"
domain = "https://qwertyuiop.space/"

#Returns homepage
@webserver.route("/")
def home():
    return render_template("index.html"), 200

#After link is entered, this function requests the html
@webserver.route('/get', methods=['POST'])
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

#Requests new html from links within parent html
@webserver.route('/route', defaults={'path': ''})
@webserver.route('/route/<path:path>')
def proxy(path):
    try:
        r = requests.get(path)
        txt = r.text
        
        newTxt = txt.replace('%','')

        ar = path.split(sep, 3)
        newAr = [ar[0], ar[1], ar[2]]
        newString = sep.join(newAr)

        writeHtml(newString, newTxt)

        return render_template("result.html"), 200
    except Exception:
        return render_template("error.html", error="Sorry, but uhh this server cannot render that...", help="* :( *"), 200

#Gets either js, css, or routing links
def links(method, mType, arg, location, soup):
    List = []
    link = soup.find_all(method, {mType : arg})
    for l in link:
        tmp = l.get(location)
        List.append(tmp)
    
    emptyList = list(filter(None, List))
    newList = list(set(emptyList))
    
    return newList

def recycle(path, finalHtml):
    n = 0
    parentString = '"' + domain + path + '/'
    childString = domain + path + '/'

    replaceString = parentString
    while n <= 100:
        replaceString += childString
        finalHtml = finalHtml.replace(replaceString, parentString)
        n += 1
    
    finalHtml = finalHtml.replace(parentString + childString, parentString)
    return finalHtml

#Requests css links and inputs it into local files for the HTML to render
def inputCSS(List, urlPath, html):
    html = delNameTags(html, 'link', "rel", "stylesheet")
    try:
        for l in List:

            r = requests.get(l)
            txt = r.text

            try:
                final = CSSBeautifier.beautify(txt, 4)
            except:
                final = txt

            pathAr = l.split("/")
            cssName = pathAr[-1] 

            sep = '.css'
            if ".css" not in cssName:
                cssFinal = cssName + ".css"
            else: 
                temp = cssName.split(sep, 1)[0]
                cssFinal = temp + ".css"
    
            cssPath = "./static/stylesheets/" + cssFinal
            open(cssPath, 'a').close
            try:
                s = final.encode('utf-8', 'ignore')
            except:
                s = final
            with open(cssPath, 'wb') as f:
                f.write(s)
                f.close

            html = html.replace(l, "." + cssPath)
    except:
        pass 
    
    return html
    
#Requests js links and inputs it into local files for the HTML to render
def inputJS(List, urlPath, html):
    html = delNameTags(html, 'script', "", "")
    try:
        for l in List:
            r = requests.get(l)
            txt = r.text

            try:
                final = JSBeautifier.beautify(txt, 4)
            except:
                final = txt
        
            try:
                final = jsbeautifier.beautify(final)
            except:
                pass

            pathAr = l.split("/")
            jsName = pathAr[-1] 

            sep = '.js'
            if ".js" not in jsName:
                jsFinal = jsName + ".js"
            else: 
                temp = jsName.split(sep, 1)[0]
                jsFinal = temp + ".js"
    
            jsPath = "./static/javascript/" + jsFinal
            open(jsPath, 'a').close
            try:
                s = final.encode('utf-8', 'ignore')
            except:
                s = final
            with open(jsPath, 'wb') as f:
                f.write(s)
                f.close

            html = html.replace(l, "." + jsPath)
    except: 
        pass
        
    return html

def delNameTags(html, tag, contentName, arg):
    soup = bs(html, 'html.parser')
    for link in soup.findAll(tag, {contentName : arg}):
        try:
            link['name'] = ""
        except:
            pass
    html = str(soup)
    return html
#Puts the servers domain name in front of the reqested website's URL
def inputURL(html, List, url):
    while True:
        try:
            List.remove(url+'/')
        except ValueError:
            break

    for i in List:
        html = html.replace(i, domain+'route/'+i)
    
    html = recycle("route", html)
    return html
#After every request, the server deletes the js and css folders from the last website
def deleteFiles(folderPath):
    for f in os.listdir(folderPath):
        filePath = os.path.join(folderPath, f)
        try:
            os.remove(filePath)
        except:
            pass

#This method is just a slave and calls all other methods ⚙️
def writeHtml(nString, txt):
    
    deleteFiles('./static/stylesheets/')
    deleteFiles('./static/javascript')

    txt = txt.replace('"//', '"https://')
    txt = txt.replace("'/", "'"+nString+'/')
    html = txt.replace('"/', '"'+nString+'/')

    soup = bs(html, 'html.parser')

    urlList = links('a', "rel", "", 'href', soup)
    jsList = links('script', "", "", 'src', soup)
    cssList = links('link', "rel", "stylesheet", 'href', soup)

    html = inputURL(html, urlList, nString)
    inputHtml = inputJS(jsList, "js", html)
    finalHtml = inputCSS(cssList, "css", inputHtml)

    try:
        finalHtml = HTMLBeautifier.beautify(finalHtml, 4)
    except:
        pass

    s = finalHtml.encode('utf-8', 'ignore')
    with open(link, 'wb') as f:
        f.write(s)
        f.close

if (__name__ == "__main__"):
    webserver.run(debug=True, host='0.0.0.0')
