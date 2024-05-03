import cv2
import streamlit as st
import time
from model import prediction_model
from urls import video_urls


if "page" not in st.session_state or st.session_state["page"]!='wordpage':
    cv2.destroyAllWindows()
    st.session_state["page"] = 'wordpage'
    cap = cv2.VideoCapture(cv2.CAP_DSHOW)

def hide_streamlit_style():
    return """
        <style>
        
        /* Hide side toolbar buttons*/
        div[data-testid="stToolbar"] {
        visibility: hidden;
        height: 0%;
        position: fixed;
        }

        /* hide header */
        header {
        visibility: hidden;
        height: 0%;
        }

        img {
        border-radius: 1rem;
        }

        .st-emotion-cache-gh2jqd {
            width: 100%;
            padding: 0rem 1rem 10rem;
            max-width: 46rem;
        }

        .st-as {
            height:2rem
        }

        .video-wrapper {
        background-color: white;
        display: inline-block;
        width: 336px;
        height: 336px;
        overflow: hidden;
        position: relative;
        border-radius: 1rem; /* Add border radius to match the image */
        align-content : center
        }

        </style>
    """
st.markdown(hide_streamlit_style(), unsafe_allow_html=True)


def update_video(character):
    return f"""
    <div class="video-wrapper">
    <video width="350" height="290" autoplay controlsList="nodownload" loop style="transform: scaleX(-1);">
        <source src="{video_urls[character]}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    </div>  
    """


def detected_word(WORD, detected_index):
    markdown_str = f'<div style="font-family: Arial, sans-serif; font-weight: bold; text-align: center; font-size: 30px;">'
    # Loop through each letter in the word
    for i, letter in enumerate(WORD):
        # Check if the current letter index is less than or equal to the detected index
        if i <= detected_index:
            # If yes, add the letter in green color
            markdown_str += f'<span style="color:#683aff;">{letter}</span>'
        else:
            # If no, add the letter in white color
            markdown_str += f'<span style="color:white;">{letter}</span>'
    markdown_str += "</div>"
    return markdown_str


if "word" not in st.session_state:
    st.session_state['word'] = 0
    st.session_state['index'] = 0

WORD_LIST = ["ABC"]
NUM_WORD = len(WORD_LIST)

# Element structure
title_placeholder = st.empty()  # stores letter title
col1, col2 = st.columns([0.5, 0.5], gap="medium")
with col1:
    video_placeholder = st.empty()  # to display video
    video_placeholder.markdown(
        update_video(
            WORD_LIST[st.session_state["word"]][st.session_state["index"]]
        ),
        unsafe_allow_html=True,
    )
with col2:
    webcam_placeholder = st.empty()  # to display webcam

matched_placeholder = st.empty()

# creating the progress bar
prob = 0
pred_conf = st.progress(prob)

while True and st.session_state["page"] == "wordpage":

    if cap.isOpened():
        ret, frame = cap.read()
    else:
        st.write("loading")

    if ret:
        current_word_index = st.session_state["word"]
        title_placeholder.header(f"Learning Word")

        frame, prob = prediction_model(
            frame,
            ord(WORD_LIST[st.session_state["word"]][st.session_state['index']])
            - ord("A"),
        )

        frame = cv2.resize(
            frame, (500, 500), fx=0.1, fy=0.1, interpolation=cv2.INTER_CUBIC
        )
        webcam_placeholder.image(frame, channels="BGR")

        matched_placeholder.markdown(
            detected_word(WORD_LIST[current_word_index],st.session_state["index"]-1), unsafe_allow_html=True
        )

        pred_conf.progress(prob)

        if prob == 100:
            print()
            st.session_state["index"] += 1
            if st.session_state["index"] == len(
                WORD_LIST[st.session_state["word"]]
            ):
                matched_placeholder.markdown(
                    detected_word(
                        WORD_LIST[current_word_index], st.session_state["index"] - 1
                    ),
                    unsafe_allow_html=True,
                )
                st.session_state["index"] = 0
                st.session_state["word"] = (st.session_state["word"] + 1) % NUM_WORD
                st.balloons()

            video_placeholder.empty()

            time.sleep(2)
            matched_placeholder.empty()
            video_placeholder.markdown(
                update_video(
                    WORD_LIST[st.session_state["word"]][st.session_state["index"]]
                ),
                unsafe_allow_html=True,
            )

cap.release()
cv2.destroyAllWindows()
