import pandas as pd
import streamlit as st
import dataManagment as md
import algorithm
import logging

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


# CONFIGURE LOG FILE
md.logsFile()


# LOAD and SPLIT DATA
dataset = md.loadData()
train_data, test_data = train_test_split(dataset, test_size=0.2, random_state=42)



# NAVIGATION PANEL
st.sidebar.title("Sistema Recomendador de Destinos Turisticos")

tab = st.sidebar.radio(
    "Funciones:", (
    "Obtener recomendacion",
    "Consultar historico"
))
    

# TAB 1
if tab == "Obtener recomendacion":
    # HEAD
    st.markdown("<h2 style='text-align: center;'>Obtener recomendacion</h2>", unsafe_allow_html=True)
    
    # FILTER
    user_origin = st.selectbox("Pais de Origen:", sorted(train_data['Origen'].unique()))    
    user_month_selection = st.selectbox("Mes de Viaje:", sorted(train_data['Mes'].unique()), format_func=lambda x: f"{x} - {train_data[train_data['Mes'] == x]['Mes_Nombre'].iloc[0]}")
    user_month = int(str(user_month_selection).split(' - ')[0])   
    user_days = st.number_input("Dias de Duracion:", min_value=3)    
    user_expense = st.number_input("Gasto Diario Previsto:", min_value=50.0, step=1.0)
    
    # DEFINE RANGE FOR DAYS AND EXPENSES
    min_days = max(3, user_days - 5)
    max_days = user_days + 5
    min_expense = max(50, user_expense - 50)
    max_expense = user_expense + 50    
    
    # GENERATE RECOMENDATIONS
    train_recommendations = algorithm.generate_recommendations(train_data, user_origin, user_month, min_days, max_days, min_expense, max_expense, 5)
    test_recommendations = algorithm.generate_recommendations(test_data, user_origin, user_month, min_days, max_days, min_expense, max_expense, 5)

    # RENAMED COLUMNS
    renamed_columns = {
        "Destino": "CCAA",
        "Destino_Provincia": "Provincia",
        "Match_Score": "% Coincidencia"
    }
    recommendations_result = pd.DataFrame(train_recommendations, columns=renamed_columns.values())    

    # SHOW RECOMENDATIONS
    st.markdown("</br><h3 style='text-align: left;'>Resultados:</h3>", unsafe_allow_html=True)
    st.table(recommendations_result)
    
    # CALCULATE MSE (error cuadratico medio) BETWEEN train_recomendations AND test_recomendations
    if train_recommendations and test_recommendations:
        train_score = train_recommendations[0][2]
        test_score = test_recommendations[0][2]

        if not pd.isna(train_score) and not pd.isna(test_score):
            mse = mean_squared_error([train_score], [test_score])
            st.write(f"El error calculado entre train_recommendations y test_recommendations es de: {mse:.2f}")
        else:
            st.write("Insuficientes datos en el conjunto de prueba, no se puede evaluar el resultado.")
            
    elif not train_recommendations and test_recommendations:
        st.write("El conjunto de entrenamiento no tiene recomendaciones, no se puede evaluar el resultado.")         
    elif train_recommendations and not test_recommendations:
        st.write("El conjunto de prueba no tiene recomendaciones, no se puede evaluar el resultado.")        
    else:
        st.write("Tanto el conjunto de entrenamiento como el conjunto de prueba están vacíos, no se puede evaluar el resultado.")

    # CALIFICATION
    st.markdown("</br><h3 style='text-align: left; padding-bottom: 0;'>Puntua la recomendacion:</h3>", unsafe_allow_html=True)
    user_rating = st.slider("", 1, 5, 5)

    # SEND AND SAVE CALIFICATION
    if st.button("Enviar calificacion"):
        if not recommendations_result.empty:
            for index, recommendation in recommendations_result.iterrows():
                destination = recommendation['CCAA']
                destination_province = recommendation['Provincia']

            # CONFIGURE MASK
            mask = (dataset['Origen'] == user_origin) & \
                   (dataset['Mes'] == user_month) & \
                   (dataset['Gasto_Medio_Diario_PorVisitante'].between(min_expense, max_expense, inclusive='both')) & \
                   (dataset['Tiempo_Medio_Estancia'].between(min_days, max_days, inclusive='both')) & \
                   (dataset['Destino_Provincia'] == destination_province)
            
            # ASSIGNED CALIFICATION
            if dataset[mask].empty:
                logging.warning(f"No se encontraron coincidencias para la recomendación {destination} en el dataset.")
            else:
                dataset.loc[mask, 'Calificacion'] = user_rating     
        
                
# TAB 2
elif tab == "Consultar historico":
    # HEAD
    st.markdown("<h2 style='text-align: center;'>Historico de datos</h2>", unsafe_allow_html=True)

    # FILTER
    user_residence_country = st.selectbox("Pais de Origen:", ["Todos los paises"] + sorted(train_data['Origen'].unique()))

    # GRAPH
    st.markdown("</br><h3 style='text-align: left;'>Provincia mas visitada:</h3>", unsafe_allow_html=True)
    
    if user_residence_country == "Todos los paises":
        filtered_by_residence = train_data
    else:
        filtered_by_residence = train_data[train_data['Origen'] == user_residence_country]

    province_tourism = filtered_by_residence.groupby('Destino_Provincia')['Total_Turistas'].sum().reset_index()
    province_tourism = province_tourism.sort_values(by='Total_Turistas', ascending=False).head(15)

    st.bar_chart(province_tourism.set_index('Destino_Provincia'))
    