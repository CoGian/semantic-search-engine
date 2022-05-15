import os
from typing import Optional
from scipy.spatial import distance
import yaml
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import webbrowser
from src.postgres_connector import PostgresConnector
from nltk.corpus import stopwords
from rapidfuzz import fuzz


stop_words = set(stopwords.words('english'))

app = FastAPI()

with open('config/postgres.yaml', 'r') as config_file:
	config = yaml.load(config_file, Loader=yaml.FullLoader)

ps_connector = PostgresConnector(config)
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')


class Query(BaseModel):
	text: str
	k: int = 10
	distance_metric: Optional[str] = 'cosine'


@app.get("/")
async def root():
	return {"message": "Hello World"}


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


def get_explanation(query_text, reranked_papers):

	filtered_query_words = [w.lower() for w in query_text.split() if not w.lower() in stop_words]

	explanations = []
	for paper in reranked_papers:
		paper_text = paper.title + " " + paper.abstract
		paper_words = paper_text.split()
		query_word_index_list = [[] for _ in filtered_query_words]
		for i, query_word in enumerate(filtered_query_words):
			for j, paper_word in enumerate(paper_words):
				if fuzz.ratio(query_word, paper_word, score_cutoff=90.0):
					query_word_index_list[i].append(j)

		flat_query_word_index_list = sorted(set([index for sublist in query_word_index_list for index in sublist]))
		explanation = []
		for index, paper_word_index in enumerate(flat_query_word_index_list):
			if index > 0 and paper_word_index - flat_query_word_index_list[index - 1] > 5:
				explanation.append(paper_word_index)
			elif index == 0:
				explanation.append(paper_word_index)

		explanation_sents = []
		for index in explanation:
			lo = index - 5
			hi = index + 5
			if lo < 0:
				lo = 0
			if hi > len(paper_words):
				hi = len(paper_words)

			explanation_sents.append(" ".join(paper_words[lo:hi]))

		explanations.append(explanation_sents)

	return explanations
