from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui-cambiar-en-produccion'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facturacion.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), default='usuario')

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    facturas = db.relationship('Factura', backref='cliente', lazy=True)

class Producto(db.Model):
    __tablename__ = 'productos'
    id_producto = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(200), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

class Factura(db.Model):
    __tablename__ = 'facturas'
    id_factura = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, default=0.0)
    detalles = db.relationship('DetalleFactura', backref='factura', lazy=True, cascade='all, delete-orphan')

class DetalleFactura(db.Model):
    __tablename__ = 'detalle_factura'
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_factura = db.Column(db.Integer, db.ForeignKey('facturas.id_factura'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    producto = db.relationship('Producto', backref='detalles')



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debe iniciar sesión para acceder.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        usuario = Usuario.query.get(session['usuario_id'])
        if usuario.rol != 'administrador':
            flash('Acceso no autorizado.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# RUTAS DE AUTENTICACON 
@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.password, password):
            session['usuario_id'] = usuario.id_usuario
            session['usuario_nombre'] = usuario.nombre
            session['usuario_rol'] = usuario.rol
            flash(f'Bienvenido, {usuario.nombre}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente.', 'info')
    return redirect(url_for('login'))



@app.route('/dashboard')
@login_required
def dashboard():
    total_clientes = Cliente.query.count()
    total_productos = Producto.query.count()
    total_facturas = Factura.query.count()
    ventas_total = db.session.query(db.func.sum(Factura.total)).scalar() or 0
    
    return render_template('dashboard.html',
                         total_clientes=total_clientes,
                         total_productos=total_productos,
                         total_facturas=total_facturas,
                         ventas_total=ventas_total)

# GESTION  CLIENTES

@app.route('/clientes')
@login_required
def clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    if request.method == 'POST':
        cliente = Cliente(
            nombre=request.form.get('nombre'),
            direccion=request.form.get('direccion'),
            telefono=request.form.get('telefono'),
            email=request.form.get('email')
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente agregado exitosamente.', 'success')
        return redirect(url_for('clientes'))
    
    return render_template('cliente_form.html', cliente=None)

@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    
    if request.method == 'POST':
        cliente.nombre = request.form.get('nombre')
        cliente.direccion = request.form.get('direccion')
        cliente.telefono = request.form.get('telefono')
        cliente.email = request.form.get('email')
        db.session.commit()
        flash('Cliente actualizado exitosamente.', 'success')
        return redirect(url_for('clientes'))
    
    return render_template('cliente_form.html', cliente=cliente)

@app.route('/clientes/eliminar/<int:id>')
@login_required
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado exitosamente.', 'success')
    return redirect(url_for('clientes'))

# GESTION PRODUCTOS 

@app.route('/productos')
@login_required
def productos():
    productos = Producto.query.all()
    return render_template('productos.html', productos=productos)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    if request.method == 'POST':
        producto = Producto(
            descripcion=request.form.get('descripcion'),
            precio=float(request.form.get('precio')),
            stock=int(request.form.get('stock'))
        )
        db.session.add(producto)
        db.session.commit()
        flash('Producto agregado exitosamente.', 'success')
        return redirect(url_for('productos'))
    
    return render_template('producto_form.html', producto=None)

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    
    if request.method == 'POST':
        producto.descripcion = request.form.get('descripcion')
        producto.precio = float(request.form.get('precio'))
        producto.stock = int(request.form.get('stock'))
        db.session.commit()
        flash('Producto actualizado exitosamente.', 'success')
        return redirect(url_for('productos'))
    
    return render_template('producto_form.html', producto=producto)

@app.route('/productos/eliminar/<int:id>')
@login_required
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado exitosamente.', 'success')
    return redirect(url_for('productos'))

#  GESTION FACTURAS 

@app.route('/facturas')
@login_required
def facturas():
    facturas = Factura.query.order_by(Factura.fecha.desc()).all()
    return render_template('facturas.html', facturas=facturas)

@app.route('/facturas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_factura():
    if request.method == 'POST':
        id_cliente = request.form.get('id_cliente')
        productos_json = request.form.get('productos')
        
        import json
        productos_data = json.loads(productos_json)
        
        factura = Factura(id_cliente=id_cliente)
        db.session.add(factura)
        db.session.flush()
        
        total = 0
        for item in productos_data:
            producto = Producto.query.get(item['id_producto'])
            cantidad = int(item['cantidad'])
            subtotal = producto.precio * cantidad
            
            detalle = DetalleFactura(
                id_factura=factura.id_factura,
                id_producto=producto.id_producto,
                cantidad=cantidad,
                precio_unitario=producto.precio,
                subtotal=subtotal
            )
            db.session.add(detalle)
            
            producto.stock -= cantidad
            total += subtotal
        
        factura.total = total
        db.session.commit()
        
        flash('Factura creada exitosamente.', 'success')
        return redirect(url_for('ver_factura', id=factura.id_factura))
    
    clientes = Cliente.query.all()
    productos = Producto.query.filter(Producto.stock > 0).all()
    return render_template('factura_form.html', clientes=clientes, productos=productos)

@app.route('/facturas/ver/<int:id>')
@login_required
def ver_factura(id):
    factura = Factura.query.get_or_404(id)
    return render_template('factura_detalle.html', factura=factura)

#  REPORTES

@app.route('/reportes/clientes')
@login_required
def reporte_clientes():
    clientes = Cliente.query.all()
    datos = []
    for cliente in clientes:
        total_facturas = len(cliente.facturas)
        total_ventas = sum(f.total for f in cliente.facturas)
        datos.append({
            'cliente': cliente,
            'total_facturas': total_facturas,
            'total_ventas': total_ventas
        })
    return render_template('reporte_clientes.html', datos=datos)

@app.route('/reportes/ventas', methods=['GET', 'POST'])
@login_required
def reporte_ventas():
    facturas = []
    total = 0
    
    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            facturas = Factura.query.filter(
                Factura.fecha.between(fecha_inicio, fecha_fin)
            ).all()
            total = sum(f.total for f in facturas)
    
    return render_template('reporte_ventas.html', facturas=facturas, total=total)

#  INICIALIZACION 

def inicializar_db():
    with app.app_context():
        db.create_all()
        
        if Usuario.query.count() == 0:
            admin = Usuario(
                nombre='Administrador',
                email='admin@sistema.com',
                password=generate_password_hash('admin123'),
                rol='administrador'
            )
            db.session.add(admin)
            db.session.commit()
            print('Usuario administrador creado: admin@sistema.com / admin123')

if __name__ == '__main__':
    inicializar_db()
    app.run(debug=True)