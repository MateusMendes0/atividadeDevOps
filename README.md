# Atividade DevOps com FastAPI

Aplicação do exercício de Docker, GitHub Actions e Container Registry.
Na versão atual (`2.0`), o endpoint `GET /hello` retorna `Hello World 2` em texto puro.

## Executar localmente

Requisito: Python 3.10 ou superior. No PowerShell, na pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8080
```

Abra <http://localhost:8080/hello> no navegador ou, em outro terminal, execute:

```powershell
curl.exe http://localhost:8080/hello
```

Resposta esperada:

```text
Hello World 2
```

A documentação interativa da API fica em <http://localhost:8080/docs>.
Para encerrar o servidor, pressione `Ctrl+C`.

## Criar a imagem Docker

Com o Docker em execução, rode na raiz do projeto:

```powershell
docker build -t atividadedevops:2.0 .
```

O `Dockerfile` utiliza Python 3.13, instala as dependências e inicia a aplicação
com Uvicorn na porta 8080. O `.dockerignore` exclui o ambiente virtual local e
outros arquivos desnecessários do contexto de build.

## Validação local da versão 1.0

Na primeira validação, a porta 8080 da máquina estava ocupada. Por isso, foi utilizada a
porta externa 8081, mantendo a aplicação na porta 8080 dentro do container:

```powershell
docker run -d --name atividadedevops-v1 -p 8081:8080 atividadedevops:1.0
curl.exe -i http://localhost:8081/hello
```

Resultado confirmado: status `HTTP/1.1 200 OK` e corpo `Hello World`.
O container iniciou sem erros e permaneceu em execução, sem reinicializações.

Para consultar o estado e os logs:

```powershell
docker ps --filter name=atividadedevops-v1
docker logs atividadedevops-v1
```

As evidências estão em [evidencias/validacao-local-v1.txt](evidencias/validacao-local-v1.txt).

Para parar o container e, posteriormente, iniciar o mesmo container novamente:

```powershell
docker stop atividadedevops-v1
docker start atividadedevops-v1
```

## Validar a versão 2.0 localmente

Em uma porta livre, execute a imagem local da nova versão:

```powershell
docker run --rm -p 8082:8080 atividadedevops:2.0
```

Em outro terminal:

```powershell
curl.exe -i http://localhost:8082/hello
```

Resposta esperada: status `HTTP/1.1 200 OK` e corpo `Hello World 2`.

## Pipeline do GitHub Actions

O arquivo [.github/workflows/docker.yml](.github/workflows/docker.yml) configura
a execução automática em cada push para a branch `main`. O fluxo é:

1. Baixar o código do repositório.
2. Construir a imagem com o `Dockerfile` da raiz.
3. Verificar a existência da imagem com `docker image inspect`.
4. Autenticar no GitHub Container Registry (GHCR).
5. Publicar `ghcr.io/mateusmendes0/atividadedevops:2.0`.

A autenticação utiliza `secrets.GITHUB_TOKEN`, fornecido automaticamente pelo
GitHub Actions, com as permissões `contents: read` e `packages: write` declaradas
no workflow. Não é necessário cadastrar um token manualmente para este fluxo.

A versão da imagem é definida em `IMAGE_VERSION`, atualmente `2.0`.
O push para `main` dispara uma nova execução da pipeline e publica essa tag.

## Versões da imagem no GHCR

| Imagem | Resposta de `GET /hello` |
| --- | --- |
| `ghcr.io/mateusmendes0/atividadedevops:1.0` | `Hello World` |
| `ghcr.io/mateusmendes0/atividadedevops:2.0` | `Hello World 2` |

A atualização da pipeline para a tag `2.0` preserva a tag `1.0` no registry.
A primeira publicação foi concluída nesta [execução do GitHub Actions](https://github.com/MateusMendes0/atividadeDevOps/actions/runs/37359216432).

As evidências do download e da execução da imagem `1.0` publicada estão em
[evidencias/validacao-registry-v1.txt](evidencias/validacao-registry-v1.txt).
As evidências do build e do teste local da versão `2.0` estão em
[evidencias/validacao-local-v2.txt](evidencias/validacao-local-v2.txt).
