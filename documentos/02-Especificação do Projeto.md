# Especificações do Projeto

## Perfis de Usuários

<table>

<tbody>

<tr>

<th colspan="2">Perfil 1: Cliente</th>

</tr>

<tr>

<td width="150px"><b>Descrição</b></td>

<td width="600px">

Pessoa que utiliza os serviços oferecidos pelo salão e necessita consultar a disponibilidade das profissionais e realizar agendamentos.

</td>

</tr>

<tr>

<td><b>Necessidades</b></td>

<td>

1. Consultar os horários disponíveis das profissionais;

2. Realizar agendamentos de forma simples e rápida;

3. Consultar informações relacionadas aos seus agendamentos;

4. Utilizar o sistema principalmente por dispositivos móveis;

5. Ter acesso às funcionalidades destinadas ao perfil de Cliente.

</td>

</tr>

</tbody>

</table>

<table>

<tbody>

<tr>

<th colspan="2">Perfil 2: Profissional</th>

</tr>

<tr>

<td width="150px"><b>Descrição</b></td>

<td width="600px">

Profissional que presta serviços no salão e necessita acompanhar sua agenda, seus horários de trabalho e os atendimentos realizados.

</td>

</tr>

<tr>

<td><b>Necessidades</b></td>

<td>

1. Consultar sua agenda de atendimentos;

2. Gerenciar seus horários de trabalho;

3. Realizar e acompanhar agendamentos;

4. Registrar os atendimentos realizados;

5. Registrar informações relacionadas aos serviços prestados e às formas de pagamento;

6. Acompanhar informações relacionadas aos seus repasses.

</td>

</tr>

</tbody>

</table>

<table>

<tbody>

<tr>

<th colspan="2">Perfil 3: Proprietária</th>

</tr>

<tr>

<td width="150px"><b>Descrição</b></td>

<td width="600px">

Responsável pela administração do salão e pelo acompanhamento das atividades operacionais e financeiras do estabelecimento.

</td>

</tr>

<tr>

<td><b>Necessidades</b></td>

<td>

1. Acompanhar as agendas das profissionais;

2. Consultar horários disponíveis, agendados e atendimentos realizados;

3. Acompanhar os repasses realizados pelas profissionais;

4. Registrar e consultar despesas do salão;

5. Realizar o fechamento financeiro semanal;

6. Consultar informações financeiras diárias e mensais;

7. Gerenciar informações necessárias ao funcionamento do estabelecimento.

</td>

</tr>

</tbody>

</table>


## Histórias de Usuários

Com base na análise dos perfis de usuários foram identificadas as seguintes histórias de usuários:

|EU COMO... `PERSONA`| QUERO/PRECISO ... `FUNCIONALIDADE` |PARA ... `MOTIVO/VALOR` |
|--------------------|--------------------------------------|-------------------------|
|Cliente| criar uma conta e acessar o sistema | utilizar as funcionalidades disponibilizadas para clientes. |
|Cliente| consultar os horários disponíveis das profissionais | escolher um horário adequado para meu atendimento. |
|Cliente| realizar um agendamento | reservar um atendimento com uma profissional. |
|Profissional| consultar minha agenda | acompanhar os atendimentos programados. |
|Profissional| gerenciar meus horários de trabalho | manter minha disponibilidade atualizada. |
|Profissional| realizar agendamentos | organizar atendimentos solicitados pelas clientes. |
|Profissional| registrar um atendimento realizado | manter o histórico dos serviços prestados. |
|Profissional| registrar a forma de pagamento de um atendimento | manter as informações financeiras do atendimento organizadas. |
|Proprietária| consultar as agendas das profissionais | acompanhar a rotina de atendimentos do salão. |
|Proprietária| acompanhar os repasses das profissionais | controlar os valores destinados ao salão. |
|Proprietária| registrar despesas do salão | manter o controle das saídas financeiras do estabelecimento. |
|Proprietária| realizar o fechamento financeiro semanal | acompanhar o resultado financeiro do período. |
|Proprietária| consultar informações financeiras mensais | acompanhar o desempenho financeiro do estabelecimento. |


## Project Model Canvas

