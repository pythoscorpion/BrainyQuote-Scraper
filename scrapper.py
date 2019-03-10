import requests, json, re, sys
from bs4 import BeautifulSoup
from string import ascii_lowercase

Authors=[]

f = open("./accomplished.txt","w+")
accomplished = f.readlines()
f.close()

lenmax = 0
# use ascii_lowercase instead of 'x' for full scraping
for letter in 'x':
    
    page_counter = 1
    repeat = 0
    url = ""
    
    while True:
        if page_counter == 1:
            url = "https://www.brainyquote.com/authors/" + letter
        else:
            url = "https://www.brainyquote.com/authors/" + letter + str(page_counter)
        print(url)
        r = requests.get(url)
        #if url has been redirected
        if len(r.history) > 0:
            break
        links = re.findall("/authors/[\w]{4,}",r.text)
        for link in links:
            if not any(link in s for s in accomplished):
                if link not in Authors:
                    Authors.append(link)
                    if len(link) > lenmax:
                        lenmax = len(link)
        page_counter += 1

print("{} Authors remaining".format(len(Authors)))

def stdprint(stdout):
    sys.stdout.write("\r{0}".format(stdout))
    sys.stdout.flush()

counter = 0

for link in Authors:
    counter += 1
    stdout = ""
    
    try:
        quotes=[]
        referer = "https://www.brainyquote.com" + link
        percent = float(counter)/len(Authors)
        stdout = "{}{}{:d}%".format(referer,' '*(33+lenmax-len(referer)), int(round(percent*100)))
        
        headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
        r = requests.get(referer,headers=headers)
        VID = (re.findall("nVID=.{2}[\w]*",str(r.content))[0].split("\'"))[1]
        ID = (re.findall("G_DM_ID=.{1,3}[\d]*",str(r.content))[0].split("\""))[1]
        soup = BeautifulSoup(r.content,'html.parser')
        result = soup.find_all('a', {'class',re.compile("b-qt")})
        
        for x in result:
            quote = re.findall('>.{3,}',str(x))
            quote = quote[0][1:-4]
            quotes.append(link.replace("/authors/","")+"@@"+quote+'\n')
            
        url = "https://www.brainyquote.com/api/inf"
        headers = {
            "authority": "www.brainyquote.com",
            "method": "POST",
            "path": "/api/inf",
            "scheme": "https",
            "accept": "*/*",
            "accept-ancoding": "gzip,deflate,br",
            "accept-aanguage": "en-US,en;q=0.9,fa;q=0.8",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://www.brainyquote.com",
            "referer": referer,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            "x-requested-with": "XMLHttpRequest"
            }
        
        for pageNumber in range(2,100):
            payload = {"typ":"author","langc":"en","v":"8.4.1:2962932","ab":"b","pg":pageNumber,"id":ID,"vid":VID,"fdd":"d","m":0}
            r = requests.post(url, data=json.dumps(payload), headers=headers)
            if "{\"message\":\"Bad request, invalid page\"}" in r.content.decode('utf-8'):
                break
            soup = BeautifulSoup(r.content,'html.parser')
            result = soup.find_all('a', {'class',re.compile("b-qt")})
            if not (len(result) > 0):
                stdout = r.content.decode('utf-8') 
            for x in result:
                quote = re.findall('>.{3,}',str(x))
                quote = quote[0][1:-4]
                quotes.append(link.replace("/authors/","")+"@@"+quote+'\n')
                
        with open("./quotes.txt","a") as f:
            for q in quotes:
                f.write(q)
                
        if len(quotes) > 0:
            with open("./accomplished.txt","a") as f:
                f.write(link+'\n')
                
    except Exception as e:
        print(e)
        
    stdprint(stdout)
    
