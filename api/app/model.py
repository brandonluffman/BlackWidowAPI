from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json 
import spacy
import requests
from bs4 import BeautifulSoup
import re
import datetime
import requests
from requests_html import HTMLSession
from youtube_transcript_api import YouTubeTranscriptApi
import praw
from praw.models import MoreComments
from tld import get_tld
import time
from collections import Counter
from pydantic import BaseModel

app = FastAPI()
nlp = spacy.load('./output/model-last')
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Input(BaseModel):
    sentence: str


@app.get("/")
def home():
    return "hello world"

@app.post('/model')
async def model(sentence_input: Input):
    doc = nlp(sentence_input.sentence)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    # return entities
    items = [x.text for x in doc.ents]
    # Counter(items).most_common(10)
    # docs = []
    # docs.append(doc)
    return items






    # model_text = " ".join(final_text)

    # json_object = json.dumps(model_text)
    # print(json_object)
    
    # # url = "http://127.0.0.1:8000/model"
        
    # # # Send the POST request with the item data
    # # response = requests.post(url, json={"sentence": json_object})

    # # # Check if the request was successful
    # # if response.status_code != 200:
    # #     raise HTTPException(status_code=response.status_code, detail=response.json()["detail"])

    # # # Return the response body
    # # return response.json() 




### ----------------------------------------------- ###

#  # def get_product_names(self,response,text):
#     # nlp = spacy.load('./output/model-best')
#     # doc = nlp(text)
#     # items = [x.text for x in doc.ents]
#     # Counter(items).most_common(10)
#     # docs.append(doc)
#     # return docs


