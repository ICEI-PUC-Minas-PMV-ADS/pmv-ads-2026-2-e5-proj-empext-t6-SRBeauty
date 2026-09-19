# Ata Intermediária da Sprint


## Sprint 01


Tipo de reunião: Acompanhamento intermediário da Sprint

### Objetivo da reunião
A reunião intermediária da Sprint teve como objetivo acompanhar o andamento inicial do projeto, revisar os requisitos levantados para o sistema de automatização de agendamentos do salão de beleza, identificar as funcionalidades prioritárias e organizar as próximas atividades de desenvolvimento.
Neste momento do projeto, a equipe ainda se encontra na etapa inicial de análise e organização dos requisitos, não tendo sido iniciada a implementação definitiva das funcionalidades.

### Contexto do sistema
O sistema será desenvolvido para automatizar o processo de agendamento de horários de um salão de beleza, permitindo que clientes e profissionais realizem ou acompanhem agendamentos de acordo com a disponibilidade das profissionais.
Além do controle da agenda, a solução deverá apoiar atividades administrativas e financeiras do salão, como registro de atendimentos, cálculo de repasses, controle de despesas, fechamento financeiro e acompanhamento dos valores recebidos e repassados.
O sistema contará com três perfis principais de acesso:

* Cliente: consulta horários disponíveis e realiza agendamentos;
* Profissional: acompanha sua agenda e registra os atendimentos realizados;
* Proprietária: gerencia horários, despesas, repasses e informações financeiras.

### Situação dos requisitos
Durante a reunião, os requisitos funcionais e não funcionais foram revisados e organizados em um quadro Kanban.
Para esta etapa da Sprint, os requisitos RF04, RF05, RF06, RF07, RF08 e RF10 foram direcionados para Em Análise, pois envolvem regras de negócio e controles financeiros que precisam ser detalhados antes da implementação.
Os demais requisitos permanecem no Backlog, aguardando análise e priorização.

A situação atual do quadro é:

BACKLOG

* Validar escopo com o cliente
* Finalizar protótipo completo
* Implementar funcionalidade da Sprint
* Elaborar plano e executar testes
* Documentar e preparar entrega da Etapa 2

READY

* Validar escopo com o cliente
* Finalizar protótipo completo
* Definir funcionalidade da Sprint

IN PROGRESS

* Validação e documentação do escopo
* Desenvolvimento do protótipo
* Implementação da funcionalidade da Sprint

IN REVIEW

* Protótipo completo
* Funcionalidade implementada
* Plano de testes
* Evidências dos testes
* Ata da Reunião Etapa 2

DONE

Os cards irão para esta coluna conforme forem finalizados.

### Pontos discutidos

Durante a análise, foram identificados alguns pontos considerados importantes para o funcionamento correto do sistema:

* O sistema deverá impedir que uma mesma profissional tenha dois atendimentos agendados para o mesmo horário.
* A disponibilidade das profissionais deverá considerar seus respectivos horários de trabalho.
* O percentual de repasse deverá estar associado ao tipo de serviço, e não diretamente à profissional.
* Os pagamentos realizados com cartão deverão permitir o registro da taxa da maquininha repassada à cliente.
* O controle do pagamento dos repasses deverá substituir o controle atualmente realizado por meio da anotação de “OK” na agenda física.
* As despesas deverão ser registradas de forma estruturada para possibilitar o fechamento financeiro semanal e as consultas mensais.
* As informações financeiras e os repasses deverão permanecer armazenados de maneira rastreável para permitir conferências futuras.
* O sistema deverá possuir diferentes níveis de acesso de acordo com o perfil do usuário.

### Decisões tomadas
A equipe decidiu que o desenvolvimento não deverá ser iniciado antes que as principais regras de negócio estejam suficientemente detalhadas.
Foi definida como prioridade a análise dos requisitos relacionados ao controle financeiro e aos repasses, especialmente RF04, RF05, RF06, RF07, RF08 e RF10.
Também foi estabelecido que as regras de conflito de horários e disponibilidade das profissionais deverão ser consideradas desde a modelagem inicial do sistema, uma vez que constituem parte fundamental do processo de agendamento.

### Próximas atividades

Para a continuidade da Sprint, foram definidas as seguintes atividades:

