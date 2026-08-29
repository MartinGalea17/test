import os
import pandas as pd
from difflib import get_close_matches
from collections import defaultdict
import logging
logger = logging.getLogger(__name__)

class BacteriaRepository:
    def __init__(self):
        self.bacteria = None

    #openining the file 
    def load_bacteria(self):    
        df = pd.read_csv("updated_database.csv",low_memory=False)
        self.bacteria = df

    #getting species 
    def get_species_names(self):
        species_names = (self.bacteria["species"].dropna().str.strip()) #selecting the species column, dropna removes missing values, str.strip removes white space

        species_names = species_names[species_names != ""]

        
        return species_names.unique().tolist()# unique removes duoplicates tolist coverts from a numphy array to a noram phyton list

    def get_clinicalgroup(self):
        clinical_group_names = (self.bacteria["clinical_group"].dropna().str.strip())
        clinical_group_names = clinical_group_names[clinical_group_names != ""]

        return clinical_group_names.unique().tolist() 

    def find_bacterium(self,species_name):
        species_name = species_name.strip().lower()

        matches = self.bacteria[self.bacteria["species"].str.strip().str.lower() == species_name]
        if matches.empty:
            return None

        
        return matches.iloc[0]
        

    def get_clinical_group(self,clinical_group):
        clinical_group = clinical_group.strip().lower()

        matches = self.bacteria[self.bacteria["clinical_group"].str.strip().str.lower() == clinical_group]
        return matches

    

repo = BacteriaRepository()
repo.load_bacteria()

print(
    repo.bacteria[
        repo.bacteria["species"].str.contains(
            "Staphylococcus aureus",
            case=False,
            na=False
        )
    ]["species"].apply(repr)
)







    
#repo = BacteriaRepository()
#repo.load_bacteria()

##print(type(repo.bacteria))
#print(repo.bacteria.shape)
#print(repo.bacteria.columns[:20])
#print(repo.bacteria.head())

#species = repo.get_species_names()
##print(species[:1000])

#groups = repo.get_clinicalgroup()
#print(groups[:100])

#result = repo.find_bacterium("Eschericia coli")
#print(result)