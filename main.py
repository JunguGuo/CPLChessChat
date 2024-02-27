import openai
import streamlit as st
import re
import pandas as pd
# from elevenlabs import generate, play, set_api_key
import streamlit.components.v1 as components
from PIL import Image
from components.sidebar import sidebar
import numpy as np

# st.markdown("<h1 style='text-align: center; color: black;'>John G. White Chess Collection</h1>", unsafe_allow_html=True)
st.set_page_config(page_title="Chess Chat", page_icon="♟️",
                   layout="centered", initial_sidebar_state="collapsed")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stActionButton .css-1a1tcp.e1ewe7hr3 {display: none;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

sidebar()

# password = st.text_input('Enter password', type= 'password')


# elevenlabs api
# set_api_key("d862c7b12db7211fc86caa76d3c8d09f")


#
openai.api_key = st.secrets["OPENAI_API"]
df = pd.read_csv('collection.csv')
maps_df = df.dropna(subset=['longitude', 'latitude'])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4-0125-preview"

if "option_prompt" not in st.session_state:
    st.session_state["option_prompt"] = ""

if "option0_asked" not in st.session_state:
    st.session_state["option0_asked"] = False
if "option1_asked" not in st.session_state:
    st.session_state["option1_asked"] = False
if "option2_asked" not in st.session_state:
    st.session_state["option2_asked"] = False
if "option3_asked" not in st.session_state:
    st.session_state["option3_asked"] = False
if "option4_asked" not in st.session_state:
    st.session_state["option4_asked"] = False

if "messages" not in st.session_state:
    st.session_state.messages = []
    system_content = """You are a helpful assistant."""
    st.session_state.messages.append(
        {"role": "system", "content": system_content})
    st.session_state.messages.append(
        {"role": "assistant", "content": """Hello!"""})


# auto scroll to bottom
js = f"""
<script>
    function scroll(dummy_var_to_force_repeat_execution){{
        var textAreas = parent.document.querySelectorAll('section.main');
        for (let index = 0; index < textAreas.length; index++) {{
            textAreas[index].style.color = 'red'
            textAreas[index].scrollTop = textAreas[index].scrollHeight;
        }}
    }}
    scroll({len(st.session_state.messages)})
</script>
"""
st.components.v1.html(js)


def extract_id_numbers(chat_response):
    id_numbers = []
    pattern = r"ID (\d+)"
    matches = re.findall(pattern, chat_response)

    for match in matches:
        id_numbers.append(int(match))

    return id_numbers


def truncate(string, length):
    if len(string) <= length:
        return string
    else:
        return string[:length] + "..."


def process_prompt(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # , avatar= "😼"
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        msgs = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        # msgs[-1]["content"] += " " + "(Respond in the tone of a witty and eccentric cat)"
        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=msgs,
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

        id_numbers = extract_id_numbers(full_response)

        if id_numbers:
            try:
                records = list(map(lambda id: df[df['ID'] == id], id_numbers))
                tabs = st.tabs(list(map(lambda record:
                                        truncate(
                                            'ID ' + str(record['ID'].values[0]) + ": " + record['Title'].values[0], 25),
                                        records)))

                for i in range(len(records)):
                    with tabs[i]:
                        st.subheader(f"{records[i]['Title'].values[0]}")
                        st.image(f"./images/{records[i]['ID'].values[0]}.jpg",
                                 caption=f"{records[i]['ID'].values[0]} : {records[i]['Title'].values[0]} -- {records[i]['Author'].values[0]}")
                        # Chess set

                        ID = str(records[i]['ID'].values[0])
                        # st.write(str(type(records[i]['ID'])))
                        if ID == "21":
                            components.html("""
                                            <div class="sketchfab-embed-wrapper"> <iframe title="Lewis Chess Set" frameborder="0" allowfullscreen mozallowfullscreen="true" webkitallowfullscreen="true" allow="autoplay; fullscreen; xr-spatial-tracking" xr-spatial-tracking execution-while-out-of-viewport execution-while-not-rendered web-share width="640" height="480" src="https://sketchfab.com/models/eddbebab12424c8aa610a21b9b7e19e5/embed"> </iframe> <p style="font-size: 13px; font-weight: normal; margin: 5px; color: #4A4A4A;"> <a href="https://sketchfab.com/3d-models/lewis-chess-set-eddbebab12424c8aa610a21b9b7e19e5?utm_medium=embed&utm_campaign=share-popup&utm_content=eddbebab12424c8aa610a21b9b7e19e5" target="_blank" rel="nofollow" style="font-weight: bold; color: #1CAAD9;"> Lewis Chess Set </a> by <a href="https://sketchfab.com/britishmuseum?utm_medium=embed&utm_campaign=share-popup&utm_content=eddbebab12424c8aa610a21b9b7e19e5" target="_blank" rel="nofollow" style="font-weight: bold; color: #1CAAD9;"> The British Museum </a> on <a href="https://sketchfab.com?utm_medium=embed&utm_campaign=share-popup&utm_content=eddbebab12424c8aa610a21b9b7e19e5" target="_blank" rel="nofollow" style="font-weight: bold; color: #1CAAD9;">Sketchfab</a></p></div>
                                            """,
                                            height=480,
                                            )
                        if ID == "4":
                            st.video(
                                "https://www.youtube.com/watch?v=xmZC8bUU1MI")
                        st.map(df[df['ID'] == records[i]['ID'].values[0]], 4)
                        # if ID == "21":
                        #     st.write("hahaha")
                        # else:
                        #     pass
                        # components.html("""<div class="sketchfab-embed-wrapper"> <iframe title="Lewis Chess Set" frameborder="0" allowfullscreen mozallowfullscreen="true" webkitallowfullscreen="true" allow="autoplay; fullscreen; xr-spatial-tracking" xr-spatial-tracking execution-while-out-of-viewport execution-while-not-rendered web-share width="640" height="480" src="https://sketchfab.com/models/eddbebab12424c8aa610a21b9b7e19e5/embed"> </iframe> <p style="font-size: 13px; font-weight: normal; margin: 5px; color: #4A4A4A;"> <a href="https://sketchfab.com/3d-models/lewis-chess-set-eddbebab12424c8aa610a21b9b7e19e5?utm_medium=embed&utm_campaign=share-popup&utm_content=eddbebab12424c8aa610a21b9b7e19e5" target="_blank" rel="nofollow" style="font-weight: bold; color: #1CAAD9;"> Lewis Chess Set </a> by <a href="https://sketchfab.com/britishmuseum?utm_medium=embed&utm_campaign=share-popup&utm_content=eddbebab12424c8aa610a21b9b7e19e5" target="_blank" rel="nofollow" style="font-weight: bold; color: #1CAAD9;"> The British Museum </a> on <a href="https://sketchfab.com?utm_medium=embed&utm_campaign=share-popup&utm_content=eddbebab12424c8aa610a21b9b7e19e5" target="_blank" rel="nofollow" style="font-weight: bold; color: #1CAAD9;">Sketchfab</a></p></div>""",height=480,)
            except Exception:
                pass

        # for id in id_numbers:
        #     record = df[df['ID'] == id]
        #     title = record['Title'].values[0]
        #     author = record['Author'].values[0]
        #     st.image (f"./images/{id}.jpg", caption = f"{id} : {title} -- {author}" )
            # st.write (f"./images/{id}.jpg")

        # try:
        #     audio = generate( text=full_response, voice="Bella", model='eleven_monolingual_v1')
        #     st.audio(audio)
        # except Exception:
        #     print("audio api error")

        # Chess game
        if "opening" in full_response:
            components.html("""<iframe id="10790895" allowtransparency="true" frameborder="0" style="width:100%;border:none;" src="//www.chess.com/emboard?id=10790895"></iframe><script>window.addEventListener("message",e=>{e['data']&&"10790895"===e['data']['id']&&document.getElementById(`${e['data']['id']}`)&&(document.getElementById(`${e['data']['id']}`).style.height=`${e['data']['frameHeight']+30}px`)});</script>""",
                            height=400,
                            )

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})

        options = [""":question: What's the oldest chess book in the collection?""",
                   """:question: What are some extraordinary chess sets in the collection? """,
                   """:question: Do you hold any treasures from the magical world of Harry Potter? """,
                   """:question: Do you have any items connected to the Netflix sensation, 'Queen's Gambit'?""",
                   """:question: Can you guide me through the strategic intricacies of a famous chess opening?"""
                   ]

        # This doesn't work...
        # for i in range(len(options)):
        #     st.button(options[i], on_click = lambda: st.session_state.update({"option_prompt": options[i]}))
        st.divider()
        if (st.session_state["option0_asked"] == False):
            st.button(options[0], on_click=lambda: (
                st.session_state.update({"option_prompt": options[0]}),
                st.session_state.update({"option0_asked": True})
            ))
        if (st.session_state["option1_asked"] == False):
            st.button(options[1], on_click=lambda: (
                st.session_state.update({"option_prompt": options[1]}),
                st.session_state.update({"option1_asked": True})
            ))
        if (st.session_state["option2_asked"] == False):
            st.button(options[2], on_click=lambda: (
                st.session_state.update({"option_prompt": options[2]}),
                st.session_state.update({"option2_asked": True})
            ))
        if (st.session_state["option3_asked"] == False):
            st.button(options[3], on_click=lambda: (
                st.session_state.update({"option_prompt": options[3]}),
                st.session_state.update({"option3_asked": True})
            ))
        if (st.session_state["option4_asked"] == False):
            st.button(options[4], on_click=lambda: (
                st.session_state.update({"option_prompt": options[4]}),
                st.session_state.update({"option4_asked": True})
            ))
        # st.button(options[0], on_click = lambda: st.session_state.update({"option_prompt": options[0]}))
        # st.button(options[1], on_click = lambda: st.session_state.update({"option_prompt": options[1]}))
        # st.button(options[2], on_click = lambda: st.session_state.update({"option_prompt": options[2]}))
        # st.button(options[3], on_click = lambda: st.session_state.update({"option_prompt": options[3]}))
        # st.button(options[4], on_click = lambda: st.session_state.update({"option_prompt": options[4]}))

    return


