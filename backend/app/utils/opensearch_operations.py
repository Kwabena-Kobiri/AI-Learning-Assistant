# app/utils/opensearch_operations.py
from opensearchpy import OpenSearch, RequestsHttpConnection
from app.config import Config

opensearch_client = OpenSearch(
    [Config.OPENSEARCH_URL],
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    timeout=60,  # Increase the timeout to 30 seconds
    max_retries=3,  # Increase the number of retries
    retry_on_timeout=True,  # Enable retries on timeout
)

# opensearch_client = OpenSearch(
#     hosts=[{"host": "52.31.193.32", "port": 4008}],
#     use_ssl=True,
#     verify_certs=True,
#     connection_class=RequestsHttpConnection,
#     timeout=60,  # Increase the timeout to 30 seconds
#     max_retries=3,  # Increase the number of retries
#     retry_on_timeout=True,  # Enable retries on timeout
# )
