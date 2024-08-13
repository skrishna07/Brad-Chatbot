import collections
import re
from difflib import SequenceMatcher
import langchain.chains.combine_documents
import langchain.chains.history_aware_retriever
import langchain.chains.retrieval
import langchain_community.callbacks
from azure.cosmos import CosmosClient, PartitionKey
from .azure_no_sql import (AzureCosmosDBNoSqlVectorSearch, )
from dotenv import load_dotenv, find_dotenv
import os
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .Log import Logger

from dotenv import load_dotenv

load_dotenv(find_dotenv())
logger = Logger()
store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def text_similarity(a, b):
    vectorizer = TfidfVectorizer().fit_transform([a, b])
    vectors = vectorizer.toarray()
    return cosine_similarity(vectors)[0, 1]


# Load environment variables from .env file
load_dotenv()

cosmos_key = os.getenv('WebChat_Key')

cosmos_database = os.getenv('WebChat_DB')

cosmos_collection = os.getenv('WebChatChunk_Container')

cosmos_vector_property = "embedding"

os.environ["AZURE_OPENAI_API_KEY"] = os.getenv('Azure_OPENAI_API_KEY')

os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv('Azure_OPENAI_API_BASE')

os.environ["AZURE_OPENAI_API_VERSION"] = os.getenv('Azure_OpenAIVersion')

os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = os.getenv('Azure_OpenAIDeploymentName')

os.environ["AZURE_EMBEDDINGS_DEPLOYMENT_NAME"] = "bradsol-ada-embeddings"
 


indexing_policy = {
    "indexingMode": "consistent",
    "includedPaths": [{"path": "/*"}],
    "excludedPaths": [{"path": '/"_etag"/?'}],
    "vectorIndexes": [{"path": "/embedding", "type": "quantizedFlat"}],
}

vector_embedding_policy = {
    "vectorEmbeddings": [
        {
            "path": "/embedding",
            "dataType": "float32",
            "distanceFunction": "cosine",
            "dimensions": 384,
        }
    ]
}

cosmos_client = CosmosClient(os.getenv('WebChat_EndPoint'), cosmos_key)
database_name = cosmos_database
container_name = cosmos_collection
partition_key = PartitionKey(path="/id")
cosmos_container_properties = {"partition_key": partition_key}
cosmos_database_properties = {"etag": None, "match_condition": None}

openai_embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_EMBEDDINGS_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_key=os.getenv('Azure_OPENAI_API_KEY'),
)

vectorstore = AzureCosmosDBNoSqlVectorSearch(embedding=openai_embeddings,
                                             cosmos_client=cosmos_client,
                                             database_name=database_name,
                                             container_name=container_name,
                                             vector_embedding_policy=vector_embedding_policy,
                                             indexing_policy=indexing_policy,
                                             cosmos_container_properties=cosmos_container_properties,
                                             cosmos_database_properties=cosmos_database_properties)

qa_retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 1},
    return_source_documents=True,
)

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"), temperature=0.5, max_tokens=500
)

prompt_search_query = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    ("system",
     """
    Generate a question based on the given chat history only.Take into account
    previous questions and answers while creating the new search query. Do not add any other context to the question. Ensure the reformatted search query closely matches the original question asked.
    If the same question has been asked previously, return the exact same query without reformatting.
     """)
])

history_aware_retriever = langchain.chains.history_aware_retriever.create_history_aware_retriever(
    llm, qa_retriever, prompt_search_query)

