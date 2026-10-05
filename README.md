# Atividade DevOps com FastAPI

Aplicação inicial do exercício de Docker, GitHub Actions e Container Registry.
O endpoint `GET /hello` retorna `Hello World` em texto puro.

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
Hello World
```

A documentação interativa da API fica em <http://localhost:8080/docs>.
Para encerrar o servidor, pressione `Ctrl+C`.

## Criar a imagem Docker

Com o Docker em execução, rode na raiz do projeto:

```powershell
docker build -t atividadedevops:1.0 .
```

O `Dockerfile` utiliza Python 3.13, instala as dependências e inicia a aplicação
com Uvicorn na porta 8080. O `.dockerignore` exclui o ambiente virtual local e
outros arquivos desnecessários do contexto de build.

## Validar o container localmente

Na validação, a porta 8080 da máquina estava ocupada. Por isso, foi utilizada a
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
