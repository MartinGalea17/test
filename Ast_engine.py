
from new_preset_repo import PresetRepository
from bacteria_repo import BacteriaRepository
from eucast_repo import EucastRepository
from organism_resistance_repo import OrganismResistanceRepo
from rules_engine import RulesEngine
import operator
import time 
import streamlit as st

class ASTEngine:
    def __init__(self):
        # createing the repos objects
        self.presets = PresetRepository()
        self.bacteria = BacteriaRepository()
        self.eucast = EucastRepository()

        resistance_repo = OrganismResistanceRepo()
        self.rules_engine = RulesEngine(resistance_repo)

    def load_data(self):
        #loading the repos data, presets was not laoded as its an sqllite data base
        self.bacteria.load_bacteria()
        self.eucast.load_breakpoints()

    def build_panel(self, organism, site, extra_antibiotics=None):
        #getting the species and group from the bacteria repo
        bacteria = self.bacteria.find_bacterium(organism)
        if bacteria is None:
            return None 

        species = bacteria["species"]
        clinical_group = bacteria["clinical_group"]
         

        print("SPECIES:", repr(species))
        print("CLINICAL GROUP:", repr(clinical_group))
        print("SITE:", repr(site))
        #getting the presets by name 
        preset = self.presets.get_presets_by_name(species, site)
        if not preset:
            preset = self.presets.get_presets_by_group(clinical_group, site)

        if not preset:
            return {
            "bacterium_found": True,
            "preset_found": False,
            "species": species,
            "clinical_group": clinical_group}

        preset_id = preset[0]["id"]
        antibiotics = self.presets.get_antibiotics(preset_id)
        panel_antibiotics = [dict(row) for row in antibiotics]

        if extra_antibiotics:
            for extra in extra_antibiotics:
                already_exists = False

                for existing in panel_antibiotics:
                    if(
                        existing["antibiotic"].strip().lower() == extra["antibiotic"].strip().lower() and 
                        existing["method"].strip().lower() == extra["method"].strip().lower()
                    ):
                        already_exists = True
                        break

                if not already_exists:
                    panel_antibiotics.append(extra)
   
        return {
        "bacterium_found": True,
        "preset_found": True,
        "species": species,
        "clinical_group": clinical_group,
        "preset_id":preset_id,
        "antibiotics": panel_antibiotics,
        "preset": [dict(row) for row in preset]}
       

    def build_results(self,organism,results,eucast_date=None):
       """ For each antibiotic in results: find its relevant breakpoint check whether method is MIC or Disc
          compare entered value with breakpoint assign S / I / R store final interpretation"""


       matched_breakpoints = self.get_relevant_breakpoints(organism,eucast_date) # GETTING THE RELEVANT BREAKPOINTS FOR THE ORGANISM
       if matched_breakpoints is None:
           return None  # No matching breakpoints found
       final_results = {}
       for antibiotic_name, results_data in results.items():
         for breakpoint in matched_breakpoints:
             eucast_antibiotic = breakpoint.get("antibiotic", "")
             if eucast_antibiotic.strip().lower() == antibiotic_name.strip().lower():
                print("MATCHED", antibiotic_name)
                print("RESULT DATA", results_data)
                print("BREAKPOINT", breakpoint)

                value = results_data["value"]
                method = results_data["method"]

                if method.strip().lower() == "strip":
                    selected_breakpoint = breakpoint.get("MIC", {})
                elif method.strip().lower() == "disc":
                    selected_breakpoint = breakpoint.get("disk", {}).get("zone_mm", {})
                else:
                    continue  # Skip if method is not recognized
                interpretation = self.interpret_results(value, selected_breakpoint)
                final_results[antibiotic_name] = {
                    "value": value,
                    "method": method,
                    "interpretation": interpretation,
                    "breakpoint": selected_breakpoint}
                break

       final_results = self.rules_engine.apply_intrinsic_resistance(organism, final_results)
       return final_results

    def get_breakpoint_date(self, entries, eucast_date):
        if eucast_date is None:
            return entries

        eucast_date = str(eucast_date).strip()

        filtered_entries = [] 

        for entry in entries:
            entry_date = entry.get("eucast_version")

            if str(entry_date).strip() == eucast_date:
                filtered_entries.append(entry)

        return filtered_entries

    def interpret_results(self, value, selected_breakpoint):
        susceptible = selected_breakpoint.get("S")
        resistant = selected_breakpoint.get("R")

        s_parsed = self.parse_breakpoints(susceptible)
        r_parsed = self.parse_breakpoints(resistant)

        comparison_operators = {
            "≤": operator.le,
            "≥": operator.ge,
            "<": operator.lt,
            ">": operator.gt
        }

        try:
            value = float(value)
        except (TypeError, ValueError):
            return "Invalid result"

        #susceptible
        if s_parsed is not None:
            bp_operator, bp_number = s_parsed

            if comparison_operators[bp_operator](value,bp_number):
                return "➤ Sensitive"

        #resistant
        if r_parsed is not None:
            bp_operator, bp_number = r_parsed
        
            if comparison_operators[bp_operator](value,bp_number):
                return "➤ Resistant"

        #intermediate
        if s_parsed is not None and r_parsed is not None:
            return "➤ Intermediate"

        return "No Breakpoint"


    def parse_breakpoints(self,breakpoint_value):
        if breakpoint_value is None:
            return None 

        operators = ["≤", "≥", "<", ">"]

        for operator in operators:
            if breakpoint_value.startswith(operator):
                number_part = breakpoint_value[len(operator):]
                number = float(number_part)

                return operator, number
                

    def get_available_antibiotics(self,organism,eucast_date=None): #function to get the available antibiotics for a given organism based on the eucast breakpoints for the extra antibiotics part in the app 
        matched_breakpoints = self.get_relevant_breakpoints(organism,eucast_date) #Getting the relevant breakpoints for the organism
        

        available_antibiotics = [] 
        if matched_breakpoints is None:
            return []  # No matching breakpoints found
        for breakpoint in matched_breakpoints:
            antibiotic = breakpoint.get("antibiotic", "").strip()
            if not antibiotic:
                continue 

            mic = breakpoint.get("MIC", {})
            disk = breakpoint.get("disk", {}).get("zone_mm", {})    

            if mic.get("S") not in ["", "-"] or mic.get("R") not in ["", "-"]:
                available_antibiotics.append({"antibiotic": antibiotic, "method": "strip"})
            if disk.get("S") not in ["", "-"] or disk.get("R") not in ["", "-"]:
                available_antibiotics.append({"antibiotic": antibiotic, "method": "disc"})

        return sorted(available_antibiotics,key=lambda item:(item["antibiotic"], item["method"]))
             
               
    def get_relevant_breakpoints(self, organism, eucast_date=None):

        bacteria = self.bacteria.find_bacterium(organism)

        if bacteria is None:
            return []

        species = bacteria["species"].strip().lower()
        clinical_group = bacteria["clinical_group"].strip().lower()

        # Only new part: filter entries by EUCAST date first
        entries = self.get_breakpoint_date(self.eucast.breakpoint_data,eucast_date)

        matched_breakpoints = None

        # Keep your original matching logic
        for entry in entries:
            eucast_organism = entry.get("organism")
            eucast_clinical_group = entry.get("clinical_group")

            if isinstance(eucast_organism, str):
                if eucast_organism.strip().lower() == species:
                    matched_breakpoints = entry.get("breakpoints", [])
                    break

            if isinstance(eucast_clinical_group, str):
                if eucast_clinical_group.strip().lower() == clinical_group:
                    matched_breakpoints = entry.get("breakpoints", [])
                    break

            elif isinstance(eucast_clinical_group, list):
                for group in eucast_clinical_group:
                    if group.strip().lower() == clinical_group:
                        matched_breakpoints = entry.get("breakpoints", [])
                        break

                if matched_breakpoints is not None:
                    break

        # keep the rest of your existing breakpoint filtering here

        # if nothing matches
        if matched_breakpoints is None:
            return []

        #filter individual breakpoint records 
        relevant_breakpoints = []

        for breakpoint in matched_breakpoints:
            bp_name = breakpoint.get("name", "")
            if isinstance(bp_name,str):
                bp_names = [item.strip().lower() for item in bp_name.split(",")if item.strip()]
            elif isinstance(bp_name,list):
                bp_names = [item.strip().lower() for item in bp_name if item]
            bp_group = breakpoint.get("group","")
            if isinstance(bp_group, str):
                bp_groups = [item.strip().lower() for item in bp_group.split(",") if item.strip()]
            elif isinstance(bp_group, list):
                bp_groups = [item.strip().lower() for item in bp_group if item]


            exclude_name = breakpoint.get("exclude_name","")
            if isinstance(exclude_name,str):
                exclude_names = [item.strip().lower() for item in exclude_name.split(",") if item.strip()]
            elif isinstance(exclude_name, list):
                exclude_names = [item.strip().lower() for item in exclude_name if item]
            exclude_group = breakpoint.get("exclude_group","")
            if isinstance(exclude_group, str):
                exclude_groups = [item.strip().lower() for item in exclude_group.split(",") if item.strip()]
            elif isinstance(exclude_group, list):
                exclude_groups = [item.strip().lower() for item in exclude_group if item]

            if species in exclude_names:
                 continue

            if clinical_group in exclude_groups:
                continue

            if bp_names:
                if species not in bp_names:
                    continue

            elif bp_groups:
                if clinical_group not in bp_groups:
                    continue

            relevant_breakpoints.append(breakpoint)

        return relevant_breakpoints

    
      

engine = ASTEngine()
if engine:
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)

for percent_complete in range(100):
    time.sleep(0.01)
    my_bar.progress(percent_complete + 1, text=progress_text)
time.sleep(1)
my_bar.empty()
