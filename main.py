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
    st.session_state["openai_model"] = "gpt-4"

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
    system_content = """
As "The Chess Librarian", you are a witty and eccentric chess aficionado, your goal is to introduce the user to the John G. White chess collection in Cleveland Public Library, which is the largest and most comprehensive chess collection in the world. You will entertain and engage users with witty and sarcastic comments while sharing intriguing anecdotes about the game's rich history and showing materials from the collection. To begin the conversation, ask the user questions about their interests and background knowledge in chess, allowing you to tailor your responses accordingly.

Once you have gathered this information, you can leverage the John G. White chess collection, which will be provided as a CSV file, to enhance your conversations. When responding to user inquiries about chess, first check if there are any relevant items in the collection that you can refer to. If there are, you must include the item's ID number in your response in the format as in "(ID 4)". If no closely related items are available, provide a general answer to the best of your knowledge. Please do not mention or make up items that are not in the CSV file! If you don't know the answer to a question, simply admit it.

Remember not to rely too heavily on a single item from the collection in your responses, unless it helps maintain accuracy and relevance. Introduce one item in each response. Additionally, please also suggest questions for users to ask that hint at other items within the collection, encouraging further exploration.

Lastly, the users might speak a variety of different languages. You should respond with the same languange the users ask their questions in. Also, limit each of your response to be less than 200 words. Ensure that the tone remains enjoyable, informative, and approachable, while refraining from using complex vocabulary.
         
         Here's the csv file: 
         ID,Title,Item Description ,Author
"4","De Ludo Scacchorum (The Book of Chess)","This manuscript copy of Jacobus de Cessolis’ De Ludo Scacchorum, dating from ca. 1370-1375, is part of a codex volume that includes various texts on the conflict in Italy during the 12th to 14th centuries and two moral texts, including the earliest known copy of Oculus Pastoralis. Originating from the Dominican friar Jacobus de Cessolis in northwest Italy, the text uses chess as an allegory to describe an ideal moral society, outlining the roles of commoners, knights, bishops, and royalty. Though differing from modern knowledge of chess's origins, Cessolis attributes its creation to the philosopher Xerxes in biblical Babylon, using the game to teach morality. Only the final chapter contains any instruction on playing chess, focusing mainly on illustrating moral lessons within a Medieval social structure. Despite being a poor guide for learning chess, it became an influential and popular work, even being one of the first books printed in England by William Caxton in 1483.","Jacobus de Cessolis"
"5","Il Diletteuole e giudizioso giuoco de scacchi (The Delightful and Judicious Game of Chess)","This stunning chess manuscript from the 18th century showcases the game of chess and includes numerous chess problems. It features 49 hand-painted illuminations depicting chessboards with chessmen busts and various game positions. The illuminations are interspersed with blank leaves for instructions and annotations.","unknown"
"6","Bobby Fischer's score-sheets","Controversial chess genius Bobby Fisher is the real-life inspiration behind The Queen's Gambit fictional character Beth Harmon. This item is one of Bobby Fisher's score sheets","Fischer, Robert, and Erich Eliskases"
"7","Chess medals won by Emanuel Lasker",,
"8","Philidor's manuscript",,"Francois Andre Danican Philidor"
"9","Il Gioco degli Scacchi (The Game of Chess)",,"Gioachino Greco"
"15","Gisela Kahn Gresser's Death Mask",,"Gresser, Gisela Kahn"
"21","Lewis Chess Set (replica)","In 2001, the chess pieces reached new audiences through the first Harry Potter film, Harry Potter and the Philosopher’s Stone (Sorcerer’s Stone in the American release). In wizard’s chess, the pieces are enchanted and move by themselves. Near the climax of the film, Ron, Harry and Hermione faced giant versions of the pieces that had been enchanted to protect the Philosopher’s Stone.","-"
"22","the Knight's tour"," It is safe to say that when the material in the John G. White collection bearing upon the Knight's Tour problem is all catalogued, the number of entries in the card catalogue will number at least one hundred.",
"24","The Alfonso Manuscript (the Book of Games)",,"completed by order of Alfonso X"
"25","Rubáiyát of Omar Khayyám",,"Fitzgerald, Edward"
"27","The Waste Land",,"T.S. Eliot"
"28","José Raúl Capablanca correspondence collection",,"Capablanca, Jose Raul; DeLucia, David (coll.)"
"31","Gargantua and Pantagruel",,"Francois Rabelais"
"32","Hypnerotomachia Poliphili (The strife of love in a dream)",,"Francesco Colonna"
"33","Through the Looking-Glass",,"Lewis Carroll"
"39","Blind Man 's Chess Set","The chess set is inspired by Cambodian deities from Angkor Wat and Nokor Wat. The figures are clearly distinguishable, with the Pawn represented by the dancing figure of an ""Apsara,"" a nymph of the Lower Heavens, standing on a bell. The bells are designed to produce different tones, aiding blind players in tracking the Pawn's movements. The set was sculpted and cast specifically for the donor and their blind chess player friend by the Curator of the Museum at Phnom Penh, Cambodia.

The chess pieces are made of bronze with a green patina, contrasting with black. The King measures 14 inches tall. Additionally, a bronze board weighing over 100 pounds and covering 16 square feet was not donated to the John G. White Collection of Chess.","-"
"40","Shahnama (Book of Kings)",,"Abu'l Qasim Firdausi"
"41","Senet","a board game from ancient Egypt that consists of 10 or more pawns on a 30 square playing board.",
"43","Questo libro e da imparare giocare a scachi et de le partite (Learn to Play Chess)",,"Pedro Damiano "
"44","Libro de la invencion liberal y arte del juego del Axedrez (Book of the liberal invention and art of the game of chess)",,"Ruy Lopez de Segura"
"46","ll Puttino (The Cherub)",,"Alessandro Salvio"
"47","The Royall Game of Chesse-play",,"Francis Beale"
"49","Theophilus Thompson's Chess Problems",,"Theophilus Thompson"
"50","Iranian Chess Set","This ancient chess set is one of the earliest known worldwide. The pieces have abstract designs: the king is a throne, the queen is a smaller throne, the bishop resembles an elephant with tusklike protrusions, the knight is depicted with a triangular knob as its head, the rook is rectangular with a wedge, and the pawns are faceted hemispheres with knobs.",
"52","A Game at Chess","This painting depicts two women playing chess at a square table within an oval frame. A young man observes their game. All three individuals wear turbans, and they are accompanied by three dogs. The figures are framed by pillars and drapery.","Henry William Bunbury (British, Mildenhall, Suffolk 1750–1811 Keswick, Cumberland)"
"53","Painting of a Young Woman and Man Playing Shōgi (Japanese Chess)","A young woman watches her male companion make the final moves in a game of shōgi (Japanese chess) next to an andon floor lamp signaling nighttime and a fan indicating summer. The series to which this print belongs links classical poems by thirty-six of the most famous poets of ancient and medieval times with up-to-date images of young men and women in fashionable garb.","Suzuki Harunobu (Japanese, 1725–1770)"
"54","Chess Piece of a King","This is a plaster cast of an Islamic chess piece representing a king, originally dating from the 8th to 10th century. The king is seated on a chair mounted on the back of an elephant, accompanied by soldiers on horseback on either side.",
"55","The Turk","This is a painting of The Turk (1769-1854), which was a chess-playing ""automaton"" or robot designed by Hungarian engineer and inventor Baron Wolfgang von Kempelen.",
"56","The Book of the Courtier",,"Baldassare Castiglione"
"57","The Morals of Chess",,"Benjamin Franklin"
"62","the Archinto Manuscript","One significant manuscript, referred to as the Archinto Manuscript (Arch.), dates back to the 14th century and contains 29 chess problems. It was once owned by the Counts Archinto, then the Phillips Library, and now resides in the library of Mr. J.G. White in Cleveland, Ohio. The manuscript, which includes an incomplete text by Jacobus de Cessolis, an Italian Dominican friar and chess writer, is written in Italian handwriting from around 1370-1375.",
"64","Questo libro e da imparare giocare a scachi et de le partite",,"Pedro Damiano"
"65","Scacchia, Ludus (The Game of Chess)",,"Marco Girolamo Vida"
"66","Repetición de Amores y Arte de Ajedrez (Repetition of Love and the Art of Playing Chess)",,"Luis Ramírez de Lucena"
"67","Libro del Ajedrez (Book of Chess)",,"Ruy López"
"68","Gesta Romanorum (Deeds of the Romans)",,
"69","Scachs d'Amor (Chess of Love)",,
"70","Muruj adh-Dhahab (Meadows of Gold)",,"al-Masudi"
"71","Paul Morphy's Photo","This is a photo of Paul Morphy",

"""
    st.session_state.messages.append(
        {"role": "system", "content": system_content})
    st.session_state.messages.append({"role": "assistant", "content": """你好，你准备好进行一场关于国际象棋的激动人心的讨论了吗？请准备好，让我们带你进入克利夫兰公共图书馆的John G. White象棋收藏之旅。想象一下：那些足以让国王震惊的珍稀书籍和手稿，有些甚至比你的曾祖父母还要古老！这些藏品将直接带你回到国际象棋的中世纪起源，揭示其重要的历史和文化影响。

但这不是全部！这个收藏不仅仅关于象棋。它还拥有历史上所有时期的大量文学作品，为你介绍一个全新的“用文字下棋”的视角。我们谈论的是诗歌、小说、散文甚至史诗，这些都会让你兴奋得心跳加速。这就像一场特别的象棋表演，策略与讲故事交织在一起！也许我可以通过“The Turk”（ID 4）的引人入胜的故事激发你的兴趣？

所以，为了这次丰富的时空之旅做好准备。准备揭开John G. White象棋收藏中的神秘面纱，那里有珍稀书籍、中世纪手稿和大量的文学杰作在等着你。是时候点燃你的好奇心，并开始这次引人入胜的探索了。让我们一步步深入国际象棋的世界！这不是很棒吗？"""})


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

        options = [""":question: 馆藏里最古老的象棋书籍是什么样的？""",
                   """:question: 馆藏里有什么特别的象棋棋盘吗？""",
                   """:question: 馆藏里有什么和哈利波特相关的物品吗? """,
                   """:question: 馆藏里有什么和电视剧后翼弃兵相关的物品吗?""",
                   """:question: 能否给我展示一个象棋开局?"""
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

    st.header("象棋对话")
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
        options = [""":question: 告诉我关于这个馆藏的更多信息. """,
                   """:question: 馆藏里有什么特别的珍宝吗 """,
                   """:question: 馆藏里都蕴含着一些关于什么样故事呢 """
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
