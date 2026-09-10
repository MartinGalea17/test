from organism_resistance_repo import OrganismResistanceRepo


class RulesEngine:

    def __init__(self, resistance_repo):
        self.resistance_repo = resistance_repo

    def get_organism_rules(self, organism_name):
        profile = self.resistance_repo.get_organism_profile(organism_name)
        return profile

    def get_intrinsic_resistance(self, organism_name):
        profile = self.get_organism_rules(organism_name)

        if not profile:
            return []

        return profile.get("intrinsic_resistance", [])

    def get_baseline_mechanisms(self, organism_name):
        profile = self.get_organism_rules(organism_name)

        if not profile:
            return []

        return profile.get("baseline_mechanisms",[])

    def apply_intrinsic_resistance(self, organism_name, ast_results):
        updated_results = {antibiotic: result.copy() for antibiotic, result in ast_results.items()}

        intrinsic_rules = self.get_intrinsic_resistance(organism_name)

        for rule in intrinsic_rules:
            target = rule["target"].strip().lower()
            interpretation = rule["interpretation"]

            for antibiotic, result_data in updated_results.items():
                if antibiotic.strip().lower() == target:
                

                    result_data["original_interpretation"] = result_data["interpretation"]
                    result_data["interpretation"] = interpretation
                    result_data["rule_applied"] = "Intrinsic resistance"

                    break

        return updated_results


repo = OrganismResistanceRepo()
rules_engine = RulesEngine(repo)

int_rules = rules_engine.get_intrinsic_resistance("klebsiella aerogenes")
base_mechanisms = rules_engine.get_baseline_mechanisms("klebsiella aerogenes")

print(int_rules)
print(base_mechanisms)