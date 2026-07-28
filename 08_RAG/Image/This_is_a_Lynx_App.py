#%% packages
import streamlit as st
from groq import Groq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import base64
import os


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
 
# intantiate model
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
MODEL_TEMP = 2.0

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Load image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
 
image_path = "./data/cat.jpg"
base64_image = encode_image(image_path)

st.title("This is a lynx")
user_input = st.chat_input(placeholder="Convince me that this is a lynx")
st.image(image_path)

if user_input is not None:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Assess the rightfulness of the user input arguments concerning the input image and answer accordingly with yes or no and explain your answer."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_input},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model=MODEL_NAME,
        temperature=MODEL_TEMP,
    )
    

    st.chat_message("user").write(user_input)
    st.chat_message("assistant").write(chat_completion.choices[0].message.content)
