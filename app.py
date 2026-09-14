import json
import os
import streamlit as st
import pandas as pd
from streamlit_lottie import st_lottie

from Hinfst_dialogs import check_heamophilus
from add_edit_intrinsic_dialog import add_edit_intrinsic
from add_edit_phenotypes_dialog import add_edit_phenotpes
from add_edit_basemech_dialog  import add_edit_base_mechanisms
from new_preset_repo import load_preset_repository
from eucast_repo import EucastRepository
from save_delete_dialogs import confirm_data_change
from Ast_engine import ASTEngine
from organism_resistance_repo import load_reistance_repository



preset_repo = load_preset_repository()
site_options = preset_repo.get_sites()
resistance_repo = load_reistance_repository()



#load bacterium animation
def load_lottie_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

bacterium_animation = load_lottie_file("Bacteriumsinglecellorganism.json")
paper_animation = load_lottie_file("Document Icon Lottie Animation.json")
save_animation = load_lottie_file("approve.json")
info_status = load_lottie_file("Info_status.json")
search_results = load_lottie_file("Search.json")


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
                st.header("⚙️ Settings tab.")
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
                                st.warning("Do not save yet!!👀")
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
                with tab2:
                    st.subheader("📖 Rules editing tab")
                    rule_type = ["Intrinsic resistance","Resistance groups","Phenotypes"]
                    selected_rule_type = st.selectbox("Select rule type:",rule_type)

                    if selected_rule_type == "Intrinsic resistance":
                        st.subheader("Intrinsic resistance rules")
                        st.divider()
                        organisms = resistance_repo.get_all_organisms()
                        organism_names = [row["organism"] for row in organisms]
                        selected_organism = st.selectbox("Select organism:", organism_names)
                       
                        intrinsic_resistance = resistance_repo.get_intrinsic_resistance(selected_organism)
                        intrinsic_df = pd.DataFrame([dict(row) for row in intrinsic_resistance])
                        intrinsic_editor_df = st.data_editor(intrinsic_df, use_container_width=True,hide_index=True,num_rows="fixed")

                        
                        if st.button("➕ Add / Edit"):
                            add_edit_intrinsic()
                       
                        
                    if selected_rule_type == "Resistance groups":
                        st.subheader("Base line mechanism rules")
                        st.divider()
                        organisms = resistance_repo.get_all_organisms()
                        organism_names = [row["organism"] for row in organisms]
                        selected_organism = st.selectbox("Select organism:", organism_names)
                        baseline_mechanisms = resistance_repo.get_baseline_mechanisms(selected_organism)
                        baseline_mechanism_df = pd.DataFrame([dict(row) for row in baseline_mechanisms])
                        edited_baseline_mechanism_df = st.data_editor(baseline_mechanism_df, use_container_width=True, hide_index=True,num_rows="fixed")

                        if st.button("➕ Add / Edit"):
                            add_edit_base_mechanisms()


                    if selected_rule_type == "Phenotypes":
                        st.subheader("Expected pheonotype rules")
                        st.divider()
                        organisms = resistance_repo.get_all_organisms()
                        organism_names = [row["organism"] for row in organisms]
                        selected_organism = st.selectbox("Select organism:", organism_names)

                        if st.button("➕ Add / Edit"):
                            add_edit_phenotpes()


                     
            with tab3:
                st.write("This is the logs tab.")
                tab1,tab2,tab3,tab4 = st.tabs(["Preset logs","Mechanisms logs","Notification logs","App logs"])




    if menu_options == "Data":
        data_container = st.container(border=True)
        with data_container:
            st.title("Antibiotic Preset & Sensitivity Section")
            st.write("This section provides antibiotic preset information for various bacteria and automatic antibiotic results. Please select from the following tabs.")
            tab1, tab2, tab3 = st.tabs(["🔍 AST preset lookup", "🧐Antibiotic Sensitivities", "testing"])
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
                    col1, col2, col3, col4 = st.columns(4)
                        
                    with col1:
                        filter_by_sterility = st.selectbox("Filter by: ",options=site_options,index=0,key="filter_by_sterility")
                    with col2:
                        sample_type = st.selectbox(options=sample_type_options,label="Sample type")
                        #st.radio("Filter by:", options=["ALL"] + sample_type_options, index=0, horizontal=False,key="sterility")
                    with col3:
                        administration_type = st.selectbox(options=administration_options, label="Administration type")
                        #administration_type = st.radio("Filter by:",options=["ALL"] + administration_options, index=0, horizontal=False,key="administration_type")
                    with col4:
                        eucast_date = st.selectbox("Select eucast date:",options=date_options, index=0,key="eucast_data")

                    confirm_filters = st.button("Apply filters")
                    #confirm filters logic
                    if confirm_filters:
                        st.session_state["selected_site"] = filter_by_sterility
                        st.session_state["selected_sample_type"] = sample_type
                        st.session_state["selected_administration"] = administration_type
                        st.session_state["selected_eucast_date"] = eucast_date


                
                col1, col2 = st.columns(2)
                
                with col1:
                    organism_input_container = st.container(border=False)
                    with organism_input_container:
                        icon_col, title_col = st.columns([0.3,1])
                        with icon_col:
                             st_lottie(bacterium_animation, height=70, key="bacterium animation")
                        with title_col:
                            st.title("Organism input")
                                
                            organism_input = st.text_input("Enter organism name: ").strip().lower()
                                


                        antibiotic_input_container = st.container(border=True)
                        with antibiotic_input_container:
                            if "haemophilus" in organism_input and "selected_site" in st.session_state["filter_by_sterility"]:
                                check_heamophilus()
                                if "haemophilus" not in organism_input and "selected_site" in st.session_state["filter_by_sterility"]:
                                    return None
                            else:
                                organism_input and "selected_site" in st.session_state["filter_by_sterility"]
                                
                                extra_antibiotic_options = engine.get_available_antibiotics(organism_input)
                                extra_antibiotics = st.multiselect("Select extra antibiotics:",options=extra_antibiotic_options,format_func=lambda item: f"{item['antibiotic']} - {item['method']}",help="Showing antibiotics asocciated with the selected organism only. Not all antibiotics have breakpoints available")
                                add_additional_antibiotics = st.button("➕ Add antibioticcs")

                                if add_additional_antibiotics:
                                    st.session_state["extra_antibiotics"] = extra_antibiotics

                                result = engine.build_panel(organism=organism_input, site=st.session_state["filter_by_sterility"],extra_antibiotics=st.session_state.get("extra_antibiotics", []))
                    
                                if result and result["preset_found"]:
                                    st.write("Antibiotics:")
                                    user_ast_results = {}
                                    for antibiotic in result["antibiotics"]:
                                        input_key =( f"ast_result_"
                                                    f"{antibiotic['antibiotic'].strip().lower()}_"
                                                    f"{antibiotic['method'].strip().lower()}")
                                        
                                        value = st.number_input(f"{antibiotic['antibiotic']} - {antibiotic['method']}", value=None,key=input_key)
                                        #read the ast result
                                        if value is not None:
                                            user_ast_results[antibiotic['antibiotic']] = {"value": value, "method": antibiotic['method']}
                                            #passing results to the engine
                                           
                                    if st.button("Submit results:", key="submit ast result"):
                                        interpreted_results = engine.build_results(organism= organism_input,results=user_ast_results)
                                        print("Build Results returend:", interpreted_results)
                                        st.session_state["interpreted_results"] = interpreted_results
                                        
                                        
                            
                    with col2:
                        
                        results_container= st.container(border = True)
                        
                        with results_container:
                            icon_col, title_col = st.columns([0.3, 1])
                            with icon_col:
                                st_lottie(search_results, height=70, key="search animation")
                            

                            with title_col:
                                st.title("Results:")
                               
                        interpreted_results = st.session_state.get("interpreted_results")
                        interpretation_colors = {"S": "green", "I": "yellow", "R": "red", "No breakpoint": "gray"}
                        
                        
                        if interpreted_results is not None:
                            for antibiotic, result_data in st.session_state["interpreted_results"].items():
                                interpretation = result_data["interpretation"]
                                color = interpretation_colors.get(interpretation, "gray")

                                original = result_data.get("original_interpretation")

                                flag = ""
                                if original and original != interpretation:
                                    flag =  "🚩"


                                st.markdown(f"""
                                    **Antibiotic:** {antibiotic}  
                                    **Final interpretation:** : {flag} :{color}[{result_data['interpretation']}]            
                                    """)
                                with st.expander("View results details"):
                                    st.subheader("**Breakpoint details:**")
                                    st.write("**User input Value:**", result_data["value"])
                                    format_breakpoint= lambda data:(f"S:{data.get('S') or'-'} | R:{data.get('R') or'-'}")
                                    st.write("**Eucast  breakpoint Value:**",format_breakpoint(result_data["breakpoint"]))
                                             
                                    st.write("**Testing Method:**", result_data["method"])
                                    if result_data.get("rule_applied"):
                                        st.divider()
                                        st.write("**Original EUCAST interpretation:**",
                                                 result_data.get("original_interpretation"))
                                        st.write("**Rule applied:**",
                                                 result_data.get("rule_applied"))

                                        pass
                        if "interpreted_results" not in st.session_state:
                            st.session_state.interpreted_results = None
                        if st.session_state.interpreted_results is not None:  
                            pass

                            #st.write(st.session_state["interpreted_results"]) #shows the results in a dictionary format for debugging purposes. Can be removed in production
                            




            with tab3:
                st.write("This is the testing tab.")
                name_input = st.text_input("Enter organism name:").strip().lower()
                if "haemophilus" in name_input:
                    check_heamophilus()


show_app()
