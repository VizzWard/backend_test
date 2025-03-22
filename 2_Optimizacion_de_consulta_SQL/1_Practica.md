# Ejercicio: Optimización de Consultas SQL

Dada la siguiente base de datos y consulta, optimízala para mejorar el rendimiento. Luego, realiza pruebas de carga con al menos 100,000 registros y mide la diferencia en tiempos de ejecución.

Tabla: Transactions
Columnas: id, user_id, amount, status, transaction_date
Consulta:

```mysql
SELECT user_id, SUM(amount)
FROM Transactions
WHERE status = 'completed'
GROUP BY user_id
ORDER BY SUM(amount) DESC
LIMIT 10;
```

Tareas:
1. Proponer y aplicar mejoras en índices o estructuras de tabla.
2. Realizar una prueba de rendimiento antes y después de la optimización.
3. Presentar un breve informe con resultados y conclusiones.

## ✅ Proceso Actual (Consulta Sin Optimización)

La consulta actual hace lo siguiente:

- Filtrado: Busca sólo las filas donde status = 'completed'.
- Agrupación: Agrupa los resultados por user_id.
- Agregación: Calcula la suma de amount por cada user_id.
- Ordenamiento: Ordena los resultados por la suma (SUM(amount)) de mayor a menor. 
- Límite: Devuelve solo los 10 primeros resultados.

## 🚩 Problemas Potenciales:

- Falta de Índices Apropiados: Si la columna status no tiene un índice, el filtrado será muy lento. 
- Agrupación y Ordenamiento Ineficientes: GROUP BY combinado con ORDER BY puede ser muy costoso si se realiza sobre toda la tabla. 
- Escalabilidad: Para 100,000 registros o más, esta consulta puede ser muy lenta.
