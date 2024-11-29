import numpy as np
import matplotlib.pyplot as plt

# Générer des données
x = np.linspace(0, 2 * np.pi, 100)  # 100 points de 0 à 2π
y = np.sin(x)  # Calculer le sinus

# Tracer
plt.figure(figsize=(10, 5))  # Taille de la figure
plt.plot(x, y, label='sin(x)', color='blue')  # Tracer la courbe
plt.title('Tracé de la fonction sinus')  # Titre
plt.xlabel('x (radians)')  # Étiquette de l'axe x
plt.ylabel('sin(x)')  # Étiquette de l'axe y
plt.axhline(0, color='black', lw=0.5, ls='--')  # Ligne horizontale au niveau 0
plt.axvline(0, color='black', lw=0.5, ls='--')  # Ligne verticale au niveau 0
plt.grid(True)  # Activer la grille
plt.legend()  # Afficher la légende
plt.show()  # Afficher le graphique
