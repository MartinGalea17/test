import sqlite3
import streamlit as st
import logging 


class PresetRepository:

    def __init__(self, db_path="presets_merged.db"):
        self.db_path = db_path

    def connect(self):

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        return conn

    def get_all_presets(self):

        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM presets")
        results = cursor.fetchall()
        conn.close()

        return results

    def get_presets_by_gram(self, gram_stain):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """SELECT *
        FROM presets
        WHERE gram_stain = ?
        """,
        (gram_stain,)
    )

        results = cursor.fetchall()
        conn.close()
        return results


    def get_presets_by_gram_and_site(self,gram_stain, site):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(""" SELECT * FROM presets WHERE LOWER(gram_stain) = LOWER(?) AND LOWER(SITE) = LOWER(?)""",(gram_stain, site))

        results = cursor.fetchall()
        conn.close()

        return results

    def get_sites(self):
         conn = self.connect()
         cursor = conn.cursor()

         cursor.execute(   """
        SELECT DISTINCT LOWER(site) AS site
        FROM presets
        WHERE site IS NOT NULL
        AND site != ''
        ORDER BY site
        """)

         results = cursor.fetchall()
         conn.close()

         return [row["site"] for row in results]

    def get_clinical_groups(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(   """
        SELECT DISTINCT LOWER(clinical_group) AS clinical_group
        FROM presets
        WHERE clinical_group IS NOT NULL
        AND clinical_group != ''
        ORDER BY clinical_group
        """)

        results = cursor.fetchall()
        conn.close()

        return [row["clinical_group"] for row in results]

    def get_names(self):
        conn = self.connect()
        cursor = conn.cursor()
    
        cursor.execute(   """
        SELECT DISTINCT LOWER(name) AS name
        FROM presets
        WHERE name IS NOT NULL
        AND name != ''
        ORDER BY name
        """)
    
        results = cursor.fetchall()
        conn.close()
    
        return [row["name"] for row in results]


    def get_preset_by_search(self,gram_stain,site,search_mode,search_value):
         conn = self.connect()
         cursor = conn.cursor()

         if search_mode == "Species name":
             column = "name"
         elif search_mode == "Group":
             column = "clinical_group"
         else:
             conn.close()
             return []

         cursor.execute(
             f""" 
             SELECT * 
             FROM presets
             WHERE LOWER (gram_stain) = LOWER(?)
             AND LOWER (site) = LOWER(?)
             AND LOWER ({column}) = LOWER(?)
             """,
             (gram_stain,site,search_value)
         )
         results = cursor.fetchall()

         conn.close()
         return results


    def get_antibiotics(self, preset_id):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
           """
        SELECT id, antibiotic, method, sort_order
        FROM preset_antibiotics
        WHERE preset_id = ?
        ORDER BY sort_order
        """,
            (preset_id,)
        )

        results = cursor.fetchall()
        conn.close()

        return results

    def update_preset_field(self,preset_id,field,new_value):

        allowed_fields =["name","clinical_group","gram_stain","morphology","site","info","medium","guidance","cefinase","typing"]

        if field not in allowed_fields:
            raise ValueError("Invalid preset field")

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            f"""
            UPDATE presets
            SET {field} = ?
            WHERE id = ? 
            """,
            (new_value, preset_id)
        )

        conn.commit()
        conn.close()

    def update_antibiotic(self, antibiotic_id, antibiotic, method):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE preset_antibiotics
            SET antibiotic = ?,
                method = ?
            WHERE id = ?
            """,
            (antibiotic,antibiotic_id,method)
        )

        conn.commit()
        conn.close()

    def add_antibiotic(self, preset_id, antibiotic, method):
    
            conn = self.connect()
            cursor = conn.cursor()
    
            cursor.execute(
                """
                INSERT INTO preset_antibiotics
                (preset_id,
                antibiotic,
                method,
                sort_order)
                VALUES (?,?,?,?)
                """,
                (preset_id, antibiotic, method,0)
            )
    
            conn.commit()
            conn.close()

    def delete_antibiotic(self, antibiotic_id, antibiotic, method):
        
            conn = self.connect()
            cursor = conn.cursor()
        
            cursor.execute(
                """
                DELETE FROM preset_antibiotics
                WHERE id = ?
                """,
                (antibiotic_id,)
                )
        
            conn.commit()
            conn.close()

    def create_audit_table(self):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(  """
        CREATE TABLE IF NOT EXISTS preset_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            preset_id INTEGER,
            username TEXT,
            action TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_id INTEGER,
            field_name TEXT,
            old_value TEXT,
            new_value TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

        conn.commit()
        conn.close()

    def log_change(self,cursor,preset_id,username,action,target_type,target_id,field_name,old_value,new_value):

        cursor.execute(
        """
        INSERT INTO preset_audit_log (
            preset_id,
            username,
            action,
            target_type,
            target_id,
            field_name,
            old_value,
            new_value
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            preset_id,
            username,
            action,
            target_type,
            target_id,
            field_name,
            old_value,
            new_value
        )
    )

repo = PresetRepository()

repo.create_audit_table()

@st.cache_resource
def load_preset_repository():
    return PresetRepository()

