import ollama
import streamlit as st

from openai import OpenAI

st.set_page_config(
    page_title="Ollama x Streamlit UI",
    page_icon="🎈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def icon(emoji: str):
    """
    Shows an emoji as a Notion-style page icon.

    :param emoji: The emoji to display.

    Returns:
        None
    """

    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


def extract_model_names(models_info: list) -> tuple:
    """
    Extracts the model names from the models information.

    :param models_info: A dictionary containing the models' information.

    Return:
        A tuple containing the model names.
    """

    return tuple(
        model["name"]
        for model in models_info["models"]
        if model["name"].lower() != "llava:latest"
    )


def main():
    """
    The main function that runs the application.
    """

    icon("🚀")
    st.subheader("Ollama Playground", divider="red", anchor=False)

    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # required, but unused
    )

    models_info = ollama.list()
    available_models = extract_model_names(models_info)

    if available_models:
        selected_model = st.selectbox(
            "Pick a model available locally on your system ↓", available_models
        )

    else:
        st.warning("You have not pulled any model from Ollama yet!", icon="⚠️")
        # if st.toggle("Toggle to download model"):
        #     with st.spinner("Pulling model"):
        #         ollama.pull(model)

        st.page_link("https://ollama.com/library", label="Find models here", icon="🤖")
        st.stop()

    message_container = st.container(height=500, border=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "😎"
        with message_container.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter a prompt here..."):
        try:
            st.session_state.messages.append({"role": "user", "content": prompt})

            message_container.chat_message("user", avatar="😎").markdown(prompt)

            with message_container.chat_message("assistant", avatar="🤖"):
                with st.spinner("wait for it..."):
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )
                # stream response
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(e, icon="⛔️")


if __name__ == "__main__":
    main()
