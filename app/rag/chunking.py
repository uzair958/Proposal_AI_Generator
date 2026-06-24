from langchain.text_splitter import RecursiveCharacterTextSplitter


def get_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
        ],
    )


def chunk_text(text: str):
    splitter = get_text_splitter()

    return splitter.split_text(text)