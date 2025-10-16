from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from functools import wraps
import pandas as pd
import numpy as np
import oracledb
import config
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(config.Config)

# Configurar Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")
else:
    gemini_model = None

def get_connection():
    return oracledb.connect(
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        dsn=app.config['DB_DSN'],
        wallet_location=app.config['WALLET_LOCATION'],
        wallet_password=app.config['WALLET_PASSWORD']
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Por favor, inicia sesión para acceder.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if (username == app.config['LOGIN_USERNAME'] and 
            password == app.config['LOGIN_PASSWORD']):
            session['logged_in'] = True
            session['username'] = username
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT nombre_comunidad FROM COMUNIDADES ORDER BY nombre_comunidad')
        comunidades = [row[0] for row in cursor.fetchall()]
        
        cursor.execute('SELECT DISTINCT sexo FROM INGRESOS WHERE sexo IS NOT NULL ORDER BY sexo')
        sexos = [row[0] for row in cursor.fetchall()]
        
        cursor.execute('SELECT nombre_categoria FROM CATEGORIAS_DIAGNOSTICO ORDER BY nombre_categoria')
        categorias = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return render_template('index.html', comunidades=comunidades, sexos=sexos, categorias=categorias)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/api/data')
@login_required
def get_data():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM VISTA_DASHBOARD WHERE 1=1'
        params = []
        
        comunidad = request.args.get('comunidad')
        if comunidad:
            query += ' AND comunidad_atencion = :1'
            params.append(comunidad)
        
        sexo = request.args.get('sexo')
        if sexo:
            query += f' AND sexo = :{len(params) + 1}'
            params.append(sexo)
        
        categoria = request.args.get('categoria')
        if categoria:
            query += f' AND categoria_diagnostico = :{len(params) + 1}'
            params.append(categoria)
        
        fecha_inicio = request.args.get('fecha_inicio')
        if fecha_inicio:
            query += f' AND fecha_ingreso >= :{len(params) + 1}'
            params.append(fecha_inicio)
        
        fecha_fin = request.args.get('fecha_fin')
        if fecha_fin:
            query += f' AND fecha_ingreso <= :{len(params) + 1}'
            params.append(fecha_fin)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=columns)
        
        cursor.close()
        conn.close()
        
        if df.empty:
            return jsonify({'error': 'No se encontraron datos con los filtros seleccionados'})
        
        # Valores por defecto
        pacientes_uci = 0
        dias_uci_promedio = 0
        ingresos_uci_dict = {}
        
        # Calcular UCI
        if 'DIAS_UCI' in df.columns:
            df['DIAS_UCI_NUM'] = pd.to_numeric(df['DIAS_UCI'], errors='coerce')
            df_con_uci = df[df['DIAS_UCI_NUM'] > 0]
            pacientes_uci = len(df_con_uci)
            
            if pacientes_uci > 0:
                dias_uci_promedio = float(df_con_uci['DIAS_UCI_NUM'].mean())
                if pd.isna(dias_uci_promedio):
                    dias_uci_promedio = 0
            
            sin_uci = len(df) - pacientes_uci
            ingresos_uci_dict = {'Sin UCI': sin_uci, 'Con UCI': pacientes_uci}
        
        # Estancia promedio
        estancia_promedio = 0
        if 'ESTANCIA_DIAS' in df.columns:
            estancia = pd.to_numeric(df['ESTANCIA_DIAS'], errors='coerce')
            estancia_promedio = float(estancia.mean())
            if pd.isna(estancia_promedio):
                estancia_promedio = 0
        
        # Coste total
        coste_total = 0
        if 'COSTE_APR' in df.columns:
            coste = pd.to_numeric(df['COSTE_APR'], errors='coerce')
            coste_total = float(coste.sum())
            if pd.isna(coste_total):
                coste_total = 0
        
        result = {
            'comunidades': df['COMUNIDAD_ATENCION'].value_counts().to_dict() if 'COMUNIDAD_ATENCION' in df.columns else {},
            'sexos': df['SEXO'].value_counts().to_dict() if 'SEXO' in df.columns else {},
            'categorias': df['CATEGORIA_DIAGNOSTICO'].value_counts().to_dict() if 'CATEGORIA_DIAGNOSTICO' in df.columns else {},
            'ingresos_por_mes': df['MES_INGRESO'].value_counts().sort_index().to_dict() if 'MES_INGRESO' in df.columns else {},
            'estancia_promedio': estancia_promedio,
            'coste_total': coste_total,
            'ingresos_uci': ingresos_uci_dict,
            'pacientes_uci': pacientes_uci,
            'dias_uci_promedio': dias_uci_promedio
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/table')
@login_required
def get_table_data():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        conn = get_connection()
        cursor = conn.cursor()
        
        count_query = 'SELECT COUNT(*) FROM VISTA_DASHBOARD WHERE 1=1'
        data_query = 'SELECT * FROM (SELECT a.*, ROWNUM rnum FROM (SELECT * FROM VISTA_DASHBOARD WHERE 1=1'
        params = []
        
        filter_clause = ''
        comunidad = request.args.get('comunidad')
        if comunidad:
            filter_clause += ' AND comunidad_atencion = :1'
            params.append(comunidad)
        
        sexo = request.args.get('sexo')
        if sexo:
            filter_clause += f' AND sexo = :{len(params) + 1}'
            params.append(sexo)
        
        categoria = request.args.get('categoria')
        if categoria:
            filter_clause += f' AND categoria_diagnostico = :{len(params) + 1}'
            params.append(categoria)
        
        fecha_inicio = request.args.get('fecha_inicio')
        if fecha_inicio:
            filter_clause += f' AND fecha_ingreso >= :{len(params) + 1}'
            params.append(fecha_inicio)
        
        fecha_fin = request.args.get('fecha_fin')
        if fecha_fin:
            filter_clause += f' AND fecha_ingreso <= :{len(params) + 1}'
            params.append(fecha_fin)
        
        count_query += filter_clause
        if params:
            cursor.execute(count_query, params)
        else:
            cursor.execute(count_query)
        total = cursor.fetchone()[0]
        
        offset = (page - 1) * per_page
        data_query += filter_clause + f') a WHERE ROWNUM <= {offset + per_page}) WHERE rnum > {offset}'
        
        if params:
            cursor.execute(data_query, params)
        else:
            cursor.execute(data_query)
        
        columns = [desc[0] for desc in cursor.description if desc[0] != 'RNUM']
        rows = cursor.fetchall()
        
        items = []
        for row in rows:
            item = {columns[i]: row[i] for i in range(len(columns))}
            items.append(item)
        
        cursor.close()
        conn.close()
        
        result = {
            'items': items,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'current_page': page
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/table')
@login_required
def table_view():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT nombre_comunidad FROM COMUNIDADES ORDER BY nombre_comunidad')
        comunidades = [row[0] for row in cursor.fetchall()]
        
        cursor.execute('SELECT DISTINCT sexo FROM INGRESOS WHERE sexo IS NOT NULL ORDER BY sexo')
        sexos = [row[0] for row in cursor.fetchall()]
        
        cursor.execute('SELECT nombre_categoria FROM CATEGORIAS_DIAGNOSTICO ORDER BY nombre_categoria')
        categorias = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return render_template('data_table.html', comunidades=comunidades, sexos=sexos, categorias=categorias)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/chat')
@login_required
def chat_view():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    try:
        if not gemini_model:
            return jsonify({'error': 'El servicio de IA no está configurado. Por favor, configura GOOGLE_API_KEY.'}), 500
        
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'Por favor, proporciona una pregunta.'}), 400
        
        # Obtener el esquema de la base de datos
        conn = get_connection()
        cursor = conn.cursor()
        
        ORACLE_USER = app.config['DB_USER']
        
        cursor.execute(f"""
            SELECT table_name, column_name
            FROM all_tab_columns
            WHERE owner = UPPER('{ORACLE_USER}')
            ORDER BY table_name, column_id
        """)
        
        esquema = {}
        for table, column in cursor:
            esquema.setdefault(table, []).append(column)
        
        esquema_texto = "\n".join(
            f"{tabla}({', '.join(columnas)})" for tabla, columnas in esquema.items()
        )
        
        # Generar SQL con Gemini
        prompt_sql = f"""
Eres un asistente experto en SQL para Oracle. Genera solo la consulta SQL compatible con Oracle.
Usa este esquema de base de datos:
{esquema_texto}

IMPORTANTE: 
- La vista VISTA_DASHBOARD contiene todos los datos principales agregados
- Para contar pacientes, usa COUNT(*) o COUNT(DISTINCT id_columna)
- Para promedios, usa AVG()
- Para sumas, usa SUM()
- NO uses punto y coma al final
- NO uses saltos de línea innecesarios
- Devuelve SOLO la consulta SQL, sin explicaciones

Pregunta del usuario:
{question}
"""
        
        raw_sql = gemini_model.generate_content(prompt_sql)
        sql_generado = raw_sql.text.strip().strip("```sql").strip("```").strip()
        sql_generado = sql_generado.replace(";", "")
        sql_generado = sql_generado.replace("\n", " ").replace("\t", " ")
        
        # Ejecutar SQL
        cursor.execute(sql_generado)
        resultados = cursor.fetchall()
        columnas = [col[0] for col in cursor.description]
        
        df = pd.DataFrame(resultados, columns=columnas)
        texto_resultado = df.to_markdown(index=False)
        
        cursor.close()
        conn.close()
        
        # Interpretar resultados con Gemini
        prompt_explicacion = f"""
Eres un analista especializado en salud mental que presenta datos a investigadores del sector sanitario.

Pregunta original: {question}
Resultados obtenidos:
{texto_resultado}

INSTRUCCIONES:
1. Presenta los datos clave de forma directa y precisa (cifras exactas, porcentajes, promedios)
2. Proporciona un análisis breve y profesional de los hallazgos (máximo 2-3 frases)
3. Si es relevante, menciona implicaciones clínicas o epidemiológicas
4. Usa terminología técnica apropiada para investigadores sanitarios
5. Sé conciso: los investigadores necesitan información rápida y precisa

Formato de respuesta:
📊 DATOS: [Cifras principales]
� ANÁLISIS: [Interpretación breve de los resultados]
"""
        
        response = gemini_model.generate_content(prompt_explicacion)
        answer = response.text.strip()
        
        return jsonify({
            'answer': answer,
            'sql_query': sql_generado
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
