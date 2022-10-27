from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3
import os, csv, json


# Need to define the ENV variables to get the credentials
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#using-environment-variables
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, os.getenv('AWS_DEFAULT_REGION'))
index_name = os.getenv('OPENSEARCH_INDEX')

# API Reference: https://opensearch-project.github.io/opensearch-py/api-ref/clients/opensearch_client.html
client = OpenSearch(
    hosts = [{'host': os.getenv('OPENSEARCH_DOMAIN_ENDPOINT'), 'port': 443}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)


def create_index():
    if (not client.indices.exists(index=index_name)):
        # https://opensearch.org/docs/1.3/opensearch/supported-field-types/index/
        body = {
            "mappings":{
                "properties": {
                    "title": {"type": "text", "analyzer": "standard"},
                    "languageTag": {"type": "keyword"},
                    "description": {"type": "text", "analyzer": "standard"},
                    "estimate_time": {"type": "integer"},
                    "tags": {"type": "text", "analyzer": "standard"},
                    "authors": {"type": "text", "analyzer": "standard"},
                    "organization": {"type": "integer"},
                    "provider": {"type": "keyword"}
                }
            }
        }
        response = client.indices.create(index_name, body=body)

        print(response)

def import_dataset():
    with open("lo.csv", "r") as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
            body = {           
                "title": line[1],
                "languageTag": line[4],
                "description": line[2],
                "estimate_time": line[3],
                "provider": line[7],
                "organization": line[8],
                "authors": line[6].split("|"),
                "tags": line[5].split("|")
            }    
            print(body)
            # Create or Update document
            response = client.index(index=index_name, id=line[0], body=body)
            print(response)

#print("================== CLUSTER ==================")
"""
 Print information about the cluster
 """
#print(client.info())

#create_index()

#index_infos = client.indices.get(index=index_name)
#print("================== INDEX ==================")
#print(index_infos)

#print("================== IMPORT DATASET ==================")
#import_dataset()

print("================== SEARCH ==================")
query = {
  'size': 5,
  'query': {
    'multi_match': {
      'query': "Maura",
      'fields': ['title', 'description', 'tags^2', 'authors']
    }
  }
}

response = client.search(
    index=index_name,
    body=query
)

#obj = json.loads(response)
print(json.dumps(response, indent=2))




