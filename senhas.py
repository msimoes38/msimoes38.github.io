import os
import dotenv
import keyring


def compor_env(env_path: str = "", servico: str = "") -> None:
    """Auxilia a composição de um arquivo .env que contenha, em cada linha,
    um par do tipo: SERVICO_USUARIO="Nome de Usuário" ex.: GMAIL_USUARIO="jose.silva".

    Args:
        env_path (str): caminho completo até um arquivo .env já existente.

        servico (str): representa parte de uma chave de dicionário, um termo pelo qual
        a entrada correspondente será encontrada. A entrada, no caso presente, é o 
        efetivo login/"nome de usuário" para o serviço envolvido.

    Returns:
        Nada (None).
    """    
    servico = servico.upper()
    if env_path == "": 
        env_path = os.path.join(os.path.dirname(__file__), ".env")

    usuario_temp = input("Digite o login para o serviço desejado: ")
    with open(env_path, "a") as f:
        f.writelines(f'\n{servico}_USUARIO="{usuario_temp}"')

    dotenv.load_dotenv(env_path)


def armazenar_senha(servico: str = ""):
    """Auxilia o armazenamento seguro, criptografado, de senhas.

    Args:
        servico (str): representa parte de uma chave de dicionário, um termo pelo qual
        a entrada correspondente será encontrada. A entrada, no caso presente, é o 
        efetivo login/"nome de usuário" para o serviço envolvido.

    Returns:
        Nada (None).
    """        
    # Variáveis que você pode customizar:
    SVC_USU_ENV = servico + "_USUARIO"

    # Configurando caminhos:
    project_path = os.path.dirname(__file__)
    env_path = os.path.join(project_path, ".env")

    # Garante que haja um arquivo de texto com os logins que se deseje
    # utilizar para acesso:
    if not os.path.isfile(env_path): 
        compor_env(env_path, servico)

        # MINHA ALTERAÇÃO - PEDE SENHA NOVAMENTE
        login = os.environ[SVC_USU_ENV]
        senha = input(f"Digite a senha para o serviço/login ({SVC_USU_ENV}/{login}): ")
        print("A senha foi encriptada e armazenada seguramente no Windows Credential Locker.")                          
        keyring.set_password(servico, login, senha)
        senha = None

    else:
        dotenv.load_dotenv(env_path)

    # Definindo variáveis básicas:
    try:
        login = os.environ[SVC_USU_ENV]
    except KeyError as e:
        compor_env(env_path, servico)

        # MINHA ALTERAÇÃO - PEDE SENHA NOVAMENTE
        login = os.environ[SVC_USU_ENV]
        senha = input(f"Digite a senha para o serviço/login ({SVC_USU_ENV}/{login}): ")
        print("A senha foi encriptada e armazenada seguramente no Windows Credential Locker.")                          
        keyring.set_password(servico, login, senha)
        senha = None

    finally:
        login = os.environ[SVC_USU_ENV]

    if not keyring.get_password(servico, login):
        senha = input(f"Digite a senha para o serviço/login ({SVC_USU_ENV}/{login}): ")
        print("A senha foi encriptada e armazenada seguramente no Windows Credential Locker.")                          
        keyring.set_password(servico, login, senha)
        senha = None


# Exemplo com RECOMENDAÇÃO de uso por meio de um exemplo: (krnunes)
# Criando instância de Pepe.SpSemPapel e efetuando login nela:
#   import senhas
#   from pepe import SpSemPapel

#   o nome do serviço é de livre digitação, mas mantenha consistência 
#   para que você mesmo possa saber como registrou o nome do serviço para 
#   poder recuperar login/senha atrelados a ele:

#   S_SP = "SPSEMPAPEL"
#   SP_USU_ENV = S_SP + "_USUARIO"
#
#   senhas.armazenar_senha(S_SP)
#   login = os.environ[SP_USU_ENV]
#
#   sp = SpSemPapel(True)
#   sp.login(login, keyring.get_password(S_SP, login))

# !!! Note que acima, passa-se a senha DIRETAMENTE como argumento,
# em vez de, como abaixo (NÃO RECOMENDADO), criar-se uma variável que
# armazene a senha como intermediária:
#   [...]
#   senha = keyring.get_password(S_SP, sp_login)
#   sp.login(sp_login, senha)
