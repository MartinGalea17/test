import streamlit as st
import json
from h_inf_logic import check_factors, check_haemolysis, check_cefinase, haeinf_logic

with open("h_inf.json") as f:
    hinf_messages = json.load(f)

#haemophilus logic check includeing eucast descition tree 
@st.dialog("Check Heamophilus",width="medium")
def check_heamophilus():
    st.write("Haemophilus check. Enter growth factors and haemolysis results.")
    
    x_input = st.radio("Factor X:", options=[0,1],format_func=lambda result:("positive" if result == 1 else "Negative"), horizontal=True, index =None)
    v_input = st.radio("Factor V:", options=[0,1],format_func=lambda result:("positive" if result == 1 else "Negative"), horizontal=True, index =None)
    xv_input = st.radio("Factor XV:", options=[0,1],format_func=lambda result:("positive" if result == 1 else "Negative"), horizontal=True, index =None)

    #check if the factors match any known patterns
    if None in (x_input, v_input, xv_input):
        st.info("Please select input all growth factors to proceed.")
        return 

    group_result = check_factors(x_input,v_input,xv_input)

    if group_result is None:
        st.warning("The combination of growth factors does not match any known Haemophilus groups.")
        return
    st.info(f"Factor group: {group_result}")

    haemolysis_input = None
    #haemolysis check
    if group_result:
        haemolysis_input = st.radio("Haemolysis:", options=[0,1],format_func=lambda result:("Positive" if result == 1 else "Negative"), 
                                    horizontal=True, index =None)
    if haemolysis_input is None:
        st.info("Please select haemolysis result to proceed.")
        return

    haemolyis_result = check_haemolysis(group_result, haemolysis_input)
    st.success(f"Identification Result: {haemolyis_result}")

    if "H. influenzae" not in  haemolyis_result:
        st.info("The identified organism is not H. influenzae, cefinase test is not applicable.")
        return

    st.divider()
    st.subheader("Resistance mechanism testing")

    cefinase_input = st.radio("Cefinase (Bet-Lactamase) test:", options=[0,1],format_func=lambda result:("Positive" if result == 1 else "Negative"),
                               horizontal=True, index =None)

    if cefinase_input is None:
        st.info("Please select a cefinase result to proceed.")
        return

    # Calculate this on every dialog rerun
    cefinase_result = check_cefinase(haemolyis_result,cefinase_input,)
    st.write(f"Cefinase result: **{cefinase_result}**")

    #penicillin and augmentin testing
    st.divider()
    penicillin_input = st.number_input("Penicillin (PCG) zone size in mm: ", min_value=0, max_value=100, step=1, value=None, placeholder="Enter diamenter in mm")
    if penicillin_input is None:
        st.info("Please enter the penicillin zone diameter result to proceed.")
        return 

    #branch 1: PCG >= 12mm
    if penicillin_input >= 12:
        final_result = haeinf_logic(penicillin_input,cefinase_result,augmentin_input=None,hinf_messages=hinf_messages)
        st.success(f"Penicillin Result: {final_result}")
        return

    # From this point, PCG must be below 12 mm
    st.warning("PCG is below 12 mm. A beta-lactam resistance ""mechanism may be present.")


    #Branch 2: PCG < 12mm and cefinase negative
    if cefinase_result == "No enzyme":
        final_result = haeinf_logic(penicillin_input,cefinase_result,augmentin_input=None,hinf_messages=hinf_messages)
        st.success(f"Final Result: {final_result}")
        return
    
    #branch 2: PCG < 12mm and cefinase positive
    if cefinase_result == "BLPR":
        st.info("Penicillin result is <12 mm and cefinase test is positive. Furthur tesing is required with Augemntin)")
        augmentin_input =st.number_input("Augmentin (AMC) zone size in mm: ", min_value=0, max_value=100, step=1, value=None, placeholder="Enter diamenter in mm")
        if augmentin_input is None:
            st.info("Please enter the amoxicillin-clavulanic acid result to proceed.")
            return
        
        final_result = haeinf_logic(penicillin_input,cefinase_result,augmentin_input,hinf_messages)
        st.success(f"Final Result: {final_result}")
        return
    st.error("The cefinase result could not be interpreted. Please check the input and try again.")
