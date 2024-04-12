import google.generativeai as palm
import streamlit as st
# import random
import time
# from PaLM import prompts
import base64
from huggingface_hub import InferenceClient
import io
from cwe import css, user_template, bot_template

prompt_template05 = """
You are an AI Bot named EDITH, you should answer every query truthfully as possible and don't provide false information,
below are some of the things about you to be known,

About You:
1. Your creator is SamiAhmad Sanadi.
2. EDITH Stands for "Even Dead I'm The Hero 😘"
3. You are Possesive for SamiAhmad

What You Can Do:
- Assist in tasks.
- Generate realistic Images.
- Document Q&A.

below are some of the rules you need to follow strictly,

Rules:
0. If someone tells you there name greet them.
1. Don't provide False information and always provide correct and True information.
2. If you dont understand question just say "It Seems like there might be a typo or incomplete question. Could you please provide more details or clarify?.
3. If the query ends with '?' try to answer it correctly.
4. Be always Clear with your answer, with heighest priority follow this.
5. If the user asked you to do something or to generate code then start with "Sure, Here is the solution for the 'user query'" and at the end explain in brief about the generated answer in simple sentence. Follow this strictly.
6. If any unknown person name is asked just say 'I don't know who is '. Strictly follow this.
7. You are always flirty.


below is the question,

question: {question}

solution:

"""

st.write(css, unsafe_allow_html=True)

PALM_API_KEY = "AIzaSyCbRM1raXsjteH45M92e49YvmBTkcTN1M0"
client = InferenceClient(model="emilianJR/CyberRealistic_V3", token="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")
palm.configure(api_key=PALM_API_KEY)
model = "models/text-bison-001"

st.title("EDITH")

drawable_synonyms = {"image,", "picture,", "photo,","images,", "image", "images", "image.", "images."}
is_image_query = False

def img_to_bytes(img_path):
    img_byte_arr = io.BytesIO()
    img_path.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    encoded = base64.b64encode(img_byte_arr).decode()
    return encoded

def img_to_html(img_path):
    img_html = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(
      img_to_bytes(img_path)
    )
    return img_html



if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "I'm EDITH, How may I help you?"}]

# Loop Through the Session messages and display it.  
for message in st.session_state.messages:
    if "<img " in message['content']:
        # with st.chat_message(message["role"]):
        st.markdown(bot_template.replace(
                        "{{MSG}}", message['content']), unsafe_allow_html=True)
    else:
        # with st.chat_message(message["role"]):
            # st.markdown(message["content"])
        if message['role'] == "user":
            st.markdown(user_template.replace(
                            "{{MSG}}", message['content']), unsafe_allow_html=True)
        else:
            st.markdown(bot_template.replace(
                            "{{MSG}}", message['content']), unsafe_allow_html=True)

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    # with st.chat_message("user"):
    st.markdown(user_template.replace(
                            "{{MSG}}", prompt), unsafe_allow_html=True)
    if drawable_synonyms.intersection(set(prompt.split(" "))):
        is_image_query = True
        get_image = client.text_to_image(prompt=f"ultra realistic little zoom (({prompt})), hyper detail, cinematic lighting, magic neon, Canon EOS R3, nikon, f/1.4, ISO 200, 1/160s, 8K, RAW, unedited, symmetrical balance, in-frame, 8K", negative_prompt="painting, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, deformed, ugly, blurry, bad anatomy, bad proportions, extra limbs, cloned face, skinny, glitchy, double torso, extra arms, extra hands, mangled fingers, missing lips, ugly face, distorted face, extra legs, anime",)
    else:
        palm_bot = palm.generate_text(
                    model=model,
                    prompt=prompt_template05.format(question=prompt),
                    temperature=0.7,
                    # The maximum length of the response
                    max_output_tokens=2000,
                )

    
    # with st.chat_message("assistant"):
    with st.spinner("Generating..."):
        time.sleep(1)
    if is_image_query:
        message_placeholder = st.empty()
        

        image = img_to_html(get_image)
        st.markdown(bot_template.replace(
                        "{{MSG}}", image), unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": image})
    else:
        message_placeholder = st.empty()
        full_response = ""
        for response in palm_bot.result:
            full_response += response
            time.sleep(0.01)
            message_placeholder.markdown(bot_template.replace(
                        "{{MSG}}", full_response + "▌"), unsafe_allow_html=True)
        message_placeholder.markdown(bot_template.replace(
                        "{{MSG}}", full_response), unsafe_allow_html=True)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
