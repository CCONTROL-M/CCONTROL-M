try:
    import backend
    print('Módulo backend importado com sucesso!')
    
    try:
        from backend.app.main import app
        print('App importado com sucesso!')
    except Exception as e:
        print(f'Erro ao importar app: {str(e)}')
        
except Exception as e:
    print(f'Erro ao importar backend: {str(e)}') 