# Instruções de utilização

## Módulo de Serviços e Execução de Atendimentos

A aplicação Flask inclui endpoints JSON e interface web para catálogo de serviços e execução de atendimentos, definidos dentro do escopo do Desenvolvedor 3. Após entrar no sistema, acesse `/servicos` e `/atendimentos`. Consulte [SERVICES_API.md](SERVICES_API.md) para documentação de entidades, endpoints, exemplos, dependências de integração e instruções de teste.

### Executar localmente no Windows

Abra o PowerShell na raiz do repositório (`C:\SRBeauty`) e ative o ambiente virtual:

```powershell
.\venv\Scripts\Activate.ps1
Set-Location .\pmv-ads-2026-2-e5-proj-empext-t6-SRBeauty\codigo-fonte
python app.py
```

Acesse `http://127.0.0.1:5000`. Se o comando `python` não for reconhecido ou a ativação estiver bloqueada, execute diretamente pelo ambiente virtual, ainda na pasta `codigo-fonte`:

```powershell
& ..\..\venv\Scripts\python.exe app.py
```

## Módulos integrados

Agenda, serviços, atendimentos, repasses, financeiro e relatórios são servidos pela mesma aplicação Flask. Depois de autenticar como proprietária, use `/repasses`, `/financeiro` e `/relatorios`; não é necessário iniciar um servidor FastAPI separado. As páginas e APIs financeiras exigem acesso de proprietária.

No desenvolvimento, `srbeauty.db` é o banco único de usuários, serviços, atendimentos, repasses, financeiro e relatórios. Repasses compartilha as tabelas principais porque seus cálculos dependem dos serviços concluídos e dos profissionais existentes. Ao iniciar, a aplicação cria as tabelas que faltarem nesse banco.

Para importar os lançamentos do banco financeiro anterior (`Financeiro e Relatorios/salao_financeiro.db`) para o banco principal, execute uma vez na pasta `codigo-fonte`:

```powershell
python -m flask --app app migrate-finance-db
```

O comando preserva os IDs, os lançamentos, os fechamentos e as taxas; pode ser repetido com segurança. O arquivo anterior é mantido como cópia de origem e não é mais usado pela aplicação. Em hospedagem, configure `DATABASE_URL` com o banco persistente (por exemplo, PostgreSQL) e execute o mesmo comando para importar os dados iniciais. Configure também `SECRET_KEY` com um valor secreto próprio antes de publicar.

As páginas do financeiro estão protegidas pela sessão do sistema e chamam APIs no mesmo domínio, sem depender de `localhost` ou de uma porta separada.

Para rodar os testes, na mesma pasta e com o ambiente virtual ativo:

```powershell
python -m unittest discover -s tests -v
```

## Estratégia de Organização de Codificação 

Nesse primeiro eixo do curso, para simplificar a utilização do Git e a organização das pastas e artefatos de implementação no sistema de arquivos, sugerimos que o projeto seja estruturado de modo que cada aluno trabalhe com seus arquivos nas suas respectivas pastas, identificadas por nomes das suas respectivas telas. Por exemplo:
- Pasta src (root do projeto): index.html, index.css, index.js - Desenvolvedora responsável: Maria.
- Pasta src\clientes: clientes.html, clientes.css, clientes.js - Desenvolvedor responsável: João.
- Pasta src\funcionarios: funcionarios.html, funcionarios.css, funcionarios.js  - Desenvolvedora responsável: Silvia.

## Instalação do Site

O site em HTML/CSS/JS é um projeto estático, logo pode ser utilizado tanto em servidores como em navegadores web. Clique <a href="https://icei-puc-minas-pmv-ads.github.io/pmv-ads-2022-1-e1-proj-web-t3-vida-de-estudante/src/paginaHome/index.html">aqui</a> para acessá-lo. 

## Histórico de versões

### [0.1.0] - 03/05/2022
#### Adicionado
- Homepage: arquivos HTML, CSS, JS e imagens.

### [0.1.1] - 15/05/2022
#### Atualizado
- Homepage: arquivos HTML, CSS, JS e imagens.

#### Adicionado
- Livros: arquivos HTML, CSS, JS e imagens.
- Tutorias: arquivo HTML.
- Cadastro: arquivos HTML e CSS.
- Login: arquivos HTML e CSS.

### [0.1.2] - 10/06/2022
#### Atualizado
- Homepage: arquivos HTML, CSS, JS e imagens.
- Livros: arquivos HTML, CSS, JS e imagens.
- Tutorias: arquivos HTML, CSS, JS e imagens.
- Cadastro: arquivos HTML, CSS e JS.
- Login: arquivos HTML, CSS e JS.

#### Adicionado
- Perfil: arquivos HTML, CSS, JS e imagens.

### [0.1.3] - 22/06/2022
#### Atualizado
- Homepage: arquivos HTML, CSS, JS e imagens.
- Livros: arquivos HTML, CSS, JS e imagens.
- Tutorias: arquivos HTML, CSS, JS e imagens.
- Cadastro: arquivos HTML, CSS e JS.
- Login: arquivos HTML, CSS e JS.
- Perfil: arquivos HTML, CSS, JS e imagens.
