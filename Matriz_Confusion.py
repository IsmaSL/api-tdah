from sklearn.metrics import confusion_matrix, accuracy_score, recall_score, precision_score, f1_score
import pandas as pd

# Etiquetas reales y predichas
etiquetas_reales = ["Distraido", "Atento", "Distraido", "Atento", "Medianamente Atento", "Atento", "Distraido", "Atento", "Atento", "Atento"]
etiquetas_predichas = ["Distraido", "Medianamente Atento", "Medianamente Atento", "Atento", "Medianamente Atento", "Atento", "Distraido", "Medianamente Atento", "Atento", "Medianamente Atento"]

# Crear matriz de confusión
matriz_confusion = confusion_matrix(etiquetas_reales, etiquetas_predichas, labels=["Atento", "Medianamente Atento", "Distraido"])

# Convertir la matriz de confusión a un DataFrame para una mejor visualización
df_matriz_confusion = pd.DataFrame(matriz_confusion, 
                                   columns=["Predicho Atento", "Predicho Medianamente Atento", "Predicho Distraido"], 
                                   index=["Real Atento", "Real Medianamente Atento", "Real Distraido"])

print(df_matriz_confusion, '\n-------------------------------------------------------------------------------')

# Calcular Accuracy
accuracy = accuracy_score(etiquetas_reales, etiquetas_predichas)
print(f"Accuracy: {accuracy:.2f}")

# Calcular Recall, Precision y F1-Score para cada clase. 
# Dado que es un problema de clasificación multiclase, se especifica el parámetro 'average'.
# Usar 'macro' para calcular métricas para cada etiqueta y encontrar su media no ponderada.
recall = recall_score(etiquetas_reales, etiquetas_predichas, average='macro')
precision = precision_score(etiquetas_reales, etiquetas_predichas, average='macro')
f1 = f1_score(etiquetas_reales, etiquetas_predichas, average='macro')

print(f"Recall: {recall:.2f}")
print(f"Precision: {precision:.2f}")
print(f"F1-Score: {f1:.2f}")