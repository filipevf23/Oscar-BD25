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
    aux = db.execute(
        """
        SELECT DISTINCT ca.categoria_ano_id, no.nomeado_id, no.nome, f.filme_id, f.nome as filme_nome
        FROM nomeacao n
        JOIN concorre c on c.nomeacao_id = n.nomeacao_id
        JOIN nomeado no on no.nomeado_id = c.nomeado_id
        JOIN filme f on f.filme_id = n.filme_id
        JOIN categoria_ano ca ON ca.categoria_ano_id = n.categoria_ano_id
        WHERE ca.cerimonia_id = ?
        AND n.ganhou = '1.0'
        """
    , (id,)).fetchall()
    cerimonia = db.execute(
        """
        SELECT DISTINCT cer.cerimonia_id, cer.ano, ca.categoria, n.nome, ca.categoria_ano_id
        FROM cerimonia AS cer
        JOIN categoria_ano AS ca ON ca.cerimonia_id = cer.cerimonia_id
        JOIN nomeacao AS n ON n.categoria_ano_id = ca.categoria_ano_id
        WHERE n.ganhou = '1.0'
        AND cer.cerimonia_id = ?
        ORDER BY ca.categoria
        """
        , (id,)
    ).fetchall()
    ano = cerimonia[0]['ano']
    nomeados = []
    for row in cerimonia:
        aux1 = []
        aux2 = []
        aux3 = []
        aux4 = []
        for r in aux:
            if r['categoria_ano_id'] == row['categoria_ano_id']:
                if r['nomeado_id'] not in aux1 and r['nome'] not in aux2:
                    aux1.append(r['nomeado_id'])
                    aux2.append(r['nome'])
                aux3.append(r['filme_id'])
                aux4.append(r['filme_nome'])
        nomeados.append({'nomeados_id':aux1, 'nomes':aux2, 'filmes_id':aux3, 'filme_nomes':aux4})
    for i in nomeados:
        print(i)
    suffix = getSuffix(id)
    return render_template('cerimonia.html', cerimonia=cerimonia, nomeados=nomeados, id=id, suffix=suffix, ano=ano )

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

@APP.route('/categorias/<int:id>')
def categoria(id):
    categoria = db.execute(
        """
        SELECT c.categoria_id, c.categoria_canonica, ca.categoria, c.classe, ca.categoria_ano_id, cer.cerimonia_id, cer.ano
        FROM categoria AS c
        JOIN categoria_ano AS ca ON ca.categoria_id = c.categoria_id
        JOIN cerimonia AS cer ON cer.cerimonia_id = ca.cerimonia_id
        WHERE c.categoria_id = ?
        ORDER BY cer.cerimonia_id ASC
        """
    , (id,)).fetchall()
    categoria_canonica = categoria[0]['categoria_canonica']
    ano = categoria[0]['ano']
    classe = categoria[0]['classe']
    return render_template('categoria.html', categoria=categoria, categoria_canonica=categoria_canonica, classe=classe, ano=ano)

@APP.route('/categorias-ano/')
def categorias_ano():
    categorias_ano = db.execute(
        """
        SELECT cat.categoria_canonica, ca.categoria, ca.categoria_ano_id, cer.cerimonia_id, cat.categoria_id
        FROM cerimonia as cer
        JOIN categoria_ano as ca on ca.cerimonia_id = cer.cerimonia_id
        JOIN categoria as cat on cat.categoria_id = ca.categoria_id
        ORDER BY cer.cerimonia_id DESC, ca.categoria ASC
        """
    ).fetchall()
    suffixes = [getSuffix(row['cerimonia_id']) for row in categorias_ano]
    return render_template('categorias_ano.html', categorias_ano=categorias_ano, suffixes=suffixes)

