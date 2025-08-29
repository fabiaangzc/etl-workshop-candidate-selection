import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

# Conexión a MySQL
user = 'root'
password = 'root'
host = 'localhost'
port = 3306
database = 'selection_dw'
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

# Contrataciones por tecnología
query_tech = """
SELECT t.technology, COUNT(*) AS total_hired
FROM fact_selection f
JOIN dim_technology t ON f.technology_id = t.technology_id
WHERE f.hired = 1
GROUP BY t.technology
ORDER BY total_hired DESC;
"""
df_tech = pd.read_sql(query_tech, engine)

# Mostrar el DataFrame
print("\n>>> Hires por tecnología")
print(df_tech)

plt.figure(figsize=(9, 7))
plt.barh(df_tech["technology"], df_tech["total_hired"])
plt.gca().invert_yaxis()  # la mayor arriba
plt.xlabel("Contrataciones")
plt.title("Contrataciones por Tecnología (Hires)")
plt.tight_layout()
plt.show()

# Contrataciones por año
query_year = """
SELECT d.year, COUNT(*) AS total_hired
FROM fact_selection f
JOIN dim_date d ON f.date_id = d.date_id
WHERE f.hired = 1
GROUP BY d.year
ORDER BY d.year;
"""
df_year = pd.read_sql(query_year, engine)

# Mostrar el DataFrame
print("\n>>> Hires por año")
print(df_year)

plt.figure(figsize=(6,4))
plt.bar(df_year['year'], df_year['total_hired'], color='orange')
plt.xlabel('Año')
plt.ylabel('Contrataciones')
plt.title('Contrataciones por Año')
plt.tight_layout()
plt.show()

# Contrataciones por seniority
query_seniority = """
SELECT s.seniority, COUNT(*) AS total_hired
FROM fact_selection f
JOIN dim_seniority s ON f.seniority_id = s.seniority_id
WHERE f.hired = 1
GROUP BY s.seniority
ORDER BY total_hired DESC;
"""
df_seniority = pd.read_sql(query_seniority, engine)

# Mostrar el DataFrame
print("\n>>> Hires por seniority")
print(df_seniority)

plt.figure(figsize=(8,5))
plt.barh(df_seniority["seniority"], df_seniority["total_hired"])
plt.gca().invert_yaxis()
plt.xlabel("Contrataciones")
plt.title("Contrataciones por Seniority (Hires)")
plt.tight_layout()
plt.show()

# Contrataciones por país (EE.UU., Brasil, Colombia, Ecuador)
query_country = """
SELECT c.country, d.year, COUNT(*) AS total_hired
FROM fact_selection f
JOIN dim_country c ON f.country_id = c.country_id
JOIN dim_date d ON f.date_id = d.date_id
WHERE f.hired = 1
  AND c.country IN ('United States of America', 'Brazil', 'Colombia', 'Ecuador')
GROUP BY c.country, d.year
ORDER BY c.country, d.year;
"""
df_country = pd.read_sql(query_country, engine)

# Mostrar el DataFrame
print("\n>>> Hires por país en el tiempo")
print(df_country)

for country in df_country['country'].unique():
    data = df_country[df_country['country'] == country]
    plt.plot(data['year'], data['total_hired'], marker='o', label=country)
plt.xlabel('Año')
plt.ylabel('Contrataciones')
plt.title('Contrataciones por País')
plt.legend()
plt.tight_layout()
plt.show()

# Contrataciones por rango de experiencia
query_exp = """
SELECT 
  CASE 
    WHEN c.yoe IS NULL THEN 'Desconocido'
    WHEN c.yoe BETWEEN 0 AND 2 THEN '0-2 años'
    WHEN c.yoe BETWEEN 3 AND 5 THEN '3-5 años'
    WHEN c.yoe BETWEEN 6 AND 10 THEN '6-10 años'
    ELSE '10+ años'
  END AS experiencia_rango,
  COUNT(*) AS total_hired
FROM fact_selection f
JOIN dim_candidate c ON f.candidate_id = c.candidate_id
WHERE f.hired = 1
GROUP BY experiencia_rango
ORDER BY 
  CASE experiencia_rango
    WHEN 'Desconocido' THEN 0
    WHEN '0-2 años'    THEN 1
    WHEN '3-5 años'    THEN 2
    WHEN '6-10 años'   THEN 3
    WHEN '10+ años'    THEN 4
  END;
"""
df_exp = pd.read_sql(query_exp, engine)
print("\n>>> Contrataciones por rango de experiencia (YOE)")
print(df_exp)

# Gráfico
orden = ['Desconocido', '0-2 años', '3-5 años', '6-10 años', '10+ años']
df_exp['experiencia_rango'] = pd.Categorical(df_exp['experiencia_rango'], categories=orden, ordered=True)
df_exp = df_exp.sort_values('experiencia_rango')

plt.figure(figsize=(7,4))
plt.barh(df_exp['experiencia_rango'], df_exp['total_hired'], color="teal")
plt.xlabel('Contrataciones')
plt.title('Contrataciones por Rango de Experiencia (YOE)')
plt.tight_layout()
plt.show()

# Tasa de contratación (Hire Rate)
query_hire_rate = """
SELECT 
    ROUND(100.0 * SUM(hired) / COUNT(*), 2) AS hire_rate_percent,
    SUM(hired) AS total_hires,
    COUNT(*) AS total_applications
FROM fact_selection;
"""
df_hire_rate = pd.read_sql(query_hire_rate, engine)

print("\n>>> Tasa de contratación (Hire Rate):")
print(df_hire_rate)

# Visualización simple del porcentaje de contratados (barra única)
plt.figure(figsize=(4, 5))
plt.bar(['Hire Rate'], df_hire_rate['hire_rate_percent'], color='#4CAF50')
plt.ylabel('% de Contratados')
plt.title(
    f"Tasa de contratación: {df_hire_rate['hire_rate_percent'].iloc[0]}%\n"
    f"(Contratados={df_hire_rate['total_hires'].iloc[0]}, Total={df_hire_rate['total_applications'].iloc[0]})"
)
plt.ylim(0, 100)
plt.tight_layout()
plt.show()