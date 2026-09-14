import pandas as pd 
import streamlit as st 
from bacteria_repo import BacteriaRepository

bacteria_repo = BacteriaRepository()



@st.dialog("ADD/Edit", width="large")
def add_edit_phenotpes():

    #gettig bacteria from database 
    bacteria = bacteria_repo.load_bacteria()
    organism_name = bacteria_repo.get_species_names()

    select_organism = st.selectbox("Select organism:", organism_name, index=None, placeholder="Search for an organism")

    if not select_organism:
        return

    
    pass