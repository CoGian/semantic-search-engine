1. Clone Github repo:
   1. git clone git@github.com:CoGian/semantic-search-engine.git
2. Change directory to the repo’s directory
   1. cd semantic-search-engine
3. Download postgresql dump and and istall all the dependencies needed :
   1. sh install.sh
4. Run application:
   1. uvicorn src.api:app --reload