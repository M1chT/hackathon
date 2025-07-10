from dotenv import load_dotenv
import logging

from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool

import os
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

def search_best_practices_tool():
    """
    Ingest data from various URLs to create a knowledge base for marketing strategies of best practices to use.
    """
    logger.info("Searching for best practices...")
    urls = [
        "https://www.park.edu/blog/effective-marketing-strategies/",
        "https://www.wix.com/blog/marketing-strategies",
        "https://www.salesforce.com/ap/marketing/email/best-practices/",
        # "https://www.mastercardservices.com/en/test-learn/what-we-do/test-learn-foundations?campaign_id=701UH00000NAoeFYAT&channel=sep&cmp=2025.q1.rca-sem-testlearn-nonbranded-foundations.promotion%20strategy&keyword=promotion%20strategy&gad_source=1&gad_campaignid=20604773226&gbraid=0AAAAADR5mscd29-OdZ1nGLC3mfAp1G1jx&gclid=CjwKCAjwg7PDBhBxEiwAf1CVuxDM7rxxlyONQUJ5tHgANY1cmGmaXCfRYy_fuoep3pzzGvtJSmbhNxoC6zwQAvD_BwE",
        # "https://www.shopify.com/sg/blog/how-to-market-a-product",
    ]
    docs = []
    for url in urls:
        try:
            loaded = WebBaseLoader(url).load()
            docs.extend(loaded)  # loaded is already List[Document]
        except Exception as e:
            print(f"Failed to load {url}: {e}")
    # docs = [WebBaseLoader(url).load() for url in urls]

    # docs_list = [item for sublist in docs for item in sublist]

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=100, chunk_overlap=50
    )
    doc_splits = text_splitter.split_documents(docs)
    # Create an in-memory vector store from the documents
    vectorstore = InMemoryVectorStore.from_documents(
        documents=doc_splits,
        embedding=OpenAIEmbeddings(api_key=OPENAI_API_KEY),
    )
    retriever = vectorstore.as_retriever()
    retriever_tool = create_retriever_tool(
        retriever,
        "retrieve_marketing_strategies",
        "Search and return information about marketing strategies",
    )
    return retriever_tool
