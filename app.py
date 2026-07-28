import streamlit as st 
import os 
import time
import langchain
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from tavily import TavilyClient
import pytesseract as pyt
import numpy as np
from langchain.messages import SystemMessage, HumanMessage
from langchain.agents import create_agent
import streamlit as st
from PIL import Image



#==============ForntEnd==============
st.title("AI Resume Maker & Job Apply Link")
st.image("airesumeagent.jpeg")

GOOGLE_API_KEY =st.sidebar.text_input("Google API Key",type='password')
GROQ_API_KEY =st.sidebar.text_input("GROQ API Key",type='password')
TAVILY_API_KEY =st.sidebar.text_input("TAVILY API Key",type='password')

if not (GOOGLE_API_KEY) and not (GROQ_API_KEY) and not (TAVILY_API_KEY) :
    st.sidebar.warning("pass api keys")
    st.stop
else:
    st.success("Api Keys Loaded")

#==============MODEL AND AGENT CODE==============
# tool 1
def search_latest_news_jobs(query):
    """This function helps to get 
    latest news or latest jobs 
    related to user given query 
    using tavily"""
    
    from tavily import TavilyClient
    client = TavilyClient(api_key = TAVILY_API_KEY)
    return client.search(query)

# Step : Model and Agent creation
model1 = ChatGoogleGenerativeAI(
    model = "gemini-3.5-flash-lite",
    google_api_key = GOOGLE_API_KEY
)

model2 = ChatGroq(
    model = "qwen/qwen3.6-27b",
    api_key = GROQ_API_KEY
)

#===========Agent with tool===========
agent = create_agent(
    model = model1,   # can be model2 also,
    tools = [search_latest_news_jobs]
)

# Let's Generate Prompt for Resume using model
def prompt_generator():
    prompt = """You are a helpful AI Resume 
    maker, I want you to use chain-of-thoughts 
    and give detailed prompt for model 
    where user want to generate resume 
    for fresher or experienced one 
    in HTML format, you have to give proper 
    set of instructions, and make sure to keep 
    design professional"""

    response = model1.invoke(prompt)
    prompt_ans = response.content[-1]['text']
    # print(prompt_ans)

    file_name = 'prompt.txt'
    with open(file_name, 'w') as f:
        f.write(prompt_ans)
prompt_generator()

# Final_Agent
#Tool 2
def prompt_reader():
    with open('prompt.txt','r') as f:
        prompt = f.read()
    return prompt

prompt = """I want complete Professional
Resume with Dynamic Design using Advanced CSS and JS
and must show user input details
System instructions: Only Give HTML code as output use dark green text and dark theme
Use myimage.jpeg as image"""

final_prompt = prompt + prompt_reader()
#===============================upload_image=========================
FILE = st.sidebar.file_uploader(
    "choose an image file",
    type= ["jpg","jpeg","png","webp"]
)

if FILE is not None:
try:
        image = Image.open(FILE)
        st.sidebar.image(image,caption = "Uploaded Image",use_container_width=True)
        if image.mode in ("RGBA","P"):
            image = image.convert("RGB")
            
        base_name  = os.path.splitext(FILE.name)[0]
        save_path = f"{base_name}.jpg"
        
        image.save(save_path,"JPEG")
        st.sidebar.success(f"Image successfully saved as `{save_path}`!")

except Exception as e:
         st.error(f"Error proccessing image:{e}")


            
# Change this when required new resume by user, pass details

user_info = st.text_input("Give Your Information : ")
user_photo = st.sidebar.file_uploader("Upload Pic", type='image/jpeg')
user_query = f"""Give Resume for Python Developer.
    user details : {user_info}
    use user profile image from given {user_photo}"""

final_query = final_prompt + user_query


if st.button("Generate Resume"):
    with st.spinner("Agent Creating Resume..."):
        response = agent.invoke({'messages':[{'role':'user',"content":final_query}]})
        code = response['messages'][-1].content[-1]['text']

        st.html(code,width="stretch",unsafe_allow_javascript=True)
