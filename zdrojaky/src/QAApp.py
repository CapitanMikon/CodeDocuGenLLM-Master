# langsmith integration
from dotenv import load_dotenv
load_dotenv()
import json

import chromadb

from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from vectordb_manager import VectorDbManager
from utility.constants import CHROMA_DB_ABSOLUTE_PATH, OPTIONS_ROLE, OPTIONS_ANSWER_TYPE, \
    CHAT_SYSTEM_PROMPT_TEMPLATE
from utility.utils import get_embedding_function

from typing_extensions import TypedDict
from typing import List, Annotated


class GraphState(TypedDict):
    question: str
    response: str
    documents: List[str]


def get_method_list_from_repo(repo) -> list:
    try:
        db_manager = VectorDbManager()
        db_manager.connect(repo)
        return db_manager.get_all_methods_in_collection()
    except:
        return []


def select_first_indexed_repo() -> str:
    indexed_repositories = get_collections_from_chromadb()
    if len(indexed_repositories) == 0:
        raise Exception("No indexed repository, could not find any collections")
    return indexed_repositories[0]


def get_collections_from_chromadb() -> list:
    # return ["futurabm-dev-main-test-coreapp", "rimska-kalkulacka"]
    collections = []
    for collection in chromadb.PersistentClient(path=CHROMA_DB_ABSOLUTE_PATH).list_collections():
        collections.append(collection.name)
    return collections


def get_vectordb() -> Chroma:
    print(f"Vectordb: {SELECTED_REPOSITORY}, with dir: {CHROMA_DB_ABSOLUTE_PATH}")
    vectordb = Chroma(
        collection_name=SELECTED_REPOSITORY,
        embedding_function=get_embedding_function(),
        persist_directory=CHROMA_DB_ABSOLUTE_PATH
    )
    return vectordb


MODEL: str = "llama3.1:8b-instruct-q4_K_S"
TEMPERATURE: float = 0.0
SELECTED_REPOSITORY: str = select_first_indexed_repo()
AVAILABLE_MODELS: list = ["llama3.1:8b-instruct-q4_K_S"]
chat_history = []

SELECTED_ROLE = OPTIONS_ROLE[0]
SELECTED_ANSWER_TYPE = OPTIONS_ANSWER_TYPE[0]


def build_system_prompt():
    persona_prompt = ""
    response_prompt = ""

    if SELECTED_ROLE == OPTIONS_ROLE[1]:
        persona_prompt = "You are a kind programmer coworker. "
    else:
        persona_prompt = "You are a programmer and documentation expert. "

    if SELECTED_ANSWER_TYPE == OPTIONS_ANSWER_TYPE[0]:
        response_prompt = response_prompt.replace("{TYPE}", " brief ")
    elif SELECTED_ANSWER_TYPE == OPTIONS_ANSWER_TYPE[1]:
        response_prompt = response_prompt.replace("{TYPE}", " detailed ")
    else:
        response_prompt = response_prompt.replace("a{TYPE}", "")

    return persona_prompt + response_prompt + CHAT_SYSTEM_PROMPT_TEMPLATE


def format_docs(docs):
    return "\n\n".join(doc[0].page_content + "\n\nImplementation:\n" + doc[0].metadata["code"] for doc in docs)


# define langgraph nodes
def retrieve(state):
    print("-RETRIEVE DOCUMENTS START-")
    query = state["question"]

    documents = get_vectordb().similarity_search_with_relevance_scores(query)
    # documents = []

    if len(documents) > 0:
        print("\tRETRIEVED:")
        for doc in documents:
            print(f"\t{doc}")
    else:
        print("\tRETRIEVED: EMPTY")

    print("-RETRIEVE DOCUMENTS END-")
    return {"documents": documents}


def filter_relevant_documents(state):
    print("-FILTER RELEVANT DOCUMENTS START-")
    llm_json_mode = ChatOllama(
        model=MODEL,
        temperature=TEMPERATURE,
        format="json"
        # verbose=True,
    )
    filtered_documents = []
    documents = state["documents"]
    query = state["question"]
    filter_doc_llm_prompt_template = """Here is the retrieved document: \n\n {document} \n\n Here is the user question: \n\n {question}. 

Carefully and objectively assess whether the document contains at least some information that is relevant to the question.

Return JSON with single key, binary_score, that is 'yes' or 'no' score to indicate whether the document contains at least some information that is relevant to the question."""

    instructions = """You are a grader assessing relevance of a retrieved document to a user question.

If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant."""

    for d in documents:
        formatted_prompt = filter_doc_llm_prompt_template.format(document=d[0].page_content, question=query)
        result = llm_json_mode.invoke([SystemMessage(content=instructions)] + [HumanMessage(content=formatted_prompt)])
        grade = json.loads(result.content)['binary_score']

        if grade.lower() == "yes":
            print(f"RELEVANT: {d}")
            filtered_documents.append(d)
        else:
            print(f"NOT RELEVANT: {d}")

    print("-FILTER RELEVANT DOCUMENTS END-")
    return {"documents": filtered_documents}


def no_documentation(state):
    print("-NO DOCUMENTATION EXISTS START-")

    response = AIMessage(content="Sorry, there is no documentation for what you asked.")
    # response = "Sorry, there is no documentation for what you asked."

    print("-NO DOCUMENTATION EXISTS END-")
    return {"response": response}


