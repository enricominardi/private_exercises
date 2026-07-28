#%% packages
#from langchain_core.prompts import ChatPromptTemplate
#from langchain_core.output_parsers import StrOutputParser
from groq import Groq
import docx
import pymupdf4llm
import streamlit as st
import os
import pandas as pd
import json

# Load Groq API key from Streamlit secrets and set as environmental variable
try:
    if "groq" in st.secrets and "api_key" in st.secrets["groq"]:
        groq_api_key = st.secrets["groq"]["api_key"]
        os.environ["GROQ_API_KEY"] = groq_api_key
    else:
        st.error("Groq API key not found in Streamlit secrets. Please set it in .streamlit/secrets.toml or Streamlit Cloud secrets.")
        st.stop()
except:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
    os.getenv("GROQ_API_KEY")

# read documents
def get_text(filename):
    doc = docx.Document(filename)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

## word
doc = get_text('./data/Analyse_Entwicklung_GV.docx')

## pdf
#llama_reader = pymupdf4llm.LlamaMarkdownReader()
#pdf = llama_reader.load_data("./data/Beschlussvorlage.pdf")

pdf = pymupdf4llm.to_markdown(
    "./data/Beschlussvorlage.pdf", 
    page_chunks=True,
    write_images=True,
    image_path=".data",
    image_format="png",
    extract_words=True
    )

## excel
# deserialize
def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

xls = pd.read_excel("data/Entwicklung_GV.xlsx").to_json()

xls = json.dumps(xls, default=set_default)

 
# model parameters
#MODEL_NAME = "openai/gpt-oss-20b"
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
MODEL_TEMP = 0.2

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

st.title("Create annotations")
start = st.button("Start", type="primary")
user_input = """
all output should be in German.
Create annotations of the most important keyfacts and implications for the train freight business (Güterverkehr) from the analysis (analysis_content) and and the json dataframe provided (xls_content).
Select only annotations that are related to a topic mentioned in the provided management board draft (pdf_content).
and that support or highlight critical aspects of this topic for the future board decision. 
Map each of these resulting annotations to the most relevant sentence of the provided pdf file (pdf_content).
Concatenate together the annotations that belong to the same sentence of the provided pdf file (pdf_content).
Return the tuples of annotations and the related sentence of the provided pdf file (pdf_content).
"""

if start:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Act as an assistant to the executive board members of the german railways for the freight transportation." 
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": user_input
                    },
                    {
                        "type": "text",
                        "text": f"analysis_content: {doc}"
                    }, 
                    {
                        "type": "text",
                        "text": f"pdf_content: {pdf}"
                    },
                    {
                        "type": "text",
                        "text": f"xls_content: {xls}"
                    }
                ]
            }
        ],
        model=MODEL_NAME,
        temperature=MODEL_TEMP,
    )

    st.chat_message("user").write(user_input)
    st.chat_message("assistant").write(chat_completion.choices[0].message.content)
