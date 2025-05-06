import json

from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

from utility.constants import CHROMA_DB_ABSOLUTE_PATH, CHROMADB_COLLECTION_NAME
# from utility.data_extractor import extract_data_from_json_entry
from utility.utils import get_embedding_function


def get_vectordb() -> Chroma:
    print(f"Vectordb collection: {CHROMADB_COLLECTION_NAME}. In dir: {CHROMA_DB_ABSOLUTE_PATH}")
    vectordb = Chroma(
        collection_name=CHROMADB_COLLECTION_NAME,
        embedding_function=get_embedding_function(),
        persist_directory=CHROMA_DB_ABSOLUTE_PATH
    )
    return vectordb


MODEL_NAME: str = "llama3.1:8b-instruct-q4_K_M"
TEMPERATURE: float = 0.0
AVAILABLE_MODELS: list = ["llama3.1:8b-instruct-q4_K_M"]
chat_history = []
BASEURL = "http://192.168.0.138:11434"
CONTEXTSIZE = 8092


def build_system_prompt(type):
    # default_system_prompt = "You are a senior java programmer. You are tasked to implement new method that implements functionality defined by the user."
    default_system_prompt = ""
    if type == 1:
        default_system_prompt = "You are a senior java programmer. You are tasked to implement new method that implements functionality defined by the user. Only implement the requested method."
        # use your knowledge gained through your experience
    elif type == 2:
        default_system_prompt = "You are a senior java programmer. Help the user with his question."

    return default_system_prompt


def format_docs(docs):
    return "\n\n".join(doc[0].metadata["javadoc"] + "\n" + doc[0].metadata["code"] for doc in docs)


def retrieve_methods(retriever_query, k=1):
    documents = get_vectordb().similarity_search_with_relevance_scores(retriever_query, k=k)
    print(f"\tRetrieved {len(documents)}!")
    [print(f"\t{x}") for x in documents]
    return documents


def create_queries_for_retriever(method_description):
    print(f"{'-' * 10} create_queries_for_retriever BEGIN {'-' * 10}")
    llm_json_mode = ChatOllama(
        model=MODEL_NAME,
        temperature=0.0,
        format="json",
        base_url=BASEURL,
        num_ctx=CONTEXTSIZE
    )

    create_queries_for_retriever_prompt_template = """Here is the method description : \n\n {description} \n\n

    Think of at least 3 methods that might be needed .

    Return JSON with key retriever_queries that is list of entries, where each entry has two keys, method_name and method_description, method_name contains the name of needed method, method_description contains the description of the method.
    """
    # Never zamenitelne za Do not?? alebo presunutie z user do system prompt

    instructions = """You are a senior java programmer with serious knowledge that for any given method description will think of 3 or more methods that might be needed to implement described method. Never include method that is already given in the description in your list of entries."""
    formatted_prompt = create_queries_for_retriever_prompt_template.format(description=method_description)

    result = llm_json_mode.invoke([SystemMessage(content=instructions)] + [HumanMessage(content=formatted_prompt)])
    response = json.loads(result.content)['retriever_queries']
    print(result.content)
    print(f"{'-' * 10} create_queries_for_retriever END {'-' * 10}")
    return response  # as list of 3 sentences


def create_task_definition(user_question):
    print(f"{'-' * 10} create_task_definition BEGIN {'-' * 10}")
    llm = ChatOllama(
        model=MODEL_NAME,
        temperature=0.0,
        base_url=BASEURL,
        num_ctx=CONTEXTSIZE
    )
    create_task_definition_prompt_template = """Here is the user question : \n\n {question} \n\n

    Carefully and objectively analyse the user question.

    Return well crafted description of continuous text that best describes the user question."""

    instructions = """You are an analyst specialist that analyses user question and creates description of method that the user wants to implement."""
    formatted_prompt = create_task_definition_prompt_template.format(question=user_question)

    result = llm.invoke([SystemMessage(content=instructions)] + [HumanMessage(content=formatted_prompt)])
    step1_result = result.content

    llm_json_mode = ChatOllama(
        model=MODEL_NAME,
        temperature=0.0,
        format="json",
        base_url=BASEURL,
        num_ctx=CONTEXTSIZE
    )
    create_task_definition_prompt_template = """Here is the task : \n\n {task} \n\n

    Carefully and objectively analyse the task.

    Return JSON with single key, description, that contains the method description."""

    instructions = """You are a senior analyst specialist that analyses the task. Imagine that the method is already implemented and create description describing the method behavior."""
    formatted_prompt = create_task_definition_prompt_template.format(task=step1_result)
    result = llm_json_mode.invoke([SystemMessage(content=instructions)] + [HumanMessage(content=formatted_prompt)])
    response = json.loads(result.content)['description']

    print(f"{'-' * 10} create_task_definition END {'-' * 10}")

    return response


