import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Fonction pour calculer la fraction volumique fibres nette
def calculate_net_volume_fraction(w_GOP, rho_GOP, rho_m):
    return w_GOP / (w_GOP + (rho_GOP / rho_m) * (1 - w_GOP))

# Fonction pour calculer le module de Young avec les équations fournies
def calculate_youngs_modulus(z, h, V_GOP_net, E_m, rho_m, E_GOP, rho_GOP, d_GOP, h_GOP, distribution, porosity_model, porosity_factor):
    V_GOP_avg = V_GOP_net / (V_GOP_net + (rho_GOP / rho_m) * (1 - V_GOP_net))
    lambda_param = 2 * (d_GOP / h_GOP)
    delta_1 = (E_GOP / E_m - 1) / (E_GOP / E_m + lambda_param)
    delta_2 = delta_1

    # Distribution fonctionnelle
    if distribution == "FU":
        V_GOP = V_GOP_avg * np.ones_like(z)
    elif distribution == "FGV":
        V_GOP = V_GOP_avg * (z / h + 0.5)
    elif distribution == "FGA":
        V_GOP = V_GOP_avg * (0.5 - z / h)
    elif distribution == "FGO":
        V_GOP = V_GOP_avg * (1 - 2 * np.abs(z) / h)
    elif distribution == "FGX":
        V_GOP = V_GOP_avg * (2 * np.abs(z) / h)
    else:
        raise ValueError("Invalid distribution.")

    X_1 = (1 + lambda_param * delta_1 * V_GOP) / (1 - delta_1 * V_GOP)
    X_2 = (1 + lambda_param * delta_2 * V_GOP) / (1 - delta_2 * V_GOP)
    E_composite = 0.49 * X_1 * E_m + 0.51 * X_2 * E_m

    if porosity_model == "P-1":
        porosity_effect = 1 - porosity_factor * (np.cos(np.pi * z / h))
    elif porosity_model == "P-2":
        porosity_effect = 1 - porosity_factor * (1 - np.cos(np.pi * z / h))
    else:
        porosity_effect = 1

    E_composite_porous = E_composite * porosity_effect
    return E_composite, V_GOP, E_composite_porous

# Interface utilisateur Streamlit
st.title("Calculs composites avec renforts et porosité")

st.sidebar.header("Entrée des paramètres")
E_m = st.sidebar.number_input("Module de Young de la matrice (GPa)", min_value=0.0, value=4.6, format="%.11f")
rho_m = st.sidebar.number_input("Densité de la matrice (kg/m^3)", min_value=0.0, value=1380.0, format="%.11f")
E_GOP = st.sidebar.number_input("Module de Young de fibre (GPa)", min_value=0.0, value=444.8, format="%.11f")
rho_GOP = st.sidebar.number_input("Densité de fibre (kg/m^3)", min_value=0.0, value=2250.0, format="%.11f")
w_GOP = st.sidebar.slider("Fraction massique de fibre (0-1)", min_value=0.0, max_value=1.0, value=0.1, format="%.11f")
V_GOP_net = calculate_net_volume_fraction(w_GOP, rho_GOP, rho_m)
st.sidebar.write(f"Fraction volumique fibres nette calculée : {V_GOP_net:.4f}")
d_GOP = st.sidebar.number_input("Taille moyenne des dGOP (m)", min_value=0.0, value=500e-9, format="%.11f")
h_GOP = st.sidebar.number_input("Épaisseur moyenne des hGOP (m)", min_value=0.0, value=0.95e-9, format="%.11f")
h = st.sidebar.number_input("Épaisseur totale du composite (h) (m)", min_value=0.0, value=0.01, format="%.11f")
porosity_model = st.sidebar.selectbox("Modèle de porosité", ["Aucun", "P-1", "P-2"])
porosity_factor = st.sidebar.slider("Facteur de porosité (0-1)", min_value=0.0, max_value=1.0, value=0.1, format="%.11f")

# Calcul de la densité effective
rho_composite = V_GOP_net * rho_GOP + (1 - V_GOP_net) * rho_m
st.sidebar.write(f"Densité effective du composite : {rho_composite:.4f} kg/m³")

# Calcul et tracé
z = np.linspace(-h / 2, h / 2, 100)
distributions = ["FU", "FGV", "FGA", "FGO", "FGX"]

# Graphique 1 : Module de Young avec porosité
fig1, ax1 = plt.subplots(figsize=(10, 6))
for dist in distributions:
    E_composite_porous = calculate_youngs_modulus(
        z, h, V_GOP_net, E_m, rho_m, E_GOP, rho_GOP, d_GOP, h_GOP, dist, porosity_model, porosity_factor
    )[2]
    ax1.plot(z / h, E_composite_porous, label=f"Distribution: {dist}")
ax1.set_title("Module de Young avec porosité pour différentes distributions fonctionnelles")
ax1.set_xlabel("z/h")
ax1.set_ylabel("Module de Young (GPa)")
ax1.legend()
ax1.grid()
st.pyplot(fig1)

# Graphique 2 : Densité effective en fonction de la fraction volumique
V_GOP_range = np.linspace(0.0, 0.6, 100)
rho_composite_range = V_GOP_range * rho_GOP + (1 - V_GOP_range) * rho_m
fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.plot(V_GOP_range, rho_composite_range, label="Densité effective")
ax2.set_title("Densité effective du composite en fonction de la fraction volumique")
ax2.set_xlabel("Fraction volumique de fibre")
ax2.set_ylabel("Densité effective (kg/m³)")
ax2.legend()
ax2.grid()
st.pyplot(fig2)

# Graphique 3 : Comparaison des modèles de porosité
fig3, ax3 = plt.subplots(figsize=(10, 6))
for model in ["Aucun", "P-1", "P-2"]:
    E_composite_porous = calculate_youngs_modulus(
        z, h, V_GOP_net, E_m, rho_m, E_GOP, rho_GOP, d_GOP, h_GOP, "FU", model, porosity_factor
    )[2]
    ax3.plot(z / h, E_composite_porous, label=f"Porosité: {model}")
ax3.set_title("Comparaison des modèles de porosité")
ax3.set_xlabel("z/h")
ax3.set_ylabel("Module de Young (GPa)")
ax3.legend()
ax3.grid()
st.pyplot(fig3)

# Graphique 4 : Impact du facteur de porosité
porosity_factors = np.linspace(0.0, 1.0, 50)
E_impact = []
for porosity in porosity_factors:
    E_composite_porous = calculate_youngs_modulus(
        z, h, V_GOP_net, E_m, rho_m, E_GOP, rho_GOP, d_GOP, h_GOP, "FU", porosity_model, porosity
    )[2]
    E_impact.append(np.mean(E_composite_porous))
fig4, ax4 = plt.subplots(figsize=(10, 6))
ax4.plot(porosity_factors, E_impact, label="Impact du facteur de porosité")
ax4.set_title("Impact du facteur de porosité sur le module de Young global")
ax4.set_xlabel("Facteur de porosité")
ax4.set_ylabel("Module de Young global (GPa)")
ax4.legend()
ax4.grid()
st.pyplot(fig4)
