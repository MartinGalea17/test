


repo = preset_repository()
repo.load_presets()

print("Loaded negative:", len(repo.neg_presets))
print("Loaded positive:", len(repo.pos_presets))


result = repo.get_panel(
    organism="streptococcus pyogenes",
    clinical_group="Beta haemolytic streptococci group A,B,C,G",
    site="other",
    mode="DISC"
)

print("\nMIC panel:")
print(result)



from eucast_repo import EucastRepository

repo = EucastRepository()

repo.load_from_folder("breakpoint_folder")

print("\nVERSIONS:", repo.data.keys())

version = list(repo.data.keys())[0]

print("\nORGANISM INDEX SAMPLE:")
print(repo.index_by_org[version].keys())

print("\nANTIBIOTIC INDEX SAMPLE:")
print(repo.index_by_ab[version].keys())


entry = repo.index_by_org["2024"]["streptococcus pyogenes"][0]
print(entry["clinical_group"])



engine = ASTEngine()
engine.load_data()

print("All repositories loaded successfully.")


panel = engine.build_panel(
    organism="streptococcus pyogenes",
    site="other",
    mode="MIC"
)

print("\nPANEL:")
print(panel["panel"])

results = {
    "benzylpenicillin": 0.5,
    "vancomycin": 1,
    "levofloxacin": 2
}

output = engine.interpret_results(
    organism="Staphylococcus aureus",
    site="other",
    mode="MIC",
    results=results
)

print("\nRESULTS:")
for ab, data in output["results"].items():
    print(ab, data)
