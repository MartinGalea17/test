import json
import os
import streamlit as st
import pandas as pd 
from Hinfst_dialogs import check_heamophilus
from preset_repo import repo as preset_repo
from eucast_repo import EucastRepository

#loading the eucast repository 
@st.cache_resource
def load_eucast_repository():
    repo = EucastRepository()
    repo.load_breakpoints()
    return repo


repo = load_eucast_repository()

date_options = sorted(set(repo.eucast_date))
sample_type_options = sorted(set(repo.sample_types))
administration_options = sorted(set(repo.administrations))

#main app

st.set_page_config(page_title="testing App", page_icon="🧫", layout="wide")



def show_app():
    title_container = st.container(border=True)
    title_container.title("Testing App")

    with st.sidebar:
        st.sidebar.title(" ☰  MENU")
        st.sidebar.markdown("Select an option from the menu below:")
        menu_options = st.sidebar.selectbox("Select an option:", ["Data", "Settings"])
    
    if menu_options == "Settings":
        notification_container = st.container(border=True)
        tab1, tab2, tab3 = st.tabs(["🔔Manage Notifications", "⚙️Settings", "👥Users"])
        with notification_container:
            st.subheader("Notifications")
            with tab1:
                st.title("This is the Notifications tab.")
            with tab2:
                st.subheader("Settings tab.")
                tab1, tab2, tab3 = st.tabs(["🗂️ Presets", "📖 Organism/resistance mechanisms", "📝 Logs"])
                with tab1:
                    presets_container = st.container(border=True)
                    with presets_container:
                        types = ["Gram Positive", "Gram Negative"]
                        selected_type = st.selectbox("Select preset type", types)
                        if selected_type == "Gram Positive":
                            df = pd.DataFrame(preset_repo.positive_presets)
                            pos_edited_df = st.data_editor(df,use_container_width=True,hide_index=True,num_rows="dynamic")
                            save, undo = st.columns(2)
                            with save:
                                if st.button("💾 Save changes to Gram-positive presets"):
                                    pass
                            with undo:
                                if st.button("🔄 Undo last change to Gram-negative presets"):
                                  pass
                        if selected_type == "Gram Negative":
                            df = pd.DataFrame(preset_repo.negative_presets)
                            neg_edited_df = st.data_editor(df,use_container_width=True,hide_index=True,num_rows="dynamic")
                            save, undo = st.columns(2)
                            with save:
                                if st.button("💾 Save changes to Gram-positive presets"):
                                    pass
                            with undo:
                                if st.button("🔄 Undo last change to Gram-negative presets"):
                                    pass
            with tab3:
                st.write("This is the logs tab.")




    if menu_options == "Data":
        data_container = st.container(border=True)
        with data_container:
            st.title("Antibiotic Preset & Sensitivity Section")
            st.write("This section provides antibiotic preset information for various bacteria and automatic antibiotic results. Please select from the following tabs.")
            tab1, tab2, tab3 = st.tabs(["🔍 AST preset lookup", "💊Antibiotic Sensitivities", "testing"])
            with tab1:
                st.title("📋 Antibiotic Presets lookup module.")
                st.subheader("This section provides antibiotic presets for various bacteria. Please select from the options below.")
                st.divider()
                col1, col2, col3, col4 = st.columns(4)
            
                with col2:
                    filter_gram = st.radio("Filter by gram stain", options= ["All", "Positive", "Negative"], index=0, horizontal=False)
                  
                with col3:
                    filter_search = st.radio("Search by:", options=["Species name","Group"], index=0, horizontal=False)
                with col4:
                    filter_site = st.radio("Filter by:", options = ["Sterile","Urine","Eye-swab","Non-sterile"], index=0, horizontal=False)

                #get presets by gram
                active_presets = preset_repo.get_presets_by_gram(filter_gram)

                # filter presets by site
                active_presets = preset_repo.filter_by_site(active_presets, filter_site)

                #build selct box options 
                organism_options = []
                for entry in active_presets:
                    if filter_search == "Species name":
                        value = entry.get("name", "").strip().lower()
                    else:
                        value = entry.get("clinical_group", "").strip().lower()
                    if value and value != "n/a":
                        organism_options.append(value)

                organism_options = sorted(set(organism_options))

                with col1:
                    select_organism = st.selectbox(
                        "Select organism" if filter_search == "Species name" else "Select Group",options=organism_options,index=None, placeholder="Select...")

                st.divider()

                # find final preset
                if select_organism:
                    matching_presets = preset_repo.filter_by_search(active_presets, filter_search, select_organism)
                    st.write("Matches found:", len(matching_presets))
                    for preset in matching_presets:
                        st.write(preset)



            with tab2:
                st.title("🎛️ Filters")
                st.write("Use the below filters to obtain the correct result")
                st.divider()
                filters_contianer = st.container(border=True)
                with filters_contianer:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        MICordisc = st.radio("Filter by:", options=["MIC","Disc"], index=0, horizontal=False,key="MICordisc")
                    with col2:
                        sterility = st.radio("Filter by:", options=["ALL"] + sample_type_options, index=0, horizontal=False,key="sterility")
                    with col3:
                        administration_type = st.radio("Filter by:",options=["ALL"] + administration_options, index=0, horizontal=False,key="administration_type")
                    with col4:
                        eucast_date = st.radio("Select eucast date:",options=date_options, index=0, horizontal=False,key="eucast_data")


                result_container = st.container(border=True)
                with result_container:
                    
                    organism_input_container = st.container(border=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        with organism_input_container:
                            st.title("🦠 Organism Input")
                    with col2:
                        final_result_contianer = st.container(border=True)
                        with final_result_contianer:
                            st.title("📄Results")




            with tab3:
                st.write("This is the testing tab.")
                name_input = st.text_input("Enter organism name:").strip().lower()
                if "haemophilus" in name_input:
                    check_heamophilus()


               


           
            
        



show_app()