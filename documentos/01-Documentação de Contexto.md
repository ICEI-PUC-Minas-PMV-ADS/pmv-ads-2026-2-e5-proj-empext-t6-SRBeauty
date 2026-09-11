# Introdução

O presente projeto tem como finalidade o desenvolvimento de um sistema web para automatizar o processo de agendamento de horários e apoiar a gestão das atividades de um salão de beleza. 

A proposta surge a partir da necessidade de utilizar a tecnologia para organizar os processos relacionados à agenda, aos atendimentos e ao controle financeiro do estabelecimento.

O sistema será utilizado por diferentes perfis de usuários, incluindo clientes, profissionais e a proprietária do salão. Cada perfil terá acesso a funcionalidades específicas de acordo com suas necessidades. As clientes poderão consultar a disponibilidade de horários e realizar agendamentos, enquanto as profissionais poderão acompanhar seus horários e registrar os atendimentos realizados. A proprietária, por sua vez, terá acesso a recursos de gestão da agenda e de controle financeiro.

Além da automatização dos agendamentos, o sistema deverá contribuir para a organização das informações relacionadas aos serviços prestados, pagamentos, repasses das profissionais, despesas e resultados financeiros. Dessa forma, a solução busca integrar diferentes atividades do salão em um único ambiente, reduzindo a dependência de controles manuais e facilitando o acesso às informações.


## Problema

A organização dos horários e das atividades de um salão de beleza envolve informações que precisam ser constantemente atualizadas e compartilhadas entre clientes, profissionais e responsável pela gestão. Quando esses processos são realizados predominantemente de forma manual, podem ocorrer dificuldades no controle da disponibilidade dos horários, conflitos de agenda, duplicidade de agendamentos e perda ou inconsistência de informações.

Outro desafio está relacionado ao controle financeiro. Além de registrar os atendimentos realizados, é necessário identificar o tipo de serviço prestado, a forma de pagamento, eventuais taxas de cartão, os valores destinados ao salão e os repasses realizados pelas profissionais. O controle de despesas e a consolidação dessas informações também são importantes para que a proprietária consiga acompanhar a situação financeira do estabelecimento.

Diante desse contexto, surge o seguinte problema: como utilizar um sistema informatizado para automatizar o agendamento de horários e, ao mesmo tempo, organizar as informações relacionadas aos atendimentos e à gestão financeira de um salão de beleza, reduzindo conflitos de agenda e a dependência de controles manuais?


## Objetivos

### Objetivo Geral

Desenvolver um sistema web para automatizar o processo de agendamento de horários de um salão de beleza, proporcionando maior organização da agenda e apoiando o controle dos atendimentos e das informações financeiras do estabelecimento.

### Objetivos Específicos

* Permitir que clientes consultem os horários disponíveis das profissionais;
* Permitir que clientes e profissionais realizem agendamentos;
* Impedir conflitos e duplicidade de horários para uma mesma profissional;
* Permitir o cadastro e gerenciamento dos horários de trabalho das profissionais;
* Permitir o registro dos atendimentos realizados e dos serviços prestados;
* Registrar as diferentes formas de pagamento, como Pix, dinheiro e cartão;
* Permitir o registro de taxas de maquininha nos pagamentos realizados por cartão;
* Automatizar o cálculo dos repasses ao salão com base no percentual definido para cada tipo de serviço;
* Permitir o registro e acompanhamento dos pagamentos dos repasses das profissionais;
* Permitir o registro das despesas do salão;
* Apoiar o fechamento financeiro semanal;
* Disponibilizar consultas diárias e mensais para acompanhamento da agenda e das informações financeiras;
* Garantir autenticação e controle de acesso de acordo com o perfil do usuário;
* Manter histórico rastreável das operações relacionadas aos repasses e pagamentos.


## Justificativa

