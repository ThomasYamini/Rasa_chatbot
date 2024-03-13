import pandas as pd

data = pd.read_excel("./inventaire-du-patrimoine-breton-couche-simplifiee.xlsx")

# Extract entity values from user input
commune_values = "Brest"
# commune = commune_values[0] if commune_values else "Cacaboudin"
print("Commune values:", commune_values)
# print("Commune:", commune_values)
# Filter data based on user input
filtered_data = data[data['commune'] == commune_values]

# Get relevant information
result = filtered_data[['titre_courant', 'commentaire_descriptif']].head(1)
attraction_types = filtered_data['denomination'].drop_duplicates().head(1)

print(result)
print(attraction_types)