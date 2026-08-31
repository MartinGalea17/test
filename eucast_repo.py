import json
import os
import re
import logging
from collections import defaultdict
import streamlit as st

logger = logging.getLogger(__name__)


class EucastRepository:
    def __init__(self):
        self.breakpoint_data = []
        self.organisms = []
        self.clinical_groups = []
        self.eucast_date = []

        self.antibiotics = []
        self.include_names = []
        self.include_groups = []
        self.exclude_names = []
        self.exclude_groups = []
        self.sample_types = []
        self.administrations = []


    def load_breakpoints(self):
        folder = "breakpoint_folder"

        for filename in os.listdir(folder):
               if filename.endswith(".json"):
                      file_path = os.path.join(folder, filename)

                      with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)

                      self.breakpoint_data.append(data)

        (self.organisms,self.clinical_groups, self.eucast_date) = self.extract_breakoints_values(self.breakpoint_data)
        (self.antibiotics,self.include_names,self.include_groups,self.exclude_names,self.exclude_groups,self.sample_types,self.administrations,) = self.extract_nested_values(self.breakpoint_data)
        self.sample_types = self.clean_sample_types(self.sample_types)

    def extract_breakoints_values(self, breakpoints): #getting top level info 
        organisms = [] 
        clinical_groups= [] 
        eucast_date = []

        for entry in breakpoints:
            organism = entry.get("organism","")
            clinical_group = entry.get("clinical_group","")
            date = entry.get("eucast_version","").strip().lower()

            if date:
                 eucast_date.append(date)

            if isinstance(organism,str):
                organism = organism.strip()

                if organism:
                     organisms.append(organism)

            elif isinstance(organism,list): #organism is a list this elif will sperate them into names and append one by one 
                 for name in organism:
                      name = name.strip()

                      if name:
                           organisms.append(name)

            if isinstance(clinical_group, str):
                clinical_group = clinical_group.strip()

                if clinical_group:
                     clinical_groups.append(clinical_group)

            elif isinstance(clinical_group,list):
                for group in clinical_group:
                     group = group.strip()

                     if group:
                          clinical_groups.append(group)

           
        

        return organisms, clinical_groups, eucast_date

    def extract_nested_values(self,breakpoint_data): # most will not be needed in the main logic as this info will be lost alone. 
         antibiotics = []
         include_names = [] 
         include_groups = [] 
         exclude_names = [] 
         exclude_groups = [] 
         sample_types = []
         administrations = []

         for entry in breakpoint_data:
              for bp in entry.get("breakpoints",[]):
                   antibiotic = bp.get("antibiotic","").strip()
                   include_name = bp.get("name","").strip()
                   include_group = bp.get("group","").strip()
                   exclude_name = bp.get("exclude_name","").strip()
                   exclude_group = bp.get("exclude_group","").strip()
                   sample_type = bp.get("sample_type", "")
                   administration = bp.get("administration", "")

                   if antibiotic:
                        antibiotics.append(antibiotic)
                   if include_name:
                        include_names.append(include_name)
                   if include_group:
                        include_groups.append(include_group)
                   if exclude_name:
                        exclude_names.append(exclude_name)
                   if exclude_group:
                         exclude_groups.append(exclude_group)

                   if  isinstance(sample_type, str):
                        sample_type = sample_type.strip()
                        if sample_type:
                             sample_types.append(sample_type)

                   elif isinstance(sample_type, list):
                        for type_name in sample_type:
                             type_name = type_name.strip()
                             if type_name:
                                  sample_types.append(type_name)

                   if  isinstance(administration, str):
                         administration = administration.strip()
                         if administration:
                              administrations.append(administration)

                   elif isinstance(administration, list):
                         for admin in administration:
                              admin = admin.strip()
                              if admin:
                                   administrations.append(admin)

              
         return antibiotics, include_names, include_groups, exclude_names , exclude_groups, sample_types, administrations

    def clean_sample_types(self,sample_types):
         cleaned_sample_types = []
         sample_type_options = ["all indications","urinary tract","uncomplicated uti","meningitis","pneumonia","skin and soft tissue","systemic infection"]

         for sample in sample_types:
              sample = sample.strip().lower()
              if sample in sample_type_options:
                    cleaned_sample_types.append(sample)

         return cleaned_sample_types



#testing

repo = EucastRepository()
repo.load_breakpoints()

print("Eucast date:", repo.eucast_date)


print("\nSample types:")
for sample_type in sorted(set(repo.sample_types)):
     print(sample_type)
print("Administrations:", sorted(set(repo.administrations)))


