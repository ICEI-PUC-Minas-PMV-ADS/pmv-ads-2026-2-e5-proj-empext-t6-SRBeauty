
# Metodologia

## Gerenciamento de Projeto

O desenvolvimento do SR Beauty adota práticas inspiradas em metodologias ágeis, com uma adaptação do Scrum para a organização e acompanhamento das atividades do projeto.

O trabalho é dividido em etapas e sprints, permitindo que as funcionalidades e demais entregas sejam desenvolvidas de forma incremental. As atividades são organizadas a partir das necessidades do projeto e dos requisitos definidos para o sistema, possibilitando revisões e ajustes ao longo do desenvolvimento.

Para o acompanhamento das tarefas, é utilizado um quadro no GitHub Projects seguindo uma organização semelhante ao Kanban, permitindo visualizar atividades pendentes, em desenvolvimento e concluídas. Esse processo auxilia na definição de prioridades e no acompanhamento do progresso das entregas.

O GitHub também é utilizado para o controle de versão do código-fonte e da documentação, permitindo que as alterações realizadas durante o desenvolvimento sejam registradas e integradas ao projeto de forma organizada.

A aplicação dessas práticas busca manter o desenvolvimento estruturado, facilitar o acompanhamento das atividades e permitir que o projeto evolua de maneira incremental a partir das validações realizadas durante cada etapa.

### Divisão de Papéis

A equipe do SR Beauty é composta por cinco integrantes, que atuam de forma colaborativa nas diferentes etapas do projeto. As responsabilidades são distribuídas conforme as necessidades de cada sprint, envolvendo atividades de levantamento e análise de requisitos, documentação, prototipação, desenvolvimento, testes e validação da solução.

<ul>

  <li><b>Equipe de Desenvolvimento:</b>
    <ul>
      <li>Flávia Sergina Rodrigues</li>
      <li>Júlio César Villaça Cardoso</li>
      <li>Luiz Guilherme Martins Franchim</li>
      <li>Pâmella Almeida da Silva</li>
      <li>Virgílio Parreiras Campos Zenith</li>
    </ul>
  </li>

  <li><b>Parceira do Projeto:</b> Simone Rodrigues, responsável por apresentar as necessidades do estabelecimento e participar da validação dos requisitos e das funcionalidades desenvolvidas</li>

  <li><b>Orientador:</b> José Wilson da Costa, responsável pelo acompanhamento e orientação acadêmica do projeto</li>

</ul>

Como o projeto utiliza uma adaptação de práticas ágeis, os integrantes não permanecem restritos a uma única função durante todo o desenvolvimento. As atividades podem ser redistribuídas entre os membros da equipe de acordo com as demandas de cada etapa, favorecendo a colaboração e o compartilhamento de conhecimento.

### Processo

Para organizar e acompanhar as atividades do projeto, a equipe utiliza o GitHub em conjunto com o GitHub Projects. As tarefas são distribuídas em um quadro Kanban, permitindo acompanhar o andamento das atividades ao longo de cada etapa do desenvolvimento.

O quadro é organizado nas seguintes colunas:

<ul>

  <li><b>Backlog:</b> reúne as atividades e funcionalidades previstas para o projeto que ainda não foram selecionadas para desenvolvimento.</li>

  <li><b>To Do:</b> reúne as tarefas selecionadas para execução na etapa ou sprint atual.</li>

  <li><b>In Progress:</b> contém as tarefas que estão sendo desenvolvidas pela equipe.</li>

  <li><b>Review / Testing:</b> reúne as tarefas concluídas que ainda precisam ser revisadas, testadas ou validadas antes de serem consideradas finalizadas.</li>

  <li><b>Done:</b> contém as tarefas concluídas e validadas.</li>

</ul>

Essa organização permite acompanhar de forma visual o progresso das funcionalidades, da documentação, dos testes e das demais atividades relacionadas ao desenvolvimento do SR Beauty.

O quadro Kanban do projeto está disponível no GitHub Projects e é apresentado, em seu estado atual, na figura abaixo:

