# Voto-digital-ciudadano-Backend
## Ejecución del Backend

Para construir las imágenes Docker y levantar los contenedores del backend, ejecuta el siguiente comando desde el directorio raíz del proyecto:

```
docker-compose up --build
```

Una vez iniciado, el backend quedará disponible en:

```
http://localhost:8000
```


## Estructura del Proyecto

```
.
├── dao/                 Acceso a datos
├── routers/             Rutas de la API
├── services/            Lógica de negocio
├── schemas.py           Modelos Pydantic
├── database.py          Conexión a la base de datos
├── database_setup.py    Inicialización de tablas
├── create_admin_user.py Script para crear usuario admin
├── auth.py              Autenticación y seguridad
├── main.py              Punto de entrada de la aplicación
├── Dockerfile           Imagen del backend
├── docker-compose.yml   Orquestación de contenedores
├── requirements.txt     Dependencias Python
```
