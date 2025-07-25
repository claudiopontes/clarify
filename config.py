# Principais configurações do nosso sistema
DB_PATH = 'dados.db'

# Configurações do Flask
FLASK_HOST = '127.0.0.1'    # ou 0.0.0.0. para aceitar conexões de qualquer IP  
FLASK_PORT = 5000           # porta de acesso
FLASK_DEBUG = True          # coloque false para produção
FLASK_THREADED = True       # ativar o modo multi-threading
FLASK_USE_RELOADER = True   # atualizaçao automática para salvar o arquivo