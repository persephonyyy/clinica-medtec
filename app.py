from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import conectar, criar_tabelas
from algoritmos import ordenar_por_nome, buscar_por_nome

app = Flask(__name__)
criar_tabelas()


@app.route("/")
def inicio():
    conexao = conectar()
    total_pacientes = conexao.execute("SELECT COUNT(*) FROM pacientes").fetchone()[0]
    total_consultas = conexao.execute("SELECT COUNT(*) FROM consultas").fetchone()[0]
    proximas = conexao.execute("""
        SELECT consultas.data, consultas.hora, pacientes.nome AS paciente_nome
        FROM consultas
        JOIN pacientes ON consultas.paciente_id = pacientes.id
        WHERE consultas.data >= date('now')
        ORDER BY consultas.data, consultas.hora
        LIMIT 5
    """).fetchall()
    conexao.close()
    return render_template(
        "inicio.html",
        total_pacientes=total_pacientes,
        total_consultas=total_consultas,
        proximas=proximas,
    )


@app.route("/pacientes")
def listar_pacientes():
    busca = request.args.get("busca", "")

    conexao = conectar()
    pacientes = conexao.execute("SELECT * FROM pacientes").fetchall()
    conexao.close()

    if busca:
        pacientes = buscar_por_nome(pacientes, busca)
    pacientes = ordenar_por_nome(pacientes)

    return render_template("pacientes.html", pacientes=pacientes, busca=busca)


@app.route("/pacientes/novo", methods=["GET", "POST"])
def novo_paciente():
    if request.method == "POST":
        nome = request.form["nome"]
        telefone = request.form["telefone"]
        nascimento = request.form["data_nascimento"]

        conexao = conectar()
        conexao.execute(
            "INSERT INTO pacientes (nome, telefone, data_nascimento) VALUES (?, ?, ?)",
            (nome, telefone, nascimento),
        )
        conexao.commit()
        conexao.close()
        return redirect(url_for("listar_pacientes"))

    return render_template("form_paciente.html", paciente=None)


@app.route("/pacientes/<int:id>/editar", methods=["GET", "POST"])
def editar_paciente(id):
    conexao = conectar()

    if request.method == "POST":
        nome = request.form["nome"]
        telefone = request.form["telefone"]
        nascimento = request.form["data_nascimento"]

        conexao.execute(
            "UPDATE pacientes SET nome = ?, telefone = ?, data_nascimento = ? WHERE id = ?",
            (nome, telefone, nascimento, id),
        )
        conexao.commit()
        conexao.close()
        return redirect(url_for("listar_pacientes"))

    paciente = conexao.execute(
        "SELECT * FROM pacientes WHERE id = ?", (id,)
    ).fetchone()
    conexao.close()
    return render_template("form_paciente.html", paciente=paciente)


@app.route("/pacientes/<int:id>/excluir", methods=["POST"])
def excluir_paciente(id):
    conexao = conectar()
    conexao.execute("DELETE FROM consultas WHERE paciente_id = ?", (id,))
    conexao.execute("DELETE FROM pacientes WHERE id = ?", (id,))
    conexao.commit()
    conexao.close()
    return redirect(url_for("listar_pacientes"))


@app.route("/consultas")
def listar_consultas():
    data_filtro = request.args.get("data", "")

    sql = """
        SELECT consultas.id, consultas.data, consultas.hora, consultas.motivo,
               pacientes.nome AS paciente_nome
        FROM consultas
        JOIN pacientes ON consultas.paciente_id = pacientes.id
    """
    parametros = ()

    if data_filtro:
        sql += " WHERE consultas.data = ?"
        parametros = (data_filtro,)

    sql += " ORDER BY consultas.data, consultas.hora"

    conexao = conectar()
    consultas = conexao.execute(sql, parametros).fetchall()
    conexao.close()
    return render_template("consultas.html", consultas=consultas, data_filtro=data_filtro)


@app.route("/consultas/nova", methods=["GET", "POST"])
def nova_consulta():
    conexao = conectar()

    if request.method == "POST":
        conexao.execute(
            "INSERT INTO consultas (data, hora, motivo, paciente_id) VALUES (?, ?, ?, ?)",
            (
                request.form["data"],
                request.form["hora"],
                request.form["motivo"],
                request.form["paciente_id"],
            ),
        )
        conexao.commit()
        conexao.close()
        return redirect(url_for("listar_consultas"))

    pacientes = conexao.execute("SELECT id, nome FROM pacientes ORDER BY nome").fetchall()
    conexao.close()
    return render_template("form_consulta.html", consulta=None, pacientes=pacientes)


@app.route("/consultas/<int:id>/editar", methods=["GET", "POST"])
def editar_consulta(id):
    conexao = conectar()

    if request.method == "POST":
        conexao.execute(
            "UPDATE consultas SET data = ?, hora = ?, motivo = ?, paciente_id = ? WHERE id = ?",
            (
                request.form["data"],
                request.form["hora"],
                request.form["motivo"],
                request.form["paciente_id"],
                id,
            ),
        )
        conexao.commit()
        conexao.close()
        return redirect(url_for("listar_consultas"))

    consulta = conexao.execute("SELECT * FROM consultas WHERE id = ?", (id,)).fetchone()
    pacientes = conexao.execute("SELECT id, nome FROM pacientes ORDER BY nome").fetchall()
    conexao.close()
    return render_template("form_consulta.html", consulta=consulta, pacientes=pacientes)


@app.route("/consultas/<int:id>/excluir", methods=["POST"])
def excluir_consulta(id):
    conexao = conectar()
    conexao.execute("DELETE FROM consultas WHERE id = ?", (id,))
    conexao.commit()
    conexao.close()
    return redirect(url_for("listar_consultas"))


@app.route("/api/pacientes")
def api_pacientes():
    conexao = conectar()
    linhas = conexao.execute("SELECT * FROM pacientes ORDER BY nome").fetchall()
    conexao.close()
    return jsonify([dict(linha) for linha in linhas])


@app.route("/api/consultas")
def api_consultas():
    conexao = conectar()
    linhas = conexao.execute("""
        SELECT consultas.id, consultas.data, consultas.hora, consultas.motivo,
               pacientes.nome AS paciente
        FROM consultas
        JOIN pacientes ON consultas.paciente_id = pacientes.id
        ORDER BY consultas.data, consultas.hora
    """).fetchall()
    conexao.close()
    return jsonify([dict(linha) for linha in linhas])


if __name__ == "__main__":
    app.run(debug=True)