import pandas as pd
import sqlite3

# Caminho do Excel
caminho_entrada = "Base_D_Dados\oscars.xlsx"

# Lê o Excel
df = pd.read_excel(caminho_entrada)

# Conecta no SQLite
conn = sqlite3.connect("Base_D_Dados\Oscars.db")
cur = conn.cursor()

#Reiniciar BD
cur.execute('Delete from filme')
cur.execute('Delete from cerimonia')
cur.execute('Delete from categoria')
cur.execute('Delete from categoria_ano')
cur.execute('Delete from nomeacao')
cur.execute('Delete from concorre')
#Reinicia os valores criados pelo SQL
cur.execute("DELETE FROM sqlite_sequence;")


#Cerimonia
df_cerimonia = df[['Ceremony','Year']]

for _, row in df_cerimonia.iterrows():
    cerimonia_id = int(row['Ceremony'])
    ano = str(row['Year'])
    cur.execute("""
        INSERT OR IGNORE INTO cerimonia (cerimonia_id, ano)
        VALUES (?, ?)
    """, (cerimonia_id, ano))

#Categoria
df_categoria = df[['CanonicalCategory','Class']].drop_duplicates()

for _, row in df_categoria.iterrows():
    classe = str(row['Class'])
    canonico = str(row['CanonicalCategory'])
    cur.execute("""
        INSERT OR IGNORE INTO categoria (categoria_canonica,classe)
        VALUES (?,?)
    """,(canonico,classe))


#Filme
df_filme = df[['Film','FilmId']]  

for _, row in df_filme.iterrows():
    if pd.isna(row['Film']):
        continue
    nome = str(row['Film'])  
    id = str(row['FilmId'])
    cur.execute("""
        INSERT OR IGNORE INTO filme (filme_id,nome)
        VALUES (?,?)
    """, (id,nome,))  

#Nomeado 
for j,row in df.iterrows():
    #Confere se existe nomeado e id, se falta id cria, se não tem nenhum ignora
    if pd.isna(row['Nominees']) and pd.isna(row['NomineeIds']):
        continue
    elif pd.isna(row['NomineeIds']):
        id = f"nn{row['Ceremony']}{j}"
    else:
        id = str(row['NomineeIds'])
    nome = str(row['Nominees'])
    cur.execute("""
        INSERT OR IGNORE INTO nomeado (nomeado_id,nome)
        VALUES (?,?)
        """,(id,nome))
    
#Categoria_Ano   
df_catAno = df[['Category','Class','CanonicalCategory','Ceremony']].drop_duplicates()
for _,row in df_catAno.iterrows():
    categoria = str(row['Category'])
    classe = str(row['Class'])
    canonico = str(row['CanonicalCategory'])
    cerimonia_id = int(row['Ceremony'])

    cur.execute("""
        Select categoria_id
        from categoria
        where classe like ? and categoria_canonica like ?
    """,(classe,canonico))
    categoria_id =  cur.fetchone()[0]

    cur.execute("""
        INSERT OR IGNORE INTO categoria_ano (categoria,categoria_id,cerimonia_id)
        VALUES (?,?,?)
        """,(categoria,categoria_id,cerimonia_id))    

#Nomeação 
for _,row in df.iterrows():
    #Confere se existe nomeacao e id, se falta id cria, se não tem nenhum ignora
    if pd.isna(row['NomId']): 
        id = f"anw{row['Ceremony']}{j}"
    else:
        id = str(row['NomId'])
    filme = str(row['FilmId'])
    nome = str(row['Name'])
    winner =  str(row['Winner']) 
    detail = str(row['Detail'])
    note = str(row['Note'])
    citation = str(row['Citation'])
    mf = str(row['MultifilmNomination'])
    #Para pegar os Ids corretos:
    categoria = str(row['Category'])
    cerimonia_id = int(row['Ceremony'])

    cur.execute("""
        Select categoria_ano_id
        from categoria_ano
        where categoria = ? AND cerimonia_id = ?
        """,(categoria,cerimonia_id))
    categoria_ano_id = cur.fetchone()[0]

    cur.execute("""
        INSERT OR IGNORE INTO nomeacao (nomeacao_id,categoria_ano_id
                ,filme_id,nome,ganhou,nota,detalhe,citation,multi_filme)
        VALUES (?,?,?,?,?,?,?,?,?)
    """,(id,categoria_ano_id,filme,nome,winner,note,detail,citation,mf))

#Concorre
for j, row in df.iterrows():
    #Basicamente faz o mesmo em nomeado e nomeação, os que não existem cria o mesmo
    #e como está pegando por linha vai ser necessariamente a mesma ligação
    if pd.isna(row['NomineeIds']) and pd.notna(row['Nominees']):
        nomeado_id = f"nn{row['Ceremony']}{j}"
    elif pd.notna(row['NomineeIds']):
        nomeado_id = str(row['NomineeIds'])
    else:
        continue  

    if pd.isna(row['NomId']):
        nomeacao_id =  f"anw{row['Ceremony']}{j}"
    else:
        nomeacao_id = str(row['NomId'])

    cur.execute("""
        INSERT OR IGNORE INTO concorre(nomeado_id, nomeacao_id)
        VALUES (?, ?)
    """, (nomeado_id, nomeacao_id))


# Salva alterações e fecha
conn.commit()
conn.close()

print("Foi")
