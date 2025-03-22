import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import time

# Conexión a la base de datos
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="180219",
    database="transactiondb",
    port=3306
)
cursor = conn.cursor()

# Función para ejecutar consultas y medir el tiempo

def execute_query(query):
    start_time = time.time()
    cursor.execute(query)
    results = cursor.fetchall()
    elapsed_time = (time.time() - start_time) * 1000  # Convertir a milisegundos
    return elapsed_time, results

# Consultas a ejecutar
queries = {
    "Consulta Original": "SELECT user_id, SUM(amount) FROM Transactions WHERE status = 'completed' GROUP BY user_id ORDER BY SUM(amount) DESC LIMIT 10;",
    "Consulta Optimizada": "SELECT user_id, SUM(amount) as total_amount FROM Transactions USE INDEX (idx_status_user_id) WHERE status = 'completed' GROUP BY user_id ORDER BY total_amount DESC LIMIT 10;"
}

# Ejecución de las consultas
results = {}
for label, query in queries.items():
    elapsed_time, data = execute_query(query)
    results[label] = elapsed_time
    print(f"{label}: {elapsed_time:.4f} ms")

# Crear gráfico de barras
plt.figure(figsize=(8, 5))
bars = plt.bar(results.keys(), results.values(), color=['blue', 'green'])
plt.title('Comparación de rendimiento de consultas SQL')
plt.ylabel('Tiempo de ejecución (ms)')

# Añadir etiquetas con el tiempo encima de cada barra
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.2f} ms', ha='center', va='bottom')

plt.savefig("performance_comparison.png")

# Cerrar la conexión
cursor.close()
conn.close()
