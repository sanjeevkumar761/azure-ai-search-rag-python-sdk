from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import ComplexField, SearchIndex, SimpleField, SearchableField
from azure.search.documents.indexes.models import SearchFieldDataType
from azure.storage.blob import BlobServiceClient, BlobClient
import os

load_dotenv()

def download_blobs():
    # Replace with your connection string
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    # Replace with your container name
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a reference to the container
    container_client = blob_service_client.get_container_client(container_name)

    # Optionally, list all blobs in the container and download them
    for blob in container_client.list_blobs():
        print(f"Downloading {blob.name}...")
        blob_client = container_client.get_blob_client(blob.name)
        
        # Define the download file path
        download_file_path = os.path.join("./", blob.name)
        os.makedirs(os.path.dirname(download_file_path), exist_ok=True)
        
        # Download the blob to a local file
        with open(download_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

    print("Download completed.")

def create_index():
    service_name = os.getenv("AZURE_SEARCH_SERVICE_NAME")
    endpoint = f"https://{service_name}.search.windows.net/"
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    # Create a SearchIndexClient
    client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

    # Define the index schema
    index = SearchIndex(
        name=index_name,
        fields=[
            SimpleField(name="docid", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String, searchable=True, filterable=True)
        ]
    )
    # Create the index
    client.create_index(index)    

def chunk_text(text, chunk_size=1000):
    """
    Splits the text into chunks of specified size.
    
    Args:
        text (str): The text to split.
        chunk_size (int): The size of each chunk, default is 1000 characters.
    
    Returns:
        list: A list of text chunks.
    """
    # Ensure text is a string and chunk_size is a positive integer
    if not isinstance(text, str) or not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("Text must be a string and chunk_size must be a positive integer.")
    
    # Split the text into chunks
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

def index_documents():


    # Replace with your Azure Cognitive Search service name, index name, and admin/api keys
    service_name = os.getenv("AZURE_SEARCH_SERVICE_NAME")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")

    # Create a SearchIndexClient
    endpoint = f"https://{service_name}.search.windows.net/"
    admin_client = SearchIndexClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(api_key))

    # Assuming you have a search index already set up, get a SearchClient
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(api_key))

    # Specify the path to your text document
    file_path = './state_of_the_union.txt'

    # Open the file and read its contents
    with open(file_path, 'r', encoding='utf-8') as file:
        text_document = file.read()

    # Now text_document contains the contents of your text file
    #print(text_document)
    # Load your document
    #text_document = "Your long text document content here..."
    chunks = chunk_text(text_document, 1000)  # Chunk the document

    # Create documents to index
    documents = [{"docid": str(i), "content": chunk} for i, chunk in enumerate(chunks)]

    # Index documents
    search_client.upload_documents(documents=documents)
# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_simple_query.py
DESCRIPTION:
    This sample demonstrates how to get search results from a basic search text
    from an Azure Search index.
USAGE:
    python sample_simple_query.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SEARCH_SERVICE_ENDPOINT - the endpoint of your Azure Cognitive Search service
    2) AZURE_SEARCH_INDEX_NAME - the name of your search index (e.g. "hotels-sample-index")
    3) AZURE_SEARCH_API_KEY - your search API key
"""

import os

service_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")



def simple_text_query(question: str) -> str:
    # [START simple_query]
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

    results = search_client.search(search_text=question, top=1)

    content = ""
    for result in results:
        #print(" ")
        #print("###### Here is the result:")
        #print(result["content"])
        content = content + result["content"]
    # [END simple_query]
    return content

def generate_llm_response(question: str) -> str:
    import os
    from openai import AzureOpenAI
        
    client = AzureOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),  
        api_version="2024-02-01",
        azure_endpoint = os.getenv("OPENAI_API_BASE")
        )
        
       
    # Send a completion call to generate an answer
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL_DEPLOYMENT_NAME") , # model = "deployment_name".
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Always answer questions from given content"},
            {"role": "user", "content": question + " \n Use Reference content: " + simple_text_query(question)},
        ]
    )

    #print(response.choices[0].message.content)
    return response.choices[0].message.content

if __name__ == "__main__":
    #download_blobs()
    #create_index()
    #index_documents()
    response = generate_llm_response("What did President say about American Rescue Plan?")
    print(response) 

