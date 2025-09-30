

from app import app, db, Cliente, Producto, Factura, DetalleFactura, Usuario
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def seed_database():
    with app.app_context():
        print("Iniciando carga de datos de prueba...")
        
       
        print("Limpiando base de datos...")
        DetalleFactura.query.delete()
        Factura.query.delete()
        Producto.query.delete()
        Cliente.query.delete()
        Usuario.query.delete()
        db.session.commit()
        
        
        print("Creando usuarios...")
        usuarios = [
            Usuario(
                nombre='Administrador',
                email='admin@sistema.com',
                password=generate_password_hash('admin123'),
                rol='administrador'
            ),
            Usuario(
                nombre='Usuario Demo',
                email='usuario@sistema.com',
                password=generate_password_hash('usuario123'),
                rol='usuario'
            )
        ]
        db.session.add_all(usuarios)
        db.session.commit()
        print(f"✓ {len(usuarios)} usuarios creados")
        
        
        print("Creando clientes...")
        clientes_data = [
            {
                'nombre': 'Juan Pérez',
                'direccion': 'Av. Corrientes 1234, CABA',
                'telefono': '011-4444-5555',
                'email': 'jperez@email.com'
            },
            {
                'nombre': 'María García',
                'direccion': 'Calle San Martín 567, Rosario',
                'telefono': '0341-444-5566',
                'email': 'mgarcia@email.com'
            },
            {
                'nombre': 'Carlos López',
                'direccion': 'Av. Libertador 890, CABA',
                'telefono': '011-5555-6666',
                'email': 'clopez@email.com'
            },
            {
                'nombre': 'Ana Martínez',
                'direccion': 'Mitre 345, Córdoba',
                'telefono': '0351-777-8888',
                'email': 'amartinez@email.com'
            },
            {
                'nombre': 'Roberto Fernández',
                'direccion': 'Belgrano 678, Mendoza',
                'telefono': '0261-999-0000',
                'email': 'rfernandez@email.com'
            },
            {
                'nombre': 'Laura Sánchez',
                'direccion': 'Rivadavia 234, La Plata',
                'telefono': '0221-444-5555',
                'email': 'lsanchez@email.com'
            },
            {
                'nombre': 'Empresa ABC S.A.',
                'direccion': 'Av. del Libertador 1500, CABA',
                'telefono': '011-6666-7777',
                'email': 'ventas@empresaabc.com'
            },
            {
                'nombre': 'Comercial XYZ',
                'direccion': 'Av. Santa Fe 2345, CABA',
                'telefono': '011-8888-9999',
                'email': 'compras@comercialxyz.com'
            }
        ]
        
        clientes = [Cliente(**data) for data in clientes_data]
        db.session.add_all(clientes)
        db.session.commit()
        print(f"✓ {len(clientes)} clientes creados")
        
        
        print("Creando productos...")
        productos_data = [
            {'descripcion': 'Notebook Dell Inspiron 15', 'precio': 85000.00, 'stock': 15},
            {'descripcion': 'Mouse Logitech M170', 'precio': 3500.00, 'stock': 50},
            {'descripcion': 'Teclado Mecánico RGB', 'precio': 12000.00, 'stock': 25},
            {'descripcion': 'Monitor LG 24" Full HD', 'precio': 45000.00, 'stock': 20},
            {'descripcion': 'Auriculares Sony WH-1000XM4', 'precio': 65000.00, 'stock': 12},
            {'descripcion': 'Webcam Logitech C920', 'precio': 18000.00, 'stock': 30},
            {'descripcion': 'Disco SSD 500GB Samsung', 'precio': 15000.00, 'stock': 40},
            {'descripcion': 'Memoria RAM 8GB DDR4', 'precio': 8000.00, 'stock': 60},
            {'descripcion': 'Router TP-Link AC1200', 'precio': 12500.00, 'stock': 22},
            {'descripcion': 'Impresora HP DeskJet 2720', 'precio': 28000.00, 'stock': 18},
            {'descripcion': 'Pendrive 64GB SanDisk', 'precio': 2500.00, 'stock': 100},
            {'descripcion': 'Hub USB 4 Puertos', 'precio': 3000.00, 'stock': 35},
            {'descripcion': 'Cable HDMI 2m', 'precio': 1500.00, 'stock': 80},
            {'descripcion': 'Mousepad Gamer XL', 'precio': 4500.00, 'stock': 45},
            {'descripcion': 'Silla Gamer Ergonómica', 'precio': 95000.00, 'stock': 8},
            {'descripcion': 'Micrófono USB Blue Yeti', 'precio': 38000.00, 'stock': 10},
            {'descripcion': 'Tablet Samsung Galaxy Tab A8', 'precio': 55000.00, 'stock': 14},
            {'descripcion': 'Smart TV 43" Samsung', 'precio': 120000.00, 'stock': 6},
            {'descripcion': 'Parlantes Edifier R1280T', 'precio': 22000.00, 'stock': 16},
            {'descripcion': 'Cargador Inalámbrico 15W', 'precio': 5500.00, 'stock': 28}
        ]
        
        productos = [Producto(**data) for data in productos_data]
        db.session.add_all(productos)
        db.session.commit()
        print(f"✓ {len(productos)} productos creados")
        
        
        print("Creando facturas de prueba...")
        facturas_creadas = 0
        
        # Generar facturas de los últimos 90 días
        for i in range(30):  # 30 facturas de prueba
            # Fecha aleatoria en los últimos 90 días
            dias_atras = random.randint(0, 90)
            fecha = datetime.now() - timedelta(days=dias_atras)
            
           
            cliente = random.choice(clientes)
            
            
            factura = Factura(
                id_cliente=cliente.id_cliente,
                fecha=fecha,
                total=0
            )
            db.session.add(factura)
            db.session.flush()
            
            # Agregar entre 1 y 5 productos aleatorios
            num_productos = random.randint(1, 5)
            productos_factura = random.sample(productos, num_productos)
            
            total_factura = 0
            for producto in productos_factura:
                cantidad = random.randint(1, 5)
                subtotal = producto.precio * cantidad
                
                detalle = DetalleFactura(
                    id_factura=factura.id_factura,
                    id_producto=producto.id_producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                    subtotal=subtotal
                )
                db.session.add(detalle)
                total_factura += subtotal
                
                
                producto.stock = max(0, producto.stock - cantidad)
            
            factura.total = total_factura
            facturas_creadas += 1
        
        db.session.commit()
        print(f"✓ {facturas_creadas} facturas creadas")
        
       
        print("\n" + "="*60)
        print("DATOS DE PRUEBA CARGADOS EXITOSAMENTE")
        print("="*60)
        print(f"\n📊 Resumen:")
        print(f"   • Usuarios: {Usuario.query.count()}")
        print(f"   • Clientes: {Cliente.query.count()}")
        print(f"   • Productos: {Producto.query.count()}")
        print(f"   • Facturas: {Factura.query.count()}")
        print(f"\n🔑 Credenciales de acceso:")
        print(f"   • Admin: admin@sistema.com / admin123")
        print(f"   • Usuario: usuario@sistema.com / usuario123")
        print(f"\n🌐 Acceder en: http://localhost:5000")
        print("="*60 + "\n")

if __name__ == '__main__':
    seed_database()