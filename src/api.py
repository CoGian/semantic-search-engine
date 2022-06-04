import os
from typing import Optional
import yaml
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import webbrowser
from starlette.responses import RedirectResponse

from src.postgres_connector import PostgresConnector
from src.utils import rerank, get_explanation

app = FastAPI()

with open('config/postgres.yaml', 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)

ps_connector = PostgresConnector(config)
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')


class Query(BaseModel):
    text: str
    k: int = 10
    distance_metric: Optional[str] = 'cosine'


@app.get("/", summary="redirects to Swagger UI")
async def root():
    return RedirectResponse(url="/docs")


@app.post("/search")
async def search(query: Query):
    query_embedding = model.encode(sentences=[query.text])[0]
    papers = ps_connector.get_k_results(query_embedding, query.k)

    reranked_papers = rerank(query, papers, query_embedding)
    explanations = get_explanation(query.text, reranked_papers)
    reranked_papers = {index: {
        'title': paper.title,
        'local_link': paper.local_link,
        'explanation': explanations[index]
    } for index, paper in enumerate(reranked_papers)}

    return reranked_papers


@app.get("/open_file")
async def open_file(local_link: str):
    webbrowser.open_new("file://" + os.path.abspath(local_link))
