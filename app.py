import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import shutil
import mimetypes
from pytube import YouTube

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Set page config as the first Streamlit command
st.set_page_config(page_title="Blog Generator", page_icon="📝")

# Helper function to check if a URL points to an image
def is_image_url(url):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    return any(url.lower().endswith(ext) for ext in image_extensions)

# Helper function to fetch YouTube video metadata
def fetch_youtube_content(url):
    try:
        yt = YouTube(url)
        content = f"Title: {yt.title}\nDescription: {yt.description or 'No description available'}"
        return content
    except Exception as e:
        return f"Error fetching YouTube content: {str(e)}"

# Helper function to fetch text content from a URL
def fetch_text_from_url(url):
    try:
        if "youtube.com" in url or "youtu.be" in url:
            return fetch_youtube_content(url)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract text from paragraphs, headings, etc.
        text_content = ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
        return text_content if text_content else "No text content could be extracted from the URL."
    except Exception as e:
        return f"Error fetching URL content: {str(e)}"

# Helper function to save inputs and outputs to a timestamped directory
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

# Function to generate blog content based on input type and user type
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
                # Handle URL pointing to an image
                response = requests.get(input_data, stream=True)
                response.raise_for_status()
                image_content = response.content
                prompt = f"Write a blog post based on this image in approximately {word_count} words. Use a {tone} tone suitable for {user_type}."
                response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_content}])
                return response.text
            else:
                # Handle URL pointing to text content or YouTube video
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

# Function to render the share button
def render_share_button(blog_content):
    st.subheader("Share Your Blog Post")
    st.write("Click below to share your blog post via email, WhatsApp, or other apps. If sharing is not supported, the text will be copied to your clipboard.")
    
    # Escape backticks in blog_content outside the string
    escaped_blog_content = blog_content.replace('`', '\\`')
    
    # Custom JavaScript for sharing or copying to clipboard
    share_script = """
    <button onclick="shareBlog()">Share Blog Post</button>
    <script>
    function shareBlog() {
        const text = `%s`;
        if (navigator.share) {
            navigator.share({
                title: 'My Blog Post',
                text: text,
                url: window.location.href
            }).then(() => alert('Shared successfully!'))
              .catch((error) => console.log('Error sharing:', error));
        } else {
            navigator.clipboard.writeText(text).then(() => {
                alert('Blog post copied to clipboard! You can now paste it to share.');
            });
        }
    }
    </script>
    """ % escaped_blog_content  # Use % formatting to embed the escaped string

    st.write(share_script, unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a Page", ["Text Blog Generator", "URL Blog Generator", "Image Blog Generator"])

# Sidebar user type selection
user_type = st.sidebar.selectbox("Target Audience", ["Researchers", "Common Students", "Data Scientists"])

# Placeholder to store blog content for sharing
if 'blog_content' not in st.session_state:
    st.session_state.blog_content = ""

# Page 1: Text Blog Generator
if page == "Text Blog Generator":
    st.title("📝 Text Blog Generator with Gemini API")
    st.write("Enter text to generate a blog post tailored for your audience!")

    # Input widget for text
    input_data = st.text_area("Blog Content", placeholder="Enter the text to inspire your blog post...", height=200)

    # Word count slider
    word_count = st.slider("Approximate Word Count", min_value=100, max_value=1000, value=300, step=50, key="text_word_count")

    # Generate button
    if st.button("Generate Blog", key="text_generate"):
        if not input_data:
            st.error("Please provide text input!")
        else:
            with st.spinner("Generating your blog post..."):
                blog_content = generate_blog_from_input("Text", input_data, user_type, word_count)
                st.session_state.blog_content = blog_content  # Store for sharing
                st.subheader("Generated Blog Post")
                st.write(blog_content)
                
                # Save inputs and outputs
                save_input_output("Text", input_data, blog_content)
                
                # Download option
                st.download_button(
                    label="Download Blog Post",
                    data=blog_content,
                    file_name=f"blog_post_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
                    mime="text/plain",
                    key="text_download"
                )

    # Share button
    if st.session_state.blog_content:
        render_share_button(st.session_state.blog_content)

# Page 2: URL Blog Generator
elif page == "URL Blog Generator":
    st.title("📝 URL Blog Generator with Gemini API")
    st.write("Enter a URL to generate a blog post based on its content, tailored for your audience!")

    # Input widget for URL
    input_data = st.text_input("URL", placeholder="Enter a URL (e.g., webpage, YouTube video, or image URL)...")

    # Word count slider
    word_count = st.slider("Approximate Word Count", min_value=100, max_value=1000, value=300, step=50, key="url_word_count")

    # Generate button
    if st.button("Generate Blog", key="url_generate"):
        if not input_data:
            st.error("Please provide a URL!")
        else:
            with st.spinner("Generating your blog post..."):
                blog_content = generate_blog_from_input("URL", input_data, user_type, word_count)
                st.session_state.blog_content = blog_content  # Store for sharing
                st.subheader("Generated Blog Post")
                st.write(blog_content)
                
                # Save inputs and outputs
                save_input_output("URL", input_data, blog_content)
                
                # Download option
                st.download_button(
                    label="Download Blog Post",
                    data=blog_content,
                    file_name=f"blog_post_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
                    mime="text/plain",
                    key="url_download"
                )

    # Share button
    if st.session_state.blog_content:
        render_share_button(st.session_state.blog_content)

# Page 3: Image Blog Generator
elif page == "Image Blog Generator":
    st.title("📝 Image Blog Generator with Gemini API")
    st.write("Upload an image to generate a blog post, tailored for your audience!")

    # Input widget for image
    input_data = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png", "gif"])

    # Word count slider
    word_count = st.slider("Approximate Word Count", min_value=100, max_value=1000, value=300, step=50, key="image_word_count")

    # Generate button
    if st.button("Generate Blog", key="image_generate"):
        if not input_data:
            st.error("Please upload an image!")
        else:
            with st.spinner("Generating your blog post..."):
                blog_content = generate_blog_from_input("Image File", input_data, user_type, word_count)
                st.session_state.blog_content = blog_content  # Store for sharing
                st.subheader("Generated Blog Post")
                st.write(blog_content)
                
                # Save inputs and outputs
                save_input_output("Image File", input_data, blog_content)
                
                # Download option
                st.download_button(
                    label="Download Blog Post",
                    data=blog_content,
                    file_name=f"blog_post_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
                    mime="text/plain",
                    key="image_download"
                )

    # Share button
    if st.session_state.blog_content:
        render_share_button(st.session_state.blog_content)

# Footer
st.write("Powered by Streamlit and Google Gemini API")


