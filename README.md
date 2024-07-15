

1. pip install -r requirements.txt  
2. Save .env-sample as .env  
3. Update values of environment variables in .env  
4. Execute the following steps in rag-ai-search.py  
    download_blobs()  
    create_index()  
    index_documents()  
    response = generate_llm_response("What did President say about American Rescue Plan?")  
    print(response)    