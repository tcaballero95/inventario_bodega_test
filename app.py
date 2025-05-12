# Copyright (c) 2024 tcaballero95
#
# -*- coding:utf-8 -*-
# @Script: app.py
# @Environment: inventario_bodega
# @Author: tcaballero95
# @Email: tomas.caballero1995@gmail.com
# @Create At: 2024-11-12 15:13:52
# @Last Modified By: Your Name
# @Last Modified At: 2024-11-14 14:17:12
# @Description: Aplicación para manejo de inventario bodega MORAN.

#%% IMPORTS
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_gsheets import GSheetsConnection

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from datetime import datetime

#%% PAGE CONFIG
page_title = "Inventario bodega"
layout = "centered"

st.set_page_config(page_title=page_title, layout=layout)

st.header("Inventario Bodega Morán", divider="gray")

#%% APP CONFIG
datos_ingresos_str = ["Proyecto", "Código"] 
datos_ingresos_int = ["Alto", "Ancho", "Largo"]

#%% MAIN MENU
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

page_selected = option_menu(
    menu_title=None,
    options=["Resumen", "Nuevo Ingreso", "Inventario"],
    icons=["bar-chart-fill", "plus-circle-fill", "boxes"],
    orientation="horizontal"
)

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)
# df = conn.read(worksheet="test_db", dtype={'Fecha': str, 'Proyecto': str, 'Código': str, 'Alto': int, 'Ancho': int, 'Largo': int})

#%% PAGES
if page_selected == "Resumen":
    # db = pd.read_csv('test_db.csv', dtype={'Fecha': str, 'Proyecto': str, 'Código': str, 'Alto': int, 'Ancho': int, 'Largo': int})
    db = conn.read(worksheet="test_db", ttl=0, dtype={'Fecha': str, 'Proyecto': str, 'Código': str})
    
    st.subheader('Espacio Utilizado', divider='gray')
    cols_eu = st.columns(4)
    
    db['m2'] = db['Ancho'] * db['Largo']
    db['m3'] = db['m2'] * db['Alto']
    
    used_m2 = round(db['m2'].sum()/10000, 1)
    used_m3 = round(db['m3'].sum()/1000000, 1)
    used_m2_percent = round((used_m2/190)*100, 1)
    used_m3_percent = round((used_m2/(190*4))*100, 1)


    cols_eu[0].metric(label="Metros cuadrados", value=f"{used_m2} m\u00b2")
    cols_eu[1].metric(label="Metros cúbicos", value=f"{used_m3} m\u00b3")
    cols_eu[2].metric(label="Porcentaje m\u00b2", value=f"{used_m2_percent} %")
    cols_eu[3].metric(label="Porcentaje m\u00b3", value=f"{used_m3_percent} %")
    

    proj_len = []
    for proj in db['Proyecto'].unique():
        proj_len.append(len(db[db["Proyecto"] == proj]))
    
    fig1, ax1 = plt.subplots(dpi=300)
    ax1.bar(db['Proyecto'].unique(), proj_len, label=proj_len, color="#ff4b4b")
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax1.grid()
    ax1.set_axisbelow(True)

    st.subheader('Proyectos', divider='gray')
    cols_res_proj = st.columns([0.3, 0.7], vertical_alignment='center')
    cols_res_proj[0].dataframe(pd.DataFrame({'Proyecto': db['Proyecto'].unique(), 'N° paquetes': proj_len}), hide_index=True)
    cols_res_proj[1].pyplot(fig1)


if page_selected == "Nuevo Ingreso":
    date = datetime.now()

    with st.form("nuevo_ingreso", border=False):
        cols_str = st.columns(2)
        for i, dato in enumerate(datos_ingresos_str):
            cols_str[i].text_input(f"{dato}", key=dato)
        
        cols_int = st.columns(3)
        for i, dato in enumerate(datos_ingresos_int):    
            cols_int[i].number_input(f"{dato} [cm]", min_value=0, step=1, format="%i", key=dato)

        submitted = st.form_submit_button("Añadir al inventario")
        
        if submitted:
            datos = {dato: st.session_state[dato] for dato in datos_ingresos_str+datos_ingresos_int}
            datos["Fecha"] = date.strftime("%Y/%m/%d %H:%M")
            st.write(datos)
            db = conn.read(worksheet="test_db", ttl=0, dtype={'Fecha': str, 'Proyecto': str, 'Código': str})
            conn.update(worksheet='test_db', data=db._append(datos, ignore_index=True))
            st.success('Datos añadidos al inventario!')


if page_selected == "Inventario":
    db = conn.read(worksheet="test_db", ttl=0, dtype={'Fecha': str, 'Proyecto': str, 'Código': str})
    proj_selected = st.selectbox('Proyectos', db['Proyecto'].unique(), index=None)
    if proj_selected:
        st.dataframe(db[db["Proyecto"] == proj_selected], use_container_width=True, hide_index=True)
    else:
        st.dataframe(db, use_container_width=True, hide_index=True)

    with st.expander('Editar datos de inventario', expanded=False):
        with st.form('inventario', border=False):
            # db = pd.read_csv('test_db.csv', dtype={'Fecha': str, 'Proyecto': str, 'Código': str, 'Alto': int, 'Ancho': int, 'Largo': int})
            db = conn.read(worksheet="test_db", ttl=0, dtype={'Fecha': str, 'Proyecto': str, 'Código': str})

            updated_db = st.data_editor(db, num_rows='dynamic', key='inventario', use_container_width=True)

            save = st.form_submit_button('Guardar')
            if save:
                # updated_db.to_csv('test_db.csv', sep=',', index=False)
                conn.update(worksheet="test_db", data=updated_db)
# %%
