

import sys
import os
from app import app, db, Usuario
from werkzeug.security import generate_password_hash

def inicializar_sistema():
    
    with app.app_context():
        
        db.create_all()
        
       
        admin = Usuario.query.filter_by(email='admin@sistema.com').first()
        
        if not admin:
            print("="*60)
            print("PRIMERA EJECUCIÓN - CREANDO USUARIO ADMINISTRADOR")
            print("="*60)
            
            admin = Usuario(
                nombre='Administrador',
                email='admin@sistema.com',
                password=generate_password_hash('admin123'),
                rol='administrador'
            )
            db.session.add(admin)
            db.session.commit()
            
            print("\n✓ Usuario administrador creado exitosamente")
            print("\n🔑 Credenciales de acceso:")
            print("   Email: admin@sistema.com")
            print("   Contraseña: admin123")
            print("\n⚠️  IMPORTANTE: Cambie la contraseña después del primer ingreso")
            print("="*60 + "\n")
        else:
            print("✓ Base de datos inicializada correctamente\n")

def mostrar_info():
    """Muestra información del sistema"""
    print("\n" + "="*60)
    print("SISTEMA DE FACTURACIÓN - FLASK + ADMINLTE")
    print("="*60)
    print(f"\n🌐 URL de acceso: http://localhost:5000")
    print(f"📊 Modo: {app.config.get('ENV', 'development')}")
    print(f"🔒 Debug: {app.config.get('DEBUG', False)}")
    print(f"\n💡 Para detener el servidor: Ctrl+C")
    print("="*60 + "\n")

def main():
    """Función principal"""
    
    modo = 'development'
    if len(sys.argv) > 1:
        if '--modo=produccion' in sys.argv:
            modo = 'production'
            app.config.from_object('config.ProductionConfig')
        elif '--modo=testing' in sys.argv:
            modo = 'testing'
            app.config.from_object('config.TestingConfig')
    
    
    inicializar_sistema()
    
    
    mostrar_info()
    
 

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Servidor detenido correctamente")
        sys.exit(0)
    except Exception as e:
        print(f"\n Error al iniciar el servidor: {e}")
        sys.exit(1)