* Detalhar as regras de negócio relacionadas aos requisitos em análise;
* Definir as entidades e informações necessárias para os agendamentos;
* Definir a estrutura de profissionais, clientes, serviços e horários de trabalho;
* Detalhar o cálculo dos repasses por tipo de serviço;
* Definir o fluxo de registro de pagamentos e despesas;
* Definir os perfis de acesso e suas respectivas permissões;
* Avaliar a regra de prevenção de agendamentos duplicados em nível de aplicação e banco de dados;
* Priorizar os requisitos que deverão entrar na etapa de desenvolvimento;
* Iniciar a modelagem da solução após a validação das regras de negócio.

### Pendências

Permanecem como pendências para a próxima etapa:

* Validar com a Proprietária os percentuais de repasse de cada tipo de serviço;
* Definir quais categorias de despesas serão utilizadas no sistema;
* Detalhar o fluxo de fechamento financeiro semanal;
* Definir quais informações deverão aparecer nos relatórios diários e mensais;
* Validar as regras de disponibilidade e horários de trabalho das profissionais;
* Detalhar os critérios de cancelamento ou alteração de agendamentos, caso aplicáveis.

### Encaminhamento

Ao final da reunião, a equipe concluiu que o projeto possui os requisitos principais identificados, porém algumas regras de negócio ainda precisam ser detalhadas antes do início da implementação.
A próxima etapa será concentrada no refinamento dos requisitos em análise e na preparação da estrutura necessária para iniciar o desenvolvimento do sistema de agendamento e gestão do salão.


## Sprint 02

Tipo de reunião: Apresentação e validação do protótipo com a Proprietária

### Objetivo da reunião

A reunião teve como objetivo apresentar à Proprietária o protótipo do sistema de gestão do SR Beauty, validar o escopo levantado na Sprint anterior, coletar apontamentos sobre os fluxos apresentados e definir as próximas atividades de desenvolvimento.
Neste momento do projeto, a equipe já concluiu o protótipo em front-end, que reproduz as telas e os fluxos principais do sistema com dados ilustrativos. O back-end e a implementação definitiva das regras de negócio ainda não foram iniciados.

### Contexto do sistema

O sistema será desenvolvido para automatizar o processo de agendamento de horários de um salão de beleza, permitindo que clientes e profissionais realizem ou acompanhem agendamentos de acordo com a disponibilidade das profissionais.
Além do controle da agenda, a solução deverá apoiar atividades administrativas e financeiras do salão, como registro de atendimentos, cálculo de repasses, controle de despesas, fechamento financeiro e acompanhamento dos valores recebidos e repassados.
O protótipo apresentado contempla os três perfis principais de acesso definidos na Sprint anterior:

* Cliente: agenda, reagenda e cancela horários, acompanha seu histórico e mantém seus dados de contato;
* Profissional: acompanha sua agenda do dia, define disponibilidade e bloqueios de horário, registra seus atendimentos e consulta seus próprios repasses;
* Proprietária: acompanha agenda, serviços, profissionais, repasses, despesas e relatórios do salão.

### Situação do protótipo e dos requisitos

Durante a reunião, o protótipo foi apresentado à Proprietária, percorrendo as telas de cada perfil. Os requisitos RF-01 a RF-13 relacionados a agendamento, controle de acesso, repasses, despesas e relatórios, foram representados no protótipo para validação de fluxo e de usabilidade.
O protótipo é somente de interface: os dados são fictícios e as regras (como o bloqueio de conflito de horários e o cálculo dos repasses) são apenas simuladas, e serão implementadas junto com o back-end.

A situação atual do quadro é:

BACKLOG

* #9 Implementar funcionalidade da Sprint
* #24 Horário de funcionamento e escala das profissionais
* #25 Lógica de validação de conflitos (impedir que dois clientes agendem a mesma profissional no mesmo minuto)
* #26 Gestão de bloqueios de agenda
* #27 Endpoints para a visão da agenda semanal/diária (visão da proprietária e visão da profissional)

READY

* #14 Definir funcionalidade da Sprint

IN PROGRESS

* #15 Validação e documentação do escopo
* #17 Implementação da funcionalidade da Sprint
* #11 Documentar e preparar entrega da Etapa 2
* #10 Elaborar plano e executar testes

IN REVIEW

