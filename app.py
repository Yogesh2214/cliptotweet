import os
import streamlit as st
import openai
import pyperclip

st.set_page_config(page_title="Clip-to-Tweet AI Assistant for Podcasters", page_icon="🎙️", layout="centered")

# Sidebar with instructions and API key
with st.sidebar:
    st.title("🛠️ How to Use")
    st.markdown("""
    1. Upload a short podcast/audio clip (max 60 seconds).
    2. Wait for the transcript to appear.
    3. Select your tweet tone and number of tweets.
    4. Generate and copy your tweets!
    """)
    st.markdown("---")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = st.text_input("Enter your OpenAI API key", type="password")
    st.markdown("---")
    st.markdown("[Give Feedback](https://tally.so/r/nrR0G2) 📝")
    st.markdown("<sub>Made with ❤️ for podcasters</sub>", unsafe_allow_html=True)

st.title("🎙️ Clip-to-Tweet AI Assistant")
st.write(":sparkles: Turn your podcast clips into tweetable content in seconds!")

uploaded_file = st.file_uploader("Upload audio file (mp3, wav, m4a, ogg, ≤60s)", type=["mp3", "wav", "m4a", "ogg"])

if uploaded_file and api_key:
    # Set OpenAI API key
    openai.api_key = api_key
    
    with st.expander("1️⃣ Transcript", expanded=True):
        try:
            st.info("Transcribing audio with Whisper...")
            with st.spinner("Transcribing..."):
                audio_bytes = uploaded_file.read()
                # Get the file extension from the uploaded file
                file_extension = uploaded_file.name.split('.')[-1].lower()
                temp_filename = f"temp_audio.{file_extension}"
                
                with open(temp_filename, "wb") as f:
                    f.write(audio_bytes)
                with open(temp_filename, "rb") as audio_file:
                    transcript = openai.Audio.transcribe(
                        model="whisper-1",
                        file=audio_file
                    )
            st.success("Transcription complete!")
            st.markdown(f"**Transcript:**\n\n{transcript['text']}")
            
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
        except Exception as e:
            st.error(f"Transcription failed: {e}")
            transcript = None
        
    if 'transcript' in locals() and transcript and transcript.get('text'):
        with st.expander("2️⃣ Generate Tweets", expanded=True):
            tone = st.selectbox("Select tweet tone", ["Informative", "Witty", "Inspirational", "Casual", "Professional"])
            num_tweets = st.slider("Number of tweets", 1, 3, 2)
            if st.button("Generate Tweets"):
                try:
                    st.info("Generating tweets with GPT...")
                    with st.spinner("Generating tweets..."):
                        prompt = f"""
You are an expert social media manager for podcasts. Given the following transcript, write {num_tweets} tweet(s) in a {tone.lower()} tone. Each tweet should be under 280 characters, engaging, and suitable for Twitter. Number each tweet.

Transcript:
{transcript['text']}
"""
                        response = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant."},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        tweets = response["choices"][0]["message"]["content"]
                    st.success("Tweets generated!")
                    st.subheader("Generated Tweets:")
                    # Split tweets by line numbers (1. 2. 3.)
                    import re
                    tweet_list = re.split(r"\n?\d+\. ", tweets)
                    tweet_list = [t.strip() for t in tweet_list if t.strip()]
                    for idx, tweet in enumerate(tweet_list, 1):
                        st.markdown(f"**Tweet {idx}:**")
                        st.code(tweet, language=None)
                        st.button(f"Copy Tweet {idx}", key=f"copy_{idx}", on_click=st.write, args=(f"Copied Tweet {idx}!",))
                except Exception as e:
                    st.error(f"Tweet generation failed: {e}")

# Footer
st.markdown("---")
st.markdown("<center><sub>Made with ❤️ by Yogesh. | [Feedback](https://tally.so/r/nrR0G2)</sub></center>", unsafe_allow_html=True) 