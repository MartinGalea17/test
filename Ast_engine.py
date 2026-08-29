from new_preset_repo import PresetRepository
from bacteria_repo import BacteriaRepository
from eucast_repo import EucastRepository

class ASTEngine:
    def __init__(self):
        # createing the repos objects
        self.presets = PresetRepository()
        self.bacteria = BacteriaRepository()
        self.eucast = EucastRepository()

    def load_data(self):
        #loading the repos data, presets was not laoded as its an sqllite data base
        self.bacteria.load_bacteria()
        self.eucast.load_breakpoints()

    def build_panel(self, organism, site,mode):
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

    
        return {
        "bacterium_found": True,
        "preset_found": True,
        "species": species,
        "clinical_group": clinical_group,
        "preset_id":preset_id,
        "antibiotics": [dict(row) for row in antibiotics],
        "preset": [dict(row) for row in preset]}
       

    def build_results(self,organism,results):
       """ For each antibiotic in results: find its relevant breakpoint check whether method is MIC or Disc
          compare entered value with breakpoint assign S / I / R store final interpretation"""


       bacteria = self.bacteria.find_bacterium(organism)

       if bacteria is None:
         return None

       species = bacteria["species"]
       clinical_group = bacteria["clinical_group"]

       matched_breakpoints = None
       
       for entry in self.eucast.breakpoint_data:
           eucast_orgasnism = entry.get("organism")
           eucast_clinical_group = entry.get("clinical_group")
           eucast_breakpoints = entry.get("breakpoints")

           if isinstance(eucast_orgasnism,str):
               if eucast_orgasnism.strip().lower() == species.strip().lower():
                   break
               

           if isinstance(eucast_clinical_group,str):
               if eucast_clinical_group.strip().lower() == clinical_group.strip().lower():
                   break
           elif isinstance(eucast_clinical_group,list):
                for group in eucast_clinical_group:
                    if group.strip().lower() == clinical_group.strip().lower():

                        matched_breakpoints = entry.get("breakpoints", [])
                        break

                        
         #match loaded antibiotics from preset to the eucast antibiotics 
       if matched_breakpoints is None:
           return None
       for antibiotic_name, results_data in results.items():
         for breakpoint in matched_breakpoints:
             breakpoint.get("antibiotic")
               
  


