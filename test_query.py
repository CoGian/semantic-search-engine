import yaml
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text, Column, Integer, String
from src.postgres_connector import PostgresConnector, Paper
from sqlalchemy.orm import declarative_base, Session

with open('config/postgres.yaml', 'r') as config_file:
	config = yaml.load(config_file, Loader=yaml.FullLoader)

ps_connector = PostgresConnector(config)
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

query = 'transformers deep learning and natural language processing'

query_embedding = model.encode(sentences=[query])[0]

session = Session(ps_connector.engine)
papers = session.query(Paper).order_by(Paper.embedding.l2_distance(query_embedding)).limit(5).all()
for paper in papers:
	print(paper.title)


