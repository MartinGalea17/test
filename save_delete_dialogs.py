import streamlit as st
from streamlit_lottie import st_lottie
import json
import pandas as pd

from new_preset_repo import load_preset_repository


preset_repo = load_preset_repository()

#load bacterium animation
def load_lottie_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

save_animation = load_lottie_file("approve.json")


@st.dialog("Confirm data change")
def confirm_data_change(preset_id,original_preset_df,edited_preset_df,original_ab_df,edited_ab_df):

    st.warning("Are you sure you want to change this data?.")
    col1, col2 = st.columns(2)
    user = st.session_state.get("username", "Unknown User")
    with col1:
        if st.button("✅ Yes, change"):
            #save logic
            original_row = original_preset_df[original_preset_df["id"] == preset_id].iloc[0]

            edited_row = edited_preset_df[edited_preset_df["id"] == preset_id].iloc[0]

            # comparing the original_row vs edited_row

            fields = [
            "name",
            "clinical_group",
            "gram_stain",
            "morphology",
            "site",
            "info",
            "medium",
            "guidance",
            "cefinase",
            "typing"
        ]

            for field in fields:

                old_value = original_row[field]
                new_value = edited_row[field]

                if old_value != new_value:

                    preset_repo.update_preset_field(preset_id,field,new_value,user)
                    saved_preset = preset_repo.get_preset_by_id(preset_id)
                    st.write("DATABASE VALUE:",saved_preset[field])
                                
                    st.write("UPDATED", field,old_value,"→",new_value)
            #loop to detect changes and deletions
            for _, original_ab_row in original_ab_df.iterrows():
                antibiotic_id = original_ab_row["id"]
                edited_match = edited_ab_df[edited_ab_df["id"] == antibiotic_id]
                if not edited_match.empty:
                    edited_ab_row = edited_match.iloc[0]
                    old_antibiotic =  original_ab_row["antibiotic"]
                    new_antibiotic = edited_ab_row["antibiotic"]
            
                    old_method = original_ab_row["method"]
                    new_method = edited_ab_row["method"]
            
                    if(old_antibiotic != new_antibiotic or old_method != new_method):
                        preset_repo.update_antibiotic(antibiotic_id,new_antibiotic,new_method,user)

                else: 
                    preset_repo.delete_antibiotic(antibiotic_id,user)

            # loop to check for new inserts 
            for _, edited_ab_row in edited_ab_df.iterrows():
                edited_id = edited_ab_row["id"]
                if pd.isna(edited_id):# detecing a missing id in the edited df
                    new_antibiotic = edited_ab_row["antibiotic"]
                    new_method = edited_ab_row["method"]


                    if new_antibiotic and new_method:
                        preset_repo.add_antibiotic(preset_id, new_antibiotic, new_method, user)

            

            st.session_state["confirm_result"] = "saved"
            st.rerun()  # only rerun after deletion    
            
             

    with col2:
        if st.button("❌ Cancel"):
            st.session_state["confirm_result"] = "cancelled"
            st.info("Data change cancelled.")
            st.rerun()