A utilização de uma solução informatizada pode proporcionar melhorias significativas na organização da rotina de um salão de beleza. A automatização do processo de agendamento permite centralizar as informações de horários e disponibilidade das profissionais, reduzindo a possibilidade de conflitos e facilitando a consulta por parte das clientes.

A solução também pode contribuir para diminuir o esforço necessário para a realização de controles administrativos. Informações que precisam ser registradas e consultadas frequentemente, como atendimentos, pagamentos, repasses e despesas, poderão ser armazenadas de forma estruturada e recuperadas quando necessário.

Outro fator relevante é a possibilidade de melhorar o acompanhamento financeiro. A consolidação das entradas e saídas permite que a proprietária tenha uma visão mais clara dos resultados do salão, facilitando o acompanhamento semanal e mensal das atividades.

Do ponto de vista das profissionais e clientes, a disponibilização de uma agenda informatizada tende a tornar o processo de marcação de horários mais organizado e acessível. Para a proprietária, a centralização das informações poderá facilitar a tomada de decisões e a conferência das movimentações financeiras.

Assim, o desenvolvimento do sistema se justifica pela oportunidade de aplicar recursos de tecnologia da informação a uma necessidade concreta de um pequeno negócio, buscando melhorar seus processos operacionais e administrativos sem perder de vista a simplicidade de utilização.


## Relação com a Extensão Universitária

O projeto possui relação direta com a Extensão Universitária por promover a aplicação prática dos conhecimentos adquiridos no ambiente acadêmico na resolução de uma necessidade identificada em um estabelecimento real.

A proposta possibilita que os conhecimentos relacionados à Engenharia de Software, Análise de Sistemas, Banco de Dados, Desenvolvimento Web, Interface de Usuário e Segurança da Informação sejam utilizados para compreender um problema do cotidiano e propor uma solução tecnológica adequada ao contexto do parceiro.

Nesse sentido, a extensão estabelece uma relação de troca entre a universidade e a comunidade. A equipe responsável pelo projeto aplica seus conhecimentos acadêmicos em uma situação prática, enquanto o parceiro participa do processo apresentando suas necessidades, dificuldades e características de trabalho. Essa interação contribui para que o sistema desenvolvido esteja alinhado à realidade de utilização e não apenas a requisitos definidos de forma teórica.

O projeto também proporciona aos estudantes a oportunidade de vivenciar etapas do desenvolvimento de software, desde o levantamento e análise dos requisitos até a modelagem, implementação, testes e avaliação da solução. Dessa forma, a atividade contribui tanto para a formação acadêmica e profissional dos estudantes quanto para a melhoria dos processos do estabelecimento parceiro.


## Descrição do Parceiro

O parceiro deste projeto é o Simone Rodrigues Espaço de Beleza, estabelecimento atuante no segmento de serviços de beleza desde 2017. O espaço foi fundado com o propósito de oferecer serviços de beleza com qualidade, cuidado e atendimento personalizado.

O quadro societário é composto por uma única sócia, Simone Rodrigues, que é responsável pela gestão e condução das atividades do estabelecimento. Entre os serviços oferecidos estão depilação, design de sobrancelhas, manicure e pedicure, tendo como foco o cuidado, o bem-estar e a autoestima das clientes.

Por possuir diferentes profissionais, serviços e horários de atendimento, o estabelecimento apresenta uma rotina que envolve a organização da agenda, controle da disponibilidade das profissionais, registro dos atendimentos e acompanhamento de informações financeiras. Essas características tornam o salão um contexto adequado para a aplicação de uma solução de automatização de agendamento e apoio à gestão.

O sistema proposto será desenvolvido considerando as particularidades apresentadas pelo parceiro, buscando oferecer uma ferramenta simples, acessível e adequada à sua rotina. A participação da proprietária será importante para a validação dos requisitos, das regras de negócio e da solução desenvolvida, permitindo que o resultado final esteja alinhado às necessidades reais do estabelecimento.
