# Test en local

## 🔨 1. Crear un Contenedor MySQL con Docker

Descargar la imagen de MySQL

```bash
docker pull mysql
```

Crear un contenedor para MySQL.

```bash
docker run --name mysql-test-transactions-db -e MYSQL_ROOT_PASSWORD=180219 -e MYSQL_DATABASE=transactiondb -p 3306:3306 -d mysql
```

## 🔨 2. Crear la Tabla Transactions

```mysql
USE testdb;

CREATE TABLE IF NOT EXISTS Transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    transaction_date DATE NOT NULL
);
```

## 🔨 3. Poblar la Tabla con Datos Ficticios

Vamos a crear un procedimiento para insertar 100,000 registros de prueba.

```mysql
DELIMITER //

CREATE PROCEDURE PopulateTransactions()
BEGIN
    DECLARE i INT DEFAULT 1;
    WHILE i <= 100000 DO
        INSERT INTO Transactions (user_id, amount, status, transaction_date)
        VALUES (
            FLOOR(1 + (RAND() * 1000)),  -- user_id aleatorio entre 1 y 1000
            ROUND(RAND() * 1000, 2),     -- amount aleatorio entre 0.00 y 1000.00
            IF(RAND() > 0.2, 'completed', 'pending'),  -- Mayoría de 'completed'
            DATE_ADD(CURDATE(), INTERVAL -FLOOR(RAND() * 365) DAY)
        );
        SET i = i + 1;
    END WHILE;
END//

DELIMITER ;
```

Ejecuta esto para insertar los datos:

```mysql
CALL PopulateTransactions();
```

## 🔨 5. Crear Índices para Optimización

```mysql
CREATE INDEX idx_status_user_id ON Transactions (status, user_id);
CREATE INDEX idx_status_amount ON Transactions (status, amount);
```

## 🔨 6. Ejecutar las Consultas y Medir Rendimiento

Ejecuta la consulta original:

```mysql
SELECT user_id, SUM(amount)
FROM Transactions
WHERE status = 'completed'
GROUP BY user_id
ORDER BY SUM(amount) DESC
LIMIT 10;
```

Ahora, ejecuta la consulta optimizada:

```mysql
SELECT user_id, SUM(amount) as total_amount
FROM Transactions USE INDEX (idx_status_user_id)
WHERE status = 'completed'
GROUP BY user_id
ORDER BY total_amount DESC
LIMIT 10;
```

## 📊 Revisar Resultados con Performance Schema

```mysql
SELECT event_id, sql_text, timer_wait / 1000000000 AS time_ms
FROM performance_schema.events_statements_history
ORDER BY event_id DESC
LIMIT 2;
```

## ✅ Visualización de Resultados: Generar un Reporte con Python

### 📌 1. Instalar Dependencias en tu entorno (.venv)

Vamos a usar Python para conectarnos a MySQL, ejecutar las consultas y graficar los resultados con `matplotlib` o `pandas`.

```bash
pip install mysql-connector-python
pip install pandas
pip install matplotlib
```

### 📌 2. Script Python para Ejecutar Consultas y Visualizar Resultados

[performance_report.py](performance_report.py)

📌 ¿Qué hace este script?

- Se conecta a tu base de datos MySQL.
- Ejecuta ambas consultas (original y optimizada).
- Mide el tiempo de ejecución de cada consulta. 
- Genera un gráfico de barras comparando ambos tiempos.