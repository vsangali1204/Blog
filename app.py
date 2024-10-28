import os
from flask import * # Flask, render_template, request, redirect, url_for, flash, session
import pymysql
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configurações MySQL
app.config['MYSQL_HOST'] = 'blog-educaciona.mysql.uhserver.com'
app.config['MYSQL_USER'] = 'adminblog'
app.config['MYSQL_PASSWORD'] = 'S@ngali9962'
app.config['MYSQL_DB'] = 'blog_educaciona'
app.secret_key = 'sua_chave_secreta'

# Função para obter conexão com o banco de dados
def get_db_connection():
    connection = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# Decorador para verificar login
def login_obrigatorio(f):
    @wraps(f)
    def funcao_decorada(*args, **kwargs):
        if 'logado' not in session:
            flash('Por favor, faça login para acessar esta página', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return funcao_decorada

# Rotas principais
@app.route('/')
def inicio():
    connection = get_db_connection()
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM artigos ORDER BY data_criacao DESC LIMIT 3")
            ultimos_artigos = cur.fetchall()
    finally:
        connection.close()
    return render_template('inicio.html', artigos=ultimos_artigos)
    # return "Olá, mundo! Bem-vindo ao meu aplicativo Flask."

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        email = request.form['email']

        # Hash da senha
        senha_hash = generate_password_hash(senha)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO usuarios (usuario, senha, email) VALUES (%s, %s, %s)', 
                           (usuario, senha_hash, email))
            conn.commit()
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('login'))  
        except Exception as e:
            flash(f'Erro ao adicionar usuario: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cur:
                cur.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario,))
                usuario_dados = cur.fetchone()
        finally:
            connection.close()

        if usuario_dados and check_password_hash(usuario_dados['senha'], senha):
            session['logado'] = True
            session['usuario'] = usuario
            session['id_usuario'] = usuario_dados['id']
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('Credenciais inválidas!', 'danger')
    return render_template('login.html')

@app.route('/sair')
def sair():
    session.clear()
    flash('Você foi desconectado', 'success')
    return redirect(url_for('inicio'))

# ----------------------- Rotas para Artigos -------------------------
@app.route('/artigos', methods=['GET', 'POST'])
#@login_obrigatorio
def artigos():
    connection = get_db_connection()
    if request.method == 'POST':
        if request.form.get('action') == 'adicionar':
            titulo = request.form['titulo']
            conteudo = request.form['conteudo']
            id_usuario = session['id_usuario']
            try:
                with connection.cursor() as cur:
                    cur.execute("INSERT INTO artigos(titulo, conteudo, id_usuario) VALUES(%s, %s, %s)",
                                (titulo, conteudo, id_usuario))
                    connection.commit()
                flash('Artigo adicionado com sucesso!', 'success')
            except Exception as e:
                flash('Erro ao adicionar artigo: {}'.format(e), 'danger')

        elif request.form.get('action') == 'editar':
            titulo = request.form['titulo']
            conteudo = request.form['conteudo']
            artigo_id = request.form['artigo_id']
            try:
                with connection.cursor() as cur:
                    cur.execute("UPDATE artigos SET titulo = %s, conteudo = %s WHERE id = %s AND id_usuario = %s",
                                (titulo, conteudo, artigo_id, session['id_usuario']))
                    connection.commit()
                flash('Artigo editado com sucesso!', 'success')
            except Exception as e:
                flash('Erro ao editar artigo: {}'.format(e), 'danger')

        return redirect(url_for('artigos'))

    try:
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM artigos ORDER BY data_criacao DESC")
            artigos = cur.fetchall()
    finally:
        connection.close()
    return render_template('artigos.html', artigos=artigos)

