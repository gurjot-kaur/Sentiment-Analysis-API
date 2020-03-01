
from metaflow import FlowSpec, step, retry, catch, batch, IncludeFile, Parameter, conda, conda_base,S3
import boto3
import csv

def get_python_version():

    import platform
    versions = {'3' : '3.7.4'}
    return versions[platform.python_version_tuple()[0]]


@conda_base(python=get_python_version())
class SentimentAnalysis(FlowSpec):

    edgar_data = IncludeFile("data", default = 'testlist.csv')

    @conda(libraries={'pandas' : '1.0.1'})
    @step
    def start(self):
        import pandas
        from io import StringIO

        # Load the data set into a pandas dataframe.
        self.dataframe = pandas.read_csv(StringIO(self.edgar_data))

        self.links = list(self.dataframe['link'])
        self.next(self.scrapping)

    @conda(libraries={'pandas' : '1.0.1', 're':'4.4.0', 'pathlib':'1.0.1','random':'2.2.1','urllib.parse':'','bs4':'4.8.2','furl':'2.1.0','selenium':'3.141.1'})
    @step
    def scrapping(self):
        import re
        from pathlib import Path
        import urllib.request
        import boto3
        from metaflow import S3
        from urllib.parse import urljoin
        import pandas as pd
        from bs4 import BeautifulSoup
        from furl import furl
        from selenium import webdriver

        soup = BeautifulSoup(html, 'lxml')
        meta, participants, content = {}, [], []
        h1 = soup.find('h1', itemprop='headline')
        if h1 is None:
            return
        h1 = h1.text
        meta['company'] = h1[:h1.find('(')].strip()
        meta['symbol'] = h1[h1.find('(') + 1:h1.find(')')]
        match = quarter_pattern.search(title)
        if match:
            meta['quarter'] = match.group(0)



        SA_URL = 'https://seekingalpha.com/'
        TRANSCRIPT = re.compile('Earnings Call Transcript')

        next_page = True
        page = 1
        driver = webdriver.Firefox()
        while next_page:
            print(f'Page: {page}')
            url = f'{SA_URL}/earnings/earnings-call-transcripts/{page}'
            driver.get(urljoin(SA_URL, url))
            response = driver.page_source

            soup = BeautifulSoup(response, 'lxml')
            links = soup.find_all(name='a', string=TRANSCRIPT)
            if len(links) == 0:
                next_page = False
            else:
                for link in links:
                    transcript_url = link.attrs.get('href')
                    article_url = furl(urljoin(SA_URL, transcript_url)).add({'part': 'single'})
                    driver.get(article_url.url)
                    html = driver.page_source
                    result = parse_html(html)
                    if result is not None:
                        meta, participants, content = result
                        meta['link'] = link
                        store_result(meta, participants, content)
                    sleep(5 + (random() - .5) * 2)
        driver.close()
        for x in participants:
            f = open("testdata.txt","a")
            f.write(str_response)
            f.close()

        with S3(s3root='s3://outputbucket1221/') as s3:
            s3.put_files([('testdata','testdata.txt')])



        self.next(self.predicting)

    @conda(libraries={'pandas' : '1.0.1','nltk': '3.4.5','smart_open':'1.9.0'})
    @step
    def predicting(self):
        import boto3
        from metaflow import S3
        import re
        import pandas as pd
        from nltk import tokenize
        import string
        import nltk
        from nltk.corpus import stopwords
        from smart_open import smart_open
        import requests

        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('words')

        listed = []
        with smart_open('s3://inputbucket1221/testdata.txt', 'r') as s3_source:
            Line = s3_source.readline()

            while Line!='':
                Line1 = Line.split(".")
                for Sentence in Line1:
                    listed.append(Sentence)
                Line = s3_source.readline()

        L=[]
        for x in listed:
            if len(x) > 5:
                L.append(x)


        df = pd.DataFrame()

        df['Text'] = L
        print(df['Text'])

        def remove_punct(text):
            text  = "".join([char for char in text if char not in string.punctuation])
            text = re.sub('[0-9]+', '', text)
            return text

        df['Textclean'] = df['Text'].apply(lambda x: remove_punct(x))
        df = df.dropna()


        url = 'http://localhost:5000/model/predict'
        #myobj = {"The Model Asset Exchange is a crucial element of a developer's toolkit."}
        #data = {'text':['We did it!']}

        #x = requests.post(url, json = data)

        #print(x.text)
        senti_list = []
        for x in df['Textclean']:
            data = {'text':[x]}
            res = (requests.post(url, json = data)).text.split()
            if float(res[4][:-1]) > float(res[6][:-3]):
                temp = (x,"Positive")
                senti_list.append(temp)
            elif float(res[4][:-1]) < float(res[6][:-3]):
                temp = (x,"Negative")
                senti_list.append(temp)
            else:
                temp = (x,"Neutral")
                senti_list.append(temp)
        sentiment = pd.DataFrame(senti_list,columns = ['Sentence', 'Sentiment'])

        #sentiment.to_csv('sample.csv',index=False)


        sentiment.to_csv('final_sentiment.csv',index=False)

        with S3(s3root='s3://outputbucket1221/') as s3:
            s3.put_files([('final_sentiment.csv','final_sentiment.csv')])




        self.next(self.end)

    @step
    def end(self):
        """
        End the flow.
        """
        pass

if __name__ == '__main__':
    SentimentAnalysis()
