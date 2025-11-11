import streamlit as st
import polars as pl
from typing import Literal

ks_db = 'crowdfunding_comps.db'
ks_table = 'kickstarter_records_w_embeds'
ks_table_cols = ['id','name','blurb','goal','category_parent_name','category_name','embeddings']
ks_kpi_cols = ['prelaunch_activated', 'launched_at','deadline','backers_count','creator_name'
               ,'usd_pledged','percent_funded', 'url_project']

css = """<style>
    /* Import fonts: Poppins (headers) and Roboto (body) */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&family=Roboto:wght@400;700&display=swap');

    /* Set all headers (H1-H6) to Poppins */
    h1, h2, h3, h4, h5, h6, .stHeading, .stHeading * {
        font-family: 'Poppins', sans-serif !important;
    }

    /* Set all normal text to Roboto */
    body, .stApp, .main, .block-container, p, div:not(.stCodeBlock), .stText {
        font-family: 'Roboto', sans-serif !important;
    }

    /* Exclude source code elements */
    .stCodeBlock, pre, code {
        font-family: monospace !important; 
    }

    .dataframe th, .dataframe td {
    white-space: pre-wrap;
    vertical-align: top;
    font-size: 14px;
    }
    .dataframe .blank, .dataframe .nan {
        color: #ccc;
    }
    
    </style>
    """



class Model_Cols:
  embedding_columns = ['blurb','name']

  categorical = ['category_name','category_parent_name']

  numeric_columns = ['goal']

categories = {'Technology': ['Web',
  'Apps',
  'Flight',
  'Robots',
  'Makerspaces',
  'Space Exploration',
  'Hardware',
  'Sound',
  'DIY Electronics',
  'Camera Equipment',
  'Gadgets',
  '3D Printing',
  'Fabrication Tools',
  'Wearables',
  'Software'],
 'Film & Video': ['Thrillers',
  'Drama',
  'Shorts',
  'Movie Theaters',
  'Fantasy',
  'Family',
  'Television',
  'Documentary',
  'Narrative Film',
  'Animation',
  'Comedy',
  'Webseries',
  'Horror',
  'Music Videos',
  'Science Fiction',
  'Action',
  'Experimental',
  'Festivals',
  'Romance'],
 'Crafts': ['Quilts',
  'DIY',
  'Pottery',
  'Printing',
  'Weaving',
  'Embroidery',
  'Stationery',
  'Crochet',
  'Candles',
  'Glass',
  'Woodworking',
  'Knitting',
  'Taxidermy'],
 'Games': ['Gaming Hardware',
  'Live Games',
  'Tabletop Games',
  'Video Games',
  'Playing Cards',
  'Mobile Games',
  'Puzzles'],
 'Journalism': ['Web', 'Video', 'Audio', 'Print', 'Photo'],
 'Art': ['Textiles',
  'Conceptual Art',
  'Video Art',
  'Digital Art',
  'Mixed Media',
  'Illustration',
  'Performance Art',
  'Public Art',
  'Installations',
  'Social Practice',
  'Sculpture',
  'Painting',
  'Ceramics'],
 'Publishing': ['Art Books',
  'Young Adult',
  'Anthologies',
  'Calendars',
  'Letterpress',
  'Academic',
  'Translations',
  'Zines',
  'Poetry',
  'Comedy',
  'Nonfiction',
  'Fiction',
  "Children's Books",
  'Periodicals',
  'Radio & Podcasts',
  'Literary Journals',
  'Literary Spaces'],
 'Music': ['Metal',
  'Latin',
  'Electronic Music',
  'Rock',
  'World Music',
  'Country & Folk',
  'Indie Rock',
  'Comedy',
  'Hip-Hop',
  'Classical Music',
  'Pop',
  'Kids',
  'Faith',
  'Jazz',
  'Blues',
  'R&B',
  'Punk',
  'Chiptune'],
 'Theater': ['Festivals',
  'Experimental',
  'Spaces',
  'Plays',
  'Musical',
  'Comedy',
  'Immersive'],
 'Comics': ['Webcomics',
  'Events',
  'Graphic Novels',
  'Comic Books',
  'Anthologies'],
 'Food': ['Farms',
  'Cookbooks',
  'Bacon',
  'Events',
  'Community Gardens',
  'Spaces',
  'Restaurants',
  'Small Batch',
  'Drinks',
  'Food Trucks',
  "Farmer's Markets",
  'Vegan'],
 'Dance': ['Performances', 'Residencies', 'Workshops', 'Spaces'],
 'Fashion': ['Pet Fashion',
  'Apparel',
  'Footwear',
  'Accessories',
  'Couture',
  'Childrenswear',
  'Jewelry',
  'Ready-to-wear'],
 'Design': ['Typography',
  'Architecture',
  'Toys',
  'Graphic Design',
  'Product Design',
  'Interactive Design',
  'Civic Design'],
 'Photography': ['Animals',
  'Photobooks',
  'Nature',
  'Places',
  'People',
  'Fine Art']}

parent_categories = list(categories.keys())
parent_categories.sort()