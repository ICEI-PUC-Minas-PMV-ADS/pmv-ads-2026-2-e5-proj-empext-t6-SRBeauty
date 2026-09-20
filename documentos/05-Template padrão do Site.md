# Template padrão da Aplicação

O padrão visual do SR Beauty foi desenvolvido buscando transmitir uma identidade elegante, leve e compatível com o segmento de beleza, mantendo consistência entre as diferentes telas da aplicação.

A interface utiliza HTML5, CSS3 e JavaScript no frontend, enquanto as páginas são integradas à aplicação Flask por meio dos templates utilizados pelo sistema.

Os principais elementos visuais adotados são:

<ul>

  <li><b>Paleta de cores:</b> tons de rosa queimado, nude, bege claro, marrom e branco, utilizados de forma consistente nos fundos, botões, textos, destaques e elementos de navegação;</li>

  <li><b>Cor de destaque:</b> #B76E79;</li>

  <li><b>Cor de apoio:</b> #E8CFCF;</li>

  <li><b>Fundo principal:</b> #F8F3F1;</li>

  <li><b>Cor para textos e elementos de contraste:</b> #6B4A4A;</li>

  <li><b>Tipografia de destaque:</b> Playfair Display, utilizada principalmente em títulos e elementos de identidade visual;</li>

  <li><b>Tipografia da interface:</b> Montserrat, utilizada em textos, formulários, menus e demais componentes;</li>

  <li><b>Componentes:</b> botões, campos de formulário, cartões e áreas de conteúdo utilizam bordas suaves, espaçamento consistente e elementos visuais padronizados.</li>

</ul>

A identidade visual também utiliza o logotipo do Simone Rodrigues Espaço de Beleza como elemento recorrente nas telas, reforçando a identificação do sistema com o estabelecimento parceiro.

## Estrutura das telas

As telas autenticadas do SR Beauty utilizam uma estrutura visual comum composta principalmente por:

<ul>

  <li><b>Menu lateral:</b> apresenta a identidade visual da aplicação e os acessos às principais funcionalidades do sistema;</li>

  <li><b>Área principal:</b> concentra o conteúdo correspondente à funcionalidade selecionada;</li>

  <li><b>Identificação do usuário:</b> apresenta informações básicas do usuário autenticado e seu perfil de acesso;</li>

  <li><b>Cards e painéis:</b> utilizados para organizar informações resumidas e facilitar a visualização dos dados;</li>

  <li><b>Mensagens de retorno:</b> utilizadas para informar sucesso, erro ou validações decorrentes das ações realizadas pelo usuário.</li>

</ul>

A tela de Login possui uma composição diferenciada das áreas internas do sistema, mantendo, entretanto, a mesma identidade visual, paleta de cores e tipografia utilizadas no restante da aplicação.

## Tela de Login

A tela de Login apresenta a identidade visual do SR Beauty juntamente com o formulário de autenticação. Os campos, botões e mensagens seguem o padrão visual definido para a aplicação.

![Tela de Login](img/tela-login.png)

<figure>
  <figcaption>Figura 1 - Aplicação do padrão visual na tela de Login.</figcaption>
</figure>

## Tela principal

Após a autenticação, a aplicação apresenta uma estrutura baseada em menu lateral e área principal de conteúdo. O mesmo padrão poderá ser reutilizado nas demais funcionalidades do sistema, mantendo consistência durante a navegação.

![Tela principal](img/tela-home.png)

<figure>
  <figcaption>Figura 2 - Aplicação do padrão visual na tela principal do SR Beauty.</figcaption>
</figure>

## Organização dos arquivos de interface

Os arquivos utilizados na construção das interfaces estão organizados na pasta `codigo-fonte`, incluindo os templates HTML e os recursos utilizados na apresentação da aplicação.

O código-fonte pode ser consultado em [codigo-fonte](../codigo-fonte), enquanto os recursos visuais utilizados na documentação estão disponíveis em [documentos/img](img/).