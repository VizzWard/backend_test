# 🔍 Optimización Propuesta

## 🔨 1. Agregar Índices Apropiados:

Los índices permiten búsquedas más rápidas. Vamos a agregar:

```mysql
-- Índice compuesto para optimizar filtrado y agrupación
CREATE INDEX idx_status_user_id ON Transactions (status, user_id);

-- Índice para mejorar la búsqueda del total
CREATE INDEX idx_status_amount ON Transactions (status, amount);
```

💡 ¿Por qué este índice?

- El índice idx_status_user_id permite a MySQL filtrar rápidamente por status = 'completed' y luego agrupar por user_id. 
- El índice idx_status_amount facilita la búsqueda de registros por amount cuando se realiza la agregación (SUM(amount)).

## 🔨 2. Cambiar la Consulta a Aprovechar Índices

El siguiente ajuste debería mejorar el rendimiento al utilizar índices de manera más efectiva.

```mysql
SELECT user_id, SUM(amount) as total_amount
FROM Transactions USE INDEX (idx_status_user_id)
WHERE status = 'completed'
GROUP BY user_id
ORDER BY total_amount DESC
LIMIT 10;
```

💡 ¿Por qué usar USE INDEX?

- Estamos diciéndole explícitamente a MySQL que aproveche el índice idx_status_user_id. 
- Esto mejora el rendimiento al filtrar rápidamente por status y luego agrupar por user_id.

## 🔨 3. Prueba de Rendimiento Antes y Después

Medir el rendimiento usando la consulta original y la consulta optimizada.

```mysql
-- Sin optimización
SET PROFILING = 1;
<Consulta original>
SHOW PROFILES;

-- Con optimización
SET PROFILING = 1;
<Consulta optimizada>
SHOW PROFILES;
```