@APP.route('/categorias-ano/<int:id>')
def categoria_ano(id):
    aux = db.execute(
        """
        SELECT n.nomeacao_id, no.nomeado_id, no.nome
        FROM nomeacao n
        JOIN concorre c on c.nomeacao_id = n.nomeacao_id
        JOIN nomeado no on no.nomeado_id = c.nomeado_id
        WHERE n.categoria_ano_id = ?
        """
    , (id,)).fetchall()
    nomeacoes = db.execute(
        """
        SELECT cat.categoria_canonica, ca.categoria, n.nomeacao_id, f.filme_id, f.nome AS filme_nome, 
                n.nome, ca.categoria_ano_id, cer.ano, cer.cerimonia_id, cat.categoria_id
        FROM cerimonia as cer
        JOIN categoria_ano as ca on ca.cerimonia_id = cer.cerimonia_id
        JOIN categoria as cat on cat.categoria_id = ca.categoria_id
        JOIN nomeacao as n on n.categoria_ano_id = ca.categoria_ano_id
        LEFT JOIN filme as f on f.filme_id = n.filme_id
        WHERE ca.categoria_ano_id = ?
        ORDER BY n.ganhou
        """
        , (id,)
    ).fetchall()
    ganhador = db.execute(
        """
        SELECT cat.categoria_canonica, ca.categoria, n.nomeacao_id, f.filme_id, f.nome AS filme_nome, 
                n.nome, ca.categoria_ano_id, cer.ano, cer.cerimonia_id, cat.categoria_id
        FROM cerimonia as cer
        JOIN categoria_ano as ca on ca.cerimonia_id = cer.cerimonia_id
        JOIN categoria as cat on cat.categoria_id = ca.categoria_id
        JOIN nomeacao as n on n.categoria_ano_id = ca.categoria_ano_id
        LEFT JOIN filme as f on f.filme_id = n.filme_id
        WHERE ca.categoria_ano_id = ?
        AND ganhou = '1.0'
        ORDER BY n.ganhou
        """
        , (id,)
    ).fetchall()
    nomeados = []
    for row in nomeacoes:
        aux1 = []
        aux2 = []
        for r in aux:
            if r['nomeacao_id'] == row['nomeacao_id']:
                aux1.append(r['nomeado_id'])
                aux2.append(r['nome'])
        nomeados.append({'nomeados_id':aux1, 'nomes':aux2})
    suffix = getSuffix(nomeacoes[0]['cerimonia_id'])
    return render_template('categoria_ano.html', ganhador=ganhador, nomeados=nomeados, nomeacoes=nomeacoes, suffix=suffix)

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
    aux = db.execute(
        """
        SELECT f.filme_id, no.nomeado_id, no.nome
        FROM nomeacao n
        JOIN concorre c on c.nomeacao_id = n.nomeacao_id
        JOIN nomeado no on no.nomeado_id = c.nomeado_id
        JOIN filme as f on f.filme_id = n.filme_id
        WHERE f.filme_id = ?
        """
    , (id,)).fetchall()
    filme = db.execute(""" 
        select f.nome as filme_nome, f.filme_id, c.cerimonia_id as cerimonia_id, c.ano as ano,ano.categoria as categoria,
                       n.ganhou as ganhou,ano.categoria_ano_id as categoria_ano_id, n.nome
        from filme f
        join nomeacao n on n.filme_id=f.filme_id
        join categoria_ano ano on ano.categoria_ano_id=n.categoria_ano_id
        join cerimonia c on c.cerimonia_id=ano.cerimonia_id
        where f.filme_id = ?
        Order by n.ganhou;
        """,(id,)).fetchall()
    fnome = filme[0]['filme_nome']
    cerimonia = filme[0]['cerimonia_id']
    nomeados = []
    for row in filme:
        aux1 = []
        aux2 = []
        for r in aux:
            if r['filme_id'] == row['filme_id']:
                aux1.append(r['nomeado_id'])
                aux2.append(r['nome'])
        nomeados.append({'nomeados_id':aux1, 'nomes':aux2})
    ano = filme[0]['ano']
    suffix = getSuffix(cerimonia)
    return render_template('filme.html',filme=filme,fnome=fnome, nomeados=nomeados, ano=ano,cerimonia=cerimonia, suffix=suffix)


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
        SELECT n.nomeacao_id, ca.categoria, ca.categoria_ano_id, f.nome AS filme_nome, f.filme_id, cer.ano, cer.cerimonia_id
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

@APP.route('/concorre/')
def concorre():
    aux = db.execute(
        """
        SELECT c.nomeacao_id, c.nomeado_id
        FROM concorre AS c
        ORDER BY c.nomeacao_id DESC
        """
    ).fetchall()
    concorre = [{'nomeacao_id':x, 'nomeado_id':y, 'nomeado_id_list':y.split(',')} for x,y in aux]
    return render_template('concorre.html', concorre=concorre)

