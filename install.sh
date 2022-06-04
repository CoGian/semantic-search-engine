wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1BMkYwEbI2vIUliP1brAxZC54jASLXt4f' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1BMkYwEbI2vIUliP1brAxZC54jASLXt4f" -O papers.zip && rm -rf /tmp/cookies.txt
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1hjm1tobg9Jd4Dt3pgDNOFqrt2RFG7Uk0' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1hjm1tobg9Jd4Dt3pgDNOFqrt2RFG7Uk0" -O sem_search_export.pgsql && rm -rf /tmp/cookies.txt
unzip papers.zip
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m nltk.downloader stopwords
docker pull ankane/pgvector
docker run -d -p 5432:5432 --name sem_search_postgres -e POSTGRES_PASSWORD=password ankane/pgvector
docker cp sem_search_export.pgsql sem_search_postgres:/sem_search_export.pgsql