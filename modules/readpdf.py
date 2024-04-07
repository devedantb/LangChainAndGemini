from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def readPDF(pdf_path: str):
    pdf_loader = PyPDFLoader(pdf_path)
    pages = pdf_loader.load_and_split()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    context = "\n".join(str(p.page_content) for p in pages)
    texts = text_splitter.split_text(context)
    return texts


if __name__ == "__main__":
    pdf_path = input("Enter a pdf path (local path): ")
    print(readPDF(pdf_path))
