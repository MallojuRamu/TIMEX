import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import shutil
import mimetypes
from pytube import YouTube
from PIL import Image
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import time
from twilio.rest import Client

# Set page config as the FIRST Streamlit command
st.set_page_config(page_title="Blog Generator", page_icon="📝", layout="wide")

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
USER_PHONE_NUMBER = os.getenv("USER_PHONE_NUMBER")

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")

# Load the config file for authentication
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Create the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    auto_hash=True
)

# Custom CSS
custom_css = """
<style>
body {
    font-family: 'Poppins', sans-serif;
    background: #F5F5F5;
    color: #333333;
}
h1, h2, h3, h4, h5, h6 {
    color: #6C63FF;
}
.header {
    text-align: center;
    margin-bottom: 40px;
}
.section {
    background: #FFFFFF;
    padding: 40px;
    border-radius: 16px;
    margin-bottom: 40px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.container {
    background: linear-gradient(135deg, #6C63FF, #FF6584);
    color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.container:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 24px rgba(108, 99, 255, 0.5);
}
.container h2 {
    color: white;
    font-size: 1.5em;
    margin-bottom: 10px;
}
.container p {
    color: rgba(255, 255, 255, 0.9);
    font-size: 1em;
}
.footer {
    text-align: center;
    padding: 20px;
    background: #FFFFFF;
    border-top: 1px solid #E0E0E0;
    margin-top: 40px;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}
.footer a {
    color: #6C63FF;
    text-decoration: none;
    margin: 0 10px;
}
.footer a:hover {
    color: #FF6584;
}
.footer button {
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1em;
    font-weight: 600;
    background: linear-gradient(135deg, #6C63FF, #FF6584);
}
.spinner {
    text-align: center;
}
.spinner div {
    width: 40px;
    height: 40px;
    border: 4px solid #6C63FF;
    border-top: 4px solid transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
.share-btn {
    background: linear-gradient(135deg, #6C63FF, #FF6584);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1.1em;
    font-weight: 600;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.share-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(108, 99, 255, 0.5);
}
.faq-item {
    margin-bottom: 20px;
}
.faq-item h3 {
    color: #6C63FF;
    font-size: 1.2em;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    cursor: pointer;
}
.faq-item h3 i {
    margin-right: 10px;
    color: #FF6584;
}
.faq-item .faq-answer {
    color: #333333;
    margin-top: 10px;
    font-size: 1em;
    font-weight: 300;
    margin-left: 20px;
}
.landing {
    position: relative;
    background: linear-gradient(135deg, #6C63FF, #FF6584);
    padding: 60px 20px;
    border-radius: 16px;
    text-align: center;
    color: white;
    margin: 40px 0;
    overflow: hidden;
}
.landing h1 {
    font-size: 3.5em;
    font-weight: 700;
    color: white;
    margin-bottom: 10px;
}
.landing p {
    font-size: 1.2em;
    font-weight: 300;
    color: white;
    margin-bottom: 20px;
}
.landing-btn {
    background: white;
    color: #333333;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1.1em;
    font-weight: 600;
    transition: background 0.3s ease, color 0.3s ease;
}
.landing-btn:hover {
    background: #F5F5F5;
    color: #6C63FF;
}
.logo {
    position: absolute;
    top: 20px;
    left: 20px;
    font-size: 1.5em;
    font-weight: 700;
    color: #333333;
}
.decorative-circle {
    display: none;
}
#particles-js {
    display: none;
}
.auth-container {
    background: #FFFFFF;
    padding: 40px;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    max-width: 500px;
    margin: 40px auto;
}
.auth-container h1 {
    color: #6C63FF;
    text-align: center;
    margin-bottom: 20px;
}
.auth-container p {
    color: #333333;
    text-align: center;
    margin-bottom: 20px;
}
.auth-btn {
    background: linear-gradient(135deg, #6C63FF, #FF6584);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1.1em;
    font-weight: 600;
    width: 100%;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.auth-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(108, 99, 255, 0.5);
}
.auth-link {
    color: #6C63FF;
    text-decoration: none;
    font-weight: 600;
}
.auth-link:hover {
    color: #FF6584;
    text-decoration: underline;
}
.step-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    width: 100%;
}
.step {
    text-align: center;
    flex: 1;
}
.step:not(:last-child) {
    border-right: 2px solid #000000;
    padding-right: 20px;
    margin-right: 20px;
}
.step span {
    display: block;
    width: 30px;
    height: 30px;
    color: white;
    border-radius: 50%;
    line-height: 30px;
    margin: 0 auto 5px;
}
.step p {
    color: #333333;
    font-size: 0.9em;
    margin: 0;
}
</style>
"""

