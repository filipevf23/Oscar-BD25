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
    if id != 11 and id%10 == 1:
        suffix = 'ST'
    elif id != 12 and id%10 == 2:
        suffix = 'ND'
    elif id != 13 and id%10 == 3:
        suffix = 'RD'
    else:
        suffix = 'TH'
    return render_template('cerimonia.html', cerimonia=cerimonia, id=id, suffix=suffix, ano=ano )

@APP.route('/categorias/')
def categorias():
    aux = db.execute(
        """
        SELECT cat.categoria_canonica,  cat.classe, GROUP_CONCAT(DISTINCT ca.categoria), MIN(cer.ano) AS ano, ca.cerimonia_id, cat.categoria_id
        FROM cerimonia as cer
        JOIN categoria_ano as ca on ca.cerimonia_id = cer.cerimonia_id
        JOIN categoria as cat on cat.categoria_id = ca.categoria_id
        GROUP BY cat.categoria_canonica, cat.classe
        ORDER BY ano 
        """
    ).fetchall()
    categorias = []
    for row in aux:
        categorias.append({'canonica':row[0], 'classe':row[1], 'nomes':row[2].split(","), 'ano':row[3], 'cerimonia_id':row[4], 'categoria_id':row[5]})
    return render_template('categorias.html', categorias=categorias)

