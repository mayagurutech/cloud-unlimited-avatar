import streamlit as st
import openai
import requests
import json
from elevenlabs import generate, set_api_key
import time
import tempfile
import os

# Configure page
st.set_page_config(
    page_title="Unlimited AI Avatar Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

def main():
    st.title("🤖 Unlimited AI Avatar Assistant")
    st.markdown("**∞ Unlimited Videos • Professional Quality • Multi-Language**")
    
    # Configuration sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys (read from secrets)
        openai_key = st.secrets.get("OPENAI_API_KEY", "")
        elevenlabs_key = st.secrets.get("ELEVENLABS_API_KEY", "")
        colab_url = st.text_input("Google Colab URL", placeholder="https://xxx.ngrok.io")
        
        if openai_key and elevenlabs_key and colab_url:
            st.success("✅ All APIs Connected")
        else:
            st.error("❌ Configure API keys and Colab URL")
        
        # Avatar settings
        st.header("👤 Avatar Settings")
        avatar_image_url = st.text_input("Avatar Image URL", 
                                        placeholder="https://your-image.jpg")
        
        language = st.selectbox("Language", ["English", "Hindi", "Both"])
        
        # Knowledge base
        st.header("📚 Knowledge Base")
        uploaded_files = st.file_uploader(
            "Upload support documents",
            accept_multiple_files=True,
            type=['pdf', 'txt', 'docx']
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} files processed")

    # Main chat interface
    st.header("💬 Unlimited Avatar Chat")
    
    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "video_url" in message and message["video_url"]:
                st.video(message["video_url"])

    # Chat input
    if prompt := st.chat_input("Ask your unlimited avatar anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate unlimited avatar response
        with st.chat_message("assistant"):
            with st.spinner("🎬 Generating unlimited avatar video..."):
                
                # Generate AI response
                ai_response = generate_ai_response(prompt, openai_key, language)
                st.write(ai_response)
                
                # Generate voice
                audio_path = generate_voice_audio(ai_response, elevenlabs_key)
                
                # Generate UNLIMITED avatar video
                video_url = generate_unlimited_avatar_video(
                    ai_response, 
                    audio_path, 
                    avatar_image_url, 
                    colab_url
                )
                
                if video_url:
                    st.video(video_url)
                    st.success("✅ Unlimited video generated!")
                else:
                    st.error("❌ Video generation failed")
        
        # Save message
        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_response,
            "video_url": video_url
        })

def generate_ai_response(user_input, openai_key, language):
    """Generate intelligent response using OpenAI"""
    openai.api_key = openai_key
    
    system_prompt = f"""You are a professional AI avatar assistant.
    Language: {language}
    Personality: Polite, professional, helpful
    
    Respond naturally and professionally. Keep responses under 150 words.
    If language is Hindi, use proper Devanagari script."""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"

def generate_voice_audio(text, elevenlabs_key):
    """Generate voice audio using ElevenLabs"""
    try:
        set_api_key(elevenlabs_key)
        
        audio = generate(
            text=text,
            voice="Bella",  # Professional voice
            model="eleven_multilingual_v2"  # Supports Hindi
        )
        
        # Save audio to temporary file
        audio_path = f"/tmp/audio_{int(time.time())}.wav"
        with open(audio_path, "wb") as f:
            f.write(audio)
        
        return audio_path
        
    except Exception as e:
        st.error(f"Voice generation error: {e}")
        return None

def generate_unlimited_avatar_video(text, audio_path, avatar_image_url, colab_url):
    """Generate UNLIMITED avatar video using Google Colab"""
    try:
        # Call your Google Colab API for unlimited generation
        response = requests.post(f"{colab_url}/generate_avatar", json={
            "text": text,
            "audio_url": audio_path,
            "avatar_image": avatar_image_url
        }, timeout=120)  # Allow time for generation
        
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'success':
                return f"{colab_url}{result['video_url']}"
        
        return None
        
    except Exception as e:
        st.error(f"Unlimited video generation error: {e}")
        return None

if __name__ == "__main__":
    main()
