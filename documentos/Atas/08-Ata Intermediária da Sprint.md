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
