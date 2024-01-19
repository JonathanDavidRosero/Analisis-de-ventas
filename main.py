# Impotar Librerias

import streamlit as st
import pandas as pd 
import xgboost as xgb
import sqlite3
import pycaret
import os

from pycaret.regression import *

#STREAMLIT: Aqui se crea la intervas 
st.title("""
PREDICTOR DE VENTAS
""") 
st.sidebar.header('Ingrese los parametros para predecir')

def parametros():

    T = st.sidebar.slider('Tamaño de la Finca (m^2)',5000,15000,10000)
    st.write('Tamaño (m^2)',T)

    NC = st.sidebar.selectbox('Escoja el tipo de Cultivo', ['papa', 'maiz', 'flores','mango','zanahoria','papaya','aguacate'])
    st.write('Cultivo:', NC)

    VI = st.sidebar.slider('Valor de Inversión',0,23000000,12000000)
    st.write('Valor de Inversión',VI)

    PA = st.sidebar.slider('Valor de Pagos al Personal',1000000,3000000,2000000)
    st.write('Valor por Pagos',PA)

    FV = date = st.sidebar.date_input('Seleccione la fecha de Venta')
    st.write('Fecha de Venta:', FV)

    

    data = {
        'tamanio_m2' : T,
        'nombre_cultivo' : NC,
        'valor_inversion': VI,
        'valor_pago': PA,
        'fecha_venta': FV,
    }

    predictores = pd.DataFrame(data,index=[0])

    return predictores

df = parametros()

## Se Sube la Base de Datos SQL

# Ruta relativa al directorio del script
db_path_relative = 'datos_cultivos.db'

# Ruta absoluta
db_path_absolute = os.path.abspath(db_path_relative)

# Conectar a la base de datos
conexion = sqlite3.connect(db_path_absolute)

query="""
SELECT f.tamanio_m2,c.nombre_cultivo,c.valor_inversion,pa.valor_pago,v.fecha_venta,v.valor_venta
FROM Cultivos c
JOIN Ventas v ON c.id_cultivo = v.id_cultivo
JOIN Finca f ON c.id_finca = f.id_finca
JOIN Personal p ON c.id_finca = p.id_finca
JOIN Pagos pa ON p.id_personal = pa.id_personal
"""
dataset = pd.read_sql_query(query,conexion);
print(dataset)


## Uso de Pycaret para encontrar el modelo de mejor ajuste

s = setup(dataset)

#Se compara los modelos para elegir el de mejor ajuste
compare_models()

#Se realizan pruebas al modelo para comprobar su aprendizaje
xg = create_model('lightgbm')

#Se guarda el modelo de mejor rendimiento
save_model(xg, 'modelo_lightgbm')

#Se realiza las predicciones con los datos obtenidos en Streanlit
predicciones = predict_model(xg, data=df)


predicciones = predicciones.rename(columns={'prediction_label': 'valor_venta'})

VV = predicciones['valor_venta']
#Se mustra los resultados en streamlit
st.title("""
RESULTADO
""")
st.write(VV)

st.write(predicciones)
