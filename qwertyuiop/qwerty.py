from flask import Flask, render_template, request, jsonify
from seleniumwire import webdriver
from requests import get
import requests
import os 
import webbrowser
import shutil
import json 

webserver = Flask(__name__)

@webserver.route("/")
def home():
    return render_template("index.html"), 200

@webserver.route('/go', methods=['POST'])
def go():
    myString = request.form['ecid']
    path = "C:/Users/iseba/Desktop/qwertyuiop/templates/result.html"
    
    try: 
        if "https://" in myString:
            try:
                r = requests.get(myString)
            except requests.ConnectionError:
                return render_template("error.html", error="Your supposed to input a valid url...", help="* couldn't render *"), 200
            txt = r.text
        
            newTxt = txt.replace('%','')
            final = newTxt.replace('"/', '"'+myString+'/')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(final)
                f.close
        
            return render_template("result.html"), 200

        else:
            newString = "https://"+myString
            return requests.get(newString).content, 200
    except Exception:
        return render_template("error.html", error="Hey mate, your supposed to input a url...", help="* https://idiot.com *"), 200
    
if (__name__ == "__main__"):
    webserver.run(debug=True, port=5055, host='0.0.0.0')