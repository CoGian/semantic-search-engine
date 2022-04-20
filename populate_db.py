import wget
import json
import os
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import yaml
from src.postgres_connector import PostgresConnector

import ssl

try:
	_create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
	# Legacy Python that doesn't verify HTTPS certificates by default
	pass
else:
	# Handle target environment that doesn't support HTTPS verification
	ssl._create_default_https_context = _create_unverified_https_context

with open('config/postgres.yaml', 'r') as config_file:
	config = yaml.load(config_file, Loader=yaml.FullLoader)

ps_connector = PostgresConnector(config)
model = SentenceTransformer('sentence-transformers/all-distilroberta-v1')

if not os.path.exists('papers'):
	os.mkdir('papers')

papers = []
with open('dataset.json', 'r') as fin:
	for line in tqdm(fin):
		doc = json.loads(line)
		try:
			filename = wget.download(doc['pdfUrl'], out='papers/')
		except Exception as e:
			print(e)
			continue

		paper = {'local_link': filename}
		embedding = model.encode(sentences=[doc['title'] + ' ' + doc['paperAbstract']])[0]
		paper['embedding'] = embedding
		paper['id'] = doc['id']
		papers.append(paper)

ps_connector.populate_db(papers)
