import json
import pandas as pd
from collections import defaultdict
import logging
logger = logging.getLogger(__name__)
import streamlit as st


#loading of the gram negative and gram positive presets

class PresetRepository:
    def __init__(self):
        self.negative_presets = []
        self.positive_presets = []

        self.negative_names = []
        self.negative_groups = []
        self.negative_sites = []

        self.positive_names = [] 
        self.positive_groups = []
        self.positive_sites = []


    
    def load_presets(self):
        try:
            with open("Gram_negative_preset_with_info.json", "r", encoding="utf-8") as f:
                self.negative_presets = json.load(f)
            logger.info(f"Loaded {len(self.negative_presets)} gram negative presets")
            
        except Exception as e:
            logger.error(f"Failed to load gram negative presets {e}")
            
        try:
            with open("Gram_positive_preset_with_info.json", "r", encoding ="utf-8") as f:
                self.positive_presets = json.load(f)
                logger.info(f"Loaded {len(self.positive_presets)} gram positive presets")
        except Exception as e:
              logger.error(f"Failed to load gram positive presets {e}")

        # Extracting names, groups, and sites from the loaded presets by calling the extract_preset_values method
        (self.negative_names, self.negative_groups, self.negative_sites) = self.extract_preset_values(self.negative_presets)
        (self.positive_names, self.positive_groups, self.positive_sites) = self.extract_preset_values(self.positive_presets)


    def extract_preset_values(self, presets):
        names = []
        groups = []
        sites = []

        for info in presets:
            name = info.get("name","").strip().lower()
            group = info.get("clinical_group", "").strip().lower()
            site = info.get("site", "").strip().lower()

            if name and name != "n/a":
                names.append(name)
            if group and group != "n/a":
                groups.append(group)
            if site and site != "n/a":
                sites.append(site)

        return names, groups, sites

    def get_presets_by_gram(self, gram_stain):
        gram_stain = gram_stain.strip().lower()

        if gram_stain == "negative":
            return self.negative_presets

        if gram_stain == "positive":
            return self.positive_presets
        
        if gram_stain == "all":
            return self.negative_presets + self.positive_presets

        return []

    def filter_by_site(self, presets, site):
        site = site.strip().lower()

        if site == "all":
            return presets

        filtered_presets = []

        for entry in presets:
            entry_site = entry.get("site", "").strip().lower()

            if entry_site == site:
                filtered_presets.append(entry)

        return filtered_presets

    def filter_by_search(self,presets,search_mode, search_value):
        search_mode = search_mode.strip().lower()
        search_value = search_value.strip().lower()

        filtered_presets = []

        for entry in presets:
            if search_mode == "species name":
                entry_value = entry.get("name","").strip().lower()
            elif search_mode == "group":
                entry_value = entry.get("clinical_group","").strip().lower()
            else:
                continue 

            if entry_value == search_value:
                filtered_presets.append(entry)

        return filtered_presets 


@st.cache_resource
def load_preset_repository():
    repo = PresetRepository()
    repo.load_presets()
    return repo


repo = load_preset_repository()

negative = repo.get_presets_by_gram("Negative")
positive = repo.get_presets_by_gram("Positive")
all_presets = repo.get_presets_by_gram("All")

print(len(negative))
print(len(positive))
print(len(all_presets))
len(repo.negative_presets) + len(repo.positive_presets)
print()


negative_presets = repo.get_presets_by_gram("Negative")

sterile_presets = repo.filter_by_site(
    negative_presets,
    "urines"
)

results = repo.filter_by_search(
    sterile_presets,
    "name",
    "Enterococcus faecalis"
)

print("Matches:", len(results))

for entry in results:
    print(entry["name"], entry["clinical_group"], entry["site"])