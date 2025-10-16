from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from functools import wraps
import pandas as pd
import numpy as np
import oracledb
import config

app = Flask(__name__)
app.config.from_object(config.Config)

# Función para obtener conexión
def get_connection():
    return oracledb.connect(
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        dsn=app.config['DB_DSN'],
        wallet_location=app.config['WALLET_LOCATION'],
        wallet_password=app.config['WALLET_PASSWORD']
    )

# Decorador para rutas protegidas
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
    """
    Página principal - Obtiene filtros desde las tablas normalizadas
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Obtener comunidades desde la tabla normalizada
        cursor.execute('SELECT nombre_comunidad FROM COMUNIDADES ORDER BY nombre_comunidad')
        comunidades = [row[0] for row in cursor.fetchall()]
        
        # Obtener sexos distintos desde INGRESOS
        cursor.execute('SELECT DISTINCT sexo FROM INGRESOS WHERE sexo IS NOT NULL ORDER BY sexo')
        sexos = [row[0] for row in cursor.fetchall()]
        
        # Obtener categorías desde la tabla normalizada
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
    """
    API para obtener datos del dashboard - Usa la vista normalizada
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Usar la vista VISTAMUYINTERESANTE que tiene todos los JOINs
        query = 'SELECT * FROM VISTAMUYINTERESANTE WHERE 1=1'
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
        
        # Adaptar nombres de columnas de la vista a los que espera el frontend
        result = {
            'comunidades': df['COMUNIDAD_ATENCION'].value_counts().to_dict() if 'COMUNIDAD_ATENCION' in df.columns else {},
            'sexos': df['SEXO'].value_counts().to_dict() if 'SEXO' in df.columns else {},
            'categorias': df['CATEGORIA_DIAGNOSTICO'].value_counts().to_dict() if 'CATEGORIA_DIAGNOSTICO' in df.columns else {},
            'ingresos_por_mes': df['MES_INGRESO'].value_counts().sort_index().to_dict() if 'MES_INGRESO' in df.columns else {},
            'estancia_promedio': float(df['ESTANCIA_DIAS'].replace([None, 'NULL', ''], np.nan).astype(float).mean()) if 'ESTANCIA_DIAS' in df.columns else 0,
            'coste_total': float(df['COSTE_APR'].replace([None, 'NULL', ''], np.nan).astype(float).sum()) if 'COSTE_APR' in df.columns else 0,
            'ingresos_uci': df['INGRESO_EN_UCI'].value_counts().to_dict() if 'INGRESO_EN_UCI' in df.columns else {},
            'pacientes_uci': int(df[df['INGRESO_EN_UCI'] == 'Sí'].shape[0]) if 'INGRESO_EN_UCI' in df.columns else 0,
            'dias_uci_promedio': float(df[df['INGRESO_EN_UCI'] == 'Sí']['DIAS_UCI'].replace([None, 'NULL', ''], np.nan).astype(float).mean()) if 'INGRESO_EN_UCI' in df.columns and 'DIAS_UCI' in df.columns else 0
        }
        
        for key in result:
            if isinstance(result[key], float) and pd.isna(result[key]):
                result[key] = 0
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/table')
@login_required
def get_table_data():
    """
    API para la tabla de datos - Usa la vista normalizada con paginación
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        conn = get_connection()
        cursor = conn.cursor()
        
        count_query = 'SELECT COUNT(*) FROM VISTAMUYINTERESANTE WHERE 1=1'
        data_query = 'SELECT * FROM (SELECT a.*, ROWNUM rnum FROM (SELECT * FROM VISTAMUYINTERESANTE WHERE 1=1'
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
    """
    Vista de tabla - Obtiene filtros desde las tablas normalizadas
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Obtener comunidades desde la tabla normalizada
        cursor.execute('SELECT nombre_comunidad FROM COMUNIDADES ORDER BY nombre_comunidad')
        comunidades = [row[0] for row in cursor.fetchall()]
        
        # Obtener sexos distintos desde INGRESOS
        cursor.execute('SELECT DISTINCT sexo FROM INGRESOS WHERE sexo IS NOT NULL ORDER BY sexo')
        sexos = [row[0] for row in cursor.fetchall()]
        
        # Obtener categorías desde la tabla normalizada
        cursor.execute('SELECT nombre_categoria FROM CATEGORIAS_DIAGNOSTICO ORDER BY nombre_categoria')
        categorias = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return render_template('data_table.html', comunidades=comunidades, sexos=sexos, categorias=categorias)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
