from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta'

DATABASE = 'facturacion.db'

#  FUNCIONES BASE DE DATOS =

def get_db():
    """Conectar a la base de datos"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
    return conn

def init_db():
    """Crear las tablas si no existen"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            direccion TEXT,
            telefono TEXT,
            email TEXT
        )
    ''')
    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facturas (
            id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total REAL DEFAULT 0.0,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detalle_factura (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_factura INTEGER NOT NULL,
            id_producto INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (id_factura) REFERENCES facturas(id_factura),
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        )
    ''')
    
    conn.commit()
    conn.close()
    print('✓ Base de datos inicializada correctamente')

#  RUTAS 

@app.route('/')
def index():
    return redirect(url_for('clientes'))

# GESTION DE CLIENTES

@app.route('/clientes')
def clientes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes ORDER BY nombre')
    clientes = cursor.fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clientes (nombre, direccion, telefono, email)
            VALUES (?, ?, ?, ?)
        ''', (nombre, direccion, telefono, email))
        conn.commit()
        conn.close()
        
        flash('Cliente agregado exitosamente.', 'success')
        return redirect(url_for('clientes'))
    
    return render_template('cliente_form.html', cliente=None)

@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        
        cursor.execute('''
            UPDATE clientes 
            SET nombre=?, direccion=?, telefono=?, email=?
            WHERE id_cliente=?
        ''', (nombre, direccion, telefono, email, id))
        conn.commit()
        conn.close()
        
        flash('Cliente actualizado exitosamente.', 'success')
        return redirect(url_for('clientes'))
    
    cursor.execute('SELECT * FROM clientes WHERE id_cliente=?', (id,))
    cliente = cursor.fetchone()
    conn.close()
    
    if not cliente:
        flash('Cliente no encontrado.', 'danger')
        return redirect(url_for('clientes'))
    
    return render_template('cliente_form.html', cliente=cliente)

@app.route('/clientes/eliminar/<int:id>')
def eliminar_cliente(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clientes WHERE id_cliente=?', (id,))
    conn.commit()
    conn.close()
    
    flash('Cliente eliminado exitosamente.', 'success')
    return redirect(url_for('clientes'))

#  GESTION DE PRODUCTOS 

@app.route('/productos')
def productos():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos ORDER BY descripcion')
    productos = cursor.fetchall()
    conn.close()
    return render_template('productos.html', productos=productos)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    if request.method == 'POST':
        descripcion = request.form.get('descripcion')
        precio = float(request.form.get('precio'))
        stock = int(request.form.get('stock'))
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO productos (descripcion, precio, stock)
            VALUES (?, ?, ?)
        ''', (descripcion, precio, stock))
        conn.commit()
        conn.close()
        
        flash('Producto agregado exitosamente.', 'success')
        return redirect(url_for('productos'))
    
    return render_template('producto_form.html', producto=None)

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        descripcion = request.form.get('descripcion')
        precio = float(request.form.get('precio'))
        stock = int(request.form.get('stock'))
        
        cursor.execute('''
            UPDATE productos 
            SET descripcion=?, precio=?, stock=?
            WHERE id_producto=?
        ''', (descripcion, precio, stock, id))
        conn.commit()
        conn.close()
        
        flash('Producto actualizado exitosamente.', 'success')
        return redirect(url_for('productos'))
    
    cursor.execute('SELECT * FROM productos WHERE id_producto=?', (id,))
    producto = cursor.fetchone()
    conn.close()
    
    if not producto:
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('productos'))
    
    return render_template('producto_form.html', producto=producto)