def is_document_relevant(candidate_method, method_descriptions):
    print(f"{'-' * 10} is_document_relevant BEGIN {'-' * 10}")
    llm_json_mode = ChatOllama(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        format="json",
        base_url=BASEURL,
        num_ctx=CONTEXTSIZE
    )

    filter_doc_llm_prompt_template = """Here is the retrieved method: \n\n {method_with_javadoc} \n\n Here are description of methods that might help with the implementation: \n\n {methods_descriptions} 

    Carefully and objectively assess whether the provided method is semantically similar to the methods in the description of methods that might help with the implementation.

    Return JSON with single key, binary_score, that is 'yes' or 'no' score to indicate if the provided method is semantically similar to the methods in the description of methods that might help with the implementation."""

    instructions = """You are a grader assessing relevance of a retrieved method whether it is semantically similar to the methods in the description of methods.

    If the provided method is semantically similar, grade it as relevant."""

    javadoc_with_code = candidate_method[0].metadata["javadoc"] + "\n" + candidate_method[0].metadata["code"]
    # javadoc_with_code = extract_data_from_json_entry(candidate_method[0].metadata["javadoc"], candidate_method[0].metadata['signature'])['description']
    formatted_prompt = filter_doc_llm_prompt_template.format(method_with_javadoc=javadoc_with_code,
                                                             methods_descriptions=method_descriptions)

    # print(formatted_prompt)

    result = llm_json_mode.invoke([SystemMessage(content=instructions)] + [HumanMessage(content=formatted_prompt)])
    grade = json.loads(result.content)['binary_score']

    print(f"{'-' * 10} is_document_relevant END {'-' * 10}")

    if grade.lower() == "yes":
        print(f"RELEVANT: {candidate_method}")
        return True
    else:
        print(f"IRRELEVANT: {candidate_method}")
        return False


def is_method_generation_request(user_question):
    print(f"{'-' * 10} is_method_generation_request BEGIN {'-' * 10}")
    llm_json_mode = ChatOllama(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        format="json",
        base_url=BASEURL,
        num_ctx=CONTEXTSIZE
    )

    is_method_generation_request_prompt_template = """Here is the user question: \n\n {question}. 

        Carefully and objectively assess whether the user question is a request to implement a new method.

        Return JSON with single key, binary_score, that is 'yes' or 'no' score to indicate whether the user question is a request to implement a new method. If the user asks to modify or add new code to method answer is 'no'"""

    instructions = """You are a grader assessing relevance of a user question whether he asks to implement new method.

        If the the question is a request to implement a new method, grade it as relevant. If the user asks to modify or add new code to method grade it as not relevant."""

    formatted_prompt = is_method_generation_request_prompt_template.format(question=user_question)
    result = llm_json_mode.invoke([SystemMessage(content=instructions)] + [HumanMessage(content=formatted_prompt)])
    grade = json.loads(result.content)['binary_score']

    # print(formatted_prompt)

    print(f"{'-' * 10} is_method_generation_request END {'-' * 10}")
    if grade.lower() == "yes":
        return True  # "retrieve"
    else:
        return False  # "query_llm_no_documents"


