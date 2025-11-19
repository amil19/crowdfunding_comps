# Kickstarter Comparison Engine

## DESCRIPTION
The Kickstarter Comparison Engine transforms large-scale archival crowdfunding data into actionable pre-launch intelligence, accessible through an easy-to-use user interface. 
  
Users can enter a few pieces of campaign  information and the tool will retrieve a table of metadata for similar campaigns, key performance indicators, and links to each of the campaigns.   
  
This package comprises all of the modules used to create, maintain, and operate this tool. These processes include: 
- Extracting/transforming/loading archived data
- Creating text embeddings
- Receiving user-input data
- Retrieving archive data
- Clustering campaigns
- Measuring similarity
- Visualzing results 

The database of campaigns was built using the webscrapes from https://webrobots.io/kickstarter-datasets/ that were loaded into DuckDB/MotherDuck database. The Transformers library was used to create embeddings of campaign data. The user interface was built using Streamlit and the final product was deployd to Streamlit's Community Cloud for for public access.

## Installation
There are two options for working with this tool: cloud and local. Instructions for both processes are listed below.

### Cloud
This is the easiest option to use the Kickstarter Comparison engine. To launch the tool:
* Head to https://crowdfunding-comps.streamlit.app/
* * Note: If the you receive a notification the app has gone to sleep, click the button that says "Yes, get this app back up!" The app should wake up within a few minutes.

### Local
To run the local implementation, perform the following steps:
1. Unzip the teamXXXfinal.zip file
2. Open a new terminal (could be Powershell, Git Bash, or CMD)
3. Set working directory to the folder containing the contents of the zip file using the code below (replacing <> with the actual file path):
 cd <>
4. Install necessary requirements, either via uv or pip.
-- If using uv, run "uv sync" in the terminal, then activate the venv using by running "source .venv/bin/activate" (Mac/Linux) or ".venv\Scripts\activate.bat" (Windows)
-- If using pip, run "pip install -r requirements.txt" in the terminal
5. Open the "sim_search.py" file
6. Comment out the line that reads: 
"with duckdb.connect(f"{st.secrets['DUCKDB']}?motherduck_token={st.secrets['DUCKDB_TOKEN']}") as conn:"
7. Uncomment out the line below the line from above that reads:
"with duckdb.connect(ref.ks_db, read_only=True) as conn:"
8. Save "sim_search.py"
9. Return to the terminal and enter the following command in the terminal:
"streamlit run application.py"

## EXECUTION
Once the tool is launched, either via the cloud or locally, you can use it by:
1. Entering the required information you want to find similar campaigns for, including:
- Name: The name of the campaign
- Blurb: The short description/blurb of the campaign
- Funding Goal: The funding goal
- Category: The Kickstarter parent category
- Subcategory: The Kickstarter subcategory (appears after selecting Category)
- Number of similar campaigns you want to see: The number of similar campaigns to return
2. Click "Run similarity search"
3. Review the resulting outputs