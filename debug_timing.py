import time
from src.config import get_api_key, GEMINI_MODEL, EMBED_MODEL
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

key = get_api_key()

t = time.perf_counter()
emb = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL, google_api_key=key)
emb.embed_query("motor start interlock")
print(f"Embedding call: {time.perf_counter() - t:.1f}s")

t = time.perf_counter()
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL, temperature=0, google_api_key=key, max_retries=1, timeout=60
)
print(llm.invoke("Reply with the single word: ok").content)
print(f"LLM call (tiny prompt): {time.perf_counter() - t:.1f}s")