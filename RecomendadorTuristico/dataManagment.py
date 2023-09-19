import os
import logging
import pandas as pd

def loadData():
    csv_path = os.getcwd() + "/data/DFinal.csv"
    dataset = pd.read_csv(csv_path, delimiter=";", dtype={"Tiempo_Medio_Estancia": float, "Gasto_Medio_Diario_PorVisitante": float}, decimal=",")

    # ADD COLUMN FOR CALIFICATIONS
    dataset['Calificacion'] = 1
    
    return dataset

def logsFile():
    # FOLDER
    logs_folder = os.path.join(os.getcwd(), "logs")

    # CONFIGURE FILE
    log_file_path = os.path.join(logs_folder, "app.log")
    logging.basicConfig(filename=log_file_path, level=logging.INFO)