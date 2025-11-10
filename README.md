# Trabajo Práctico Final — Introducción al Marketing Online y los Negocios Digitales

Repositorio del trabajo práctico final de la materia.

**Consigna y documento principal:** [Trabajo Práctico Final](https://docs.google.com/document/d/15RNP3FVqLjO4jzh80AAkK6mUR5DOLqPxLjQxqvdzrYg/edit?usp=sharing)
**Diagrama Entidad Relación:** [DER](./assets/DER.png)

## Autor

El paquete fue creado por 
[Franco San Martin](https://github.com/Francossanmartin)


## Dimensiones
### dim_channel

| **Campo**  | **Tipo** | **Clave** | **Descripción**                              |
| ---------- | -------- | --------- | -------------------------------------------- |
| channel_sk | INT      | PK        | Identificador interno de la dimensión canal. |
| channel_bk | STRING   | BK        | Clave de negocio (código único del canal).   |
| code       | STRING   |           | Código del canal (ONLINE / OFFLINE).         |
| name       | STRING   |           | Nombre descriptivo del canal.                |

### dim_customer

| **Campo**   | **Tipo** | **Clave** | **Descripción**                                |
| ----------- | -------- | --------- | ---------------------------------------------- |
| customer_sk | INT      | PK        | Identificador interno de la dimensión cliente. |
| customer_bk | STRING   | BK        | Clave de negocio (ID único del cliente).       |
| email       | STRING   |           | Correo electrónico del cliente.                |
| first_name  | STRING   |           | Nombre del cliente.                            |
| last_name   | STRING   |           | Apellido del cliente.                          |
| status      | STRING   |           | Estado del cliente (A = Activo, I = Inactivo). |
| created_at  | DATETIME |           | Fecha y hora de creación del registro.         |

### dim_date

| **Campo**  | **Tipo** | **Clave** | **Descripción**                              |
| ---------- | -------- | --------- | -------------------------------------------- |
| date_sk    | INT      | PK        | Identificador interno de la dimensión fecha. |
| date_key   | INT      | BK        | Clave de negocio con formato YYYYMMDD.       |
| date       | DATETIME |           | Fecha completa con hora.                     |
| year       | INT      |           | Año correspondiente.                         |
| quarter    | INT      |           | Trimestre (1 a 4).                           |
| month      | INT      |           | Número del mes (1 a 12).                     |
| month_name | STRING   |           | Nombre del mes.                              |
| day        | INT      |           | Día del mes.                                 |
| dow        | INT      |           | Día de la semana (1 = Lunes, 7 = Domingo).   |
| is_weekend | BOOLEAN  |           | Indicador de fin de semana (1 = Sí, 0 = No). |

### dim_location

| **Campo**     | **Tipo** | **Clave** | **Descripción**                                    |
| ------------- | -------- | --------- | -------------------------------------------------- |
| location_sk   | INT      | PK        | Identificador interno de la dimensión ubicación.   |
| address_bk    | STRING   | BK        | Clave de negocio (ID único de la dirección).       |
| city          | STRING   |           | Ciudad donde se encuentra la dirección.            |
| province_name | STRING   |           | Nombre de la provincia o estado.                   |
| province_code | STRING   |           | Código abreviado de la provincia.                  |
| postal_code   | STRING   |           | Código postal correspondiente.                     |
| country_code  | STRING   |           | Código del país en formato ISO (ej. AR, US, etc.). |

### dim_product

| **Campo**   | **Tipo** | **Clave** | **Descripción**                                           |
| ----------- | -------- | --------- | --------------------------------------------------------- |
| product_sk  | INT      | PK        | Identificador interno de la dimensión producto.           |
| product_bk  | STRING   | BK        | Clave de negocio (ID único del producto).                 |
| sku         | STRING   |           | Código SKU del producto.                                  |
| name        | STRING   |           | Nombre comercial del producto.                            |
| category_sk | INT      | FK        | Clave foránea que referencia a la categoría del producto. |
| first_price | FLOAT    |           | Precio inicial del producto.                              |
| status      | STRING   |           | Estado del producto (A = Activo, I = Inactivo).           |
| created_at  | DATE     |           | Fecha de creación del registro.                           |

### dim_store

| **Campo**        | **Tipo** | **Clave** | **Descripción**                                        |
| ---------------- | -------- | --------- | ------------------------------------------------------ |
| store_sk         | INT      | PK        | Identificador interno de la dimensión tienda.          |
| store_bk         | STRING   | BK        | Clave de negocio (ID único de la tienda).              |
| store_name       | STRING   |           | Nombre de la tienda.                                   |
| store_code       | STRING   |           | Código interno o identificador adicional de la tienda. |
| city             | STRING   |           | Ciudad donde se ubica la tienda.                       |
| province_name    | STRING   |           | Nombre de la provincia o estado.                       |
| province_code    | STRING   |           | Código abreviado de la provincia.                      |
| postal_code      | STRING   |           | Código postal correspondiente.                         |
| country_code     | STRING   |           | Código del país en formato ISO (ej. AR, US, etc.).     |
| status           | STRING   |           | Estado de la tienda (A = Activa, I = Inactiva).        |
| created_at_store | DATETIME |           | Fecha y hora de creación o registro de la tienda.      |


##  Esquema Estrella

Creamos 6 esquemas estrella, Cada proceso de negocio tiene su diagrama.


### fact_nps_response
![fact_nps_response](./assets/tp%20marketing%201.jpg)

### fact_order
![fact_order](./assets/tp%20marketing%202.jpg)

### fact_payment
![fact_payment](./assets/tp%20marketing%203.jpg)

### fact_sales_order_item
![fact_sales_order_item](./assets/tp%20marketing%204.jpg)

### fact_shipment
![fact_shipment](./assets/tp%20marketing%205.jpg)

### fact_web_session
![fact_web_session](./assets/tp%20marketing%206.jpg)



## DAX

Las medidas utilizadas para llevar a cabo este analisis


### Usuarios Activos


```dax
Usuarios Activos = 
DISTINCTCOUNT('fact_web_session'[customer_sk])
```
---
### NPS

```dax
NPS = 
VAR TotalRespuestas =
    COUNT ( 'fact_nps_response'[score] )
VAR Promotores =
    CALCULATE (
        COUNT ( 'fact_nps_response'[score] ),
        'fact_nps_response'[score] >= 9
    )
VAR Detractores =
    CALCULATE (
        COUNT ( 'fact_nps_response'[score] ),
        'fact_nps_response'[score] <= 6
    )
RETURN
    DIVIDE ( ( Promotores - Detractores ), TotalRespuestas ) * 100
```

### Ticket Promedio

```dax
Ticket Promedio = 
DIVIDE(
    CALCULATE(
        SUM(fact_order[total_amount]),
        fact_order[status] IN { "PAID", "FULFILLED" }


    ),
    CALCULATE(
        COUNTROWS(fact_order),
        fact_order[status] IN { "PAID", "FULFILLED" }
    )
)
```

### Ventas Totales

```dax
Ventas Totales  = 
CALCULATE(
    SUM(fact_order[total_amount]),
    fact_sales_order_item
)
```
## DASHBOARD
<img width="878" height="496" alt="image" src="https://github.com/user-attachments/assets/1cc18163-612f-4f17-82b3-ccbb7dabaa30" />

