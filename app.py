import streamlit as st
import pandas as pd
import joblib
from PIL import Image, ImageDraw, ImageFont

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")

# ----------------------------
# Dark theme + dropdown scrollbar + button styling
# ----------------------------
st.markdown("""
<style>
body { background-color: #000000; color: white; }
.block-container { background-color: #000000; color: white; }
h1, h3 { color: #2E8B57; text-align: center; }
.stButton>button {
    background-color: #2E8B57;
    color: white;
    font-size: 16px;
    height: 3em;
    width: 100%;
    border-radius: 12px;
    transition: background-color 0.3s ease;
}
.stButton>button:hover { background-color: #3CB371; }

.stSelectbox>div>div>div>select {
    background-color: black !important;
    color: blue !important;
    font-weight: bold;
}
/* Webkit scrollbar */
select::-webkit-scrollbar { width:12px; }
select::-webkit-scrollbar-track { background:#000000; }
select::-webkit-scrollbar-thumb { background-color:#1E90FF; border-radius:6px; border:3px solid #000000; }
/* Firefox scrollbar */
select { scrollbar-width: thin; scrollbar-color: #1E90FF #000000; }
/* Option text */
option { background-color:black; color:blue; }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Load data
# ----------------------------
@st.cache_data
def load_movies():
    return pd.read_csv("movies.csv")

@st.cache_resource
def load_similarity():
    with open("similarity.pkl", "rb") as f:
        return joblib.load(f)

movies = load_movies()
similarity = load_similarity()

# ----------------------------
# Extract year
# ----------------------------
def get_year(x):
    try:
        return str(x).split("-")[0]
    except:
        return ""

release_col = movies["release_date"] if "release_date" in movies.columns else movies.get("release_date.x", "")
movies["year"] = release_col.apply(lambda x: get_year(x))

# ----------------------------
# Recommend function
# ----------------------------
def recommend(movie_name):
    index = movies[movies["title"].str.lower() == movie_name.lower()].index
    if len(index) == 0:
        return []

    index = index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:9]

    results = []
    for i in movie_list:
        m = movies.iloc[i[0]]
        results.append({
            "title": m["title"],
            "year": m["year"],
            "rating": m.get("vote_average", "")
        })
    return results

# ----------------------------
# Image with overlay title (CENTERED, WIDER)
# ----------------------------
img = Image.open("poster1.jpg")  # replace with your image
img = img.resize((1100, 300))  # width increased to 1100px

draw = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("arial.ttf", 40)
except:
    font = ImageFont.load_default()

text = "🎬 Movie Recommendation System"
bbox = draw.textbbox((0,0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# semi-transparent rectangle behind text
rect_x0 = (img.width - text_width)/2 - 10
rect_y0 = 20 - 5
rect_x1 = rect_x0 + text_width + 20
rect_y1 = rect_y0 + text_height + 10
draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill=(0,0,0,150))

# draw text
x = (img.width - text_width)/2
y = 20
draw.text((x,y), text, font=font, fill="white")

# Center the image in header
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
st.image(img)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Dropdown (movie search)
# ----------------------------
movie_list_values = movies["title"].values
movie_name = st.selectbox("Search Movie", movie_list_values)

# ----------------------------
# Recommendation output
# ----------------------------
if st.button("Recommend"):
    if not movie_name:
        st.warning("Please select a movie.")
    else:
        recs = recommend(movie_name)
        if not recs:
            st.error("Movie not found.")
        else:
            st.markdown(f"""
            <div style='padding:20px; margin:10px 0; border-radius:15px; background-color:#1a1a1a; color:white;'>
            <h3 style='text-align:center; color:#2E8B57;'>Recommended Movies</h3>
            </div>
            """, unsafe_allow_html=True)

            for movie in recs:
                st.markdown(f"""
                <div style='padding:15px; margin-bottom:12px; border-radius:10px; background-color:#1a1a1a; color:white;'>
                    <h4>{movie['title']}</h4>
                    <p>📅 {movie['year']} &nbsp;&nbsp; ⭐ {movie['rating']}</p>
                </div>
                """, unsafe_allow_html=True)

# ----------------------------
# Footer with GitHub/LinkedIn (INCREASE FONT)
# ----------------------------
st.markdown("""
<p style="text-align:center; color:gray; font-size:18px;">
Developed by Amit Verma | 
<a href='https://github.com/V19Amit' style='color:#1E90FF; font-size:18px;'>GitHub</a> | 
<a href='https://www.linkedin.com/in/amit-verma-b75373326?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app' style='color:#1E90FF; font-size:18px;'>LinkedIn</a>
</p>
""", unsafe_allow_html=True)