@APP.route('/categoria-ano/<int:id>')
def categoria_ano(id):
    nomeacoes = db.execute(
        """
        SELECT cat.categoria_canonica, ca.categoria, f.nome AS filme_nome, ne.nome, ca.categoria_ano_id, cer.ano, cer.cerimonia_id, cat.categoria_id
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
    ano = ganhador['ano']
    if id != 11 and id%10 == 1:
        suffix = 'ST'
    elif id != 12 and id%10 == 2:
        suffix = 'ND'
    elif id != 13 and id%10 == 3:
        suffix = 'RD'
    else:
        suffix = 'TH'
    return render_template('categoria_ano.html', ganhador=ganhador, nomeacoes=nomeacoes, suffix=suffix)

@APP.route('/filmes/')
def filmes():
    filmes = db.execute("""
        select f.nome as nome,f.filme_id as fid,c.cerimonia_id as id,c.ano as ano,count(ano.categoria) as nomeacoes
        from filme f
        join nomeacao n on n.filme_id=f.filme_id
        join categoria_ano ano on ano.categoria_ano_id=n.categoria_ano_id
        join cerimonia c on c.cerimonia_id=ano.cerimonia_id
        Group by f.nome
        Order by c.cerimonia_id,nomeacoes desc;
        """).fetchall()
    return render_template('/filmes.html', filmes=filmes)

@APP.route('/filmes/<id>/')
def filme(id):
    filme = db.execute(""" 
        select f.nome as nome,c.cerimonia_id as cerimonia_id,c.ano as ano,ano.categoria as categoria,
                       p.nome as nomeado,n.ganhou as ganhou,ano.categoria_ano_id as categoria_ano_id,
                       p.nomeado_id as nomeado_id
        from filme f
        join nomeacao n on n.filme_id=f.filme_id
        join categoria_ano ano on ano.categoria_ano_id=n.categoria_ano_id
        join cerimonia c on c.cerimonia_id=ano.cerimonia_id
        join concorre con on con.nomeacao_id=n.nomeacao_id
        join nomeado p on p.nomeado_id=con.nomeado_id
        where f.filme_id = ?
        Order by n.ganhou;
        """,(id,)).fetchall()
    fnome = filme[0]['nome']
    cerimonia = filme[0]['cerimonia_id']
    ano = filme[0]['ano']
    if cerimonia != 11 and cerimonia%10 == 1:
        suffix = 'ST'
    elif cerimonia != 12 and cerimonia%10 == 2:
        suffix = 'ND'
    elif cerimonia != 13 and cerimonia%10 == 3:
        suffix = 'RD'
    else:
        suffix = 'TH'
    return render_template('filme.html',filme=filme,fnome=fnome,ano=ano,cerimonia=cerimonia, suffix=suffix)


@APP.route('/nomeados/')
def nomeados():
    nomeados = db.execute(
        """
        SELECT n.nomeado_id, n.nome 
        FROM nomeado AS n
        """
    ).fetchall()
    ids = []
    nomes = []
    for n in nomeados:
        ids.append(n[0].split(','))
        nomes.append(n[1].split(','))
    return render_template('nomeados.html', nomeados=nomeados, ids=ids, nomes=nomes)

@APP.route('/nomeados/<id>')
def nomeado(id):
    nomeado = db.execute(
        """
        SELECT n.nomeado_id, n.nome 
        FROM nomeado AS n
        WHERE n.nomeado_id = ?
        """
        , (id,) ).fetchone()
    nomeacoes = db.execute(
        """
        SELECT ca.categoria, ca.categoria_ano_id, f.nome AS filme_nome, f.filme_id, cer.ano, cer.cerimonia_id
        FROM nomeacao AS n
        JOIN categoria_ano AS ca ON ca.categoria_ano_id = n.categoria_ano_id
        JOIN cerimonia AS cer ON cer.cerimonia_id = ca.cerimonia_id
        JOIN concorre AS co ON co.nomeacao_id = n.nomeacao_id
        JOIN nomeado AS nom ON nom.nomeado_id = co.nomeado_id
        JOIN filme AS f ON f.filme_id = n.filme_id
        WHERE nom.nomeado_id = ?
        """
        , (id,) ).fetchall()

    return render_template('nomeado.html', nomeado=nomeado, nomeacoes=nomeacoes)

@APP.route('/paises/')
def paises():
    aux = db.execute("""
        with vit as (
        select no.nome as Pais,ca.cerimonia_id as id, count(f.nome) as Vitorias
        from nomeacao no 
        join categoria_ano ca on ca.categoria_ano_id=no.categoria_ano_id
        join categoria c on c.categoria_id=ca.categoria_id
        join filme f on f.filme_id = no.filme_id
        where c.categoria_id= 46 and no.nome != 'nan' and no.ganhou = '1.0'
        Group by no.nome 
        Order by vitorias desc
        )
        select no.nome as Pais, count(f.nome) as Nomeacoes, coalesce(vitorias,0) as vitorias
        from nomeacao no 
        join categoria_ano ca on ca.categoria_ano_id=no.categoria_ano_id
        join categoria c on c.categoria_id=ca.categoria_id
        join filme f on f.filme_id = no.filme_id
        left join vit on vit.Pais = no.nome
        where c.categoria_id= 46 and no.nome != 'nan'
        Group by no.nome 
        Order by vitorias DESC, Nomeacoes DESC;
        """).fetchall()
    auxList = []
    for p in aux:
        auxList.append({'Pais':p[0], 'Nomeacoes':p[1], 'vitorias':p[2]})
    paises = []
    for p in auxList:
        if p['Pais'] == 'Federal Republic of Germany - West; Gyula Trebitsch and Walter Koppel, Producers':
            paises.append({'Pais':'Federal Republic of Germany - West', 
                           'Nomeacoes':p['Nomeacoes'],
                           'vitorias':p['vitorias']})
        elif len(paises) == 0 or "Czech" in p['Pais'] or "German" in p['Pais']:
            paises.append(p)
        else:
            exists = False
            for w in (p['Pais'].split(' ') + p['Pais'].split(';')):
                for i in range(len(paises)):
                    if w in paises[i]['Pais']:
                        exists = True
                        paises[i]['Nomeacoes'] += p['Nomeacoes']
                        paises[i]['vitorias'] += p['vitorias']
                        break
                if exists: break
            if not exists:
                paises.append(p)
    return render_template('paises.html',paises = paises)

@APP.route('/paises/<id>')
def pais(id):
    pais = db.execute("""
        select no.nome as Pais, f.nome as Filme, f.filme_id as filme_id,
                       cerimonia.ano as ano, no.ganhou as ganhou, cerimonia.cerimonia_id as cerimonia_id
        from nomeacao no 
        join categoria_ano ca on ca.categoria_ano_id=no.categoria_ano_id
        join categoria c on c.categoria_id=ca.categoria_id
        join filme f on f.filme_id = no.filme_id
        join cerimonia on cerimonia.cerimonia_id = ca.cerimonia_id
        where c.categoria_id = 46 and no.nome = ?
        Order by cerimonia.cerimonia_id;
        """,(id,)).fetchall()
    nome = pais[0]['Pais']
    return render_template('pais.html',pais = pais,nome=nome)

@APP.route('/categorias/<int:id>')
def categoria(id):
    categoria = db.execute(
        """
        SELECT c.categoria_id, c.categoria_canonica, ca.categoria, c.classe, ca.categoria_ano_id, cer.ano
        FROM categoria AS c
        JOIN categoria_ano AS ca ON ca.categoria_id = c.categoria_id
        JOIN cerimonia AS cer ON cer.cerimonia_id = ca.cerimonia_id
        WHERE c.categoria_id = ?
        ORDER BY cer.cerimonia_id ASC
        """
    , (id,)).fetchall()
    return render_template('categoria.html', categoria=categoria)