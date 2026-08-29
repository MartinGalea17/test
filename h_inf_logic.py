import json


def check_factors(x, v, xv):
    if (x, v, xv) == (0, 0, 1):
        return "xv_required"

    elif (x, v, xv) == (1, 0, 1):
        return "x_required"

    elif (x, v, xv) == (0, 1, 1):
        return "v_required"

    return None
    

def check_haemolysis(group_result, haemolysis_input):

    # Requires both X and V
    if group_result == "xv_required":
        if haemolysis_input == 1:
            return "H. haemolyticus"

        return "H. influenzae or H. aegyptius"

    # Requires V only
    elif group_result == "v_required":
        if haemolysis_input == 1:
            return "H. parahaemolyticus"

        return "H. parainfluenzae"

    # Requires X only
    elif group_result == "x_required":
        if haemolysis_input == 0:
            return "H. ducreyi"

        return "No configured match for X-required and haemolysis-positive"

    return "No match"

def check_cefinase(identification_result,cefinase_input,):
    if "H. influenzae" not in identification_result:
        return None

    if cefinase_input == 1:
        return "BLPR"

    elif cefinase_input == 0:
        return "No enzyme"

    return "Invalid"
    

def haeinf_logic(penicillin_input,cefinase_result,augmentin_input,hinf_messages):

    messages = []

     # PCG >=12 mm
    if penicillin_input >= 12:
        return hinf_messages["hinf_no_mechanism_detected"]

    # PCG <12 mm
    messages.append(
        hinf_messages["hinf_mechanism_detected"]
    )

    # Beta-lactamase negative
    if cefinase_result == "No enzyme":
        messages.append(
            hinf_messages["hinf_beta_lactam_neg"]
        )

        # Stop here: do not interpret Augmentin
        return "\n\n".join(messages)

    # Beta-lactamase positive
    if cefinase_result == "BLPR":
        messages.append(
            hinf_messages["hinf_beta_lactam_pos"]
        )

        if augmentin_input >= 15:
            messages.append(
                hinf_messages["hinf_Aug_ge_15"]
            )
        else:
            messages.append(
                hinf_messages["hinf_Aug_lt_15"]
            )

        return "\n\n".join(messages)

    messages.append("Invalid cefinase result.")
    return "\n\n".join(messages)

