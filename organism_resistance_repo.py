import sqlite3
import streamlit as st

class OrganismResistanceRepo:
    def __init__(self, db_path="organism_resistance.db"):
        self.db_path = db_path

    def connect(self):

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_all_organisms(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM organisms")
        results = cursor.fetchall()
        conn.close()

        return results


    def find_organism(self,organism_name):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM organisms
            WHERE LOWER(organism) = LOWER(?)
            """,
            (organism_name,)
        )
        result = cursor.fetchone()
        conn.close()
        return result

    def get_aliases(self, alias):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * 
            FROM organism_aliases
            WHERE lower(alias) = LOWER(?)
            """,
            (alias,)
        )

        result = cursor.fetchone()
        conn.close()
        return result


    def get_intrinsic_resistance(self,organism_name):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                intrinsic_resistance.target_type,
                intrinsic_resistance.target,
                intrinsic_resistance.interpretation,
                intrinsic_resistance.reason
            FROM intrinsic_resistance

            JOIN organisms
            on organisms.id = intrinsic_resistance.organism_id

            WHERE LOWER(organisms.organism) = LOWER(?)
            """,
            (organism_name,)
        )

        results = cursor.fetchall()
        conn.close()
        return results
        

    def get_baseline_mechanisms(self, organism_name):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                mechanisms.name,
                mechanisms.category,
                mechanisms.description,
                organism_mechanisms.mechanism_type

            FROM organism_mechanisms

            JOIN organisms
            ON organisms.id = organism_mechanisms.organism_id

            JOIN mechanisms
            ON mechanisms.id = organism_mechanisms.mechanism_id

            WHERE LOWER(organisms.organism)=LOWER(?)
            AND organism_mechanisms.mechanism_type = 'baseline'
            """,
            (organism_name,)
        )

        results = cursor.fetchall()
        conn.close()
        return results


    def get_organism_profile(self, organism_name):
       organism = self.find_organism(organism_name)

       if not organism:
           return None

       intrinsic = self.get_intrinsic_resistance(organism_name)
       mechanisms = self.get_baseline_mechanisms(organism_name)

       return{
           "organism": dict(organism),
           "intrinsic_resistance": [dict(row) for row in intrinsic],
           "baseline_mechanisms": [dict(row) for row in mechanisms]
       }

    def update_intrinsic_antibioic(self):
        pass

    def add_intrinsic_antibiotics(self):
        pass

    def remove_intrinisc_antibiotics(self):
        pass

    def create_autid_table(self):
        pass

    def log_change(self):
        pass


@st.cache_resource
def load_reistance_repository():
    return OrganismResistanceRepo()


"""
repo = OrganismResistanceRepo()
organism = repo.find_organism("pseudomonas aeruginosa")

if organism:
    print(organism["organism"])
    print(organism["clinical_group"])
    print(organism["gram_stain"])
else:
    print("No data found")

aliase = repo.get_aliases("K. aerogenes")
if aliase:
    print(aliase["alias"])
    print(aliase["organism_id"])

resistance = repo.get_intrinsic_resistance("pseudomonas aeruginosa")

for result in resistance:
    print(result["target"])
    print(result["interpretation"])

mechanisms = repo.get_baseline_mechanisms("pseudomonas aeruginosa")

for mechanism in mechanisms:
    print(mechanism["name"])

profile = repo.get_organism_profile("pseudomonas aeruginosa")

print(profile)
"""