@app.route('/excluir/artigo/<int:id>')
@login_obrigatorio
def excluir_artigo(id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cur:
            cur.execute("DELETE FROM artigos WHERE id = %s AND id_usuario = %s", (id, session['id_usuario']))
            connection.commit()
        flash('Artigo excluído com sucesso!', 'success')
    except Exception as e:
        flash('Erro ao excluir artigo: {}'.format(e), 'danger')
    finally:
        connection.close()
    return redirect(url_for('artigos'))

# ----------------------- Rotas para Livros -------------------------
@app.route('/livros', methods=['GET', 'POST'])
#@login_obrigatorio
def livros():
    connection = get_db_connection()
    if request.method == 'POST':
        if request.form.get('action') == 'adicionar':
            titulo = request.form['titulo']
            autor = request.form['autor']
            link = request.form['link']
            id_usuario = session['id_usuario']
            try:
                with connection.cursor() as cur:
                    cur.execute("INSERT INTO livros(titulo, autor, link, id_usuario) VALUES(%s, %s, %s, %s)",
                                (titulo, autor, link, id_usuario))
                    connection.commit()
                flash('Livro adicionado com sucesso!', 'success')
            except Exception as e:
                flash('Erro ao adicionar livro: {}'.format(e), 'danger')

        elif request.form.get('action') == 'editar':
            titulo = request.form['titulo']
            autor = request.form['autor']
            link = request.form['link']
            livro_id = request.form['livro_id']
            try:
                with connection.cursor() as cur:
                    cur.execute("UPDATE livros SET titulo = %s, autor = %s, link = %s WHERE id = %s AND id_usuario = %s",
                                (titulo, autor, link, livro_id, session['id_usuario']))
                    connection.commit()
                flash('Livro editado com sucesso!', 'success')
            except Exception as e:
                flash('Erro ao editar livro: {}'.format(e), 'danger')

        return redirect(url_for('livros'))

    try:
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM livros ORDER BY data_criacao DESC")
            livros = cur.fetchall()
    finally:
        connection.close()
    return render_template('livros.html', livros=livros)

@app.route('/excluir/livro/<int:id>')
@login_obrigatorio
def excluir_livro(id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cur:
            cur.execute("DELETE FROM livros WHERE id = %s AND id_usuario = %s", (id, session['id_usuario']))
            connection.commit()
        flash('Livro excluído com sucesso!', 'success')
    except Exception as e:
        flash('Erro ao excluir livro: {}'.format(e), 'danger')
    finally:
        connection.close()
    return redirect(url_for('livros'))

# ----------------------- Rotas para Atividades -------------------------
@app.route('/atividades', methods=['GET', 'POST'])
#@login_obrigatorio
def atividades():
    connection = get_db_connection()
    if request.method == 'POST':
        if request.form.get('action') == 'adicionar':
            titulo = request.form['titulo']
            descricao = request.form['descricao']
            data_entrega = request.form['data_entrega']
            id_usuario = session['id_usuario']
            try:
                with connection.cursor() as cur:
                    cur.execute("INSERT INTO atividades(titulo, descricao, data_entrega, id_usuario) VALUES(%s, %s, %s, %s)",
                                (titulo, descricao, data_entrega, id_usuario))
                    connection.commit()
                flash('Atividade adicionada com sucesso!', 'success')
            except Exception as e:
                flash('Erro ao adicionar atividade: {}'.format(e), 'danger')

        elif request.form.get('action') == 'editar':
            titulo = request.form['titulo']
            descricao = request.form['descricao']
            data_entrega = request.form['data_entrega']
            atividade_id = request.form['atividade_id']
            try:
                with connection.cursor() as cur:
                    cur.execute("UPDATE atividades SET titulo = %s, descricao = %s, data_entrega = %s WHERE id = %s AND id_usuario = %s",
                                (titulo, descricao, data_entrega, atividade_id, session['id_usuario']))
                    connection.commit()
                flash('Atividade editada com sucesso!', 'success')
            except Exception as e:
                flash('Erro ao editar atividade: {}'.format(e), 'danger')

        return redirect(url_for('atividades'))

    try:
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM atividades ORDER BY data_criacao DESC")
            atividades = cur.fetchall()
    finally:
        connection.close()
    return render_template('atividades.html', atividades=atividades)

@app.route('/excluir/atividade/<int:id>')
@login_obrigatorio
def excluir_atividade(id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cur:
            cur.execute("DELETE FROM atividades WHERE id = %s AND id_usuario = %s", (id, session['id_usuario']))
            connection.commit()
        flash('Atividade excluída com sucesso!', 'success')
    except Exception as e:
        flash('Erro ao excluir atividade: {}'.format(e), 'danger')
    finally:
        connection.close()
    return redirect(url_for('atividades'))


# ----------------------- Rotas para Eventos -------------------------
@app.route('/eventos', methods=['GET', 'POST'])
#@login_obrigatorio
def eventos():
    connection = get_db_connection()
    if request.method == 'POST':
        if request.form.get('action') == 'adicionar':
            titulo = request.form['titulo']
            tipo_evento = request.form['tipo_evento']
            data_evento = request.form['data_evento']
            local = request.form['local']
            publico_alvo = request.form['publico_alvo']
            resumo = request.form['resumo']
            id_usuario = session['id_usuario']
            try:
                with connection.cursor() as cur:
                    cur.execute("""
                        INSERT INTO eventos(titulo, tipo_evento, data_evento, local, 
                        publico_alvo, resumo, id_usuario) 
                        VALUES(%s, %s, %s, %s, %s, %s, %s)
                    """, (titulo, tipo_evento, data_evento, local, publico_alvo, 
                         resumo, id_usuario))
                    connection.commit()
                flash('Evento adicionado com sucesso!', 'success')
            except Exception as e:
                flash('Erro ao adicionar evento: {}'.format(e), 'danger')

        elif request.form.get('action') == 'editar':
            titulo = request.form['titulo']
            tipo_evento = request.form['tipo_evento']
            data_evento = request.form['data_evento']
            local = request.form['local']
            publico_alvo = request.form['publico_alvo']
            resumo = request.form['resumo']
            evento_id = request.form['evento_id']
            try:
                with connection.cursor() as cur:
                    cur.execute("""
                        UPDATE eventos 
                        SET titulo = %s, tipo_evento = %s, data_evento = %s, 
                            local = %s, publico_alvo = %s, resumo = %s 
                        WHERE id = %s AND id_usuario = %s
                    """, (titulo, tipo_evento, data_evento, local, publico_alvo, 
                         resumo, evento_id, session['id_usuario']))
                    connection.commit()
                flash('Evento editado com sucesso!', 'success')
            except Exception as e:
                flash('Erro ao editar evento: {}'.format(e), 'danger')

        return redirect(url_for('eventos'))

    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT eventos.*, usuarios.usuario as nome_usuario 
                FROM eventos 
                LEFT JOIN usuarios ON eventos.id_usuario = usuarios.id 
                ORDER BY data_evento ASC
            """)
            eventos = cur.fetchall()
    finally:
        connection.close()
    return render_template('eventos.html', eventos=eventos)

@app.route('/excluir/evento/<int:id>')
@login_obrigatorio
def excluir_evento(id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cur:
            cur.execute("DELETE FROM eventos WHERE id = %s AND id_usuario = %s", 
                       (id, session['id_usuario']))
            connection.commit()
        flash('Evento excluído com sucesso!', 'success')
    except Exception as e:
        flash('Erro ao excluir evento: {}'.format(e), 'danger')
    finally:
        connection.close()
    return redirect(url_for('eventos'))



# ----------------------- Rotas para Publicações -------------------------
@app.route('/publicacoes', methods=['GET', 'POST'])
#@login_obrigatorio
def publicacoes():
    connection = get_db_connection()
    if request.method == 'POST':
        if request.form.get('action') == 'adicionar':
            titulo = request.form['titulo']
            link = request.form['link']
            ano = request.form['ano']
            autor = request.form['autor']
            palavras_chave = request.form['palavras_chave']
            resumo = request.form['resumo']
            origem_publicacao = request.form['origem_publicacao']
            idioma = request.form['idioma']
            id_usuario = session['id_usuario']
            
            try:
                with connection.cursor() as cur:
                    cur.execute("""
                        INSERT INTO publicacoes(titulo, link, ano, autor, palavras_chave, 
                        resumo, origem_publicacao, idioma, id_usuario) 
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (titulo, link, ano, autor, palavras_chave, resumo, 
                         origem_publicacao, idioma, id_usuario))
                    connection.commit()
                flash('Publicação adicionada com sucesso!', 'success')
            except Exception as e:
                flash('Erro ao adicionar publicação: {}'.format(e), 'danger')

        elif request.form.get('action') == 'editar':
            titulo = request.form['titulo']
            link = request.form['link']
            ano = request.form['ano']
            autor = request.form['autor']
            palavras_chave = request.form['palavras_chave']
            resumo = request.form['resumo']
            origem_publicacao = request.form['origem_publicacao']
            idioma = request.form['idioma']
            publicacao_id = request.form['publicacao_id']
            
            try:
                with connection.cursor() as cur:
                    cur.execute("""
                        UPDATE publicacoes 
                        SET titulo = %s, link = %s, ano = %s, autor = %s, 
                            palavras_chave = %s, resumo = %s, origem_publicacao = %s, 
                            idioma = %s 
                        WHERE id = %s AND id_usuario = %s
                    """, (titulo, link, ano, autor, palavras_chave, resumo, 
                         origem_publicacao, idioma, publicacao_id, session['id_usuario']))
                    connection.commit()
                flash('Publicação editada com sucesso!', 'success')
            except Exception as e:
                flash('Erro ao editar publicação: {}'.format(e), 'danger')

        return redirect(url_for('publicacoes'))

    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT publicacoes.*, usuarios.usuario as nome_usuario 
                FROM publicacoes 
                LEFT JOIN usuarios ON publicacoes.id_usuario = usuarios.id 
                ORDER BY ano DESC, titulo ASC
            """)
            publicacoes = cur.fetchall()
    finally:
        connection.close()
    return render_template('publicacoes.html', publicacoes=publicacoes)

@app.route('/excluir/publicacao/<int:id>')
@login_obrigatorio
def excluir_publicacao(id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cur:
            cur.execute("DELETE FROM publicacoes WHERE id = %s AND id_usuario = %s", 
                       (id, session['id_usuario']))
            connection.commit()
        flash('Publicação excluída com sucesso!', 'success')
    except Exception as e:
        flash('Erro ao excluir publicação: {}'.format(e), 'danger')
    finally:
        connection.close()
    return redirect(url_for('publicacoes'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
