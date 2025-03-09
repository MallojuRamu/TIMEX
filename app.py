<<<<<<< HEAD
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

# Set page config as the FIRST Streamlit command
st.set_page_config(page_title="Blog Generator", page_icon="📝", layout="wide")

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

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
    auto_hash=True  # Automatically hash plain text passwords
)

# Custom CSS with updated styles for the landing section
custom_css = """
<style>
/* Existing styles */
body {
    font-family: 'Poppins', sans-serif;
    background: #F5F5F5; /* Light gray background */
    color: #333333; /* Dark gray text */
}
h1, h2, h3, h4, h5, h6 {
    color: #6C63FF; /* Primary purple */
}
.header {
    text-align: center;
    margin-bottom: 40px;
}
.section {
    background: #FFFFFF; /* White background */
    padding: 40px;
    border-radius: 16px;
    margin-bottom: 40px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.container {
    background: linear-gradient(135deg, #6C63FF, #FF6584); /* Gradient from purple to pink */
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
    color: #333333; /* Dark gray */
    margin-top: 10px;
    font-size: 1em;
    font-weight: 300;
    margin-left: 20px;
}

/* Updated styles for the landing section */
.landing {
    position: relative;
    background: linear-gradient(135deg, #6C63FF, #FF6584); /* Gradient matching the image */
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

/* Logo styling */
.logo {
    position: absolute;
    top: 20px;
    left: 20px;
    font-size: 1.5em;
    font-weight: 700;
    color: #333333;
}

/* Remove decorative circles since they are not in the image */
.decorative-circle {
    display: none;
}

/* Remove particles.js since it's not in the image */
#particles-js {
    display: none;
}

/* Additional styles for registration and login pages */
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
</style>
"""

