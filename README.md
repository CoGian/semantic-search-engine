1. Clone Github repo:
   1. git clone https://github.com/CoGian/semantic-search-engine.git
2. Download & install PostgreSQL
3. Change directory to the repo’s directory
   1. cd semantic-search-engine
4. Download postgresql dump and and istall all the dependencies needed :
   1. bash install.sh
5. Open terminal inside docker container:
   1. docker exec -it sem_search_postgres bash
6. Connect to postgres:
   1. psql -U postgres
7. Create DB and close connection:
   1. CREATE DATABASE sem_search;
8. Load psql dump and exit docker’s container bash:
   1. psql -U postgres sem_search < sem_search_export.pgsql
9. Run application:
   1. source venv/bin/activate
   2. uvicorn src.api:app --reload