### Answer question ###
system_prompt = ("""
You are a highly knowledgeable and concise assistant specializing in generic and specific question-answering tasks. Please follow these guidelines:
 
1. Prioritize relevant information derived from the provided context when available.If the context does not contain the exact answer, use related information and synonyms within the context. If no relevant context is found, generate a general and accurate response based on LLM sources and knowledge, with a note that the answer is generated from external sources.
2. Provide precise and concise answers within the context.
3. Ensure your answers are grammatically correct and complete sentences.
4. When the context is unavailable or does not cover the question, generate the answer based on external sources, clearly stating that the answer is generated from LLM knowledge.Avoid assumptions or hallucinations.
5. Do not assume or infer information that is not explicitly mentioned in the context.
6. Do not include personal opinions or interpretations.
7. Avoid redundant information; be direct and to the point.
8. Prioritize clarity and relevance in your answers.
9. Cite specific parts of the context when forming your answer.
10. Avoid using ambiguous language; be as specific as possible.
11. If there are multiple relevant pieces of information in the context, integrate them into a cohesive answer.
12. If a question is ambiguous, state the ambiguity and request clarification.
13. Do not provide general knowledge or background information unless explicitly requested. If a general question is asked, ensure the response is apt and accurate without introducing unnecessary details.
14. If the answer requires multiple parts, number each part clearly.
15. If a question relates to the following categories, provide the appropriate response with Beep in it:
   - greeting
   - general inquiry
   - conversation ender
   - thank you
16. If the question is related to bus schedules or routes, provide the answer in the following HTML table format:
<table>
<tr>
<th>Area</th>
<th>Time</th>
</tr>
</table>
17. If the question is related to a route number or bus number, fetch the route number in context and provide the answer.
18. Remove the phrase "context states" from the answer.
19. Provide relevant answers for synonyms found in the context.
20. Ensure consistency in responses: When a question is repeated, refer to previous interactions and provide consistent answers based on the latest available context.
21. Maintain context awareness: Incorporate information from previous interactions to ensure that repeated questions receive coherent and relevant answers, even if the same question is asked again.
22. Stay on topic: Answer the question based solely on the information in the context. For questions outside the context, generate the response based on LLM knowledge and clearly state that the answer is based on external sources. 
Context: {context}

""")

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
question_answer_chain = langchain.chains.combine_documents.create_stuff_documents_chain(llm, qa_prompt)

rag_chain = langchain.chains.retrieval.create_retrieval_chain(history_aware_retriever, question_answer_chain)

QA_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
    return_source_documents=True
)


def post_process_answer(context, answer, link):
    # Ensure answer is only derived from the context
    for content in ["does not provide", "not found", "does not contain", "not provided", "does not mention",
                    "does not", "don't have"]:
        if content.lower() in answer.lower():
            return "Sorry, I don't have information. Could you please provide more precise question", ''
    if "BeepChat Assistant" in answer or "unable to" in answer or "feel free" in answer or "to ask" in answer or "How can I help you" in answer or "assist you" in answer:
        return answer, ''
    return answer, link


def handle_greet(human):
    messages = [
        (
            "system",
            "You are a highly knowledgeable and concise assistant specializing in Beep chatbot greetings handler: " \
            "Provide response for the query."
            "If question is not related to greeting, general queries, thanks or conversation ends State 'Sorry, I don't have information.'"
            "Avoid questions other than above categories, State 'Sorry, I don't have information.'"
            "Along with greetings if any questions is asked, then State 'Sorry, I don't have information.'",
        ),
        ("human", human),
    ]
    ai_msg = llm.invoke(messages)
    return ai_msg.content


def contains_greeting(text):
    # List of common greeting words
    greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']

    # Convert the input text to lowercase for case-insensitive comparison
    text_lower = text.lower()

    # Check if any greeting word is in the text
    return any(greeting in text_lower for greeting in greetings)


def AzureCosmosQA(human, session_id):
    try:
        with langchain_community.callbacks.get_openai_callback() as cb:
            if contains_greeting(human):
                result = handle_greet(human)
                if "don't have" not in result:
                    return result, cb.total_tokens, cb.total_cost, ''
            print("session_id", session_id)
            response = QA_chain.invoke(
                {"input": human},
                config={
                    "configurable": {"session_id": session_id},
                },
            )
            source_links = [doc.metadata['source'] for doc in response["context"] if 'source' in doc.metadata]
            context = [doc.page_content for doc in response["context"]]
            response = response["answer"]
            print("\n\n\n")
            print("openai_response", response)
            similarity = text_similarity(str(context), response)
            print(f"Similarity for above {response} with question - {human} - {similarity}")
            print("\n\n\n")
            if source_links:
                source_link = source_links[0]
            else:
                source_link = ''
                # response = "Sorry, I don't have information. Could you please provide more precise question"
            # if "<table>" not in response:
            if similarity < 0.075:
                source_link = ''
                #     response = "Sorry, I don't have information. Could you please provide more precise question"
            source_link = re.sub(r'.*Files', '', source_link)
            # response, source_link = post_process_answer(str(context), response, source_link)
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")
            return response, cb.total_tokens, cb.total_cost, source_link
    except Exception as e:
        error_details = logger.log(f"Error occurred in fetching response:{str(e)}", "Error")
        raise Exception(error_details)
