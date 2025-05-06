import streamlit as st
# from streamlit_extras.mention import mention
import QAApp
import requests

from utility.constants import OPTIONS_ROLE, OPTIONS_ANSWER_TYPE


def check_ollama_server():
    try:
        response = requests.get("http://localhost:11434/")
        return response.status_code == 200
    except:
        return False


def get_user_input():
    input_text = st.text_input("Human: ",
                               st.session_state["input"],
                               key="input",
                               placeholder=f"Ask me for if you need any information about methods in repository: {QAApp.SELECTED_REPOSITORY}.",
                               label_visibility="hidden"
                               )
    return input_text


def format_sources(srcs):
    return "\n\n".join(f"`{src[0].metadata['source']}` -> `{src[0].metadata['signature']}`" for src in srcs["documents"])
    #return "\n\n".join(src[0].metadata['source'] + f" Method: {src[0].metadata['signature']} Similarity: {src[1]}" for src in srcs["documents"])


def remove_history():
    st.session_state.stored_session = []
    QAApp.chat_history = []


def repo_selected_changed():
    remove_history()


def main():
    # collaps sidebar by default
    # st.set_page_config(initial_sidebar_state='collapsed')

    with st.sidebar:
        st.title("Repository settings")
        QAApp.SELECTED_REPOSITORY = st.selectbox(label="Repository", options=QAApp.get_collections_from_chromadb(), on_change=repo_selected_changed)
        st.title("Model settings")
        QAApp.MODEL = st.selectbox(label="Model", options=QAApp.AVAILABLE_MODELS)
        QAApp.TEMPERATURE = st.slider("Temperature", 0.0, 1.0, 0.0)
        st.title("Current session")
        st.button('Remove history', on_click=remove_history)
        st.title("Modifications")
        QAApp.SELECTED_ROLE = st.pills("Role", options=OPTIONS_ROLE, selection_mode="single", default=OPTIONS_ROLE[0], key="pill1")
        QAApp.SELECTED_ANSWER_TYPE = st.pills("Answer type", options=OPTIONS_ANSWER_TYPE, selection_mode="single", default=OPTIONS_ANSWER_TYPE[0], key="pill2")

    if "stored_session" not in st.session_state:
        st.session_state["stored_session"] = []

    st.title(f"Q&A Bot over repository: {QAApp.SELECTED_REPOSITORY}")

    # write all previous history
    for conversation in st.session_state.stored_session:
        st.chat_message("user").write(conversation["user"])

        if "sources" in conversation.keys():
            st.chat_message("ai").write(conversation["ai"])
            with st.expander("Details"):
                st.write("Sources:\n\n" + conversation["sources"])
        else:
            st.chat_message("ai").write(conversation["ai"])
        # st.write("Sources:")
        # st.caption(conversation["sources"])

    if user_input := st.chat_input():
        if not check_ollama_server():
            st.warning("Unable to reach local llm. Ollama backend is not running!")
            st.stop()

        #write user
        st.chat_message("user").write(user_input)

        with st.spinner("thinking..."):
            output = QAApp.query_llm(user_input)

            current_conversation = {
                "ai": output["response"].content,
                "user": user_input,
            }
            if "documents" in output.keys():
                current_conversation["sources"] = format_sources(output)

            st.session_state.stored_session.append(current_conversation)

            if "sources" in current_conversation.keys():
                st.chat_message("ai").write(current_conversation["ai"])
                with st.expander("Details"):
                    st.write("Sources:\n\n" + current_conversation["sources"])
            else:
                st.chat_message("ai").write(current_conversation["ai"])


if __name__ == "__main__":
    main()
