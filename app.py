import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():

    return render_template('index.html')

@APP.route('/cerimonias/')
def cerimonias():
    cerimonias = db.execute(
        """
        with t1 as (
            SELECT cer.ano as ano, COUNT(ca.categoria) as nomeacoes
            FROM cerimonia as cer
            JOIN categoria_ano as ca on ca.cerimonia_id = cer.cerimonia_id
            JOIN nomeacao as n on n.categoria_ano_id = ca.categoria_ano_id
            GROUP BY cer.ano
        )

        SELECT cer.cerimonia_id, cer.ano, COUNT(ca.categoria) as categorias, t1.nomeacoes as nomeacoes
        FROM cerimonia as cer
        JOIN categoria_ano as ca on ca.cerimonia_id = cer.cerimonia_id
        JOIN t1 on t1.ano = cer.ano
        GROUP BY cer.cerimonia_id, cer.ano 
        ORDER BY cer.cerimonia_id DESC
        """
    ).fetchall()
    return render_template('/cerimonias.html', cerimonias=cerimonias)

@APP.route('/cerimonia/<int:id>/')
def cerimonia(id):
    cerimonia = db.execute(
        """
        SELECT cer.cerimonia_id, cer.ano, ca.categoria, f.nome AS filme_nome, ne.nome, ca.categoria_ano_id
        FROM cerimonia AS cer
        JOIN categoria_ano AS ca ON ca.cerimonia_id = cer.cerimonia_id
        JOIN nomeacao AS n ON n.categoria_ano_id = ca.categoria_ano_id
        JOIN filme AS f ON f.filme_id = n.filme_id
        JOIN concorre AS conc ON conc.nomeacao_id = n.nomeacao_id
        JOIN nomeado AS ne ON ne.nomeado_id = conc.nomeado_id
        WHERE n.ganhou = '1.0'
        AND cer.cerimonia_id = ?
        """
        , (id,)
    ).fetchall()
    ano = cerimonia[0]['ano']
    return render_template('cerimonia.html', cerimonia=cerimonia, id=id, ano=ano )

@APP.route('/cerimonia/categoria/<int:id>')
def categoria(id):
    nomeacoes = db.execute(
        """
        SELECT cat.categoria_canonica, ca.categoria, f.nome AS filme_nome, ne.nome, ca.categoria_ano_id, cer.ano, cer.cerimonia_id
        FROM cerimonia as cer
        JOIN categoria_ano as ca on ca.cerimonia_id = cer.cerimonia_id
        JOIN categoria as cat on cat.categoria_id = ca.categoria_id
        JOIN nomeacao as n on n.categoria_ano_id = ca.categoria_ano_id
        JOIN filme as f on f.filme_id = n.filme_id
        JOIN concorre as conc on conc.nomeacao_id = n.nomeacao_id
        JOIN nomeado as ne on ne.nomeado_id = conc.nomeado_id
        WHERE ca.categoria_ano_id = ?
        ORDER BY n.ganhou
        """
        , (id,)
    ).fetchall()
    ganhador = nomeacoes[0]
    return render_template('categoria.html', ganhador=ganhador, nomeacoes=nomeacoes)

