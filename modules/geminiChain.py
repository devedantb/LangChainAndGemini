import os
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains import RetrievalQA
from langchain.vectorstores.chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from .webscraper import getDataFromUrl, urlScraper
from IPython.display import Markdown
import textwrap
from dotenv import load_dotenv
from .readpdf import readPDF

load_dotenv()


def to_markdown(text):
    text = text.replace("•", "  *")
    return Markdown(textwrap.indent(text, "> ", predicate=lambda _: True))


# set a key and model
# getting api key from .env variables
GOOGLE_API_KEY = os.getenv("gemini_key")
# defining a model
model = ChatGoogleGenerativeAI(
    model="gemini-1.0-pro",  # another models >> gemini-pro, gemini-1.0-pro, gemini-1.0-pro-001
    google_api_key=GOOGLE_API_KEY,
    temperature=0,
    convert_system_message_to_human=True,
)


# getting data from pdf and answering
def GetDataFromPDFandAnswer(
    pdf_name, prompt, pdf_data, GOOGLE_API_KEY=GOOGLE_API_KEY
):  ##pdf_path,
    try:
        texts = pdf_data
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", google_api_key=GOOGLE_API_KEY
        )
        vector_index = Chroma.from_texts(texts, embeddings).as_retriever(
            search_kwargs={"k": 5}
        )
        qa_chain = RetrievalQA.from_chain_type(
            model, retriever=vector_index, return_source_documents=True
        )
        result = qa_chain({"query": prompt})
        answer = result["result"]
        return answer
    except:
        return f"{pdf_name} is not a valid pdf"