# Inject custom CSS and Google Fonts
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
""", unsafe_allow_html=True)
st.markdown(custom_css, unsafe_allow_html=True)

# JavaScript for smooth scrolling
scroll_script = """
<script>
function scrollToContainers() {
    const containersSection = document.getElementById('containers-section');
    if (containersSection) {
        containersSection.scrollIntoView({ behavior: 'smooth' });
    }
}
</script>
"""
st.markdown(scroll_script, unsafe_allow_html=True)

# Helper functions
def is_image_url(url):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    return any(url.lower().endswith(ext) for ext in image_extensions)

def fetch_youtube_content(url):
    try:
        yt = YouTube(url)
        content = f"Title: {yt.title}\nDescription: {yt.description or 'No description available'}"
        return content
    except Exception as e:
        return f"Error fetching YouTube content: {str(e)}"

def fetch_text_from_url(url):
    try:
        if "youtube.com" in url or "youtu.be" in url:
            return fetch_youtube_content(url)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
        return text_content if text_content else "No text content could be extracted from the URL."
    except Exception as e:
        return f"Error fetching URL content: {str(e)}"

def save_input_output(input_type, input_data, output_data, directory_base="blog_posts"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_dir = os.path.join(directory_base, timestamp)
    os.makedirs(save_dir, exist_ok=True)
    
    if input_type == "Text":
        with open(os.path.join(save_dir, "input.txt"), "w", encoding="utf-8") as f:
            f.write(input_data)
    elif input_type == "URL":
        with open(os.path.join(save_dir, "input.url"), "w", encoding="utf-8") as f:
            f.write(input_data)
        if is_image_url(input_data):
            try:
                response = requests.get(input_data, stream=True)
                response.raise_for_status()
                content_type = response.headers.get('content-type', '')
                extension = mimetypes.guess_extension(content_type) or '.jpg'
                image_path = os.path.join(save_dir, f"input_image{extension}")
                with open(image_path, "wb") as f:
                    shutil.copyfileobj(response.raw, f)
            except Exception as e:
                with open(os.path.join(save_dir, "input_image_error.txt"), "w", encoding="utf-8") as f:
                    f.write(f"Error downloading image: {str(e)}")
        else:
            fetched_text = fetch_text_from_url(input_data)
            with open(os.path.join(save_dir, "input_text.txt"), "w", encoding="utf-8") as f:
                f.write(fetched_text)
    elif input_type == "Image File":
        file_extension = os.path.splitext(input_data.name)[1]
        image_path = os.path.join(save_dir, f"input_image{file_extension}")
        with open(image_path, "wb") as f:
            f.write(input_data.getvalue())

    with open(os.path.join(save_dir, "output.txt"), "w", encoding="utf-8") as f:
        f.write(output_data)

def generate_blog_from_input(input_type, input_data, user_type, word_count=300):
    try:
        if user_type == "Researchers":
            tone = "formal, detailed, and technical, focusing on in-depth analysis suitable for researchers"
        elif user_type == "Common Students":
            tone = "simple, engaging, and educational, using easy-to-understand language suitable for students"
        elif user_type == "Data Scientists":
            tone = "technical but practical, focusing on applications, tools, and methodologies relevant to data scientists"

        if input_type == "Text":
            prompt = f"Write a blog post using the following content as inspiration: '{input_data}' in approximately {word_count} words. Use a {tone} tone suitable for {user_type}."
            response = model.generate_content(prompt)
            return response.text
        elif input_type == "URL":
            if is_image_url(input_data):
                response = requests.get(input_data, stream=True)
                response.raise_for_status()
                image_content = response.content
                prompt = f"Write a blog post based on this image in approximately {word_count} words. Use a {tone} tone suitable for {user_type}."
                response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_content}])
                return response.text
            else:
                text_content = fetch_text_from_url(input_data)
                if "Error" in text_content:
                    return text_content
                prompt = f"Write a blog post using the following content as inspiration: '{text_content}' in approximately {word_count} words. Use a {tone} tone suitable for {user_type}."
                response = model.generate_content(prompt)
                return response.text
        elif input_type == "Image File":
            prompt = f"Write a blog post based on this image in approximately {word_count} words. Use a {tone} tone suitable for {user_type}."
            image_content = input_data.getvalue()
            mime_type = mimetypes.guess_type(input_data.name)[0] or "image/jpeg"
            response = model.generate_content([prompt, {"mime_type": mime_type, "data": image_content}])
            return response.text
    except Exception as e:
        return f"Error generating content: {str(e)}"

# Twilio SMS function for feedback
def send_feedback_sms(feedback_text):
    try:
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        message = client.messages.create(
            body=feedback_text,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=os.getenv("USER_PHONE_NUMBER")
        )
        return message.sid is not None
    except Exception as e:
        st.error(f"Failed to send SMS feedback: {str(e)}")
        return False

# Twilio SMS function for sharing blog post
def render_share_button(blog_content):
    st.subheader("Share Your Blog Post")
    if st.button("Send via SMS", key="send_sms_btn"):
        try:
            client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
            # Truncate to 1600 characters (SMS limit)
            truncated_content = blog_content[:1600]
            message = client.messages.create(
                body=f"Check out my blog post:\n{truncated_content}",
                from_=os.getenv("TWILIO_PHONE_NUMBER"),
                to=os.getenv("USER_PHONE_NUMBER")
            )
            if message.sid:
                st.success("Blog post sent via SMS!")
            else:
                st.error("Failed to send SMS.")
        except Exception as e:
            st.error(f"Error sending SMS: {str(e)}")

# Initialize session state
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'name' not in st.session_state:
    st.session_state.name = None
if 'blog_content' not in st.session_state:
    st.session_state.blog_content = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "login"

# Navigation logic
query_params = st.query_params
page_from_url = query_params.get("page", "login")

if st.session_state.authentication_status is True and page_from_url == "login":
    st.session_state.current_page = "home"
    st.query_params["page"] = "home"
else:
    st.session_state.current_page = page_from_url

page = st.session_state.current_page

# Registration Page
if page == "register":
    st.markdown("""
    <div class="auth-container">
        <h1>Register</h1>
        <p>Create a new account to access the Blog Generator</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(
            location='main',
            fields={
                'Form name': 'Register',
                'Email': 'Email',
                'Username': 'Username',
                'Password': 'Password',
                'Repeat password': 'Repeat Password',
                'Register': 'Register'
            }
        )
        if email_of_registered_user:
            st.success('User registered successfully! Please log in.')
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
            time.sleep(1)
            st.session_state.current_page = "login"
            st.query_params["page"] = "login"
            st.rerun()
    except Exception as e:
        st.error(f"Registration failed with error: {str(e)}")
    
    st.markdown("""
    <div class="auth-container">
        <p>Already have an account? <a href="?page=login" class="auth-link">Log In</a></p>
    </div>
    """, unsafe_allow_html=True)

