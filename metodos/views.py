from django.shortcuts import render
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import os
from django.conf import settings
from uuid import uuid4

# Estilo visual bonito para las gráficas
plt.style.use('seaborn-v0_8-whitegrid')


def index(request):
    resultado = None
    grafica_url = None

    if request.method == 'POST':
        metodo = request.POST['metodo']
        input_data = request.POST['input_data']

        try:
            if metodo == 'interpolacion_newton':
                puntos = eval(input_data)
                resultado, grafica_url = interpolacion_newton(puntos)
            elif metodo == 'diferenciacion_finita':
                valores = eval(input_data)
                resultado, grafica_url = diferenciacion_finita(valores)
        except Exception as e:
            resultado = f"Error al procesar datos: {str(e)}"

    return render(request, 'metodos/index.html', {
        'resultado': resultado,
        'grafica_url': grafica_url
    })


def interpolacion_newton(puntos):
    n = len(puntos)
    x = [p[0] for p in puntos]
    y = [p[1] for p in puntos]

    coef = np.zeros([n, n])
    coef[:, 0] = y
    for j in range(1, n):
        for i in range(n - j):
            coef[i][j] = (coef[i + 1][j - 1] - coef[i][j - 1]) / (x[i + j] - x[i])

    xp = sp.Symbol('x')
    polinomio = coef[0][0]
    for i in range(1, n):
        termino = coef[0][i]
        for j in range(i):
            termino *= (xp - x[j])
        polinomio += termino

    polinomio = sp.simplify(polinomio)
    # Redondear coeficientes para mejor presentación
    polinomio = sp.nsimplify(polinomio, rational=False)
    
    # Convertir a string con coeficientes redondeados a 3 decimales
    polinomio_str = str(polinomio)
    # Aquí puedes hacer reemplazos para redondear, por ejemplo:
    import re
    def redondear_numero(match):
        num = float(match.group())
        return f"{num:.3f}"
    polinomio_str = re.sub(r"\d+\.\d+", redondear_numero, polinomio_str)

    fig, ax = plt.subplots()
    x_vals = np.linspace(min(x), max(x), 100)
    y_vals = [sp.lambdify(xp, polinomio)(val) for val in x_vals]
    ax.plot(x_vals, y_vals, label='Interpolación de Newton', color='blue')
    ax.scatter(x, y, color='red', label='Puntos originales')
    ax.set_title('Interpolación de Newton')
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.legend()
    ax.grid(True)

    filename = f'{uuid4()}.png'
    path = os.path.join(settings.MEDIA_ROOT, filename)
    plt.savefig(path)
    plt.close()

    return polinomio_str, settings.MEDIA_URL + filename



def diferenciacion_finita(valores):
    x = np.array([p[0] for p in valores])
    y = np.array([p[1] for p in valores])
    h = x[1] - x[0]

    derivadas = [(y[i + 1] - y[i]) / h for i in range(len(y) - 1)]
    derivadas_redondeadas = [round(float(d), 3) for d in derivadas]
    x_der = x[:-1]

    fig, ax = plt.subplots()
    ax.plot(x_der, derivadas, label='Derivada aproximada', color='green', marker='o')
    ax.scatter(x, y, color='orange', label='Datos originales')
    ax.set_title('Diferenciación Finita (hacia adelante)')
    ax.set_xlabel('x')
    ax.set_ylabel("f'(x)")
    ax.legend()
    ax.grid(True)

    filename = f'{uuid4()}.png'
    path = os.path.join(settings.MEDIA_ROOT, filename)
    plt.savefig(path)
    plt.close()

    return f"Derivadas aproximadas: {derivadas_redondeadas}", settings.MEDIA_URL + filename

def home(request):
    return render(request, 'metodos/home.html')
