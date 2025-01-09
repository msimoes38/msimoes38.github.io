import os
import sys
from datetime import datetime
from pathlib import Path
import openai
# from git import Repo
from bs4 import BeautifulSoup
from tkinter import filedialog, Tk
import keyring
import senhas

# Configuração para pegar a API_Key
S_OPENAI = "OPENAI"
OPENAI_USU_ENV = S_OPENAI + "_USUARIO"
senhas.armazenar_senha(S_OPENAI)
USUARIO_OPEN_AI = os.environ[OPENAI_USU_ENV]
# openai.api_key = keyring.get_password(S_OPENAI, USUARIO_OPEN_AI)
chave_api = keyring.get_password(S_OPENAI, USUARIO_OPEN_AI)


# Definindo os Paths
PATH_TO_BLOG_REPO = Path(
    r".git"
)
PATH_TO_BLOG = PATH_TO_BLOG_REPO.parent
PATH_TO_CONTENT = PATH_TO_BLOG / "content"
PATH_TO_CONTENT.mkdir(exist_ok=True, parents=True)

SETORES = [
    '0 - História da Tributação',
    '1 - Introduction to the New Testament History and Literature',
    '2 - Bíblia Estudo',
]


def update_blog(commit_message="atualizacao blog"):
    """
    Adiciona as alterações no repositório ao Github
    """
    repo = Repo(PATH_TO_BLOG_REPO) # noqa
    repo.git.add(all=True)
    repo.index.commit(commit_message)
    origin = repo.remote(name="origin")
    origin.push()
    # repo.git.gc(auto=True)  # Executar coleta de lixo


def validar_nome_diretorio(nome):
    return ''.join(c for c in nome if c.isalnum() or c in (' ', '_', '-')).strip()


def create_new_blog(titulo, conteudo, setor):
    """
    Gera um novo "blog" em um arquivo HTML na pasta content
    """
    setor = validar_nome_diretorio(setor)
    setor_path = PATH_TO_CONTENT / setor.strip()
    setor_path.mkdir(exist_ok=True)
    
    # Critérios para nomear o novo arquivo HTML do blog
    files = len(list(PATH_TO_CONTENT.glob("*.html")))
    agora = datetime.now()
    agora_string = agora.strftime("%d-%m-%Y_at_%H-%M")
    novo_titulo = f"Post_{files + 1}_{agora_string}_{setor.strip().replace(' ', '_')}.html"
    path_to_new_content = setor_path / novo_titulo

    if not os.path.exists(path_to_new_content):
        with open(path_to_new_content, "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html>\n")
            f.write("<html>\n")
            f.write("<head>\n")
            f.write("<style>\n")
            f.write("""
                body {
                    font-family: Arial, sans-serif;
                    font-size: calc(min(max(16px, 4vw), 22px));  /* Adapta o tamanho da fonte à largura da tela entre 16px e 22px */
                }
                img {
                    max-width: 50%;
                    height: auto;
                    display: block;
                    margin: 0 auto;
                }
                h1 {
                    color: #333;
                    font-size: calc(min(max(24px, 6vw), 30px));  /* Título maior que o texto normal entre 24px e 30px */
                }
                .container {
                    width: 90%;
                    margin: auto;
                    max-width: 800px;
                }
                .prompt {
                    font-size: 12px;  /* Tamanho da fonte do texto em letras miúdas */
                    color: #666;  /* Cor do texto em letras miúdas */
                    margin-top: 20px;  /* Espaço acima do texto em letras miúdas */
                }
                @media (max-width: 800px) {
                    .container {
                        width: 100%;
                    }
                }
            """)
            f.write("</style>\n")
            f.write(f"<title> {titulo} </title>\n")
            f.write("</head>\n")

            f.write("<body>\n")
            f.write("<div class='container'>\n")
            f.write(
                "<a href='/index.html'>HOME</a> <br />\n"
            )
            f.write(
                '<a href="javascript:history.back()">Voltar</a> <br />\n'
            )
            f.write(f"<h1> {titulo} </h1>")
            f.write(conteudo)
            f.write("</div>\n")
            f.write("</body>\n")
            f.write("</html>\n")
            print("HTML do texto criado!")

            return path_to_new_content

    else:
        raise FileExistsError(f"O arquivo {path_to_new_content} já existe!")


def check_for_duplicate_links(path_to_new_content, links):
    urls = [str(link.get("href")) for link in links]
    content_path = str(Path(*path_to_new_content.parts[-3:]))
    return content_path in urls