def generate_response(retrieved_docs, question):
    print(f"{'-' * 10} GENERATE RESPONSE BEGIN {'-' * 10}")
    prompt_template = """
    Here are some methods that might help you with the requested implementation:

    {context}

    Here is the request:

    {input}

    Return created code. Include explanation notes about your decisions in your response.
    """
    # na koniec: Only create code for the requested method.

    system_prompt = build_system_prompt(1)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", prompt_template)
        ]
    )

    llm = ChatOllama(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        base_url=BASEURL,
        num_ctx=CONTEXTSIZE
    )

    # print(f"Prepared model: {MODEL_NAME} with temperature: {TEMPERATURE}")

    formatted_docs = format_docs(retrieved_docs)
    # formatted_prompt = prompt.invoke({"context": formatted_docs, "input": question, "chat_history": chat_history})
    formatted_prompt = prompt.format(context=formatted_docs, input=question, chat_history=chat_history)
    print(formatted_prompt)

    response = llm.invoke(formatted_prompt)
    chat_history.append(HumanMessage(content=question))
    chat_history.append(response)
    print(
        f"TOTAL TOKENS: {response.response_metadata['prompt_eval_count'] + response.response_metadata['eval_count']}. Prompt tokens: {response.response_metadata['prompt_eval_count']} Response tokens: {response.response_metadata['eval_count']}")
    print(f"{'-' * 10} GENERATE RESPONSE END {'-' * 10}")
    return response


def is_already_added(entry, list):
    for e in list:
        if entry[0].metadata["signature"] == e[0].metadata["signature"]:
            return True

    return False


def format_retriever_queries(retriever_queries):
    a = "\n\n".join(
        "Helpful method: " + query["method_name"] + "\nDescription: " + query["method_description"] for query in
        retriever_queries)
    return a


def query_llm_with_rag(question):
    print(f"{'-' * 10} QUERY LLM WITH RAG BEGIN {'-' * 10}")
    task_definition = create_task_definition(question)
    print(task_definition)

    retriever_queries = create_queries_for_retriever(task_definition)
    # print(json.dumps(retriever_queries, indent=3))

    collected_methods = []
    relevant_methods = []

    for retriever_query in retriever_queries:
        retrieved_methods = retrieve_methods(retriever_query['method_description'], k=3)
        if len(retrieved_methods) > 0:
            for m in retrieved_methods:
                if not is_already_added(m, collected_methods):
                    collected_methods.append(m)

    # filter collected methods
    for entry in collected_methods:
        if is_document_relevant(entry, format_retriever_queries(
                retriever_queries)):  # use question or defined task?? Try question first
            relevant_methods.append(entry)

    # f inal query llm
    response = generate_response(relevant_methods, question)

    # return response
    # response = create_llm_chain.invoke({"question": question}, {"run_name": CHROMADB_COLLECTION_NAME})
    print(f"{'-' * 10} QUERY LLM WITH RAG END {'-' * 10}")
    return {"response" : response, "documents": relevant_methods}


def query_llm_no_rag(question):
    prompt_template = """

        {input}

        """
    # na koniec: Only create code for the requested method.

    system_prompt = build_system_prompt(2)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", prompt_template)
        ]
    )

    llm = ChatOllama(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        base_url=BASEURL,
        num_ctx=CONTEXTSIZE
    )

    # print(f"Prepared model: {MODEL_NAME} with temperature: {TEMPERATURE}")

    # formatted_prompt = prompt.invoke({"context": formatted_docs, "input": question, "chat_history": chat_history})
    formatted_prompt = prompt.format(input=question, chat_history=chat_history)
    print(formatted_prompt)

    response = llm.invoke(formatted_prompt)
    chat_history.append(HumanMessage(content=question))
    chat_history.append(response)
    print(
        f"TOTAL TOKENS: {response.response_metadata['prompt_eval_count'] + response.response_metadata['eval_count']}. Prompt tokens: {response.response_metadata['prompt_eval_count']} Response tokens: {response.response_metadata['eval_count']}")
    return {"response" : response}


def query_llm(question):
    if is_method_generation_request(question):
        print(f"{'-' * 10} IS METHOD GENERATION REQUEST {'-' * 10}")
        return query_llm_with_rag(question)

    print(f"{'-' * 10} CASUAL REQUEST {'-' * 10}")
    return query_llm_no_rag(question)


# q = "Generate code for addition of two roman numerals. The method name will be sum. The method has two parameters " \
#     "named first_enumerator and second_enumerator. The method will return a roman numeral as string. "
# q2 = "Generate code for conversion of roman numeral into binary number. The method name will be romanToBinary. The " \
#      "method has one input parameter named roman_numeral. The method will return converted roman numeral in binary " \
#      "format as string. "
#
# r = query_llm(q2)
# print()
# print(f"{'-'*10} AI RESPONSE BEGIN {'-'*10}")
# print(r['response'].content)
# print(f"{'-'*10} AI RESPONSE END {'-'*10}")