# Login Page
elif page == "login" and st.session_state.authentication_status is not True:
    st.markdown("""
    <div class="auth-container">
        <h1>Login</h1>
        <p>Access your Blog Generator account</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        authenticator.login(
            location='main',
            fields={
                'Form name': 'Login',
                'Username': 'Username',
                'Password': 'Password',
                'Login': 'Login'
            }
        )
    except Exception as e:
        st.error(e)
    
    if st.session_state.get('authentication_status') is True:
        st.success(f'Welcome {st.session_state.get("name")}')
        time.sleep(1)
        st.session_state.current_page = "home"
        st.query_params["page"] = "home"
        st.rerun()
    elif st.session_state.get('authentication_status') is False:
        st.error('Username/password is incorrect')
    elif st.session_state.get('authentication_status') is None:
        st.warning('Please enter your username and password')
    
    st.markdown("""
    <div class="auth-container">
        <p>Don't have an account? <a href="?page=register" class="auth-link">Register</a></p>
    </div>
    """, unsafe_allow_html=True)

# Logout Functionality
def logout():
    authenticator.logout(location='unrendered')
    st.session_state.authentication_status = None
    st.session_state.username = None
    st.session_state.name = None
    st.session_state.current_page = "login"
    st.query_params["page"] = "login"
    st.rerun()

# Sidebar
if st.session_state.authentication_status:
    st.sidebar.title(f"Welcome, {st.session_state.name}!")
    if st.sidebar.button("Logout", key="logout_btn"):
        logout()

# Protect pages
if not st.session_state.authentication_status and page not in ["login", "register"]:
    st.warning("Please log in to access this page.")
    st.session_state.current_page = "login"
    st.query_params["page"] = "login"
    st.rerun()

# Sidebar user type selection


# Landing Section
if st.session_state.authentication_status and page == "home":
    st.markdown("""
    <div class="landing">
        <div class="logo">TIMEX</div>
        <h1>Blog Generator</h1>
        <p>Want More Blog Ideas? Let AI Think of Ideas for You</p>
        <button class="landing-btn" aria-label="Get Started" onclick="scrollToContainers()">Get Started</button>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section">
        <h2>About us</h2>
        <p>Our Blog Generation Project is an AI-powered tool designed to simplify content creation. By accepting inputs in three ways—text, images, and URLs—it transforms your ideas into engaging blog posts. Whether you’re a researcher, student, or content creator, our tool adapts to your needs, generating high-quality articles tailored to your audience. With advanced AI technology, it saves time, sparks creativity, and ensures professional results. From analyzing images to extracting insights from web pages, our platform offers a seamless and versatile solution for all your blogging needs. Start creating captivating content today with just a few clicks!</p>
        <button class="landing-btn" style="margin-top: 20px;" aria-label="Get Started for Free">Get Started for Free</button>
    </div>
    """, unsafe_allow_html=True)

# Main Content
if st.session_state.authentication_status and page == "home":
    st.markdown('<div class="section" id="containers-section"><h2>Generate Your Blog Post</h2><p>Choose a method to get started:</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="container">
            <h2><i class="fas fa-file-alt" style="margin-right: 10px;"></i> Text Input</h2>
            <p>Generate a blog post from your own text inspiration.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start with Text", key="text_btn"):
            st.session_state.current_page = "text"
            st.query_params["page"] = "text"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="container">
            <h2><i class="fas fa-link" style="margin-right: 10px;"></i> URL Input</h2>
            <p>Turn webpage or video content into a blog post.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start with URL", key="url_btn"):
            st.session_state.current_page = "url"
            st.query_params["page"] = "url"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="container">
            <h2><i class="fas fa-image" style="margin-right: 10px;"></i> Image Input</h2>
            <p>Create a blog post inspired by an image.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start with Image", key="image_btn"):
            st.session_state.current_page = "image"
            st.query_params["page"] = "image"
            st.rerun()

# Text Blog Generator Page
elif st.session_state.authentication_status and page == "text":
    st.markdown("""
    <div class="header">
        <h1><i class="fas fa-file-alt" style="margin-right: 10px;"></i> Text Blog Generator</h1>
        <p>Turn your ideas into a blog post</p>
    </div>
    <div class="section">
        <div class="step-container">
            <div class="step">
                <span style="background: #6C63FF;">1</span>
                <p>Enter Text</p>
            </div>
            <div class="step">
                <span style="background: #FF6584;">2</span>
                <p>Generate Blog</p>
            </div>
            <div class="step">
                <span style="background: #00C4B4;">3</span>
                <p>Share/Download</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.authentication_status and page != "home":
        st.title("Options")
        user_type = st.selectbox("Target Audience", ["Researchers", "Common Students", "Data Scientists"])
    else:
        user_type = None



    input_data = st.text_area("Blog Content", placeholder="Enter the text to inspire your blog post...", height=200)
    word_count = st.slider("Approximate Word Count", min_value=100, max_value=1000, value=300, step=50)
    
    if st.button("Generate Blog", key="generate_text"):
        if not input_data:
            st.error("Please provide text input!")
        else:
            st.markdown('<div class="spinner"><div></div><p style="color: #333333; margin-top: 10px;">Generating your blog post...</p></div>', unsafe_allow_html=True)
            blog_content = generate_blog_from_input("Text", input_data, user_type, word_count)
            st.session_state.blog_content = blog_content
            st.subheader("Generated Blog Post")
            if st.session_state.get('blog_content'):
                tabs = st.tabs(["Generated Blog Post", "Preview"])
                with tabs[0]:
                    st.write(st.session_state.blog_content)
                with tabs[1]:
                    st.markdown(f"""
                    <div style="background: #FFFFFF; color: #333333; padding: 20px; border-radius: 8px;">
                        <h1 style="color: #6C63FF;">Your Blog Post Title</h1>
                        <p style="color: #333333;">{st.session_state.blog_content}</p>
                    </div>
                    """, unsafe_allow_html=True)
                save_input_output("Text", input_data, blog_content)
                st.download_button(
                    label="Download Blog Post",
                    data=blog_content,
                    file_name=f"blog_post_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
                    mime="text/plain"
                )
                render_share_button(st.session_state.blog_content)
    
    if st.button("Back to Home", key="back_text"):
        st.session_state.current_page = "home"
        st.query_params["page"] = "home"
        st.rerun()

# URL Blog Generator Page
elif st.session_state.authentication_status and page == "url":
    st.markdown("""
    <div class="header">
        <h1><i class="fas fa-link" style="margin-right: 10px;"></i> URL Blog Generator</h1>
        <p>Generate a blog post from a URL</p>
    </div>
    <div class="section">
        <div class="step-container">
            <div class="step">
                <span style="background: #6C63FF;">1</span>
                <p>Enter URL</p>
            </div>
            <div class="step">
                <span style="background: #FF6584;">2</span>
                <p>Generate Blog</p>
            </div>
            <div class="step">
                <span style="background: #00C4B4;">3</span>
                <p>Share/Download</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.authentication_status and page != "home":
        st.title("Options")
        user_type = st.selectbox("Target Audience", ["Researchers", "Common Students", "Data Scientists"])
    else:
        user_type = None

    input_data = st.text_input("URL", placeholder="Enter a URL (e.g., webpage, YouTube video, or image URL)...")
    word_count = st.slider("Approximate Word Count", min_value=100, max_value=1000, value=300, step=50)
    
    if st.button("Generate Blog", key="generate_url"):
        if not input_data:
            st.error("Please provide a URL!")
        else:
            st.markdown('<div class="spinner"><div></div><p style="color: #333333; margin-top: 10px;">Generating your blog post...</p></div>', unsafe_allow_html=True)
            blog_content = generate_blog_from_input("URL", input_data, user_type, word_count)
            st.session_state.blog_content = blog_content
            st.subheader("Generated Blog Post")
            if st.session_state.get('blog_content'):
                tabs = st.tabs(["Generated Blog Post", "Preview"])
                with tabs[0]:
                    st.write(st.session_state.blog_content)
                with tabs[1]:
                    st.markdown(f"""
                    <div style="background: #FFFFFF; color: #333333; padding: 20px; border-radius: 8px;">
                        <h1 style="color: #6C63FF;">Your Blog Post Title</h1>
                        <p style="color: #333333;">{st.session_state.blog_content}</p>
                    </div>
                    """, unsafe_allow_html=True)
                save_input_output("URL", input_data, blog_content)
                st.download_button(
                    label="Download Blog Post",
                    data=blog_content,
                    file_name=f"blog_post_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
                    mime="text/plain"
                )
                render_share_button(st.session_state.blog_content)
    
    if st.button("Back to Home", key="back_url"):
        st.session_state.current_page = "home"
        st.query_params["page"] = "home"
        st.rerun()

# Image Blog Generator Page
elif st.session_state.authentication_status and page == "image":
    st.markdown("""
    <div class="header">
        <h1><i class="fas fa-image" style="margin-right: 10px;"></i> Image Blog Generator</h1>
        <p>Turn an image into a blog post</p>
    </div>
    <div class="section">
        <div class="step-container">
            <div class="step">
                <span style="background: #6C63FF;">1</span>
                <p>Upload Image</p>
            </div>
            <div class="step">
                <span style="background: #FF6584;">2</span>
                <p>Generate Blog</p>
            </div>
            <div class="step">
                <span style="background: #00C4B4;">3</span>
                <p>Share/Download</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.authentication_status and page != "home":
        st.title("Options")
        user_type = st.selectbox("Target Audience", ["Researchers", "Common Students", "Data Scientists"])
    else:
        user_type = None
    
    input_data = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png", "gif"])
    word_count = st.slider("Approximate Word Count", min_value=100, max_value=1000, value=300, step=50)
    
    if st.button("Generate Blog", key="generate_image"):
        if not input_data:
            st.error("Please upload an image!")
        else:
            st.markdown('<div class="spinner"><div></div><p style="color: #333333; margin-top: 10px;">Generating your blog post...</p></div>', unsafe_allow_html=True)
            blog_content = generate_blog_from_input("Image File", input_data, user_type, word_count)
            st.session_state.blog_content = blog_content
            st.subheader("Generated Blog Post")
            if st.session_state.get('blog_content'):
                tabs = st.tabs(["Generated Blog Post", "Preview"])
                with tabs[0]:
                    st.write(st.session_state.blog_content)
                with tabs[1]:
                    st.markdown(f"""
                    <div style="background: #FFFFFF; color: #333333; padding: 20px; border-radius: 8px;">
                        <h1 style="color: #6C63FF;">Your Blog Post Title</h1>
                        <p style="color: #333333;">{st.session_state.blog_content}</p>
                    </div>
                    """, unsafe_allow_html=True)
                save_input_output("Image File", input_data, blog_content)
                st.download_button(
                    label="Download Blog Post",
                    data=blog_content,
                    file_name=f"blog_post_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
                    mime="text/plain"
                )
                render_share_button(st.session_state.blog_content)
    
    if st.button("Back to Home", key="back_image"):
        st.session_state.current_page = "home"
        st.query_params["page"] = "home"
        st.rerun()

# FAQ Section
if st.session_state.authentication_status and page == "home":
    st.markdown("""
    <div class="section">
        <h2>Frequently Asked Questions</h2>
        <div class="faq-item">
            <h3><i class="fas fa-lightbulb"></i> How can I find blog topic ideas?</h3>
            <p class="faq-answer">To find blog topic ideas, start by identifying your audience’s questions and interests through social media, comments, or FAQs. Use tools like Google Trends, AnswerThePublic, or Ubersuggest to explore trending and searched topics. Browse other blogs for inspiration and repurpose old content with a fresh angle. You can also use AI to brainstorm creative and niche-specific topics quickly.</p>
        </div>
        <div class="faq-item">
            <h3><i class="fas fa-bullseye"></i> How do I write a good blog post to maximize conversions?</h3>
            <p class="faq-answer">Focus on engaging content and optimize with keywords provided by our tool.</p>
        </div>
        <div class="faq-item">
            <h3><i class="fas fa-heading"></i> How can I use AI to generate a good title for my content?</h3>
            <p class="faq-answer">Our AI suggests titles based on your topic for maximum impact.</p>
        </div>
        <div class="faq-item">
            <h3><i class="fas fa-tools"></i> What are the best AI tools for content creation?</h3>
            <p class="faq-answer">Our Blog Generator is a top choice, powered by advanced AI technology.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer with Feedback Form
if st.session_state.authentication_status:
    
    
    feedback_text = st.text_area(
        "Feedback",
        placeholder="Let us know how we can improve...",
        height=100,
        key="feedback_input",
        help="Your feedback helps us improve!"
    )
    
    if st.button("Submit Feedback", key="submit_feedback"):
        if feedback_text:
            if send_feedback_sms(feedback_text):
                st.success("Feedback sent successfully via SMS! Thank you for your input.")
            else:
                st.error("Failed to send feedback. Please try again later.")
        else:
            st.warning("Please enter feedback before submitting.")
    
                
    
    
    st.markdown("""
    <div class="footer">
        <p>© 2025 Blog Generator | Powered by Streamlit & Google Gemini API</p>
        <p><a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a> | <a href="#">Contact Us</a></p>
        <div style="margin-top: 20px;">
            <h3 style="color: #6C63FF;">Feedback</h3>
    """, unsafe_allow_html=True)
