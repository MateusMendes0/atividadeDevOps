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
Após instalar as dependências, o build remove o pip, que não é necessário para
executar a API e incluía bibliotecas vulneráveis na imagem base. A pipeline
também inicia um container e confirma a resposta de `/hello` antes das análises.

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
a execução automática em pushes para `main`, além da abertura, reabertura e
atualização de Pull Requests para `main`. Novos pushes na `feat/devsecops`
atualizam o PR aberto e executam essas verificações. O fluxo é:

1. Executar Gitleaks, testes e Trivy nas dependências, além do SonarCloud
   com a cobertura gerada pelos testes.
2. Após a aprovação dessas verificações, construir a imagem Docker.
3. Gerar o SBOM da imagem com Syft e analisar a imagem com Trivy.
4. Salvar os relatórios e o SBOM como artifacts da execução.
5. Somente em push para `main`, publicar a imagem no GHCR após todas as
   verificações obrigatórias passarem.

A autenticação utiliza `secrets.GITHUB_TOKEN`, fornecido automaticamente pelo
GitHub Actions, com as permissões `contents: read` e `packages: write` declaradas
no job `build-and-push`. O job Gitleaks tem apenas `contents: read`.
Não é necessário cadastrar um token manualmente para este fluxo.

A versão da imagem é definida em `IMAGE_VERSION`, atualmente `2.0`.
O push para `main` dispara uma nova execução da pipeline e publica essa tag.

## Segurança com Gitleaks

O check **Gitleaks** utiliza a imagem Docker oficial
`ghcr.io/gitleaks/gitleaks:v8.30.1`, executada diretamente pelo GitHub Actions,
com as regras padrão da ferramenta. Não exige instalação manual nem um secret
ou token adicional.

O checkout usa `fetch-depth: 0`, e a análise usa `gitleaks git` com
`--log-opts=--all` para examinar todo o histórico das referências disponíveis
no checkout. Assim, uma credencial pode ser detectada mesmo após ser removida
da versão atual de um arquivo.

Uma possível credencial exposta faz a verificação terminar com código `1`.
Como `build-and-push` depende desse job, a falha impede o build e a publicação
da imagem. Erros ao baixar a imagem do Gitleaks ou executar a análise também
fazem o job falhar.
Pushes na branch de implementação e Pull Requests nunca publicam imagens.

Os logs mostram o local das detecções, e `--redact=100` oculta os valores dos
secrets nos logs e no relatório. O arquivo JSON fica disponível no artifact
`gitleaks-report` por 14 dias, inclusive quando a análise encontra problemas.
Se a execução falhar antes de gerar o relatório, o artifact não estará disponível.

Testes de detecção devem usar somente credenciais fictícias. Não inclua uma
credencial de teste no histórico principal: mesmo apagando o arquivo em outro
commit, o histórico continuará contendo a detecção. As validações locais de
detecção podem ser feitas em um repositório temporário separado.

Os resultados da validação local estão em
[evidencias/validacao-gitleaks-local.txt](evidencias/validacao-gitleaks-local.txt).
Esses testes não substituem a evidência de execução do GitHub Actions e do
bloqueio de merge exigida pela atividade.

O Gitleaks e o build também foram aprovados no GitHub Actions. Os links e os
resultados estão em
[evidencias/validacao-gitleaks-github.txt](evidencias/validacao-gitleaks-github.txt).

## Testes da aplicação

O teste automatizado verifica o status HTTP, a mensagem `Hello World 2` e o
tipo de resposta em texto puro do endpoint `/hello`. Para executar localmente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m coverage run --branch --source=main -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m coverage xml
```

O relatório `coverage.xml` é disponibilizado no artifact `cobertura`.

## Análise de vulnerabilidades com Trivy

O Trivy analisa os arquivos de dependências do projeto e a imagem Docker
construída. Cada análise gera um relatório JSON com todas as severidades,
incluindo vulnerabilidades sem correção disponível.

Uma segunda verificação bloqueia a execução quando encontra vulnerabilidades
**HIGH** ou **CRITICAL** com correção disponível. Vulnerabilidades **LOW** e
**MEDIUM** ficam registradas no relatório e não bloqueiam a execução.
Erros na ferramenta ou na obtenção da base de vulnerabilidades fazem o job
falhar; o código de saída zero da etapa de relatório não desativa o bloqueio.

Os artifacts `trivy-dependencias` e `trivy-imagem` guardam os relatórios por
14 dias, inclusive quando a verificação seguinte encontra uma vulnerabilidade.

## SBOM da imagem com Syft

O Syft, executado pela action `anchore/sbom-action`, gera o inventário dos
componentes e versões da imagem que acabou de ser construída. O arquivo
`sbom.spdx.json` fica disponível no artifact `sbom-imagem` por 14 dias.
O SBOM é gerado antes do bloqueio do Trivy na imagem, permitindo consultar
seus componentes mesmo quando essa verificação reprova a imagem.

Os resultados aprovados no GitHub Actions estão em
[evidencias/validacao-devsecops-github.txt](evidencias/validacao-devsecops-github.txt).
O bloqueio inicial da imagem e a correção estão registrados em
[evidencias/validacao-trivy-bloqueio.txt](evidencias/validacao-trivy-bloqueio.txt).

## SonarCloud

O job **SonarCloud** analisa a aplicação Python, o Dockerfile e os workflows,
além de importar a cobertura dos testes. O arquivo `sonar-project.properties`
identifica a organização `mateusmendes0` e o projeto
`MateusMendes0_atividadeDevOps`. A autenticação usa o secret `SONAR_TOKEN`
cadastrado no GitHub.

O projeto utiliza o Quality Gate **Sonar way**, voltado ao código novo:

- Classificação A em segurança, confiabilidade e manutenibilidade.
- Cobertura mínima de 80%.
- Duplicação máxima de 3%.
- Revisão de 100% dos security hotspots.

A opção `sonar.qualitygate.wait=true` faz a análise aguardar o resultado do
Quality Gate. Se o gate reprovar, a execução falha e impede o build e a
publicação da imagem. A análise roda em PRs para `main` e em pushes para `main`.

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
