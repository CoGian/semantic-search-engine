from typing import Optional
from scipy.spatial import distance
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
	k: int = 10
	distance_metric: Optional[str] = 'cosine'
	present_paper: Optional[bool] = False


@app.get("/")
async def root():
	return {"message": "Hello World"}


@app.post("/search")
async def search(query: Query):
	query_embedding = model.encode(sentences=[query.text])[0]
	papers = ps_connector.get_k_results(query_embedding, query.k)

	reranked_papers = rerank(query, papers, query_embedding)
	reranked_papers = {index: {
		'title': paper.title,
		'local_link': paper.local_link} for index, paper in enumerate(reranked_papers)}

	return reranked_papers


def rerank(query, papers, query_embedding):

	if query.distance_metric == 'braycurtis':
		distance_func = distance.braycurtis
	elif query.distance_metric == 'canberra':
		distance_func = distance.canberra
	elif query.distance_metric == 'chebyshev':
		distance_func = distance.chebyshev
	elif query.distance_metric == 'cityblock':
		distance_func = distance.cityblock
	elif query.distance_metric == 'cosine':
		distance_func = distance.cosine
	elif query.distance_metric == 'euclidean':
		distance_func = distance.euclidean
	else:
		# default dot product return papers with the same order
		return papers

	distances = [distance_func(query_embedding, paper.embedding) for paper in papers]
	papers = [paper for _, paper in sorted(zip(distances, papers))]

	return papers



