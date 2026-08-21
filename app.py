import json
import os
import streamlit as st
import pandas as pd
from streamlit_lottie import st_lottie

from Hinfst_dialogs import check_heamophilus
from new_preset_repo import load_preset_repository
from eucast_repo import EucastRepository


preset_repo = load_preset_repository()


#load bacterium animation
def load_lottie_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

bacterium_animation = load_lottie_file("Bacteriumsinglecellorganism.json")


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
        menu_options = st.sidebar.selectbox("Select an option:", ["Settings","Data"])
    
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

                        filtered_presets = preset_repo.get_presets_by_gram(selected_type)
                        preset_df = pd.DataFrame([dict(row) for row in filtered_presets])
                        edited_df = st.data_editor(preset_df, use_container_width=True, hide_index=True, num_rows="dynamic")

                        preset_ids = preset_df["id"].tolist()
                        selected_preset_id = st.selectbox("Select preset", options=preset_ids)

                        
                        antibiotics = preset_repo.get_antibiotics(selected_preset_id)

                        antibiotic_df = pd.DataFrame([dict(row) for row in antibiotics])
                        edited_ab_df = st.data_editor(antibiotic_df, use_container_width=True,hide_index=True,num_rows="dynamic")

                        save, undo = st.columns(2)
                        with save:
                            if st.button("💾 Save changes to Gram-positive presets"):
                                pass
                        with undo:
                            if st.button("🔄 Undo last change to Gram-negative presets"):
                                pass
                     
            with tab3:
                st.write("This is the logs tab.")
                tab1,tab2,tab3,tab4 = st.tabs(["Preset logs","Mechanisms logs","Notification logs","App logs"])




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
                    filter_gram = st.radio("Filter by gram stain",options=["Gram Positive", "Gram Negative"])

                with col3:
                    filter_search = st.radio("Search by:",options=["Species name", "Group"])
                
                with col4:
                    site_options = preset_repo.get_sites()
                    new_filter_site = st.radio("Filter by site", options=site_options, index=0, horizontal=False)


                active_presets = preset_repo.get_presets_by_gram_and_site(filter_gram,new_filter_site)    
                st.write("Active presets:", len(active_presets))


                organism_options = []

                for entry in active_presets: #filtering what active_preset is getting and matching with the col3 filters 
                    if filter_search == "Species name":
                        value = entry["name"]
                    else:
                         value = entry["clinical_group"]

                    if value:
                        value = value.strip().lower()

                        if value != "n/a":
                            organism_options.append(value)

                organism_options = sorted(set(organism_options))         

                with col1:
                    select_organism = st.selectbox("Select organism" if filter_search == "Species name" else "Select Group",options=organism_options,index=None,placeholder="Select...")
                st.divider()

                if select_organism:
                    matching_presets = preset_repo.get_preset_by_search(filter_gram,new_filter_site,filter_search,select_organism)
                    col1, col2 = st.columns(2)
                    with col1:
                        for preset in matching_presets:
                            icon_col, title_col = st.columns([0.6, 6])
                            with icon_col:
                                st_lottie(bacterium_animation, height=70, key="preset bacterium animation")
                            with title_col:
                                st.subheader((preset["name"]if preset["name"] and preset["name"].lower() != "n/a"else preset["clinical_group"]))
                                st.divider()
                                st.write(f"**• Gram stain:** {preset['gram_stain']}")
                                st.write(f"**• Morphology:** {preset['morphology']}")
                                st.write(f"**• Site:** {preset['site']}")
                                st.write(f"**• Medium:** {preset['medium']}")
                                st.write(f"**• Typing:** {preset["typing"]} ")

                                if preset["info"] and preset["info"].lower() not in ["n/a", "na"]:
                                    st.info(preset["info"])

                                if preset["guidance"]:
                                    st.info("⚠ "+(preset["guidance"]))
                                antibiotics = preset_repo.get_antibiotics(preset["id"])
                                strips = []
                                discs = []
                                bmd = []

                    with col2:
                            for antibiotic in antibiotics:

                                if antibiotic["method"] == "strip":
                                    strips.append(antibiotic["antibiotic"])

                                elif antibiotic["method"] == "disc":
                                    discs.append(antibiotic["antibiotic"])

                                elif antibiotic["method"] == "BMD":bmd.append(antibiotic["antibiotic"])

                            if strips:
                                st.subheader("📏 MIC strips")
                                st.divider()
                            for antibiotic in strips:
                                st.markdown(f"• {antibiotic}")
                            if discs:
                                st.subheader("💿 Discs")
                                st.divider()

                            for antibiotic in discs:
                                st.markdown(f"• {antibiotic}")

                            if bmd:
                                st.subheader("🧫 BMD")
                                st.divider()

                            for antibiotic in bmd:
                                st.write(f"• {antibiotic}")


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
                    icon_col, title_col = st.columns([0.6, 6])
                    with col1:
                        with icon_col:
                             st_lottie(bacterium_animation, height=70, key="bacterium animation")
                        with title_col:
                            st.title("Organism input")
                            
                    with col2:
                            st.title("📄Results")




            with tab3:
                st.write("This is the testing tab.")
                name_input = st.text_input("Enter organism name:").strip().lower()
                if "haemophilus" in name_input:
                    check_heamophilus()


               


           
            
        



show_app()