def write_to_index(titulo, path_to_new_content, setor):
    """
    Atualiza os links no índice principal e na página do setor.
    """
    # Limpeza do nome do setor para evitar espaços extras e caracteres inválidos
    setor = validar_nome_diretorio(setor)

    # Atualizar o índice principal
    with open(PATH_TO_BLOG / "index.html", "r", encoding="utf-8") as index:
        soup = BeautifulSoup(index.read(), "html.parser")
    links = soup.find_all("a")
    last_link = links[-1] if links else None

    setor_index_path = PATH_TO_CONTENT / setor / "index.html"
    setor_relative_path = str(Path("content") / setor / "index.html").replace("\\", "/")

    if not any(link.get("href") == setor_relative_path for link in links):
        link_to_setor = soup.new_tag("a", href=setor_relative_path)
        link_to_setor.string = setor
        novo_paragrafo = soup.new_tag("p")
        novo_paragrafo.append(link_to_setor)
        if last_link:
            last_link.insert_after(novo_paragrafo)
        else:
            soup.body.append(novo_paragrafo)

        with open(PATH_TO_BLOG / "index.html", "w", encoding="utf-8") as f:
            f.write(str(soup.prettify(formatter="html")))

    # Atualizar a página do setor
    if not setor_index_path.exists():
        setor_index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(setor_index_path, "w", encoding="utf-8") as setor_index:
            setor_index.write(
                "<!DOCTYPE html>\n"
                "<html>\n"
                "<head>\n"
                "<style>\n"
                """
                body {
                    font-family: Arial, sans-serif;
                }
                .container {
                    width: 90%;
                    margin: auto;
                    max-width: 800px;
                }
                h2, h3 {
                    color: #333;
                    text-align: center;
                }
                .post-list {
                    list-style: none;
                    padding: 0;
                }
                .post-list li {
                    margin: 10px 0;
                    padding: 10px;
                    border: 1px solid #ddd;
                }
                .post-list a {
                    text-decoration: none;
                    color: #007BFF;
                }
                .post-list a:hover {
                    text-decoration: underline;
                }
                @media (max-width: 800px) {
                    .container {
                        width: 100%;
                    }
                }
                """
                "</style>\n"
                f"<title> {setor} </title>\n"
                "</head>\n"
                "<body>\n"
                "<div class='container'>\n"
                f"<h2> {setor} </h2>\n"
                "<ul class='post-list'>\n"
                "</ul>\n"
                "</div>\n"
                "</body>\n"
                "</html>\n"
            )

    with open(setor_index_path, "r", encoding="utf-8") as setor_index:
        soup_setor = BeautifulSoup(setor_index.read(), "html.parser")
    setor_links = soup_setor.find_all("a")
    last_setor_link = setor_links[-1] if setor_links else None  # noqa

    if not check_for_duplicate_links(path_to_new_content, setor_links):
        setor_link_to_new_blog = soup_setor.new_tag(
            "a", href=Path(*path_to_new_content.parts[-1:]).as_posix()
        )
        setor_link_to_new_blog.string = titulo
        setor_list_item = soup_setor.new_tag("li")
        setor_list_item.append(setor_link_to_new_blog)
        ul = soup_setor.find("ul", class_="post-list")
        if ul:
            ul.append(setor_list_item)
        else:
            ul = soup_setor.new_tag("ul", class_="post-list")
            ul.append(setor_list_item)
            soup_setor.body.append(ul)

    with open(setor_index_path, "w", encoding="utf-8") as f:
        f.write(str(soup_setor.prettify(formatter="html")))


def create_prompt(titulo, resumo='dissertar de acordo com o Título'):
    prompt = f"""Tenho um Blog sobre Direito Tributário.
    Quero escrever um Artigo sobre a História da Tributação, da seguinte forma.
    Título do artigo: {titulo}.
    Resumo: {resumo}.
    As informações devem ser fidedignas. 
    Incluir citações expressas das fontes das informações (livros, artigos e respectivos autores, no formato ABNT - desde que realmente existentes).
    Gere apenas os parágrafos do texto com a tag HTML correspondente (<p></p>).
    """
    return prompt


def get_setor(setores):
    for setor in setores:
        print(setor)
    print('-------------------------------------------------------')
    n_setor = int(input('Digite o número correspondente ao setor: '))
    return validar_nome_diretorio(setores[n_setor])


def get_texto_arquivo():
    while True:
        root = Tk()
        root.wm_attributes('-topmost', 1)
        caminho = filedialog.askopenfilename(parent=root, initialdir=os.path.abspath('textos'))
        root.destroy()
        
        if caminho:
            return caminho            
        else:
            print('Você deve escolher um ou mais arquivos para juntar ao expediente.')
            sair = input('Aperte qualquer tecla para continuar ou digite SAIR para cancelar. ')
            if sair.upper() == 'SAIR':
                print('Você cancelou a inserção de anexos.')
                return None


if __name__ == "__main__":
    setor = get_setor(setores=SETORES)
    titulo = input("Digite o título: ")
    texto_pronto = input('Você já possui o texto da publicação?(S/N): ')

    if texto_pronto.upper() == 'N':
        resumo_para_gpt = input("Digite um breve resumo sobre o que deseja: ")
        if len(resumo_para_gpt) > 2:
            prompt = create_prompt(titulo, resumo_para_gpt)
        else:
            prompt = create_prompt(titulo) 

        client = openai.OpenAI(
            api_key=chave_api,  # this is also the default, it can be omitted
        )

        resposta_texto = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=2000,
            temperature=0.7,
        )
        texto_conteudo = resposta_texto.choices[0].message.content
    elif texto_pronto.upper() == 'S':
        caminho_arquivo_texto = get_texto_arquivo()
        with open(caminho_arquivo_texto, 'r', encoding="utf-8") as arquivo_texto:
            texto_conteudo = arquivo_texto.read()
    else:
        sys.exit('Opção inválida. Script encerrado.')
        
    novo_conteudo = create_new_blog(titulo, texto_conteudo, setor)
    write_to_index(titulo, novo_conteudo, setor)