# Inject custom CSS and Google Fonts (remove particles.js since it's not in the image)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
""", unsafe_allow_html=True)
st.markdown(custom_css, unsafe_allow_html=True)

# JavaScript for smooth scrolling (unchanged)
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

# Helper functions (unchanged)
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
        # Define tone based on user type
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

def render_share_button(blog_content):
    st.subheader("Share Your Blog Post")
    st.write("Click below to share your blog post via email, WhatsApp, or other apps. If sharing is not supported, the text will be copied to your clipboard.")
    
    # Escape backticks and other special characters in blog_content
    escaped_blog_content = blog_content.replace('"', '\\"').replace('\n', '\\n')
    
    # Custom JavaScript for sharing or copying to clipboard
    share_script = f"""
    <button onclick="shareBlog()" class="share-btn" aria-label="Share Blog Post">Share Blog Post</button>
    <script>
    function shareBlog() {{
        const text = "{escaped_blog_content}";
        if (navigator.share) {{
            navigator.share({{
                title: 'My Blog Post',
                text: text,
                url: window.location.href
            }}).then(() => alert('Shared successfully!'))
              .catch((error) => console.log('Error sharing:', error));
        }} else {{
            navigator.clipboard.writeText(text).then(() => {{
                alert('Blog post copied to clipboard! You can now paste it to share.');
            }});
        }}
    }}
    </script>
    """
    st.markdown(share_script, unsafe_allow_html=True)

# Navigation logic using st.query_params
query_params = st.query_params
page = query_params.get("page", "login")  # Default to "login" if no "page" param

# Initialize session state for authentication
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'name' not in st.session_state:
    st.session_state.name = None
if 'blog_content' not in st.session_state:
    st.session_state.blog_content = ""

# Registration Page

# Registration Page
# Registration Page
# Registration Page
if page == "register":
    st.markdown("""
    <div class="auth-container">
        <h1>Register</h1>
        <p>Create a new account to access the Blog Generator</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write(f"Debug: Current page is '{page}'")  # Debug to confirm page
    try:
        st.write("Debug: Attempting to render registration form...")  # Debug message
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
        st.write(f"Debug: Registration result: email={email_of_registered_user}, username={username_of_registered_user}, name={name_of_registered_user}")
        if email_of_registered_user:
            st.success('User registered successfully! Please log in.')
            # Update the config file
            st.write("Debug: Updating config.yaml...")
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
            st.write("Debug: Config updated. Waiting 1 second before redirect...")
            time.sleep(1)
            st.write("Debug: Setting query param to redirect to login...")
            st.query_params["page"] = "login"
            st.write("Debug: Calling st.rerun()...")
            st.rerun()
            # Fallback JavaScript redirect
            st.markdown("""
            <script>
            setTimeout(function() {
                window.location.href = "?page=login";
            }, 1000);
            </script>
            """, unsafe_allow_html=True)
        else:
            st.error("Registration failed: No email returned. Please ensure the email and username are unique and passwords match.")
    except Exception as e:
        st.error(f"Registration failed with error: {str(e)}")
    
    st.markdown("""
    <div class="auth-container">
        <p>Already have an account? <a href="?page=login"  class="auth-link">Log In</a></p>
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
    
    if st.session_state.get('authentication_status'):
        st.success(f'Welcome *{st.session_state.get("name")}*')
         # Brief delay to show success message
        st.query_params["page"] = "home"
        st.rerun()
    elif st.session_state.get('authentication_status') is False:
        st.error('Username/password is incorrect')
    elif st.session_state.get('authentication_status') is None:
        st.warning('Please enter your username and password')
    
    st.markdown("""
    <div class="auth-container">
        <p>Don't have an account? <a href="?page=register"  class="auth-link">Register</a></p>
    </div>
    """, unsafe_allow_html=True)

# Logout Functionality
def logout():
    authenticator.logout(location='unrendered')  # Execute logout logic without rendering button
    st.session_state.authentication_status = None
    st.session_state.username = None
    st.session_state.name = None
    st.query_params["page"] = "login"
    st.rerun()

# Sidebar with user info and logout (only shown when authenticated)
if st.session_state.authentication_status:
    st.sidebar.title(f"Welcome, {st.session_state.name}!")
    if st.sidebar.button("Logout", key="logout_btn"):
        logout()

# Protect home and other pages (only accessible if authenticated)
if not st.session_state.authentication_status and page not in ["login", "register"]:
    st.warning("Please log in to access this page.")
    st.query_params["page"] = "login"
    st.rerun()

# Sidebar user type selection (only shown on generator pages and when authenticated)
if st.session_state.authentication_status and page != "home":
    st.sidebar.title("Options")
    user_type = st.sidebar.selectbox("Target Audience", ["Researchers", "Common Students", "Data Scientists"])
else:
    user_type = None  # Not needed on home page

# Landing Section (updated to match the image)
if st.session_state.authentication_status and page == "home":
    st.markdown("""
    <div class="landing">
        <div class="logo">TIMEX</div>
        <h1>Blog Generator</h1>
        <p>Want More Blog Ideas? Let AI Think of Ideas for You</p>
        <button class="landing-btn" aria-label="Get Started" onclick="scrollToContainers()">Get Started</button>
    </div>
    """, unsafe_allow_html=True)

    # Remove the logo image since it's now part of the landing section as text
    # logo = Image.open("images/1.png")
    # st.image(logo, width=150)

    # About Us Section (unchanged)
    st.markdown("""
    <div class="section">
        <h2>About us</h2>
        <p>Our Blog Generation Project is an AI-powered tool designed to simplify content creation. By accepting inputs in three ways—text, images, and URLs—it transforms your ideas into engaging blog posts. Whether you’re a researcher, student, or content creator, our tool adapts to your needs, generating high-quality articles tailored to your audience. With advanced AI technology, it saves time, sparks creativity, and ensures professional results. From analyzing images to extracting insights from web pages, our platform offers a seamless and versatile solution for all your blogging needs. Start creating captivating content today with just a few clicks!</p>
        <button class="landing-btn" style="margin-top: 20px;" aria-label="Get Started for Free">Get Started for Free</button>
    </div>
    """, unsafe_allow_html=True)

# Main Content (Blog Generator Pages, only accessible if authenticated)
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
            st.query_params["page"] = "image"
            st.rerun()

# Text Blog Generator Page (only accessible if authenticated)
elif st.session_state.authentication_status and page == "text":
    st.markdown("""
    <div class="header">
        <h1><i class="fas fa-file-alt" style="margin-right: 10px;"></i> Text Blog Generator</h1>
        <p>Turn your ideas into a blog post</p>
    </div>
    <div class="section">
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #6C63FF; color: white; border-radius: 50%; line-height: 30px;">1</span>
                <p style="color: #333333; font-size: 0.9em;">Enter Text</p>
            </div>
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #FF6584; color: white; border-radius: 50%; line-height: 30px;">2</span>
                <p style="color: #333333; font-size: 0.9em;">Generate Blog</p>
            </div>
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #00C4B4; color: white; border-radius: 50%; line-height: 30px;">3</span>
                <p style="color: #333333; font-size: 0.9em;">Share/Download</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
        st.query_params["page"] = "home"
        st.rerun()

# URL Blog Generator Page (only accessible if authenticated)
elif st.session_state.authentication_status and page == "url":
    st.markdown("""
    <div class="header">
        <h1><i class="fas fa-link" style="margin-right: 10px;"></i> URL Blog Generator</h1>
        <p>Generate a blog post from a URL</p>
    </div>
    <div class="section">
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #6C63FF; color: white; border-radius: 50%; line-height: 30px;">1</span>
                <p style="color: #333333; font-size: 0.9em;">Enter URL</p>
            </div>
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #FF6584; color: white; border-radius: 50%; line-height: 30px;">2</span>
                <p style="color: #333333; font-size: 0.9em;">Generate Blog</p>
            </div>
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #00C4B4; color: white; border-radius: 50%; line-height: 30px;">3</span>
                <p style="color: #333333; font-size: 0.9em;">Share/Download</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
        st.query_params["page"] = "home"
        st.rerun()

# Image Blog Generator Page (only accessible if authenticated)
elif st.session_state.authentication_status and page == "image":
    st.markdown("""
    <div class="header">
        <h1><i class="fas fa-image" style="margin-right: 10px;"></i> Image Blog Generator</h1>
        <p>Turn an image into a blog post</p>
    </div>
    <div class="section">
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #6C63FF; color: white; border-radius: 50%; line-height: 30px;">1</span>
                <p style="color: #333333; font-size: 0.9em;">Upload Image</p>
            </div>
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #FF6584; color: white; border-radius: 50%; line-height: 30px;">2</span>
                <p style="color: #333333; font-size: 0.9em;">Generate Blog</p>
            </div>
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #00C4B4; color: white; border-radius: 50%; line-height: 30px;">3</span>
                <p style="color: #333333; font-size: 0.9em;">Share/Download</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
        st.query_params["page"] = "home"
        st.rerun()

# FAQ Section (only on home page and when authenticated, with answers always visible)
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

# Footer with Feedback Form (only shown when authenticated)
if st.session_state.authentication_status:
    st.markdown("""
    <div class="footer">
        <p>© 2025 Blog Generator | Powered by Streamlit & Google Gemini API</p>
        <p><a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a> | <a href="#">Contact Us</a></p>
        <div style="margin-top: 20px;">
            <h3 style="color: #6C63FF;">Feedback</h3>
            <textarea placeholder="Let us know how we can improve..." style="width: 100%; max-width: 400px; padding: 10px; border-radius: 8px; background: #FFFFFF; color: #333333; border: 1px solid #6C63FF;" aria-label="Feedback Input"></textarea>
            <button style="margin-top: 10px; background: linear-gradient(135deg, #6C63FF, #FF6584);" aria-label="Submit Feedback">Submit Feedback</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
=======
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

# Set page config as the FIRST Streamlit command
st.set_page_config(page_title="Blog Generator", page_icon="📝", layout="wide")

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

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
    auto_hash=True  # Automatically hash plain text passwords
)

# Custom CSS with updated styles for the landing section
custom_css = """
<style>
/* Existing styles */
body {
    font-family: 'Poppins', sans-serif;
    background: #F5F5F5; /* Light gray background */
    color: #333333; /* Dark gray text */
}
h1, h2, h3, h4, h5, h6 {
    color: #6C63FF; /* Primary purple */
}
.header {
    text-align: center;
    margin-bottom: 40px;
}
.section {
    background: #FFFFFF; /* White background */
    padding: 40px;
    border-radius: 16px;
    margin-bottom: 40px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.container {
    background: linear-gradient(135deg, #6C63FF, #FF6584); /* Gradient from purple to pink */
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
    color: #333333; /* Dark gray */
    margin-top: 10px;
    font-size: 1em;
    font-weight: 300;
    margin-left: 20px;
}

/* Updated styles for the landing section */
.landing {
    position: relative;
    background: linear-gradient(135deg, #6C63FF, #FF6584); /* Gradient matching the image */
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

/* Logo styling */
.logo {
    position: absolute;
    top: 20px;
    left: 20px;
    font-size: 1.5em;
    font-weight: 700;
    color: #333333;
}

/* Remove decorative circles since they are not in the image */
.decorative-circle {
    display: none;
}

/* Remove particles.js since it's not in the image */
#particles-js {
    display: none;
}

/* Additional styles for registration and login pages */
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
</style>
"""

# Inject custom CSS and Google Fonts (remove particles.js since it's not in the image)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
""", unsafe_allow_html=True)
st.markdown(custom_css, unsafe_allow_html=True)

# JavaScript for smooth scrolling (unchanged)
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

# Helper functions (unchanged)
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
        # Define tone based on user type
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

def render_share_button(blog_content):
    st.subheader("Share Your Blog Post")
    st.write("Click below to share your blog post via email, WhatsApp, or other apps. If sharing is not supported, the text will be copied to your clipboard.")
    
    # Escape backticks and other special characters in blog_content
    escaped_blog_content = blog_content.replace('"', '\\"').replace('\n', '\\n')
    
    # Custom JavaScript for sharing or copying to clipboard
    share_script = f"""
    <button onclick="shareBlog()" class="share-btn" aria-label="Share Blog Post">Share Blog Post</button>
    <script>
    function shareBlog() {{
        const text = "{escaped_blog_content}";
        if (navigator.share) {{
            navigator.share({{
                title: 'My Blog Post',
                text: text,
                url: window.location.href
            }}).then(() => alert('Shared successfully!'))
              .catch((error) => console.log('Error sharing:', error));
        }} else {{
            navigator.clipboard.writeText(text).then(() => {{
                alert('Blog post copied to clipboard! You can now paste it to share.');
            }});
        }}
    }}
    </script>
    """
    st.markdown(share_script, unsafe_allow_html=True)

# Navigation logic using st.query_params
query_params = st.query_params
page = query_params.get("page", "login")  # Default to "login" if no "page" param

# Initialize session state for authentication
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'name' not in st.session_state:
    st.session_state.name = None
if 'blog_content' not in st.session_state:
    st.session_state.blog_content = ""

# Registration Page

# Registration Page
# Registration Page
# Registration Page
if page == "register":
    st.markdown("""
    <div class="auth-container">
        <h1>Register</h1>
        <p>Create a new account to access the Blog Generator</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write(f"Debug: Current page is '{page}'")  # Debug to confirm page
    try:
        st.write("Debug: Attempting to render registration form...")  # Debug message
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
        st.write(f"Debug: Registration result: email={email_of_registered_user}, username={username_of_registered_user}, name={name_of_registered_user}")
        if email_of_registered_user:
            st.success('User registered successfully! Please log in.')
            # Update the config file
            st.write("Debug: Updating config.yaml...")
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
            st.write("Debug: Config updated. Waiting 1 second before redirect...")
            time.sleep(1)
            st.write("Debug: Setting query param to redirect to login...")
            st.query_params["page"] = "login"
            st.write("Debug: Calling st.rerun()...")
            st.rerun()
            # Fallback JavaScript redirect
            st.markdown("""
            <script>
            setTimeout(function() {
                window.location.href = "?page=login";
            }, 1000);
            </script>
            """, unsafe_allow_html=True)
        else:
            st.error("Registration failed: No email returned. Please ensure the email and username are unique and passwords match.")
    except Exception as e:
        st.error(f"Registration failed with error: {str(e)}")
    
    st.markdown("""
    <div class="auth-container">
        <p>Already have an account? <a href="?page=login"  class="auth-link">Log In</a></p>
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
    
    if st.session_state.get('authentication_status'):
        st.success(f'Welcome *{st.session_state.get("name")}*')
         # Brief delay to show success message
        st.query_params["page"] = "home"
        st.rerun()
    elif st.session_state.get('authentication_status') is False:
        st.error('Username/password is incorrect')
    elif st.session_state.get('authentication_status') is None:
        st.warning('Please enter your username and password')
    
    st.markdown("""
    <div class="auth-container">
        <p>Don't have an account? <a href="?page=register"  class="auth-link">Register</a></p>
    </div>
    """, unsafe_allow_html=True)

# Logout Functionality
def logout():
    authenticator.logout(location='unrendered')  # Execute logout logic without rendering button
    st.session_state.authentication_status = None
    st.session_state.username = None
    st.session_state.name = None
    st.query_params["page"] = "login"
    st.rerun()

# Sidebar with user info and logout (only shown when authenticated)
if st.session_state.authentication_status:
    st.sidebar.title(f"Welcome, {st.session_state.name}!")
    if st.sidebar.button("Logout", key="logout_btn"):
        logout()

# Protect home and other pages (only accessible if authenticated)
if not st.session_state.authentication_status and page not in ["login", "register"]:
    st.warning("Please log in to access this page.")
    st.query_params["page"] = "login"
    st.rerun()

# Sidebar user type selection (only shown on generator pages and when authenticated)
if st.session_state.authentication_status and page != "home":
    st.sidebar.title("Options")
    user_type = st.sidebar.selectbox("Target Audience", ["Researchers", "Common Students", "Data Scientists"])
else:
    user_type = None  # Not needed on home page

# Landing Section (updated to match the image)
if st.session_state.authentication_status and page == "home":
    st.markdown("""
    <div class="landing">
        <div class="logo">TIMEX</div>
        <h1>Blog Generator</h1>
        <p>Want More Blog Ideas? Let AI Think of Ideas for You</p>
        <button class="landing-btn" aria-label="Get Started" onclick="scrollToContainers()">Get Started</button>
    </div>
    """, unsafe_allow_html=True)

    # Remove the logo image since it's now part of the landing section as text
    # logo = Image.open("images/1.png")
    # st.image(logo, width=150)

    # About Us Section (unchanged)
    st.markdown("""
    <div class="section">
        <h2>About us</h2>
        <p>Our Blog Generation Project is an AI-powered tool designed to simplify content creation. By accepting inputs in three ways—text, images, and URLs—it transforms your ideas into engaging blog posts. Whether you’re a researcher, student, or content creator, our tool adapts to your needs, generating high-quality articles tailored to your audience. With advanced AI technology, it saves time, sparks creativity, and ensures professional results. From analyzing images to extracting insights from web pages, our platform offers a seamless and versatile solution for all your blogging needs. Start creating captivating content today with just a few clicks!</p>
        <button class="landing-btn" style="margin-top: 20px;" aria-label="Get Started for Free">Get Started for Free</button>
    </div>
    """, unsafe_allow_html=True)

# Main Content (Blog Generator Pages, only accessible if authenticated)
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
            st.query_params["page"] = "image"
            st.rerun()

# Text Blog Generator Page (only accessible if authenticated)
elif st.session_state.authentication_status and page == "text":
    st.markdown("""
    <div class="header">
        <h1><i class="fas fa-file-alt" style="margin-right: 10px;"></i> Text Blog Generator</h1>
        <p>Turn your ideas into a blog post</p>
    </div>
    <div class="section">
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #6C63FF; color: white; border-radius: 50%; line-height: 30px;">1</span>
                <p style="color: #333333; font-size: 0.9em;">Enter Text</p>
            </div>
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #FF6584; color: white; border-radius: 50%; line-height: 30px;">2</span>
                <p style="color: #333333; font-size: 0.9em;">Generate Blog</p>
            </div>
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #00C4B4; color: white; border-radius: 50%; line-height: 30px;">3</span>
                <p style="color: #333333; font-size: 0.9em;">Share/Download</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
        st.query_params["page"] = "home"
        st.rerun()

# URL Blog Generator Page (only accessible if authenticated)
elif st.session_state.authentication_status and page == "url":
    st.markdown("""
    <div class="header">
        <h1><i class="fas fa-link" style="margin-right: 10px;"></i> URL Blog Generator</h1>
        <p>Generate a blog post from a URL</p>
    </div>
    <div class="section">
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #6C63FF; color: white; border-radius: 50%; line-height: 30px;">1</span>
                <p style="color: #333333; font-size: 0.9em;">Enter URL</p>
            </div>
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #FF6584; color: white; border-radius: 50%; line-height: 30px;">2</span>
                <p style="color: #333333; font-size: 0.9em;">Generate Blog</p>
            </div>
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #00C4B4; color: white; border-radius: 50%; line-height: 30px;">3</span>
                <p style="color: #333333; font-size: 0.9em;">Share/Download</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
        st.query_params["page"] = "home"
        st.rerun()

# Image Blog Generator Page (only accessible if authenticated)
elif st.session_state.authentication_status and page == "image":
    st.markdown("""
    <div class="header">
        <h1><i class="fas fa-image" style="margin-right: 10px;"></i> Image Blog Generator</h1>
        <p>Turn an image into a blog post</p>
    </div>
    <div class="section">
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #6C63FF; color: white; border-radius: 50%; line-height: 30px;">1</span>
                <p style="color: #333333; font-size: 0.9em;">Upload Image</p>
            </div>
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #FF6584; color: white; border-radius: 50%; line-height: 30px;">2</span>
                <p style="color: #333333; font-size: 0.9em;">Generate Blog</p>
            </div>
            <div style="text-align: center;">
                <span style="display: block; width: 30px; height: 30px; background: #00C4B4; color: white; border-radius: 50%; line-height: 30px;">3</span>
                <p style="color: #333333; font-size: 0.9em;">Share/Download</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
        st.query_params["page"] = "home"
        st.rerun()

# FAQ Section (only on home page and when authenticated, with answers always visible)
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

# Footer with Feedback Form (only shown when authenticated)
if st.session_state.authentication_status:
    st.markdown("""
    <div class="footer">
        <p>© 2025 Blog Generator | Powered by Streamlit & Google Gemini API</p>
        <p><a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a> | <a href="#">Contact Us</a></p>
        <div style="margin-top: 20px;">
            <h3 style="color: #6C63FF;">Feedback</h3>
            <textarea placeholder="Let us know how we can improve..." style="width: 100%; max-width: 400px; padding: 10px; border-radius: 8px; background: #FFFFFF; color: #333333; border: 1px solid #6C63FF;" aria-label="Feedback Input"></textarea>
            <button style="margin-top: 10px; background: linear-gradient(135deg, #6C63FF, #FF6584);" aria-label="Submit Feedback">Submit Feedback</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
>>>>>>> 0810847fbfe03ed6f2c6668a105e86b329787b67
