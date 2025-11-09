# Trabajo Práctico Final — Introducción al Marketing Online y los Negocios Digitales

Repositorio del trabajo práctico final de la materia.

**Consigna y documento principal:** [Trabajo Práctico Final](https://docs.google.com/document/d/15RNP3FVqLjO4jzh80AAkK6mUR5DOLqPxLjQxqvdzrYg/edit?usp=sharing)
**Diagrama Entidad Relación:** [DER](./assets/DER.png)

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


(Porcentaje de Promotores − Porcentaje de Detractores) × 100
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
