# SKKUCHAT

## Environment
rank_bm25, jsonschema, langchain, langchain-openai

## How to use
First get api key and put in .env file

Second download stopwords-ko.txt and put in root directory

Then run 
```
python run.py -mode=prepare
```
Then run
```
python run.py -mode=eval -model=bm25
```
