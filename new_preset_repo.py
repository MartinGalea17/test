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

    def get_presets_by_name(self,species_name, site): # add site later 
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * 
            FROM presets 
            WHERE LOWER(name) = LOWER (?)
            AND LOWER(site) = LOWER (?)
            
            """,
            (species_name,site)
         )
        results = cursor.fetchall()
        conn.close()
       
        return results 


    def get_presets_by_group(self,clinical_group, site):
        conn = self.connect()
        cursor = conn.cursor()
    
        cursor.execute(
            """
            SELECT * 
            FROM presets 
            WHERE LOWER(clinical_group) = LOWER (?)
            AND LOWER(site) = LOWER (?)
            """,
            (clinical_group,site)
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

    def update_preset_field(self,preset_id,field,new_value,username):

        allowed_fields =["name","clinical_group","gram_stain","morphology","site","info","medium","guidance","cefinase","typing"]

        if field not in allowed_fields:
            raise ValueError("Invalid preset field")

        conn = self.connect()
        cursor = conn.cursor()

        #get old value(any of the fields that changed)
        cursor.execute(
            f"""
            SELECT {field}
            FROM presets
            WHERE id = ?
            """,
            (preset_id,)
        )
        old_row = cursor.fetchone()
        if old_row is None:
            conn.close()
            raise ValueError("Preset not found")

        old_value = old_row[field]

        if old_value == new_value:
            conn.close()
            return 

        #update preset
        cursor.execute(
            f"""
            UPDATE presets
            SET {field} = ?
            WHERE id = ? 
            """,
            (new_value, preset_id)
        )

        #log change 
        self.log_change(cursor,preset_id,username,"UPDATE","preset",preset_id,field,old_value,new_value)
        conn.commit()
        conn.close()

    def update_antibiotic(self, antibiotic_id, antibiotic, method,username):

        conn = self.connect()
        cursor = conn.cursor()

        #get old row first
        cursor.execute(
            """
            SELECT preset_id, antibiotic, method
            FROM preset_antibiotics
            WHERE id = ?
            """,
            (antibiotic_id,)
        )

        old_row = cursor.fetchone()
        if old_row is None:
            conn.close()
            raise ValueError("Antibiotc not found")

        preset_id = old_row["preset_id"]
        old_antibiotic = old_row["antibiotic"]
        old_method = old_row["method"]

        #update the row 
        cursor.execute(
            """
            UPDATE preset_antibiotics
            SET antibiotic = ?,
                method = ?
            WHERE id = ?
            """,
            (antibiotic, method, antibiotic_id)
        )
        #log antibiotic name change
        if old_antibiotic != antibiotic:
            self.log_change(cursor,preset_id,username,"UPDATE","antibiotic",antibiotic_id,"antibiotic",old_antibiotic,antibiotic)

        #log method change
        if old_method != method:
            self.log_change(cursor,preset_id,username,"UPDATE","antibiotic",antibiotic_id,"method",old_method,method)

        conn.commit()
        conn.close()


    def add_antibiotic(self, preset_id, antibiotic, method,username):
    
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

            antibiotic_id = cursor.lastrowid

            self.log_change(
                cursor, preset_id, username, "INSERT", "antibiotic", antibiotic_id, "antibotic", None, antibiotic
            )
    
            conn.commit()
            conn.close()

    def delete_antibiotic(self, antibiotic_id,username):
        
            conn = self.connect()
            cursor = conn.cursor()

            #get antibiotic before its deleted
            cursor.execute(
                """
                SELECT preset_id, antibiotic, method
                FROM preset_antibiotics
                WHERE id = ?
                """,
                (antibiotic_id,)
            )

            old_row = cursor.fetchone()

            if old_row is None:
                conn.close()
                raise ValueError("Antibiotic not found")

            preset_id = old_row["preset_id"]
            old_antibiotic = old_row["antibiotic"]

            #delete antibiotic

            cursor.execute(
                """
                DELETE FROM preset_antibiotics
                WHERE id = ?
                """,
                (antibiotic_id,)
                )

            #log deletion
            self.log_change(
                cursor,
                preset_id,
                username,
                "DELETE",
                "antibiotic",
                antibiotic_id,
                "antibiotic", 
                old_antibiotic,
                None
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

    def get_preset_by_id(self, preset_id):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM presets
            WHERE id = ?
            """,
            (preset_id,)
        )

        result = cursor.fetchone()

        conn.close()

        return result









repo = PresetRepository()

repo.create_audit_table()

@st.cache_resource
def load_preset_repository():
    return PresetRepository()

