from typing import Optional

import yaml
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from src.postgres_connector import PostgresConnector

app = FastAPI()

with open('config/postgres.yaml', 'r') as config_file:
	config = yaml.load(config_file, Loader=yaml.FullLoader)

ps_connector = PostgresConnector(config)
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')


class Query(BaseModel):
	text: str
	k: int = 5
	distance_metric: Optional[str] = 'euclidian'
	present_paper: Optional[bool] = False


@app.get("/")
async def root():
	return {"message": "Hello World"}


@app.post("/search")
async def search(query: Query):
	query_embedding = model.encode(sentences=[query.text])[0]
	papers = ps_connector.get_k_results(query_embedding, query.k)

	papers = {index: {'title': paper.title} for index, paper in enumerate(papers)}

	return papers
