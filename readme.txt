 cmd on powershell 
 :docker exec -it redis-server redis-cli XRANGE feedback_stream - +

 use docker: redis-server


 Day
 docker: elastic search 
 created index.py
 docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.6.2

docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0
  (paste in a single line,removing all the "\")


curl -X GET "http://localhost:9200"

RUN : CREATE_INDEX.PY -> INDEX_DATA.PY

KIBANA: docker run -d --name kibana -p 5601:5601 --link elasticsearch:elasticsearch docker.elastic.co/kibana/kibana:8.11.0

add_data.py:statically aading dtaa to verify visualizations in kibaana

server.py:dynamically adding them
