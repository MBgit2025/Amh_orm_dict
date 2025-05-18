#app.py (Streamlit Frontend - Modified)
import streamlit as st
import pandas as pd
from typing import Optional, List, Dict # Keep for type hinting


st.set_page_config(page_title="Bizu_DS - Multilingual Dictionary", layout="centered")

# Import your database utility functions
from database_utils import (
    search_word_in_db,
    get_random_word_from_db,
    initialize_database
)

# --- Initialize Database (runs once per app session) ---
# This needs to be called early, before any DB operations
initialize_database()

# --- UI Setup ---
#st.set_page_config(page_title="Bizu_DS - Multilingual Dictionary", layout="centered")

# --- Header Section ---
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    try:
        # Adjust path relative to app.py
        st.image("assets/Bandirakokeb.jpg", width=180)
    except FileNotFoundError:
        st.warning("Header image not found at assets/Bandirakokeb.jpg")
    except Exception as e:
        st.write(f"Error loading image: {e}")


with col2:
    st.markdown("<h3 style='text-align: center; color: navy;'>ቋንቋ በቀላል መማሪያ - Affaan Baradha - Learn Language</h3>", unsafe_allow_html=True)

with col3:
    try:
        st.image("assets/Bandirakokeb.jpg", width=180)
    except FileNotFoundError:
        pass # Optionally hide if not found or show placeholder
    except Exception as e:
        st.write(f"Error loading image: {e}")


# Language selection dropdown
languages = ["Amharic", "OromLatin", "OromSaba", "English"]
st.markdown("<p style='font-size: larger; font-weight: bold; color: #800080;'>First Select Your Typing Language</p>", unsafe_allow_html=True)
selected_language = st.selectbox(
    label="Select your typing language",  # A non-empty, descriptive label
    options=languages,
    key='language_select',
    label_visibility="collapsed"  # This will hide the label from view
)

# Input field for the search query
st.markdown("<p style='font-size: larger; font-weight: bold; color: #000000;'>Type below the word you are looking for in the selected language</p>", unsafe_allow_html=True)
search_query = st.text_input(
    label="Enter the word to search",  # A non-empty, descriptive label
    key='search_input',
    label_visibility="collapsed" # This will hide the label from view
)

# --- Search Results ---
if search_query:
    try:
        # Directly call the database search function
        results: List[Dict[str, Optional[str]]] = search_word_in_db(selected_language, search_query)
        if results:
            st.subheader("Search Results:")
            # Create a list of dictionaries for the table
            table_data = []
            for result in results:
                table_data.append({
                    "Amharic": result.get('amharic', ''),
                    "OromLatin": result.get('oromlatin', ''),
                    "OromSaba": result.get('oromsaba', ''),
                    "English": result.get('english', '')
                })
            st.table(pd.DataFrame(table_data))
        else:
            st.info("No results found for your query.") # Use st.info for non-error messages
    except Exception as e:
        st.error(f"Error during search: {e}")
        print(f"Error during search in app.py: {e}")


# --- Random Word ---
st.subheader("Random Word ") # Changed title slightly
if st.button("Click to Get a Random Word", key='random_word_button'): # Changed button text
    try:
        # Directly call the database random word function
        random_word: Optional[Dict[str, Optional[str]]] = get_random_word_from_db()
        if random_word:
            random_word_data = {
                "Amharic": [random_word.get('amharic', '')],
                "OromLatin": [random_word.get('oromlatin', '')],
                "OromSaba": [random_word.get('oromsaba', '')],
                "English": [random_word.get('english', '')]
            }
            st.table(pd.DataFrame(random_word_data))
        else:
            st.warning("No words found in the database to pick a random one.")
    except Exception as e:
        st.error(f"Error fetching random word: {e}")
        print(f"Error fetching random word in app.py: {e}")

# --- Notes (Footer) ---
st.markdown("---")
st.write("Thanks for using this app, please send comments or corrections to mihretbizu9@gmail.com, Thank you!")
scribd_pdf_url = "https://www.scribd.com/doc/315999693/Afan-Oromo-English-English-Afan-Oromo-Dictionary"
pdf_display_name = "Afan-Oromo English-English-Afan-Oromo-Dictionary (Cambridge University Press, 1913 on Scribd)"

# Using st.markdown with an <a> tag
st.markdown(f"""References used are:
1) <a href="{scribd_pdf_url}" target="_blank">{pdf_display_name}</a> - Digitized By Google (Hosted on Scribd)
2) Google Translate and using other Supporting Websites!""", unsafe_allow_html=True)

# --- Styling (Keep your existing CSS) ---
st.markdown(
    """
    <style>
    /* Your existing CSS styles here */
    /* Main background with gradient */
    .stApp {
        background: linear-gradient(to bottom, #006400 0%, #FFFF00 50%, #8B0000 100%); /* Darker Green, Yellow, Darker Red */
        background-size: cover;
        background-attachment: fixed; /* Keeps the gradient fixed during scrolling */
    }

    /* Header */
    h1 {
        color: #000080 !important;
    }

    h3 {
        color: #000080 !important;
    }

    /* Subheaders */
    h2, h4 { /* Combined h2 and h4 rules */
        color: #000000 !important;
    }

   /* Selectbox */
    div[data-baseweb="select"] > div {
        background-color: #d3d3d3;  /* Light Gray */
        color: black !important;
        border: 2px solid #696969 !important; /* Dark Gray */
    }

    /* Style the selectbox dropdown options */
    div[data-baseweb="popover"] ul li {
        background-color: #d3d3d3 !important;  /* Light Gray */
        color: black !important;
    }

    /* Text input */
    div[data-baseweb="input"] > div {
        background-color: #d3d3d3;  /* Light Gray */
        color: black !important;
        border: 2px solid #696969 !important; /* Dark Gray */
    }
    /* Button */
    button {
        background-color: #f0f8ff !important;  /* AliceBlue - very light blue */
        color: black !important;
        border: 2px solid #000000 !important;
    }

    /* Result Paragraphs (general p tag) */
    /* This might be too broad, consider more specific selectors if needed */
    /*
    p {
        color: black !important;
        font-size: 1.2em !important; 
    }
    */

    /* Footer text - Streamlit uses specific classes, better to style generic .stMarkdown or specific elements */
    .stMarkdown p, .stWrite p { /* Target paragraphs within markdown and write */
        color: black !important;
    }


    /* Random word and search result containers (st.table outputs complex HTML) */
    /* Styling tables directly is more reliable */
    .stTable {
        background-color: #d3d3d3 !important;  /* Light Gray */
        border: 2px solid #696969 !important; /* Dark Gray */
        font-size: 1.2em !important; /* Increase font size */
    }
     .stTable > thead > tr > th { /* Target table header cells */
        font-weight: bold !important; /* Make headers bold */
        text-align: left !important;
        color: black !important; /* Ensure header text is black */
        background-color: #c0c0c0 !important; /* Slightly darker gray for header */
    }
    .stTable > tbody > tr > td {
        color: black !important; /* Ensure body text is black */
    }


    /* Divider lines */
    hr {
        border-top: 1px solid black !important;
    }

    /* Image border */
    img {
        border: 4px solid #008000 !important;
    }

    /* More specific selectors for labels if default p styling is too broad */
    /* e.g., for the "First Select Your Typing Language" label */
    .stMarkdown > div > p:first-child { /* Example, might need inspection */
         /* font-size: larger; font-weight: bold; color: #800080; */
    }


    </style>
    """,
    unsafe_allow_html=True,)
