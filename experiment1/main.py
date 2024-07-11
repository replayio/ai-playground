import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import openai
import time
import tiktoken
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS

# from langchain_community.llms import OpenAI
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain.chains import LLMChain
from langchain.indexes import VectorstoreIndexCreator

from util.time_util import formatSecondsDelta


# Load environment variables from .env* files
load_dotenv()

# NOTE: Make sure to add OPENAI_API_KEY to your .env.secret file.
# See: https://platform.openai.com/api-keys
load_dotenv(".env.secret")

local_dir = os.getenv("LOCAL_DIR")
openai.api_key = os.getenv("OPENAI_API_KEY")
Model = "gpt-4o"
MaxTokens = 256


# Function to load files from a directory
def load_index():
  glob = "*.*"

  # Create loader.
  loader = DirectoryLoader(local_dir, glob)

  # Create vector store
  documents = loader.load()
  embeddings = OpenAIEmbeddings()
  # TODO: get a better model.
  # store =
  index_creator = VectorstoreIndexCreator(vectorstore_cls=FAISS, embedding=embeddings)
  index = index_creator.from_documents(documents)

  # return store, index
  return index


# Main function
def main():
  # store, index = load_local_index()
  index = load_index()
  llm = ChatOpenAI(model=Model, temperature=0, max_tokens=MaxTokens)
  input = "What is AI?"
  # input = "What libraries does devtools use?"

  # TODO: Instead of estimating, hook into the actual query to get the exact number of tokens spent.
  # NOTE: Monitor your API tokens + activity here - https://platform.openai.com/usage
  encoding = tiktoken.encoding_for_model(Model)
  num_tokens = len(encoding.encode(input))
  print(f'QUERYing ({num_tokens} tk): "{input}"')
  start = time.time()
  
  # RAG: Search offline AND online.
  res = index.query(input, llm=llm)

  print(f'\n[{formatSecondsDelta(start)}] RESULT:')
  print(res)


if __name__ == "__main__":
  print(f"START: {local_dir}")
  main()
