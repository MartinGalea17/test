import streamlit as st 
from bacteria_repo import BacteriaRepository
from organism_resistance_repo import OrganismResistanceRepo
import pandas as pd 


bacteria_repo = BacteriaRepository()
resistance_repo = OrganismResistanceRepo()

@st.dialog("ADD/Edit", width="large")
def add_edit_intrinsic():

    #getting bacteria from database
    bacteria = bacteria_repo.load_bacteria()
    organism_name = bacteria_repo.get_species_names()


    select_organism = st.selectbox("Select organism:", organism_name, index=None, placeholder="Search for an organism")

    if not select_organism:
        return 

    existing_organism = resistance_repo.find_organism(select_organism)

    if existing_organism:
        st.success(
            "Organism already exists in resistance database")
        
        profile = resistance_repo.get_intrinsic_resistance(select_organism)
        df = pd.DataFrame([dict(row) for row in profile])
        edited_intrinsic_df = st.data_editor(df, use_container_width=True,hide_index=True,num_rows="dynamic")

        save = st.button("💾 Save changes")

    else:
        st.info(
            "Organism is not yet configured in resistance database"
        )

        blank_df = pd.DataFrame(columns=["target_type","target","interpretation","reason"])

        edited_blankintrinsic_df = st.data_editor(blank_df, hide_index=True, num_rows="dynamic",key=f"intrinsic_editor_{select_organism}",column_config={
            "target_type": st.column_config.SelectboxColumn(
                "Target type",options=["antibiotic", "class"]),
                "interpretation": st.column_config.SelectboxColumn("Interpreation", options=["S","I","R"]),
                "target": st.column_config.TextColumn("Antibiotic / class"), 
                "reason": st.column_config.TextColumn("Reason")
        })

        save = st.button("💾 Save changes")

 