[GitHub Projects](https://github.com/ICEI-PUC-Minas-PMV-ADS/pmv-ads-2026-2-e5-proj-empext-t6-SRBeauty/projects)

<figure>

  <img src="img/kanban-srbeauty.png">

  <figcaption>Figura 2 - Quadro Kanban utilizado no gerenciamento do projeto SR Beauty.</figcaption>

</figure>


<h3>Etiquetas</h3>

<p>As tarefas podem ser classificadas por meio de etiquetas de acordo com a natureza da atividade, facilitando a identificação e a organização das demandas do projeto.</p>

<ul>

  <li><b>Bug:</b> correção de erros ou comportamentos inesperados da aplicação.</li>

  <li><b>Desenvolvimento:</b> implementação e evolução das funcionalidades do sistema.</li>

  <li><b>Documentação:</b> criação ou atualização dos documentos do projeto.</li>

  <li><b>Gerenciamento:</b> atividades relacionadas à organização e acompanhamento do projeto.</li>

  <li><b>Infraestrutura:</b> configuração de ambiente, banco de dados, hospedagem e deploy.</li>

  <li><b>Testes:</b> criação, execução e registro de testes da aplicação.</li>

</ul>
  
### Ferramentas

Para o desenvolvimento do SR Beauty são utilizadas ferramentas e tecnologias relacionadas à implementação da aplicação, persistência de dados, controle de versão, gerenciamento do projeto e implantação em ambiente de produção.

As principais ferramentas e tecnologias utilizadas são:

<ul>

  <li><b>Visual Studio Code:</b> ambiente utilizado para desenvolvimento, edição e organização do código-fonte.</li>

  <li><b>Python:</b> linguagem utilizada no desenvolvimento da camada de backend da aplicação.</li>

  <li><b>Flask:</b> framework web utilizado para criação da aplicação, definição das rotas e integração entre a interface, as regras de negócio e os dados.</li>

  <li><b>Flask-Login:</b> extensão utilizada para gerenciamento de autenticação, sessões e proteção das rotas destinadas a usuários autenticados.</li>

  <li><b>Flask-SQLAlchemy:</b> extensão utilizada para integração entre a aplicação Flask e os bancos de dados utilizados pelo sistema.</li>

  <li><b>Werkzeug:</b> biblioteca utilizada para geração e verificação segura dos hashes das senhas dos usuários.</li>

  <li><b>HTML5:</b> utilizado para estruturação das páginas e dos conteúdos apresentados pela aplicação.</li>

  <li><b>CSS3:</b> utilizado para estilização, responsividade e definição da identidade visual das interfaces.</li>

  <li><b>JavaScript:</b> utilizado para comportamentos e interações executadas no lado do cliente.</li>

  <li><b>SQLite:</b> banco de dados utilizado durante o desenvolvimento local da aplicação.</li>

  <li><b>PostgreSQL:</b> sistema de gerenciamento de banco de dados utilizado no ambiente de produção.</li>

  <li><b>Git:</b> sistema utilizado para controle de versão do código-fonte e da documentação do projeto.</li>

  <li><b>GitHub:</b> plataforma utilizada para hospedagem do repositório, integração das alterações e armazenamento da documentação do projeto.</li>

  <li><b>GitHub Projects:</b> ferramenta utilizada para gerenciamento e acompanhamento das atividades por meio de um quadro Kanban.</li>

  <li><b>Render:</b> plataforma utilizada para hospedagem da aplicação web e do banco de dados PostgreSQL no ambiente de produção.</li>

  <li><b>Gunicorn:</b> servidor WSGI utilizado para execução da aplicação Flask no ambiente de produção.</li>

</ul>

A combinação dessas ferramentas permite que o desenvolvimento seja realizado em ambiente local utilizando SQLite e, posteriormente, disponibilizado em ambiente de produção utilizando PostgreSQL e Render. O Git e o GitHub são utilizados para registrar e integrar as alterações realizadas pela equipe, enquanto o GitHub Projects auxilia no acompanhamento das atividades do projeto.

Os principais ambientes e plataformas utilizados são apresentados na tabela a seguir.

| AMBIENTE | PLATAFORMA / TECNOLOGIA | LINK DE ACESSO |
|---|---|---|
| Repositório de código-fonte | GitHub | [Repositório SR Beauty](https://github.com/ICEI-PUC-Minas-PMV-ADS/pmv-ads-2026-2-e5-proj-empext-t6-SRBeauty) |
| Documentação do projeto | GitHub | [Documentação](https://github.com/ICEI-PUC-Minas-PMV-ADS/pmv-ads-2026-2-e5-proj-empext-t6-SRBeauty/tree/main/documentos) |
| Gerenciamento do projeto | GitHub Projects | https://github.com/ICEI-PUC-Minas-PMV-ADS/pmv-ads-2026-2-e5-proj-empext-t6-SRBeauty/projects |
| Ambiente de desenvolvimento | Visual Studio Code | — |
| Backend | Python / Flask | — |
| Frontend | HTML5 / CSS3 / JavaScript | — |
| Banco de dados local | SQLite | — |
| Banco de dados de produção | PostgreSQL | — |
| Hospedagem da aplicação | Render | https://srbeauty-app.onrender.com/ |
| Servidor de aplicação | Gunicorn | — |

### Estratégia de Organização de Codificação

Todos os artefatos relacionados à implementação da aplicação estão concentrados na pasta [codigo-fonte](https://github.com/ICEI-PUC-Minas-PMV-ADS/pmv-ads-2026-2-e5-proj-empext-t6-SRBeauty/tree/main/codigo-fonte), mantendo o código-fonte separado da documentação e dos demais materiais do projeto.

A organização da aplicação segue uma estrutura compatível com o desenvolvimento em Flask, distribuindo os arquivos conforme sua finalidade:

<ul>

  <li><b>app.py:</b> arquivo principal da aplicação, responsável pela configuração do Flask, definição das rotas, autenticação, integração com o banco de dados e regras de negócio implementadas.</li>

  <li><b>templates/:</b> diretório destinado às páginas HTML renderizadas pela aplicação Flask.</li>

  <li><b>static/:</b> diretório utilizado para arquivos estáticos da aplicação, como folhas de estilo, scripts e demais recursos utilizados pela interface.</li>

  <li><b>requirements.txt:</b> arquivo que registra as dependências necessárias para execução da aplicação.</li>

  <li><b>.env.example:</b> arquivo de referência para as variáveis de ambiente necessárias à configuração da aplicação.</li>

</ul>

Durante o desenvolvimento, o código é versionado com Git e armazenado no repositório do projeto no GitHub. As alterações são realizadas de forma incremental e integradas ao repositório conforme a evolução das funcionalidades.

Essa organização busca facilitar a manutenção do código, a localização dos arquivos, o controle de versões e a separação entre interface, configuração e lógica da aplicação.