<img width="3174" height="2245" alt="ProjectModelCanvasA1 pdf" src="https://github.com/user-attachments/assets/73b1e1ba-c05d-47b3-92c2-5ae178b49563" />


## Requisitos

### Requisitos Funcionais

|ID | Descrição do Requisito | Prioridade |
|-----|-----|-----|
|RF-01| A aplicação deve permitir ao usuário realizar cadastro, login e logout, além de consultar e atualizar os dados de sua conta. | ALTA |
|RF-02| O sistema deve permitir que a Cliente consulte a disponibilidade de horários das profissionais. | ALTA |
|RF-03| O sistema deve permitir que a Cliente ou a Profissional realize um agendamento, impedindo conflito ou duplicidade de horário para a mesma profissional. | ALTA |
|RF-04| O sistema deve permitir que a Profissional registre um atendimento realizado, incluindo o serviço prestado e a forma de pagamento utilizada (Pix, dinheiro ou cartão). | MÉDIA |
|RF-05| O sistema deve calcular automaticamente o valor do repasse ao salão com base no percentual definido para o tipo de serviço realizado. | ALTA |
|RF-06| Quando o pagamento for feito em cartão, o sistema deve permitir registrar a taxa da maquininha repassada à cliente. | BAIXA |
|RF-07| O sistema deve permitir registrar quando o repasse de uma profissional ao salão foi efetivamente pago. | MÉDIA |
|RF-08| O sistema deve permitir que a Proprietária registre e consulte as despesas do salão. | MÉDIA |
|RF-09| O sistema deve permitir o fechamento financeiro semanal, consolidando entradas, despesas, repasses e resultado do período. | ALTA |
|RF-10| O sistema deve permitir que a Proprietária consulte diariamente os horários agendados, horários disponíveis e atendimentos realizados. | ALTA |
|RF-11| O sistema deve permitir que a Proprietária consulte mensalmente o faturamento, as despesas, os valores recebidos, os repasses das profissionais e o resultado financeiro do período. | ALTA |
|RF-12| O sistema deve permitir o cadastro e a gestão dos horários de trabalho de cada profissional. | MÉDIA |
|RF-13| O sistema deve controlar o acesso às funcionalidades de acordo com o perfil do usuário: Cliente, Profissional ou Proprietária. | ALTA |
|RF-14| O sistema deve permitir que a Proprietária cadastre e gerencie os serviços oferecidos pelo salão, incluindo valor, duração e percentual de repasse. | ALTA |

**Prioridade: Alta / Média / Baixa.**

### Requisitos Não Funcionais

|ID | Descrição do Requisito | Prioridade |
|-----|-----|-----|
|RNF-01| O sistema deve ser acessível por navegador web e possuir interface responsiva para utilização em computadores e dispositivos móveis. | ALTA |
|RNF-02| As senhas dos usuários devem ser armazenadas utilizando mecanismo seguro de hash, não sendo mantidas em texto simples. | ALTA |
|RNF-03| O sistema deve impedir o acesso de usuários não autenticados ou sem permissão às funcionalidades restritas. | ALTA |
|RNF-04| A aplicação disponibilizada em ambiente de produção deve utilizar conexão segura por HTTPS. | ALTA |
|RNF-05| O sistema deve preservar a integridade e a consistência dos dados armazenados, evitando registros inválidos, duplicados ou relacionamentos inconsistentes. | ALTA |
|RNF-06| O sistema deve responder às operações de agendamento e consulta em até 3 segundos em condições normais de uso. | MÉDIA |
|RNF-07| A interface deve apresentar navegação consistente, textos legíveis e identificação clara das ações, campos e mensagens apresentadas ao usuário. | MÉDIA |
|RNF-08| A interface deve adotar práticas de acessibilidade, incluindo identificação adequada dos campos, contraste suficiente e possibilidade de navegação por teclado nas principais funcionalidades. | MÉDIA |
|RNF-09| O tratamento dos dados pessoais deve observar os princípios aplicáveis da Lei Geral de Proteção de Dados (LGPD), limitando a coleta e o acesso às informações necessárias ao funcionamento do sistema. | ALTA |

**Prioridade: Alta / Média / Baixa.**