* #19 Protótipo completo
* #20 Funcionalidade implementada
* #21 Plano de testes
* #22 Evidências dos testes
* #23 Ata da Reunião Etapa 2

DONE

* #16 Finalizar protótipo completo
* #7 Validar escopo com o cliente
* #13 Finalizar protótipo completo

### Pontos discutidos

Durante a apresentação, foram discutidos os seguintes pontos:

* Cada perfil visualiza apenas o menu e as informações pertinentes à sua função: a profissional consulta somente os próprios repasses e atendimentos, e a cliente acompanha somente seus agendamentos.
* O fluxo de agendamento da cliente segue a sequência serviço, profissional, data e horário disponível, com confirmação ao final. A verificação real de conflito de horários será implementada no back-end.
* A profissional pode definir sua disponibilidade semanal e bloquear horários (por exemplo, compromissos pessoais), o que deverá ser considerado na oferta de horários às clientes.
* Os serviços são apresentados com valor, duração média e percentual de repasse, reforçando que o repasse está associado ao tipo de serviço e não à profissional.
* A área de repasses e despesas apoia o fechamento financeiro semanal e as consultas mensais, em substituição às anotações na agenda física.
* Os relatórios apresentam faturamento mensal, ticket médio, taxa de ocupação, clientes atendidos e serviços mais realizados, com opção de exportação.
* Os percentuais de repasse exibidos no protótipo são ilustrativos e não correspondem aos valores praticados pelo salão. Também foi observado que, na prática, o repasse é o valor que a profissional paga ao salão, e as telas deverão refletir essa lógica.
* A proprietário avaliou o protótipo e gostou bastante da ideia que apresentamos a ela. 

### Decisões tomadas

A equipe decidiu manter o protótipo como referência visual e de fluxo para o desenvolvimento, realizando os ajustes apontados na reunião.
Ficou definido que os percentuais de repasse do protótipo serão corrigidos para os valores reais por tipo de serviço, e que as telas passarão a exibir o valor a ser repassado ao salão.
Também foi decidido que o back-end será implantado nas próximas etapas, iniciando pelas funcionalidades prioritárias definidas pela Proprietária: agendamento, controle de repasses e fluxo de caixa.
As regras de conflito de horários e de disponibilidade das profissionais continuam sendo tratadas como parte fundamental da modelagem, tanto em nível de aplicação quanto de banco de dados.

### Próximas atividades

Para a continuidade do projeto, foram definidas as seguintes atividades:

* Ajustar o protótipo conforme os apontamentos da Proprietária;
* Corrigir os percentuais de repasse por tipo de serviço e a lógica de exibição dos valores;
* Definir o horário de funcionamento do salão e a escala das profissionais;
* Implementar a lógica de validação de conflitos de agendamento, impedindo dois atendimentos da mesma profissional no mesmo horário;
* Implementar a gestão de bloqueios de agenda;
* Implementar os endpoints da agenda semanal e diária, nas visões da proprietária e da profissional;
* Concluir a modelagem de dados (profissionais, clientes, serviços, horários de trabalho, agendamentos, pagamentos, repasses e despesas);
* Implementar autenticação e níveis de acesso por perfil;
* Implementar o registro de atendimentos, pagamentos e o cálculo de repasses;
* Elaborar o plano de testes e registrar as evidências.

### Pendências

Permanecem como pendências para a próxima etapa:

* Validar com a Proprietária os percentuais de repasse de todos os tipos de serviço;
* Definir as categorias de despesas que serão utilizadas no sistema;
* Detalhar o fluxo de fechamento financeiro semanal;
* Confirmar as informações que deverão constar nos relatórios diários e mensais;
* Validar as regras de disponibilidade e horários de trabalho das profissionais;
* Definir os critérios de cancelamento e reagendamento de atendimentos;
* Definir como será registrada a taxa da maquininha nos pagamentos com cartão.

### Encaminhamento

Ao final da reunião, a equipe concluiu que o protótipo atendeu ao objetivo de validar os fluxos principais com a Proprietária. A próxima etapa será concentrada nos ajustes do protótipo, no detalhamento das regras de negócio pendentes e no início do desenvolvimento do back-end.

### Reunião com o proprietário

<img width="1600" height="811" alt="Reunião 16-09-2026" src="https://github.com/user-attachments/assets/53053300-f6f5-4b8d-a915-f753f189aaf4" />