@APP.route('/nomeacoes/<id>')
def nomeacao(id):
    nomeacao = db.execute(
        """
        SELECT n.nomeacao_id, n.categoria_ano_id, ca.categoria, no.nomeado_id, f.nome as filme_nome, n.filme_id, n.nome, n.ganhou, n.nota, n.detalhe, n.citation, n.multi_filme
        FROM nomeacao AS n
        LEFT JOIN concorre AS c ON c.nomeacao_id = n.nomeacao_id
        LEFT JOIN nomeado AS no ON no.nomeado_id = c.nomeado_id
        JOIN filme AS f ON f.filme_id = n.filme_id
        JOIN categoria_ano AS ca ON ca.categoria_ano_id = n.categoria_ano_id
        WHERE n.nomeacao_id = ?
        """
    , (id,)).fetchall()
    nomes = getNomes(nomeacao[0]['nome'])
    temNome = nomeacao[0]['nome'] != 'nan'
    temProjeto = nomeacao[0]['filme_id'] != 'nan'
    temNota = nomeacao[0]['nota'] != 'nan'
    temDetalhe = nomeacao[0]['detalhe'] != 'nan'
    temCitation = nomeacao[0]['citation'] != 'nan'
    temMultiFilme = nomeacao[0]['multi_filme'] != 'nan'
    return render_template('nomeacao.html', nomeacao=nomeacao, nomes=nomes, temNome=temNome, temProjeto=temProjeto, temNota=temNota, temDetalhe=temDetalhe, temCitation=temCitation, temMultiFilme=temMultiFilme)

@APP.route('/nomeacoes/')
def nomeacoes():
    nomeacoes = db.execute(
        """
        SELECT n.nomeacao_id, n.categoria_ano_id, ca.categoria, GROUP_CONCAT(no.nomeado_id) as nomeados_id, n.filme_id, f.nome AS filme_nome, n.nome, n.ganhou
        FROM nomeacao AS n
        JOIN concorre AS c ON c.nomeacao_id = n.nomeacao_id
        JOIN nomeado AS no ON no.nomeado_id = c.nomeado_id
        JOIN filme AS f ON f.filme_id = n.filme_id
        JOIN categoria_ano AS ca ON ca.categoria_ano_id = n.categoria_ano_id
        GROUP BY n.nomeacao_id
        ORDER BY ca.cerimonia_id ASC
        """
    ).fetchall()
    nomeados_id = [row['nomeados_id'].split(',') for row in nomeacoes]
    nomeados = [row['nome'].split(', ') for row in nomeacoes]
    return render_template('nomeacoes.html', nomeacoes=nomeacoes, nomeados_id=nomeados_id, nomeados=nomeados)

# ===================================================
#               QUESTÕES SQL
# ===================================================

@APP.route('/paises-mais-premiados/')
def paises_mais_premiados():
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
    return render_template('paises-mais-premiados.html',paises = paises)

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

@APP.route('/filmes-mais-premiados/')
def filmes_mais_premiados():
    filmes = db.execute(
        """
        WITH t1 AS (
            SELECT f.filme_id as filme_id, COUNT(n.filme_id) as vitorias
            FROM filme AS f 
            JOIN nomeacao AS n ON n.filme_id = f.filme_id
            WHERE n.ganhou = '1.0'
            GROUP BY f.filme_id
        )
        SELECT f.filme_id, f.nome, t1.vitorias, COUNT(n.filme_id) AS nomeacoes
        FROM filme AS f 
        JOIN nomeacao AS n ON n.filme_id = f.filme_id
        JOIN t1 ON t1.filme_id = f.filme_id
        GROUP BY f.filme_id, f.nome, t1.vitorias
        HAVING t1.vitorias > 1
        ORDER BY t1.vitorias DESC, nomeacoes DESC
        """
    ).fetchall()
    return render_template('filmes-mais-premiados.html', filmes=filmes)

@APP.route('/filmes-perfeitos/')
def filmes_perfeitos():
    filmes = db.execute(
        """
        WITH t1 AS (
            SELECT f.filme_id as filme_id, COUNT(n.filme_id) as vitorias
            FROM filme AS f 
            JOIN nomeacao AS n ON n.filme_id = f.filme_id
            WHERE n.ganhou = '1.0'
            GROUP BY f.filme_id
        )
        SELECT f.filme_id, f.nome, t1.vitorias, COUNT(n.filme_id) AS nomeacoes
        FROM filme AS f 
        JOIN nomeacao AS n ON n.filme_id = f.filme_id
        JOIN t1 ON t1.filme_id = f.filme_id
        GROUP BY f.filme_id, f.nome, t1.vitorias
        HAVING t1.vitorias = nomeacoes AND nomeacoes > 2
        ORDER BY t1.vitorias DESC, nomeacoes DESC
        """
    ).fetchall()
    return render_template('filmes-perfeitos.html', filmes=filmes)