def query_llm(state):
    print("-QUERY LLM START-")

    prompt_template = """
    With provided documentation:

    {context}

    Answer the user question:

    {input}
    """

    system_prompt = build_system_prompt()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", prompt_template)
        ]
    )

    llm = ChatOllama(
        model=MODEL,
        temperature=TEMPERATURE,
        # verbose=True,
    )
    print(f"Prepared model: {MODEL} with temperature: {TEMPERATURE}")

    query = state["question"]
    documents = state["documents"]

    formatted_docs = format_docs(documents)
    formatted_prompt = prompt.invoke({"context": formatted_docs, "input": query, "chat_history": chat_history})
    print(formatted_prompt)

    response = llm.invoke(formatted_prompt)
    chat_history.append(HumanMessage(content=query))
    chat_history.append(response)

    print("\tRESPONSE:")
    print(response)

    print("-QUERY LLM END-")
    return {"response": response}


def query_llm_no_documents(state):
    print("-QUERY LLM without context START-")

    prompt_template = """
    Answer the user question:

    {input}
    """
    system_prompt = "You are a programmer and documentation expert. Help the user understand the code. Assist the programmer best as you can."
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", prompt_template)
        ]
    )

    llm = ChatOllama(
        model=MODEL,
        temperature=TEMPERATURE,
        # verbose=True,
    )
    print(f"Prepared model: {MODEL} with temperature: {TEMPERATURE}")

    query = state["question"]
    formatted_prompt = prompt.invoke({"input": query, "chat_history": chat_history})
    print(formatted_prompt)

    response = llm.invoke(formatted_prompt)
    chat_history.append(HumanMessage(content=query))
    chat_history.append(response)

    print("\tRESPONSE:")
    print(response)

    print("-QUERY LLM without context END-")
    return {"response": response}


# langgraph edges
def retrieve_documents(state):
    """
    :param state: current state
    :return: next node name
    """

    print("-DECIDED TO DO RAG RETRIEVAL-")
    return "retrieve"


def decide_query_llm(state):
    """
    :param state: current state
    :return: next node name
    """

    if len(state["documents"]) == 0:
        print("-DECIDED TO STOP-\n\tREASON: no documentation")
        return "no_documentation"

    print("-DECIDED TO DO QUERY LLM-")
    return "query_llm"

def decide_repository_question_relevancy(state):
    """
    :param state: current state
    :return: next node name
    """

    print("-DECIDE IF REPOSITORY SPECIFIC QUESTION-")
    llm_json_mode = ChatOllama(
        model=MODEL,
        temperature=TEMPERATURE,
        format="json"
        # verbose=True,
    )

    query = state["question"]
    methods = ", ".join(get_method_list_from_repo(SELECTED_REPOSITORY))
    filter_doc_llm_prompt_template = """Here are all methods from the current repository: \n\n {methods} \n\n Here is the user question: \n\n {question}. 

    Carefully and objectively assess whether the user question contains at least some information that is relevant to the methods in the current repository.

    Return JSON with single key, binary_score, that is 'yes' or 'no' score to indicate whether the question contains at least some information that is relevant to the methods in the current repository."""

    instructions = """You are a grader assessing relevance of a user question to list of availible methods in current repository.

    If the the question contains methods that are in the current repository, grade it as relevant."""

    formatted_prompt = filter_doc_llm_prompt_template.format(methods=methods, question=query)
    result = llm_json_mode.invoke([SystemMessage(content=instructions)] + [HumanMessage(content=formatted_prompt)])
    grade = json.loads(result.content)['binary_score']

    if grade.lower() == "yes":
        print("-QUESTION REPO RELEVANT-")
        return "retrieve"
    else:
        print("-QUESTION NOT REPO RELEVANT-")
        return "query_llm_no_documents"


lang_graph = StateGraph(GraphState)

# Nodes
lang_graph.add_node("retrieve", retrieve)
lang_graph.add_node("filter_relevant_documents", filter_relevant_documents)
lang_graph.add_node("no_documentation", no_documentation)
lang_graph.add_node("query_llm", query_llm)
lang_graph.add_node("query_llm_no_documents", query_llm_no_documents)


# Build graph
lang_graph.set_conditional_entry_point(
    decide_repository_question_relevancy,
    {
        "retrieve": "retrieve",
        "query_llm_no_documents": "query_llm_no_documents",
    }
)
lang_graph.add_edge("retrieve", "filter_relevant_documents")
lang_graph.add_conditional_edges(
    "filter_relevant_documents",
    decide_query_llm,
    {
        "no_documentation": "no_documentation",
        "query_llm": "query_llm",
    }
)
lang_graph.add_edge("no_documentation", END)
lang_graph.add_edge("query_llm", END)
lang_graph.add_edge("query_llm_no_documents", END)

graph = lang_graph.compile()


def query_llm(question):
    response = graph.invoke({"question": question}, {"run_name": SELECTED_REPOSITORY})
    return response

## langgraph inspired by https://github.com/langchain-ai/langgraph/blob/main/examples/rag/langgraph_rag_agent_llama3_local.ipynb
