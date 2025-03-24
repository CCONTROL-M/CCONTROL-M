=== COMANDO "LIGAR OS MOTORES" ===

Existem várias maneiras de usar o comando "Ligar os motores" para iniciar rapidamente os serviços do CCONTROL-M:

OPÇÃO 1: EXECUÇÃO DIRETA
------------------------
Simplesmente clique duas vezes no arquivo "ligar_motores.cmd" no explorador de arquivos.


OPÇÃO 2: USANDO O ATALHO
------------------------
Clique duas vezes no arquivo "ligar_os_motores.bat" no explorador de arquivos.
Este é um atalho que executa o comando principal.


OPÇÃO 3: CONFIGURAÇÃO NO POWERSHELL
----------------------------------
Para configurar o comando no PowerShell e poder digitar "Ligar os motores":

1. Abra o PowerShell na pasta do projeto
2. Execute o comando:
   . .\comando_personalizado.ps1

3. Agora você pode usar:
   - Digite simplesmente "Ligar" 
   - Ou digite a frase completa "Ligar os motores"


OPÇÃO 4: CONFIGURAÇÃO PERMANENTE (AVANÇADO)
------------------------------------------
Para tornar o comando permanentemente disponível em qualquer PowerShell:

1. Encontre o perfil do PowerShell executando:
   echo $PROFILE

2. Edite o arquivo do perfil (ou crie-o se não existir):
   notepad $PROFILE

3. Adicione esta linha ao arquivo:
   . "C:\caminho\completo\para\o\projeto\CCONTROL-M\comando_personalizado.ps1"

4. Salve o arquivo e reinicie o PowerShell

Agora o comando "Ligar os motores" estará disponível em qualquer sessão do PowerShell. 