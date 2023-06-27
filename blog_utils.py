import os
import sys
from pathlib import Path
import string
import random
import openai
from git import Repo

# Definindo os Paths
PATH_TO_BLOG_REPO = Path(r'C:\Users\msimo\OneDrive\Documents\Dev\msimoes38.github.io\.git')
PATH_TO_BLOG = PATH_TO_BLOG_REPO.parent
PATH_TO_CONTENT = PATH_TO_BLOG / "content"

PATH_TO_CONTENT.mkdir(exist_ok=True, parents=True)

def random_string(tamanho):
    letras = string.ascii_lowercase + '\n'

    return ''.join(random.choice(letras) for i in range(tamanho))

# print(random_string(20))

def update_blog(commit_message='atualizacao blog'):
    repo = Repo(PATH_TO_BLOG_REPO)
    repo.git.add(all=True)
    repo.index.commit(commit_message)
    origin = repo.remote(name='origin')
    origin.push()

# Criando uma string aleatório, alterando o index.html e atualizando o git repo
random_blogpost = random_string(1000)
with open('index.html', 'a') as f:
    f.write(random_blogpost)
update_blog()
