import os
from datetime import datetime
from pathlib import Path
import openai
from git import Repo
from bs4 import BeautifulSoup as Soup
import keyring
import senhas

# Configuração para pegar a API_Key
S_OPENAI = "OPENAI"
OPENAI_USU_ENV = S_OPENAI + "_USUARIO"
senhas.armazenar_senha(S_OPENAI)
USUARIO_OPEN_AI = os.environ[OPENAI_USU_ENV]
openai.api_key = keyring.get_password(S_OPENAI, USUARIO_OPEN_AI)


# Definindo os Paths
PATH_TO_BLOG_REPO = Path(
    r"C:\Users\msimo\OneDrive\Documents\Dev\msimoes38.github.io\.git"
)
PATH_TO_BLOG = PATH_TO_BLOG_REPO.parent
PATH_TO_CONTENT = PATH_TO_BLOG / "content"
PATH_TO_CONTENT.mkdir(exist_ok=True, parents=True)

# git.cmd.Git.AUTO_GC = False


def update_blog(commit_message="atualizacao blog"):
    """
    Adiciona as alterações no repositório ao Github
    """
    repo = Repo(PATH_TO_BLOG_REPO)
    repo.git.add(all=True)
    repo.index.commit(commit_message)
    origin = repo.remote(name="origin")
    origin.push()
    # repo.git.gc(auto=True)  # Executar coleta de lixo


def create_new_blog(titulo, conteudo, cover_image=Path(r"midia\tax_logo.jpg")):
    """
    Gera um novo "blog" em um arquivo HTML na pasta content
    """
    # Imagem a ser adicionada ao topo do blog
    cover_image = Path(cover_image)
    # Critérios para nomear o novo arquivo HTML do blog
    files = len(list(PATH_TO_CONTENT.glob("*.html")))
    agora = datetime.now()
    agora_string = agora.strftime("%d-%m-%Y_at_%H-%M")
    novo_titulo = f"Post_{files + 1}_{agora_string}.html"
    path_to_new_content = PATH_TO_CONTENT / novo_titulo

    # Escreve o código HTML
    if not os.path.exists(path_to_new_content):
        with open(path_to_new_content, "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html>\n")
            f.write("<html>\n")
            f.write("<head>\n")
            f.write(f"<title> {titulo} </title>\n")
            f.write("</head>\n")

            f.write("<body>\n")
            # f.write(f"<img src='{cover_image.name}' alt='Cover Image'> <br />\n") # forma original do curso (leva em consideração que a imagem está na mesma pasta do conteudo.)
            f.write(
                f"<img src='../{cover_image}' alt='Cover Image' width='50'> <br />\n"
            )
            f.write(f"<h1> {titulo} </h1>")
            # f.write(conteudo.replace("\n", "<br />\n")) # desncessário, pois vou pedir no prompt que texto retorne com as tags <p>
            f.write(conteudo)
            f.write("</body>\n")
            f.write("</html>\n")
            print("Blog created")

            return path_to_new_content
    else:
        raise FileExistsError(f"O arquivo {path_to_new_content} já existe!")


def check_for_duplicate_links(path_to_new_content, links):
    urls = [str(link.get("href")) for link in links]
    content_path = str(Path(*path_to_new_content.parts[-2:]))
    return content_path in urls


def write_to_index(titulo, path_to_new_content):
    """
    Insere o link do novo blog em Index
    """
    with open(PATH_TO_BLOG / "index.html", "r", encoding="utf-8") as index:
        soup = Soup(index.read())
    links = soup.find_all("a")
    last_link = links[-1]

    if check_for_duplicate_links(path_to_new_content, links):
        raise ValueError("O link já existe!")
    link_to_new_blog = soup.new_tag("a", href=Path(*path_to_new_content.parts[-2:]))
    link_to_new_blog.string = f"{titulo} - {path_to_new_content.name.split('.')[0]}"
    novo_paragrafo = soup.new_tag("p")
    novo_paragrafo.append(link_to_new_blog)
    last_link.insert_after(novo_paragrafo)

    with open(PATH_TO_BLOG / "index.html", "w", encoding="utf-8") as f:
        f.write(str(soup.prettify(formatter="html")))


def create_prompt(titulo):
    prompt = f"""Blog Direito Tributário
    Estou fazendo um texto para o meu blog sobre a história da tributação.
    Poderia fazer um artigo com o seguinte título: {titulo}
    As informações devem ser fidedignas. 
    Sempre que possível, as fontes das informações (livros, artigos e respectivos autores) devem ser citadas (desde que realmente existentes).
    Por favor, gere apenas os parágrafos do texto com a tag HTML correspondente (<p></p>)
    """
    return prompt


if __name__ == "__main__":
    titulo = input("Digite o título: ")
    resposta_texto = openai.Completion.create(
        model="text-davinci-003",
        prompt=create_prompt(titulo),
        max_tokens=2000,
        temperature=0.7,
    )

    texto_conteudo = resposta_texto["choices"][0]["text"]
    novo_conteudo = create_new_blog(titulo, texto_conteudo)
    write_to_index(titulo, novo_conteudo)
    update_blog()
