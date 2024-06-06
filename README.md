
<h2 align="center"> 🚀Instalación </h2>

1. Clonar el repositorio:
    ```sh
    git clone https://github.com/JhosueArrieta/lahuertadeabril---backend.git
    ```
2. Configurar el backend:
    ```sh
    cd lahuertadeabril---backend/LaHuertaDeAbril
    python -m venv venv
    source venv/bin/activate  # En Windows usar `venv\Scripts\activate`
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver
    ```
