# Valoriza – Guía de Instalación y Ejecución

Construido con Django 5.2.8, SQLite, Ollama utilizando el modelo LLaMA 3.2, HTML/CSS/JavaScript y Docker con Docker Compose.



## INSTALACIÓN Y CONFIGURACIÓN

PRERREQUISITOS:

- Docker
    
- Docker Compose
    
- Git
    



1. Clonar el repositorio
    


```bash
git clone <url-del-repositorio>  
cd Valoriza
```


2. Construir y ejecutar con Docker Compose
    


```bash
docker-compose up --build  
Para ejecutarlo en segundo plano:  
docker-compose up --build -d
```
La primera ejecución puede tardar varios minutos porque Docker debe descargar las imágenes necesarias, preparar el entorno y descargar el modelo LLaMA 3.2 (~2GB).



3. Crear usuario administrador
    


```bash
docker-compose exec web python manage.py createsuperuser
```


## ACCESO A LA APLICACIÓN

Aplicación principal: [http://localhost:8000](http://localhost:8000)

  
Panel de administración: [http://localhost:8000/admin](http://localhost:8000/admin)  
Chat con IA: [http://localhost:8000/chat](http://localhost:8000/chat)  
Empresas: [http://localhost:8000/empresas](http://localhost:8000/empresas)  
Industrias: [http://localhost:8000/industrias](http://localhost:8000/industrias)



## VERIFICACIÓN DEL CHAT AI Y OLLAMA

Verificar el estado de Ollama:  
```bash
docker-compose exec ollama ollama list
```
También puedes probar el modelo manualmente:  
```bash
docker-compose exec ollama ollama run llama3.2 "Hola, ¿cómo estás?"
```
Ejemplos de consultas al chat:

- “Muestra 10 empresas”
    
- “¿Cuántas empresas hay?”
    
- “Empresas de agricultura”
    
- “Lista todas las industrias”
    



## COMANDOS ÚTILES DE DESARROLLO

Gestión de contenedores:

- Ver logs de todos los servicios: 
	```bash
	docker-compose logs
    ```
- Ver logs de un servicio: 
	```bash
	docker-compose logs web
    ```
- Reiniciar servicio web: 
	```bash
	docker-compose restart web
    ```
- Reiniciar Ollama: 
	```bash
	docker-compose restart ollama
    ```
- Detener servicios: 
	```bash
	docker-compose down
    ```
- Detener y eliminar volúmenes: 
	```bash
	docker-compose down -v
    ```

Comandos Django dentro del contenedor:

- Acceder al contenedor: 
	```bash
	docker-compose exec web bash
    ```
- Makemigrations: 
	```bash
	docker-compose exec web python manage.py makemigrations
    ```
- Migrate: 
	```bash
	docker-compose exec web python manage.py migrate
    ```
- Collectstatic: 
	```bash
	docker-compose exec web python manage.py collectstatic
    ```
- Shell: 
	```bash
	docker-compose exec web python manage.py shell
    ```



## GESTIÓN DE DATOS

Exportar datos:  
```bash
docker-compose exec web python manage.py dumpdata > backup.json
```
Importar datos:
```bash
docker-compose exec web python manage.py loaddata backup.json
```
Limpiar la base de datos (elimina todo):
```bash
docker-compose exec web python manage.py flush
```


## ESTRUCTURA DE LA BASE DE DATOS

El proyecto utiliza los siguientes modelos:

- Industry: industrias o rubros económicos.
    
- Sub_industry: subcategorías de industrias.
    
- Enterprise: empresas con relación a industrias.
    
- Contact: contactos empresariales asociados.
    



## CONFIGURACIÓN DEL ENTORNO

Variables de entorno principales:

- OLLAMA_HOST=[http://ollama:11434](http://ollama:11434)
    

- DEBUG=True (solo para desarrollo)
    
- ALLOWED_HOSTS=["*"] (solo para desarrollo)
    

Puertos utilizados:

- 8000: Servicio Django
    
- 11434: Ollama
    



## SOLUCIÓN DE PROBLEMAS

“No se puede conectar a Ollama”:

- docker-compose ps
    
- docker-compose restart ollama
    
- docker-compose logs ollama
    

“La base de datos está bloqueada”:

- docker-compose down
    
- docker-compose up
    

“El modelo LLaMA no se descarga”:

- docker-compose exec ollama ollama pull llama3.2
    

“Los cambios del código no se reflejan”:

- docker-compose up --build web
    



## DESARROLLO LOCAL (SIN DOCKER)

Instalar dependencias:  
```bash
pip install -r requirements.txt
```
Configurar variable de entorno:
```bash
export OLLAMA_HOST=[http://localhost:11434](http://localhost:11434)
```
Aplicar migraciones:
```bash
python manage.py migrate
```
Ejecutar la app:
```bash
python manage.py runserver
```
(Es necesario tener Ollama instalado y haber descargado el modelo LLaMA 3.2 localmente.)



## COMANDOS RESUMEN

Clonar repo y entrar:  
```bash
git clone <repo> && cd Valoriza
```
Levantar con build:
```bash
docker-compose up --build
```
Levantar en segundo plano:
```bash
docker-compose up --build -d
```
Crear superusuario:
```bash
docker-compose exec web python manage.py createsuperuser
```
Exportar datos:
```bash
docker-compose exec web django manage.py dumpdata > backup.json
```
Importar datos:
```bash
docker-compose exec web django manage.py loaddata backup.json
```
Descargar modelo LLaMA manualmente:
```bash
docker-compose exec ollama ollama pull llama3.2
```
Ver logs:
```bash
docker-compose logs
```