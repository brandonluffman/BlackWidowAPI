from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json 
# import spacy
import requests
from bs4 import BeautifulSoup
import re
import datetime
import requests
from requests_html import HTMLSession


app = FastAPI()
# nlp = spacy.load("en_core_web_sm")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return "hello world"

# @app.get("/quotes")
# def get_quotes(query:str):
#     return "hello world"























### ----------------------------------------------- ###



# @app.post("/analyze_text")
# async def analyze_text(request: Request):
#     data = await request.json()
#     # text = data.get("text")
#     # doc = nlp(data)
#     # result = {"entities": []}
#     # for ent in doc.ents:
#     #     result["entities"].append({
#     #         "text": ent.text,
#     #         "label": ent.label_
#     #     })
#     return data

#  # def get_product_names(self,response,text):
#     # nlp = spacy.load('./output/model-best')
#     # doc = nlp(text)
#     # items = [x.text for x in doc.ents]
#     # Counter(items).most_common(10)
#     # docs.append(doc)
#     # return 