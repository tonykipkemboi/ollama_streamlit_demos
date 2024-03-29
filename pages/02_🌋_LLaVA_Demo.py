import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO
import json

st.set_page_config(
    page_title="LLaVA Playground",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded",
)


def icon(emoji: str):
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


def img_to_base64(image):
    """
    Convert an image to base64 format.

    Args:
        image: PIL.Image - The image to be converted.
    Returns:
        str: The base64 encoded image.
    """
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def generate_llava_responses(response_text):
    """Yield responses from the LLaVA API response."""
    for line in response_text.splitlines():
        json_obj = json.loads(line)
        if "response" in json_obj and not json_obj["done"]:
            yield json_obj["response"]
        elif json_obj["done"]:
            break


def main():
    icon("🌋")
    st.subheader("LLaVA 1.6 Playground", divider="red", anchor=False)

    if "chats" not in st.session_state:
        st.session_state.chats = []

    if "uploaded_file_state" not in st.session_state:
        st.session_state.uploaded_file_state = None

    uploaded_file = st.file_uploader(
        "Upload an image for analysis", type=["png", "jpg", "jpeg"]
    )

    col1, col2 = st.columns(2)

    with col1:
        container1 = st.container(height=500, border=True)
        with container1:
            if uploaded_file is not None:
                st.session_state.uploaded_file_state = uploaded_file.getvalue()
                image = Image.open(BytesIO(st.session_state.uploaded_file_state))
                st.image(image, caption="Uploaded image")

    with col2:
        container2 = st.container(height=500, border=True)

        if uploaded_file is not None:
            for message in st.session_state.chats:
                avatar = "🌋" if message["role"] == "assistant" else "🫠"
                with container2.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])

            if user_input := st.chat_input(
                "Question about the image...", key="chat_input"
            ):
                st.session_state.chats.append({"role": "user", "content": user_input})
                container2.chat_message("user", avatar="🫠").markdown(user_input)

                image_base64 = img_to_base64(image)
                API_URL = "http://localhost:11434/api/generate"
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
                data = {
                    "model": "llava",
                    "prompt": user_input,
                    "images": [image_base64],
                }

                with container2.chat_message("assistant", avatar="🌋"):
                    with st.spinner("wait for it..."):
                        response = requests.post(API_URL, json=data, headers=headers)
                    if response.status_code == 200:
                        response_generator = generate_llava_responses(response.text)
                        llava_responses = " ".join(
                            response for response in response_generator
                        )
                        st.markdown(llava_responses)
                    else:
                        st.error("Failed to get a response from LLaVA.")

                st.session_state.chats.append(
                    {"role": "assistant", "content": llava_responses}
                )


if __name__ == "__main__":
    main()