@APP.route('/empresas-mais-nomeadas/')
def empresas_mais_nomeadas():
    empresas = db.execute(
        """
        with vitorias as (
            SELECT no.nomeado_id as id, COUNT(*) AS vit
            FROM concorre c
                JOIN nomeado no ON no.nomeado_id = c.nomeado_id
                join nomeacao m on m.nomeacao_id=c.nomeacao_id
                where c.nomeado_id like 'co%'
                AND m.ganhou = '1.0'
                GROUP BY id
        )

        SELECT no.nome, COUNT(*) AS nomeacoes, v.vit, no.nomeado_id as id
        FROM concorre c
        JOIN nomeado no ON no.nomeado_id = c.nomeado_id
        JOIN nomeacao m on m.nomeacao_id=c.nomeacao_id
        JOIN vitorias as v on v.id = no.nomeado_id
        where c.nomeado_id like 'co%'
        GROUP BY no.nomeado_id
        ORDER BY nomeacoes DESC, vit DESC
        Limit 20;
        """
    ).fetchall()
    return render_template('empresas-mais-nomeadas.html', empresas=empresas)

@APP.route('/taxa-de-vitoria/')
def taxa_de_vitoria():
    nomeados = db.execute(
        """
        with vitorias as (
            SELECT no.nomeado_id as id, COUNT(*) AS vit
            FROM concorre c
                JOIN nomeado no ON no.nomeado_id = c.nomeado_id
                join nomeacao m on m.nomeacao_id=c.nomeacao_id
                AND m.ganhou = '1.0'
                GROUP BY id
        )

        SELECT no.nome, COUNT(*) AS nomeacoes, v.vit, no.nomeado_id as id, ROUND(v.vit*1.0/COUNT(*) * 100) as taxa_vitoria
        FROM concorre c
        JOIN nomeado no ON no.nomeado_id = c.nomeado_id
        JOIN nomeacao m on m.nomeacao_id=c.nomeacao_id
        JOIN vitorias as v on v.id = no.nomeado_id
        GROUP BY no.nomeado_id
        ORDER BY vit DESC, nomeacoes DESC
        Limit 20;
        """
    ).fetchall()
    return render_template('taxa-de-vitoria.html', nomeados=nomeados)

@APP.route('/nomes-mais-comuns/')
def nomes_mais_comuns():
    nomes = db.execute(
        """
        WITH empresas AS (
            SELECT DISTINCT 
                TRIM(SUBSTR(n.nome, 1,
                            CASE WHEN INSTR(n.nome,' ') = 0 THEN LENGTH(n.nome)
                                    ELSE INSTR(n.nome,' ') - 1 END)) AS nome
            FROM nomeado n 
            WHERE n.nomeado_id LIKE 'co%'
        ), 
        semdoutores as (
        SELECT lower(TRIM(REPLACE(REPLACE(n.nome,'Dr. ', ''), 'DR. ', ''))) as nome
            FROM nomeado n
        )

        SELECT DISTINCT 
            lower(TRIM(SUBSTR(n.nome, 1,
                        CASE WHEN INSTR(n.nome,' ') = 0 THEN LENGTH(n.nome)
                                ELSE INSTR(n.nome,' ') - 1 END))) AS pnome,
            COUNT(*) AS vezes
        FROM semdoutores n
        WHERE lower(TRIM(SUBSTR(n.nome, 1,
                        CASE WHEN INSTR(n.nome,' ') = 0 THEN LENGTH(n.nome)
                                ELSE INSTR(n.nome,' ') - 1 END)))
            NOT IN (SELECT nome FROM empresas)
        GROUP BY pnome
        ORDER BY vezes DESC
        LIMIT 20;
        """
    ).fetchall()
    return render_template('nomes-mais-comuns.html', nomes=nomes)

@APP.route('/filmes-mais-esnobados/')
def filmes_mais_esnobados():
    filmes = db.execute(
        """
        WITH t1 AS (
            SELECT f.filme_id as filme_id, COUNT(n.filme_id) as vitorias
            FROM filme AS f 
            JOIN nomeacao AS n ON n.filme_id = f.filme_id
            WHERE n.ganhou = '1.0'
            GROUP BY f.filme_id
        )
        
        SELECT f.filme_id, f.nome, COALESCE(t1.vitorias,0) as vitorias, COUNT(n.filme_id) AS nomeacoes,
        (COUNT(n.filme_id) -  COALESCE(t1.vitorias,0)) as esnobada
        FROM filme AS f 
        JOIN nomeacao AS n ON n.filme_id = f.filme_id
        Left JOIN t1 ON t1.filme_id = f.filme_id
        GROUP BY f.filme_id, f.nome
        ORDER BY esnobada desc, nomeacoes desc
        Limit 50;
        """
    ).fetchall()
    return render_template('filmes-mais-esnobados.html', filmes=filmes)

