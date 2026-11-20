import sqlite3

def conectar():
    conexao = sqlite3.connect("clinica.db")
    conexao.row_factory = sqlite3.Row  
    conexao.execute("PRAGMA foreign_keys = ON")  
    return conexao

def criar_tabelas():
    conexao = conectar()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            data_nascimento TEXT
        )
    """)

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS consultas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            motivo TEXT,
            paciente_id INTEGER NOT NULL,
            FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
        )
    """)

    conexao.commit()
    conexao.close()

if __name__ == "__main__":
    criar_tabelas()
    print("Banco criado com sucesso!")