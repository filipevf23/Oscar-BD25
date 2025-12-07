import sqlite3

conn = sqlite3.connect("Oscar-BD25\Oscars.db")
cur = conn.cursor()

PRAGMA = cur.execute("PRAGMA foreign_keys = ON;")

# -----------------------
# Tabela cerimonia
# -----------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS cerimonia (
    cerimonia_id INTEGER PRIMARY KEY,
    ano INTEGER UNIQUE NOT NULL
);
""")

# -----------------------
# Tabela categoria
# -----------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS categoria (
    categoria_id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria_canonica TEXT NOT NULL,
    classe TEXT NOT NULL,
    UNIQUE(categoria_canonica,classe)
);
""")

# -----------------------
# Tabela filme
# -----------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS filme (
    filme_id TEXT PRIMARY KEY,
    nome TEXT NOT NULL
);
""")

# -----------------------
# Tabela nomeado
# -----------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS nomeado (
    nomeado_id TEXT PRIMARY KEY,
    nome TEXT
);
""")

# -----------------------
# Tabela categoria_ano
# -----------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS categoria_ano (
    categoria_ano_id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria TEXT NOT NULL,
    categoria_id INTEGER NOT NULL,
    cerimonia_id INTEGER NOT NULL,
    FOREIGN KEY (categoria_id) REFERENCES categoria (categoria_id),
    FOREIGN KEY (cerimonia_id) REFERENCES cerimonia (cerimonia_id),
    UNIQUE (categoria,categoria_id,cerimonia_id)
);
""")

# -----------------------
# Tabela nomeacao
# -----------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS nomeacao (
    nomeacao_id TEXT PRIMARY KEY,
    categoria_ano_id INTEGER NOT NULL,
    cerimonia_id INTEGER NOT NULL,
    filme_id TEXT,
    nome TEXT,
    ganhou TEXT,
    nota TEXT,
    detalhe TEXT,
    citation TEXT,
    multi_filme TEXT,
    FOREIGN KEY (cerimonia_id) REFERENCES cerimonia (cerimonia_id),
    FOREIGN KEY (categoria_ano_id) REFERENCES categoria_ano (categoria_ano_id),
    FOREIGN KEY (filme_id) REFERENCES filme (filme_id)
);
""")

# -----------------------
# Tabela concorre
# -----------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS concorre (
    nomeado_id TEXT,
    nomeacao_id TEXT,
    PRIMARY KEY (nomeado_id, nomeacao_id),
    FOREIGN KEY (nomeado_id) REFERENCES nomeado (nomeado_id),
    FOREIGN KEY (nomeacao_id) REFERENCES nomeacao (nomeacao_id)
);
""")

conn.commit()
conn.close()

print("Banco Oscars.db criado com sucesso!")