@APP.route("/mais-vitorias-variadas/")
def mais_vitorias_variadas():
    entidades = db.execute(
        """
        WITH t1 AS (
            SELECT DISTINCT no.nomeado_id AS nomeado_id, cat.categoria_id AS categoria_id
            FROM nomeado AS no
            LEFT JOIN concorre AS c ON c.nomeado_id = no.nomeado_id
            JOIN nomeacao AS n ON n.nomeacao_id = c.nomeacao_id
            JOIN categoria_ano AS ca ON ca.categoria_ano_id = n.categoria_ano_id
            JOIN categoria AS cat ON cat.categoria_id = ca.categoria_id
            WHERE n.ganhou = '1.0'
            ORDER BY no.nome
        )

        SELECT no.nome, no.nomeado_id AS id, COUNT(no.nomeado_id) AS vitorias_distintas
        FROM nomeado AS no
        JOIN t1 ON no.nomeado_id = t1.nomeado_id
        GROUP BY no.nome
        ORDER BY vitorias_distintas DESC, no.nome ASC 
        LIMIT 20
        """
    ).fetchall()
    return render_template('mais-vitorias-variadas.html', entidades=entidades)

@APP.route('/maior-menor/')
def maior_menor():
    nomes = db.execute(
        """ 
        WITH longo AS (
            SELECT  f.nome AS filme_longo,
                f.filme_id as filme_longo_id,
                LENGTH(f.nome) AS tamanho_longo,
                ROW_NUMBER() OVER (ORDER BY LENGTH(f.nome) DESC) AS rn
            FROM filme f
            LIMIT 10
        ),
        curto AS (
            SELECT f.nome AS filme_curto,
            f.filme_id as filme_curto_id,
                LENGTH(f.nome) AS tamanho_curto,
                ROW_NUMBER() OVER (ORDER BY LENGTH(f.nome) ASC) AS rn
            FROM filme f
            LIMIT 10
        )
        SELECT l.filme_longo, l.filme_longo_id,c.filme_curto_id , l.tamanho_longo, c.filme_curto, c.tamanho_curto
        FROM longo l
        JOIN curto c ON l.rn = c.rn
        ORDER BY l.rn;
        """
    ).fetchall()
    return render_template('maior-menor.html', nomes=nomes)

@APP.route('/smiths/')
def smiths():
    smiths = db.execute(
        """
        SELECT n.nome, ce.cerimonia_id
        FROM nomeado n
        JOIN concorre c ON n.nomeado_id = c.nomeado_id
        JOIN nomeacao na ON c.nomeacao_id = na.nomeacao_id
        JOIN categoria_ano ca ON na.categoria_ano_id = ca.categoria_ano_id
        JOIN cerimonia ce ON ca.cerimonia_id = ce.cerimonia_id
        WHERE n.nome LIKE '%Smith%' and ce.cerimonia_id BETWEEN 20 and 35;
        """
    ).fetchall()
    suffix = [getSuffix(row['cerimonia_id']) for row in smiths]
    return render_template('smiths.html', smiths=smiths, suffix=suffix)

# ======================================
# FUNÇÕES AUXILIARES
# ======================================

def getSuffix(ordNumber: int):
    if ordNumber != 11 and ordNumber%10 == 1:
        return 'ST'
    elif ordNumber != 12 and ordNumber%10 == 2:
        return 'ND'
    elif ordNumber != 13 and ordNumber%10 == 3:
        return 'RD'
    return 'TH'

def getNomes(s: str):
    if ', ' in s:
        nomes = s.split(', ')
    elif '; ' in s:
        nomes = s.split('; ')
    else: nomes = [s]
    for i in range(len(nomes)):
        if ' and ' in nomes[i]:
            nomes.insert(i+1,nomes[i].split(' and ')[1])
            nomes[i] = nomes[i].split(' and ')[0]
    for i in range(len(nomes)):
        if ': ' in nomes[i]: 
            nomes[i] = nomes[i][nomes[i].find(': ')+2:]

    return nomes
