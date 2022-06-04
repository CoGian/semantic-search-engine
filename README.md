1. Clone Github repo:
   1. git clone https://github.com/CoGian/semantic-search-engine.git
2. Change directory to the repo’s directory
   1. cd semantic-search-engine
3. Download postgresql dump and and istall all the dependencies needed :
   1. bash install.sh
4. Open terminal inside docker container:
   1. docker exec -it sem_search_postgres bash
5. Connect to postgres:
   1. psql -U postgres
6. Create DB and close connection:
   1. CREATE DATABASE sem_search;
7. Load psql dump and exit docker’s container:
   1. psql -U postgres sem_search < sem_search_export.pgsq
8. Run application:
   1. uvicorn src.api:app --reload