@app.route('/productos/eliminar/<int:id>')
def eliminar_producto(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM productos WHERE id_producto=?', (id,))
    conn.commit()
    conn.close()
    
    flash('Producto eliminado exitosamente.', 'success')
    return redirect(url_for('productos'))

#  GESTION DE FACTURAS 

@app.route('/facturas')
def facturas():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT f.*, c.nombre as cliente_nombre
        FROM facturas f
        JOIN clientes c ON f.id_cliente = c.id_cliente
        ORDER BY f.fecha DESC
    ''')
    facturas = cursor.fetchall()
    conn.close()
    return render_template('facturas.html', facturas=facturas)

@app.route('/facturas/nueva', methods=['GET', 'POST'])
def nueva_factura():
    if request.method == 'POST':
        id_cliente = request.form.get('id_cliente')
        productos_json = request.form.get('productos')
        
        if not productos_json:
            flash('Debe agregar al menos un producto.', 'danger')
            return redirect(url_for('nueva_factura'))
        
        productos_data = json.loads(productos_json)
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO facturas (id_cliente, total)
            VALUES (?, 0)
        ''', (id_cliente,))
        id_factura = cursor.lastrowid
        
        total = 0
        for item in productos_data:
            cursor.execute('SELECT precio, stock FROM productos WHERE id_producto=?', 
                         (item['id_producto'],))
            producto = cursor.fetchone()
            
            cantidad = int(item['cantidad'])
            precio_unitario = producto['precio']
            subtotal = cantidad * precio_unitario
            
            cursor.execute('''
                INSERT INTO detalle_factura 
                (id_factura, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (id_factura, item['id_producto'], cantidad, precio_unitario, subtotal))
            
            cursor.execute('''
                UPDATE productos 
                SET stock = stock - ?
                WHERE id_producto = ?
            ''', (cantidad, item['id_producto']))
            
            total += subtotal
        
        cursor.execute('UPDATE facturas SET total=? WHERE id_factura=?', 
                      (total, id_factura))
        
        conn.commit()
        conn.close()
        
        flash('Factura creada exitosamente.', 'success')
        return redirect(url_for('ver_factura', id=id_factura))
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM clientes ORDER BY nombre')
    clientes = cursor.fetchall()
    
    cursor.execute('SELECT * FROM productos WHERE stock > 0 ORDER BY descripcion')
    productos = cursor.fetchall()
    
    conn.close()
    
    return render_template('factura_form.html', clientes=clientes, productos=productos)

@app.route('/facturas/ver/<int:id>')
def ver_factura(id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT f.*, c.nombre, c.direccion, c.telefono, c.email
        FROM facturas f
        JOIN clientes c ON f.id_cliente = c.id_cliente
        WHERE f.id_factura = ?
    ''', (id,))
    factura = cursor.fetchone()
    
    if not factura:
        flash('Factura no encontrada.', 'danger')
        conn.close()
        return redirect(url_for('facturas'))
    
    cursor.execute('''
        SELECT d.*, p.descripcion
        FROM detalle_factura d
        JOIN productos p ON d.id_producto = p.id_producto
        WHERE d.id_factura = ?
    ''', (id,))
    detalles = cursor.fetchall()
    
    conn.close()
    
    return render_template('factura_detalle.html', factura=factura, detalles=detalles)

#  REPORTES 

@app.route('/reportes/clientes')
def reporte_clientes():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            c.id_cliente,
            c.nombre,
            c.direccion,
            COUNT(f.id_factura) as total_facturas,
            COALESCE(SUM(f.total), 0) as total_ventas
        FROM clientes c
        LEFT JOIN facturas f ON c.id_cliente = f.id_cliente
        GROUP BY c.id_cliente, c.nombre, c.direccion
        ORDER BY total_ventas DESC
    ''')
    datos = cursor.fetchall()
    conn.close()
    
    return render_template('reporte_clientes.html', datos=datos)

@app.route('/reportes/ventas', methods=['GET', 'POST'])
def reporte_ventas():
    facturas = []
    total = 0
    
    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT f.*, c.nombre as cliente_nombre
                FROM facturas f
                JOIN clientes c ON f.id_cliente = c.id_cliente
                WHERE DATE(f.fecha) BETWEEN ? AND ?
                ORDER BY f.fecha DESC
            ''', (fecha_inicio, fecha_fin))
            facturas = cursor.fetchall()
            
            cursor.execute('''
                SELECT COALESCE(SUM(total), 0)
                FROM facturas
                WHERE DATE(fecha) BETWEEN ? AND ?
            ''', (fecha_inicio, fecha_fin))
            total = cursor.fetchone()[0]
            
            conn.close()
    
    return render_template('reporte_ventas.html', facturas=facturas, total=total)

# INICIALIZACIN 

if __name__ == '__main__':
    init_db()
    app.run(debug=True)