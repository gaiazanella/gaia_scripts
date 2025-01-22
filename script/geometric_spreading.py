import numpy as np
import matplotlib.pyplot as plt

# Définir l'intervalle de x
x = np.linspace(-5, 5, 400)  # 400 points entre -5 et 5

# Calculer les valeurs de y = e^x
y = np.exp(-x)

# Tracer le graphe
plt.plot(x, y, linewidth=2)

# Ajouter des labels et un titre
plt.xlabel('x')
plt.ylabel('y = e^x')
plt.title('Graph of y = e^x')

# Ajouter une grille
plt.grid(True)

# Afficher le graphique
plt.show()
