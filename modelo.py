from docplex.mp.model import Model
import numpy as np

# ------------ Parametros ------------
I = [i for i in range(7)] # Conjunto de todos los productos {Fruta, Verdura, Carne, Pescado, Legumbre,  Masas, Postre}.
J = [j for j in range(5)] # Conjunto de características nutricionales {Calorías, Vitaminas, Carbohidratos, Grasas, Proteínas}. 
K = [k for k in range(2)] # Conjunto de supermercados {Líder (L), Jumbo (J)}

# precio
p = [
    #Lider, Jumbo
    [2000, 2300], # Fruta
    [2200, 2100], # Verdura
    [7500, 8500], # Carne
    [7000, 6800], # Pescado
    [2800, 3200], # Legumbre
    [3000, 2800], # Masas
    [9000, 10000] # Postre
]

# valor nutricional
v = [
    #Calorías, vitaminas, carbohidratos, grasas, proteínas
    [520.0,  3.0, 140.0,  2.0 , 3.0  ],  # Fruta
    [200.0,  4.0, 40.0 ,  2.0 , 10.0 ],  # Verdura
    [2500.0, 1.0,  0.0 , 150.0, 250.0],  # Carne
    [2080.0, 2.0,  0.0 , 130.0, 220.0],  # Pescado
    [1160.0, 2.0, 200.0,  5.0 , 90.0 ],  # Legumbre
    [1300.0, 1.0, 280.0,  3.0 , 25.0 ],  # Masas
    [5000.0, 0.5, 650.0, 250.0, 50.0 ]   # Postre
]

S = np.zeros((7,2))
M = 1000

mdl = Model(name = 'Modelo')

# --------------- Variables ----------------
x = mdl.integer_var_dict(((i,k) for i in I for k in K), name='x', lb = 0)
y = mdl.binary_var(name='y_pescado_Lider')
z = mdl.continuous_var(name='z_Lider')
w = mdl.binary_var(name='w_legumbres_Jumbo')
h = mdl.continuous_var(name='h_Jumbo')

# ------------ Función objetivo ------------
mdl.minimize(
    mdl.sum(mdl.sum(p[i][k]*x[i,k] for i in I) for k in K) 
    - 1800*z - 1000*h
)

# -------------- Restricciones --------------

# restricciones de presupuesto
mdl.add_constraint(mdl.sum(mdl.sum(p[i][k]*x[i,k] for i in I) for k in K) <= 250000)

# restricciones de calorías
mdl.add_constraint(mdl.sum(mdl.sum(x[i,k]*v[i][0] for i in I) for k in K) >= 90000)

# restricción porcentaje de proteína provenientes de carnes, pescados o legumbres adquiridos
mdl.add_constraint(
    mdl.sum(
        mdl.sum ( 
            mdl.sum(v[i][j]*x[i,k] for k in K)   
        for i in range(2, 5)) # 2:Carne, 3:Pescado, 4:Legumbres
    for j in range(3, 5)) # 3:Grasas, 4:Proteínas 

    >= 

    0.6 * (
        mdl.sum(
            mdl.sum ( 
                mdl.sum(v[i][j]*x[i,k] for k in K)   
            for i in I)
        for j in range(3, 5)) # 3:Grasas, 4:Proteínas 
    )
)

# restricción de porcentaje de postres en el total de la compra
mdl.add_constraint(mdl.sum(x[6,k] for k in K) <= 0.1 * (mdl.sum(mdl.sum(x[i,k] for i in I) for k in K)))

# Restricción de porcentaje de vitaminas para frutas y verduras
mdl.add_constraint((mdl.sum(mdl.sum(v[i][1]*x[i,k] for k in K) for i in range(0,3))) >= 0.5 * ((mdl.sum(mdl.sum(v[i][1]*x[i,k] for k in K) for i in I))))

# Restricción de proporción de frutas y verduras
mdl.add_constraint(mdl.sum(x[0,k] for k in K) == mdl.sum(x[1,k] for k in K))

# Restricción porcentaje de calorías a carbohidratos
mdl.add_constraint( 4*(mdl.sum(mdl.sum(v[i][2]*x[i,k] for k in K) for i in I)) <= 0.45 * (mdl.sum(mdl.sum(v[i][0]*x[i,k] for k in K) for i in I)) )

# Restricciones para el cambio de precio del pescado si se compra más de 2 kg
mdl.add_constraint(x[3,0] >= 5 * y)
mdl.add_constraint(x[3,0] <= 5 + M * y)

mdl.add_constraint(z >= x[3,0] - M * (1 - y))
mdl.add_constraint(z <= M * y)
mdl.add_constraint(z <= x[3,0])

# Restricciones para el cambio de precio de las legumbres si se compra más de 3 kg
mdl.add_constraint(x[4,1] >= 8 * w)
mdl.add_constraint(x[4,1] <= 8 + M * w)

mdl.add_constraint(h >= x[4,1] - M * (1 - w))
mdl.add_constraint(h <= M * w)
mdl.add_constraint(h <= x[4,1])

# Restricciones de dominio
mdl.add_constraint(z >= 0)
mdl.add_constraint(h >= 0)

# ---------------- Solución ----------------
sol = mdl.solve(log_output =True)

if sol:
    print(f'El valor de la funcion objetivo es: {mdl.objective_value}')
    for i in I:
        for k in K:
                S[i,k] = x[i,k].solution_value
    print(f'Matriz con solución de compras: \n {S} \n')
    print("1: Sí, 0: No")
    print(f"¿Francisco decidió usar el descuento del Líder?: {y.solution_value}")
    print(f"¿Francisco decidió usar el descuento del Jumbo?: {w.solution_value}")
else:
    print("No posee solución")
    