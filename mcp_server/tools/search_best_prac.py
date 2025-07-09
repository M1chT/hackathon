from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
import os


def best_practices():
    """
    Ingest data from various URLs to create a knowledge base for marketing strategies of best practices to use.
    """

    urls = [
        "https://www.park.edu/blog/effective-marketing-strategies/",
        "https://www.wix.com/blog/marketing-strategies",
        "https://www.salesforce.com/ap/marketing/email/best-practices/",
        "https://www.mastercardservices.com/en/test-learn/what-we-do/test-learn-foundations?campaign_id=701UH00000NAoeFYAT&channel=sep&cmp=2025.q1.rca-sem-testlearn-nonbranded-foundations.promotion%20strategy&keyword=promotion%20strategy&gad_source=1&gad_campaignid=20604773226&gbraid=0AAAAADR5mscd29-OdZ1nGLC3mfAp1G1jx&gclid=CjwKCAjwg7PDBhBxEiwAf1CVuxDM7rxxlyONQUJ5tHgANY1cmGmaXCfRYy_fuoep3pzzGvtJSmbhNxoC6zwQAvD_BwE",
        "https://www.shopify.com/sg/blog/how-to-market-a-product",
    ]

    docs = [WebBaseLoader(url).load() for url in urls]

    docs_list = [item for sublist in docs for item in sublist]

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=100, chunk_overlap=50
    )
    doc_splits = text_splitter.split_documents(docs_list)
    # Create an in-memory vector store from the documents
    vectorstore = InMemoryVectorStore.from_documents(
        documents=doc_splits,
        embedding=OpenAIEmbeddings(api_key=os.environ.get("OPENAI_API_KEY")),
    )
    retriever = vectorstore.as_retriever()

    return retriever
