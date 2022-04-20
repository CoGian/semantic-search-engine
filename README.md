# semantic-search-engine

docker pull ankane/pgvector

docker run -d -p 5432:5432 --name sem_search_postgres -e POSTGRES_PASSWORD=password ankane/pgvector

docker exec -it sem_search_postgres bash

psql -U postgres

CREATE DATABASE sem_search;


