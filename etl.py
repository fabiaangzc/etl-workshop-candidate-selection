import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text

# 1. Cargar el CSV
df = pd.read_csv('data/candidates.csv', sep=';')

# 2. Crear dimensiones únicas
dim_date = (
    df[['Application Date']]
    .drop_duplicates()
    .rename(columns={'Application Date': 'full_date'})
    .reset_index(drop=True)
)
dim_date['date_id'] = pd.to_datetime(dim_date['full_date']).dt.strftime('%Y%m%d').astype(int)
dim_date['year'] = pd.to_datetime(dim_date['full_date']).dt.year
dim_date['month'] = pd.to_datetime(dim_date['full_date']).dt.month
dim_date = dim_date[['date_id', 'full_date', 'year', 'month']]

dim_country = (
    df[['Country']]
    .drop_duplicates()
    .rename(columns={'Country': 'country'})
    .reset_index(drop=True)
)
dim_country['country_id'] = dim_country.index + 1
dim_country = dim_country[['country_id', 'country']]

dim_technology = (
    df[['Technology']]
    .drop_duplicates()
    .rename(columns={'Technology': 'technology'})
    .reset_index(drop=True)
)
dim_technology['technology_id'] = dim_technology.index + 1
dim_technology = dim_technology[['technology_id', 'technology']]

dim_seniority = (
    df[['Seniority']]
    .drop_duplicates()
    .rename(columns={'Seniority': 'seniority'})
    .reset_index(drop=True)
)
dim_seniority['seniority_id'] = dim_seniority.index + 1
dim_seniority = dim_seniority[['seniority_id', 'seniority']]

dim_candidate = (
    df[['First Name', 'Last Name', 'Email', 'YOE']]
    .drop_duplicates(subset=['Email'])
    .rename(columns={
        'First Name': 'first_name',
        'Last Name': 'last_name',
        'Email': 'email',
        'YOE': 'yoe'
    })
    .reset_index(drop=True)
)
dim_candidate['candidate_id'] = dim_candidate.index + 1
dim_candidate = dim_candidate[['candidate_id', 'first_name', 'last_name', 'email', 'yoe']]

# 3. Crear la tabla de hechos
df_fact = df.merge(dim_date, left_on='Application Date', right_on='full_date') \
    .merge(dim_candidate, left_on='Email', right_on='email') \
    .merge(dim_country, left_on='Country', right_on='country') \
    .merge(dim_technology, left_on='Technology', right_on='technology') \
    .merge(dim_seniority, left_on='Seniority', right_on='seniority')

# Calcular la columna 'hired'
df_fact['hired'] = ((df_fact['Code Challenge Score'] >= 7) & (df_fact['Technical Interview Score'] >= 7)).astype(int)

fact_selection = df_fact[[
    'date_id',
    'candidate_id',
    'country_id',
    'technology_id',
    'seniority_id',
    'Code Challenge Score',
    'Technical Interview Score',
    'hired'
]].rename(columns={
    'Code Challenge Score': 'code_challenge_score',
    'Technical Interview Score': 'interview_score'
})

# Ahora tienes tus DataFrames: dim_date, dim_country, dim_technology, dim_seniority, dim_candidate, fact_selection

# Opcional: guardar a CSV para revisión
# dim_date.to_csv('dim_date.csv', index=False)
# dim_country.to_csv('dim_country.csv', index=False)
# dim_technology.to_csv('dim_technology.csv', index=False)
# dim_seniority.to_csv('dim_seniority.csv', index=False)
# dim_candidate.to_csv('dim_candidate.csv', index=False)
# fact_selection.to_csv('fact_selection.csv', index

print(dim_date.head())
print(dim_country.head())
print(dim_technology.head())
print(dim_seniority.head())
print(dim_candidate.head())
print(fact_selection.head())

#Se crea la conexión a la base de datos MySQL y se cargan los datos
user = 'root'
password = 'root'
host = 'localhost'
port = 3306
database = 'selection_dw'

# Crea el engine de conexión
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

# Vacía las tablas antes de cargar los datos
with engine.connect() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    conn.execute(text("TRUNCATE TABLE fact_selection;"))
    conn.execute(text("TRUNCATE TABLE dim_candidate;"))
    conn.execute(text("TRUNCATE TABLE dim_seniority;"))
    conn.execute(text("TRUNCATE TABLE dim_technology;"))
    conn.execute(text("TRUNCATE TABLE dim_country;"))
    conn.execute(text("TRUNCATE TABLE dim_date;"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

# Carga cada DataFrame a su tabla correspondiente
dim_date.to_sql('dim_date', engine, if_exists='append', index=False)
dim_country.to_sql('dim_country', engine, if_exists='append', index=False)
dim_technology.to_sql('dim_technology', engine, if_exists='append', index=False)
dim_seniority.to_sql('dim_seniority', engine, if_exists='append', index=False)
dim_candidate.to_sql('dim_candidate', engine, if_exists='append', index=False)
fact_selection.to_sql('fact_selection', engine, if_exists='append', index=False)

print("¡Carga a MySQL completada!")