def main():

    st.header("Chess Chat")
    # st.title("Chess Chat")
    # st.subheader("John G. White Chess Collection at Cleveland Public Library")
    # image = Image.open('chess.jpg')
    # st.image(image)

    #
    # st.map(maps_df)
    # components.html("""
    #                 <div class="sketchfab-embed-wrapper"> <iframe title="Lewis Chess Set" frameborder="0" allowfullscreen mozallowfullscreen="true" webkitallowfullscreen="true" allow="autoplay; fullscreen; xr-spatial-tracking" xr-spatial-tracking execution-while-out-of-viewport execution-while-not-rendered web-share width="640" height="480" src="https://sketchfab.com/models/eddbebab12424c8aa610a21b9b7e19e5/embed"> </iframe> <p style="font-size: 13px; font-weight: normal; margin: 5px; color: #4A4A4A;"> <a href="https://sketchfab.com/3d-models/lewis-chess-set-eddbebab12424c8aa610a21b9b7e19e5?utm_medium=embed&utm_campaign=share-popup&utm_content=eddbebab12424c8aa610a21b9b7e19e5" target="_blank" rel="nofollow" style="font-weight: bold; color: #1CAAD9;"> Lewis Chess Set </a> by <a href="https://sketchfab.com/britishmuseum?utm_medium=embed&utm_campaign=share-popup&utm_content=eddbebab12424c8aa610a21b9b7e19e5" target="_blank" rel="nofollow" style="font-weight: bold; color: #1CAAD9;"> The British Museum </a> on <a href="https://sketchfab.com?utm_medium=embed&utm_campaign=share-popup&utm_content=eddbebab12424c8aa610a21b9b7e19e5" target="_blank" rel="nofollow" style="font-weight: bold; color: #1CAAD9;">Sketchfab</a></p></div>
    #                 """,
    #                 height=480
    #                 )

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if (len(st.session_state.messages) == 2):
        options = [""":question: Tell me more about the John G. White chess collection. """,
                   """:question: Can you share some of the fascinating treasures found in the collection """,
                   """:question: What are some of the prominent themes and stories featured in the collection? """
                   ]
        # This doesn't work...
        # for i in range(len(options)):
        #     st.button(options[i], on_click = lambda: st.session_state.update({"option_prompt": options[i]}))
        st.divider()
        st.button(options[0], on_click=lambda: st.session_state.update(
            {"option_prompt": options[0]}))
        st.button(options[1], on_click=lambda: st.session_state.update(
            {"option_prompt": options[1]}))
        st.button(options[2], on_click=lambda: st.session_state.update(
            {"option_prompt": options[2]}))

    if st.session_state["option_prompt"]:
        process_prompt(st.session_state["option_prompt"])
        st.session_state["option_prompt"] = ""
        st.chat_input(
            "What do you like to know about the John G. White chess collection?")
    else:
        if prompt := st.chat_input("What do you like to know about the John G. White chess collection?"):
            process_prompt(prompt)


main()
# if password == 'cambly123':
#     main()
