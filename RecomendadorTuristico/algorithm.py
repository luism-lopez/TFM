import pandas as pd

# MATCH SCORE SCALE
def scale_match_score(match_score):
    min_score = match_score.min()
    max_score = match_score.max() + 0.1
    scaled_score = 100 * (match_score - min_score) / (max_score - min_score)
    return scaled_score


# FILTRADO BASADO EN CONTENIDO
def generate_recommendations(dataset, user_origin, user_month, min_days, max_days, min_expense, max_expense, num_recommendations):
    filtered_data = dataset[
        (dataset['Origen'] == user_origin) &
        (dataset['Mes'] == user_month) &
        (dataset['Tiempo_Medio_Estancia'].between(min_days, max_days)) &
        (dataset['Gasto_Medio_Diario_PorVisitante'].between(min_expense, max_expense))
    ]
    
    # NORMALIZE
    columns_to_normalize = ['Tiempo_Medio_Estancia', 'Gasto_Medio_Diario_PorVisitante', 'Total_Turistas', 'Total_Pernoctaciones']
    normalized_data = (filtered_data[columns_to_normalize] - filtered_data[columns_to_normalize].min()) / (filtered_data[columns_to_normalize].max() - filtered_data[columns_to_normalize].min())

    # CALCULATE MATCH SCORE
    normalized_data['Match_Score'] = normalized_data['Tiempo_Medio_Estancia'] + \
                                     normalized_data['Gasto_Medio_Diario_PorVisitante'] + \
                                     normalized_data['Total_Turistas'] + \
                                     normalized_data['Total_Pernoctaciones']

    # MULTIPLY MATCH SCORE BY CALIFICATION
    normalized_data['Match_Score'] = scale_match_score(normalized_data['Match_Score'] * filtered_data['Calificacion'])

    # ADD COLUMNAS 'Destino' AND 'Destino_Provincia'
    normalized_data['Destino'] = filtered_data['Destino']
    normalized_data['Destino_Provincia'] = filtered_data['Destino_Provincia']

    # SORT AND DROP DUPLICATES, KEEPING THE ONE WITH THE HIGHEST Match_Score
    normalized_data = normalized_data.sort_values(by='Match_Score', ascending=False)
    normalized_data = normalized_data.drop_duplicates(subset=['Destino', 'Destino_Provincia'], keep='first')
    
    recommendations = normalized_data.head(num_recommendations)
    return recommendations[['Destino', 'Destino_Provincia', 'Match_Score']].values.tolist()
    