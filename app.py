import json
import os
import streamlit as st
import pandas as pd
from streamlit_lottie import st_lottie

from Hinfst_dialogs import check_heamophilus
from new_preset_repo import load_preset_repository
from eucast_repo import EucastRepository
from save_delete_dialogs import confirm_data_change
from Ast_engine import ASTEngine


preset_repo = load_preset_repository()
site_options = preset_repo.get_sites()


#load bacterium animation
def load_lottie_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

bacterium_animation = load_lottie_file("Bacteriumsinglecellorganism.json")
paper_animation = load_lottie_file("Document Icon Lottie Animation.json")
save_animation = load_lottie_file("approve.json")
info_status = load_lottie_file("info Status.json")


#initializeing the sesstion state
if "confirm_result" not in st.session_state:
    st.session_state.confirm_result = None


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

@st.cache_resource
def load_ast_engine():
    engine = ASTEngine()
    engine.load_data()
    return engine

engine = load_ast_engine()
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
                        icon_col, title_col = st.columns([0.4, 6])
                        with icon_col:
                            st_lottie(paper_animation, height=50, key="paper animation")
                        with title_col:
                            st.subheader("Presets editing tab")
                        types = ["Gram Positive", "Gram Negative"]
                        selected_type = st.selectbox("Select preset type", types)

                        filtered_presets = preset_repo.get_presets_by_gram(selected_type)
                        preset_df = pd.DataFrame([dict(row) for row in filtered_presets])
                        preset_ids = preset_df["id"].tolist()
                        selected_preset_id = st.selectbox("Select preset", options=preset_ids)
                        selected_preset_df = preset_df[preset_df["id"] == selected_preset_id].copy()
                        edited_df = st.data_editor(selected_preset_df, use_container_width=True, hide_index=True, num_rows="dynamic")

                        #antibiotic box
                        antibiotics = preset_repo.get_antibiotics(selected_preset_id)

                        st.subheader("Antibiotics associated with the choosen preset")
                        antibiotic_df = pd.DataFrame([dict(row) for row in antibiotics])
                        edited_ab_df = st.data_editor(antibiotic_df, use_container_width=True,hide_index=True,num_rows="dynamic")

                        save_col, animation_Col = st.columns(2)
                        
                        with save_col:
                            with st.container(horizontal_alignment="center"):
                                if st.button("💾 Save changes",width="content"):
                                    st.session_state.confirm_result = None
                                    confirm_data_change(selected_preset_id, preset_df,edited_df,antibiotic_df,edited_ab_df)

                        
                            with animation_Col:
                                if st.session_state.confirm_result == "saved":
                                    lottie_col, message_col = st.columns([1,5])

                                    with lottie_col:
                                        st_lottie(save_animation,height=70,key="save_success_animation")
                                    
                                    with message_col:
                                        st.success("Data changed")
                                elif st.session_state.confirm_result == "cancelled":
                                    lottie_col, message_col = st.columns([1,5])
                                    with lottie_col:
                                        st.lottie(info_status,height=70,key="info_animation")
                                    with message_col:
                                        st.info("Data was not changed")

                       
                     
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
                                animation_key_value =  f"preset_result{preset["id"]}"
                                st_lottie(bacterium_animation, height=70, key=animation_key_value)
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

            #Main antibiotic SIR panel
            with tab2:
                st.title("🎛️ Filters")
                st.write("Use the below filters to obtain the correct result")
                st.divider()
                filters_contianer = st.container(border=True)
                with filters_contianer:
                    col1, col2, col3, col4,col5 = st.columns(5)
                    with col1:
                        MICordisc = st.radio("Filter by:", options=["MIC","Disc"], index=0, horizontal=False,key="MICordisc")
                    with col2:
                        filter_by_sterility = st.radio("Filter by: ",options=site_options,index=0,horizontal=False,key="filter_by_sterility")
                    with col3:
                        sample_type = st.selectbox(options=sample_type_options,label="Sample type")
                        #st.radio("Filter by:", options=["ALL"] + sample_type_options, index=0, horizontal=False,key="sterility")
                    with col4:
                        administration_type = st.selectbox(options=administration_options, label="Administration type")
                        #administration_type = st.radio("Filter by:",options=["ALL"] + administration_options, index=0, horizontal=False,key="administration_type")
                    with col5:
                        eucast_date = st.radio("Select eucast date:",options=date_options, index=0, horizontal=False,key="eucast_data")

                    confirm_filters = st.button("Apply filters")
                    #confirm filters logic
                    if confirm_filters:
                         if confirm_filters:
                            st.session_state["selected_site"] = filter_by_sterility
                            st.session_state["selected_mode"] = MICordisc
                            st.session_state["selected_sample_type"] = sample_type
                            st.session_state["selected_administration"] = administration_type
                            st.session_state["selected_eucast_date"] = eucast_date


                result_container = st.container(border=True)
                col1, col2 = st.columns(2)
                with result_container:
                    with col1:
                        organism_input_container = st.container(border=True)
                        with organism_input_container:
                            icon_col, title_col = st.columns([0.6, 6])
                            with icon_col:
                                st_lottie(bacterium_animation, height=70, key="bacterium animation")
                            with title_col:
                                st.title("Organism input")
                                organism_input = st.text_input("Enter organism name: ").strip().lower()
                                extra_antibiotics = st.selectbox("Select extra antibiotics:",options="test",help="Showing antibiotics asocciated with the selected organism only. Not all antibiotics have breakpoints available")

                        antibiotic_input_container = st.container(border=True)
                        with antibiotic_input_container:
                            if organism_input and "selected_site" in st.session_state:
                                result = engine.build_panel(organism=organism_input, site=st.session_state["filter_by_sterility"],mode=st.session_state["selected_mode"])
                    
                                if result and result["preset_found"]:
                                    st.write("Antibiotics:")
                                    user_ast_results = {}
                                    for antibiotic in result["antibiotics"]:
                                        input_key = f"ast_result_{antibiotic["id"]}"
                                        value = st.number_input(f"{antibiotic["antibiotic"]} - {antibiotic["method"]}", value=None,key=input_key)
                                        #read the ast result
                                        if value is not None:
                                            user_ast_results[antibiotic["antibiotic"]] = {"value": value, "method": antibiotic["method"]}
                                            #passing results to the engine
                                            engine.build_results(organism= organism_input,results=user_ast_results)
                                st.button("Sumbit result", key="submit ast result")

                                    
                               

                            
                    with col2:
                        results_container= st.container(border = True)
                        with results_container:
                                ast_result = engine.build_results(organism="Staphylococcus aureus ",results=user_ast_results)
                                st.write(user_ast_results)
                                st.write(ast_result)
                            




            with tab3:
                st.write("This is the testing tab.")
                name_input = st.text_input("Enter organism name:").strip().lower()
                if "haemophilus" in name_input:
                    check_heamophilus()


               


           
            
        



show_app()