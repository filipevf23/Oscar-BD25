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

        SELECT cer.cerimonia_id as cerimonia, cer.ano, COUNT(ca.categoria) as categorias, t1.nomeacoes as nomeacoes
        FROM cerimonia as cer
        JOIN categoria_ano as ca on ca.cerimonia_id = cer.cerimonia_id
        JOIN t1 on t1.ano = cer.ano
        GROUP BY cer.cerimonia_id, cer.ano 
        """
    ).fetchall()
    return render_template('/cerimonias.html', cerimonias=cerimonias)