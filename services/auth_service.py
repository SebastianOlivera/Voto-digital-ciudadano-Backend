from fastapi import HTTPException, status
from database import get_db_connection
from dao.mesa_dao import MesaDAO
import auth
from schemas import LoginResponse, CircuitoInfo, EstablecimientoInfo

def authenticate_user(username: str, password: str) -> LoginResponse:
    """Autenticar usuario y generar token"""
    with get_db_connection() as connection:
        user = MesaDAO.get_by_username(connection, username)
        print(f"DEBUG: Usuario encontrado: {user is not None}")
        if user:
            print(f"DEBUG: Username: {user['username']}, Role: {user.get('role', 'N/A')}")
            print(f"DEBUG: Password hash starts with: {user['password_hash'][:10]}...")
        
        if not user:
            print(f"DEBUG: Usuario '{username}' no encontrado")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
    
        try:
            password_valid = auth.verify_password(password, user['password_hash'])
            print(f"DEBUG: Password verification result: {password_valid}")
        except Exception as e:
            print(f"DEBUG: Error verifying password: {e}")
            password_valid = False
        
        if not password_valid:
            print(f"DEBUG: Password verification failed for user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
        
        # Obtener información del circuito solo para usuarios que no sean superadmin
        circuito_info = None
        
        # Superadmin no requiere información de circuito
        if user['role'] == 'superadmin':
            print(f"DEBUG: Usuario superadmin '{username}' autenticado, no requiere circuito")
        elif user['circuito_id'] and user['numero_circuito']:
            # Solo usuarios normales necesitan información completa del circuito
            circuito_info = CircuitoInfo(
                id=user['circuito_id'],
                numero_circuito=user['numero_circuito'],
                establecimiento=EstablecimientoInfo(
                    id=user['establecimiento_id'],
                    nombre=user['establecimiento_nombre'],
                    departamento=user['departamento'],
                    ciudad=user['ciudad'],
                    zona=user['zona'],
                    barrio=user['barrio'],
                    direccion=user['direccion'],
                    tipo_establecimiento=user['tipo_establecimiento'],
                    accesible=user['accesible']
                )
            )
        else:
            print(f"DEBUG: Usuario de mesa sin información de circuito válida")
        
        access_token = auth.create_access_token(data={"sub": user['username']})
        return LoginResponse(
            access_token=access_token, 
            token_type="bearer",
            circuito=circuito_info,
            username=user['username'],
            role=user.get('role', 'mesa'),
            mesa_cerrada=user.get('mesa_cerrada', False)
        )