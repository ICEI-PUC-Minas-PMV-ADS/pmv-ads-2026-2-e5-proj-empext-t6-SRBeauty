# Plano de Testes de Software

## Pré-requisitos

Para a realização dos testes de software, são necessários os seguintes requisitos:

- Sistema SR Beauty disponível para acesso;
- Navegador web compatível, como Chrome, Firefox, Opera ou Edge;
- Usuário cadastrado de acordo com o perfil que será utilizado no teste;
- Dados necessários para execução dos testes, como profissionais, serviços e informações de agendamento;
- Acesso às funcionalidades correspondentes ao perfil do usuário.

#

## Testes Funcionais

Os testes funcionais a serem realizados na aplicação SR Beauty são descritos a seguir.

<table>
 <tr>
   <th>Caso de teste</th>
   <th>Requisitos associados</th>
   <th>Objetivo do teste</th>
   <th>Passos</th>
   <th>Critérios de êxito</th>
   <th>Responsável</th>
 </tr>

 <tr>
   <td>CT-1: Verificar o funcionamento do cadastro e login.</td>
   <td>
    <ul>
     <li>RF-12: O sistema deve possuir autenticação de usuários de acordo com seus perfis de acesso.</li>
    </ul>
   </td>
   <td>Verificar se o usuário consegue realizar o cadastro e acessar o sistema utilizando as credenciais cadastradas.</td>
   <td>
    <ol>
     <li>Acessar o sistema SR Beauty.</li>
     <li>Acessar a opção de cadastro.</li>
     <li>Preencher os dados solicitados.</li>
     <li>Confirmar o cadastro.</li>
     <li>Acessar a tela de login.</li>
     <li>Informar as credenciais cadastradas.</li>
     <li>Confirmar o acesso.</li>
    </ol>
   </td>
   <td>O cadastro deve ser realizado com sucesso e o usuário deve conseguir acessar o sistema utilizando as credenciais cadastradas.</td>
   <td>Júlio César Villaça Cardoso</td>
 </tr>
</table>

---

<table>
 <tr>
   <th>Caso de teste</th>
   <th>Requisitos associados</th>
   <th>Objetivo do teste</th>
   <th>Passos</th>
   <th>Critérios de êxito</th>
   <th>Responsável</th>
 </tr>

 <tr>
   <td>CT-2: Verificar a visualização da disponibilidade das profissionais.</td>
   <td>
    <ul>
     <li>RF-01: O cliente deve poder consultar a disponibilidade de horários das profissionais.</li>
     <li>RF-11: O sistema deve permitir o gerenciamento dos horários de trabalho de cada profissional.</li>
    </ul>
   </td>
   <td>Verificar se o usuário consegue consultar corretamente os horários disponíveis das profissionais.</td>
   <td>
    <ol>
     <li>Realizar login no sistema.</li>
     <li>Acessar a tela de Agenda e Agendamentos.</li>
     <li>Selecionar uma profissional.</li>
     <li>Selecionar a data desejada.</li>
     <li>Visualizar os horários disponíveis.</li>
    </ol>
   </td>
   <td>O sistema deve apresentar corretamente os horários disponíveis da profissional selecionada, considerando sua jornada de trabalho e os horários já ocupados.</td>
   <td>[Nome do responsável]</td>
 </tr>
</table>

---

<table>
 <tr>
   <th>Caso de teste</th>
   <th>Requisitos associados</th>
   <th>Objetivo do teste</th>
   <th>Passos</th>
   <th>Critérios de êxito</th>
   <th>Responsável</th>
 </tr>

 <tr>
   <td>CT-3: Verificar o funcionamento do agendamento de atendimento.</td>
   <td>
    <ul>
     <li>RF-02: O cliente ou profissional deve poder realizar o agendamento de um atendimento.</li>
    </ul>
   </td>
   <td>Verificar se um atendimento pode ser agendado corretamente para uma profissional em um horário disponível.</td>
   <td>
    <ol>
     <li>Realizar login no sistema.</li>
     <li>Acessar a tela de Agenda e Agendamentos.</li>
     <li>Selecionar o cliente.</li>
     <li>Selecionar a profissional.</li>
     <li>Selecionar a data e o horário disponível.</li>
     <li>Confirmar o agendamento.</li>
    </ol>
   </td>
   <td>O agendamento deve ser registrado corretamente e o horário deve passar a constar como ocupado na agenda da profissional.</td>
   <td>[Nome do responsável]</td>
 </tr>
</table>

---

<table>
 <tr>
   <th>Caso de teste</th>
   <th>Requisitos associados</th>
   <th>Objetivo do teste</th>
   <th>Passos</th>
   <th>Critérios de êxito</th>
   <th>Responsável</th>
 </tr>

 <tr>
   <td>CT-4: Verificar o bloqueio de conflito de horários.</td>
   <td>
    <ul>
     <li>RF-02: O sistema deve impedir conflitos ou duplicidade de agendamento para uma mesma profissional.</li>
    </ul>
   </td>
   <td>Verificar se o sistema impede que dois atendimentos sejam agendados para a mesma profissional no mesmo horário.</td>
   <td>
    <ol>
     <li>Realizar login no sistema.</li>
     <li>Agendar um atendimento para uma profissional em determinado horário.</li>
     <li>Tentar realizar outro agendamento para a mesma profissional e horário.</li>
     <li>Confirmar o segundo agendamento.</li>
    </ol>
   </td>
   <td>O sistema deve impedir o segundo agendamento e informar que o horário selecionado já está ocupado.</td>
   <td>[Nome do responsável]</td>
 </tr>
</table>

---

<table>
 <tr>
   <th>Caso de teste</th>
   <th>Requisitos associados</th>
   <th>Objetivo do teste</th>
   <th>Passos</th>
   <th>Critérios de êxito</th>
   <th>Responsável</th>
 </tr>

 <tr>
   <td>CT-5: Verificar o registro do atendimento realizado.</td>
   <td>
    <ul>
     <li>RF-03: O profissional deve poder registrar o atendimento realizado, incluindo o tipo de serviço e a forma de pagamento.</li>
    </ul>
   </td>
   <td>Verificar se o profissional consegue registrar corretamente um atendimento após sua realização.</td>
   <td>
    <ol>
     <li>Realizar login como profissional.</li>
     <li>Acessar a agenda.</li>
     <li>Selecionar um atendimento agendado.</li>
     <li>Informar o serviço realizado.</li>
     <li>Informar a forma de pagamento.</li>
     <li>Confirmar o atendimento.</li>
    </ol>
   </td>
   <td>O atendimento deve ser registrado corretamente com o serviço realizado e a forma de pagamento informada.</td>
   <td>[Nome do responsável]</td>
 </tr>
</table>

---

<table>
 <tr>
   <th>Caso de teste</th>
   <th>Requisitos associados</th>
   <th>Objetivo do teste</th>
   <th>Passos</th>
   <th>Critérios de êxito</th>
   <th>Responsável</th>
 </tr>

 <tr>
   <td>CT-6: Verificar o registro da forma de pagamento e taxa da maquininha.</td>
   <td>
    <ul>
     <li>RF-03: O profissional deve registrar a forma de pagamento do atendimento.</li>
     <li>RF-05: Quando o pagamento for realizado por cartão, o sistema deve permitir o registro da taxa da maquininha repassada ao cliente.</li>
    </ul>
   </td>
   <td>Verificar se o sistema permite registrar corretamente a forma de pagamento e, quando aplicável, a taxa da maquininha.</td>
   <td>
    <ol>
     <li>Realizar login como profissional.</li>
     <li>Acessar o registro de atendimento.</li>
     <li>Selecionar um serviço realizado.</li>
     <li>Selecionar a forma de pagamento cartão.</li>
     <li>Informar a taxa da maquininha.</li>
     <li>Confirmar o registro.</li>
    </ol>
   </td>
   <td>O sistema deve registrar o pagamento como cartão e permitir o registro da taxa da maquininha informada.</td>
   <td>[Nome do responsável]</td>
 </tr>
</table>

---

<table>
 <tr>
   <th>Caso de teste</th>
   <th>Requisitos associados</th>
   <th>Objetivo do teste</th>
   <th>Passos</th>
   <th>Critérios de êxito</th>
   <th>Responsável</th>
 </tr>

 <tr>
   <td>CT-7: Verificar o cálculo do repasse ao salão.</td>
   <td>
    <ul>
     <li>RF-04: O sistema deve calcular o valor do repasse ao salão com base no percentual definido para o tipo de serviço.</li>
    </ul>
   </td>
   <td>Verificar se o sistema calcula corretamente o valor do repasse de acordo com o percentual configurado para o serviço realizado.</td>
   <td>
    <ol>
     <li>Realizar login como profissional ou proprietário.</li>
     <li>Acessar um atendimento realizado.</li>
     <li>Selecionar o tipo de serviço.</li>
     <li>Informar ou verificar o valor do atendimento.</li>
     <li>Verificar o percentual de repasse configurado para o serviço.</li>
     <li>Consultar o valor calculado do repasse.</li>
    </ol>
   </td>
   <td>O sistema deve calcular o repasse aplicando corretamente o percentual definido para o tipo de serviço, independentemente da profissional.</td>
   <td>[Nome do responsável]</td>
 </tr>
</table>

---

<table>
 <tr>
   <th>Caso de teste</th>
   <th>Requisitos associados</th>
   <th>Objetivo do teste</th>
   <th>Passos</th>
   <th>Critérios de êxito</th>
   <th>Responsável</th>
 </tr>

 <tr>
   <td>CT-8: Verificar o registro do pagamento do repasse ao salão.</td>
   <td>
    <ul>
     <li>RF-06: O sistema deve permitir registrar quando o repasse da profissional ao salão foi efetivamente pago.</li>
    </ul>
   </td>
   <td>Verificar se o sistema permite marcar corretamente o repasse como pago.</td>
   <td>
    <ol>
     <li>Realizar login como proprietário.</li>
     <li>Acessar a área de repasses.</li>
     <li>Localizar um repasse pendente.</li>
     <li>Registrar o pagamento do repasse.</li>
     <li>Salvar a alteração.</li>
    </ol>
   </td>
   <td>O repasse deve ser identificado como pago após o registro, deixando de constar como pendente.</td>
   <td>[Nome do responsável]</td>
 </tr>
</table>

---

<table>
 <tr>
   <th>Caso de teste</th>
   <th>Requisitos associados</th>
   <th>Objetivo do teste</th>
   <th>Passos</th>
   <th>Critérios de êxito</th>
   <th>Responsável</th>
 </tr>

 <tr>
   <td>CT-9: Verificar o cadastro de despesas do salão.</td>
   <td>
    <ul>
     <li>RF-07: A proprietária deve poder registrar as despesas do salão.</li>
    </ul>
   </td>
   <td>Verificar se a proprietária consegue registrar corretamente uma despesa do salão.</td>
   <td>
    <ol>
     <li>Realizar login como proprietária.</li>
     <li>Acessar a área financeira.</li>
     <li>Acessar o cadastro de despesas.</li>
     <li>Selecionar o tipo de despesa.</li>
     <li>Informar a descrição e o valor.</li>
     <li>Confirmar o cadastro.</li>
    </ol>
   </td>
   <td>A despesa deve ser registrada corretamente e apresentada na área financeira do sistema.</td>
   <td>[Nome do responsável]</td>
 </tr>
</table>

---

<table>
 <tr>
   <th>Caso de teste</th>
   <th>Requisitos associados</th>
   <th>Objetivo do teste</th>
   <th>Passos</th>
   <th>Critérios de êxito</th>
   <th>Responsável</th>
 </tr>

 <tr>
   <td>CT-10: Verificar o fechamento financeiro semanal.</td>
   <td>
    <ul>
     <li>RF-08: O sistema deve permitir o fechamento financeiro semanal, consolidando entradas, saídas e resultado do período.</li>
    </ul>
   </td>
   <td>Verificar se o sistema apresenta corretamente as informações financeiras referentes ao período semanal.</td>
   <td>
    <ol>
     <li>Realizar login como proprietária.</li>
     <li>Acessar a área financeira.</li>
     <li>Selecionar o período semanal desejado.</li>
     <li>Consultar as entradas financeiras.</li>
     <li>Consultar as despesas.</li>
     <li>Consultar os repasses.</li>
     <li>Verificar o resultado do período.</li>
    </ol>
   </td>
   <td>O sistema deve consolidar corretamente as entradas, saídas e demais informações financeiras do período selecionado, apresentando o resultado semanal.</td>
   <td>[Nome do responsável]</td>
 </tr>
</table>

---

<table>
 <tr>
   <th>Caso de teste</th>
   <th>Requisitos associados</th>
   <th>Objetivo do teste</th>
   <th>Passos</th>
   <th>Critérios de êxito</th>
   <th>Responsável</th>
 </tr>

 <tr>
   <td>CT-11: Verificar o relatório financeiro mensal.</td>
   <td>
    <ul>
     <li>RF-10: O sistema deve permitir a visualização mensal das receitas, despesas, valores recebidos, repasses realizados e resultado do período.</li>
    </ul>
   </td>
   <td>Verificar se o sistema apresenta corretamente os dados financeiros consolidados do mês.</td>
   <td>
    <ol>
     <li>Realizar login como proprietária.</li>
     <li>Acessar a área financeira.</li>
     <li>Selecionar o mês desejado.</li>
     <li>Consultar as receitas.</li>
     <li>Consultar as despesas.</li>
     <li>Consultar os repasses.</li>
     <li>Verificar o resultado mensal.</li>
    </ol>
   </td>
   <td>O sistema deve apresentar corretamente as receitas, despesas, repasses e resultado financeiro referentes ao mês selecionado.</td>
   <td>[Nome do responsável]</td>
 </tr>
</table>

---

<table>
 <tr>
   <th>Caso de teste</th>
   <th>Requisitos associados</th>
   <th>Objetivo do teste</th>
   <th>Passos</th>
   <th>Critérios de êxito</th>
   <th>Responsável</th>
 </tr>

 <tr>
   <td>CT-12: Verificar a visualização da agenda diária pela proprietária.</td>
   <td>
    <ul>
     <li>RF-09: O sistema deve permitir à proprietária visualizar os horários agendados, horários disponíveis e atendimentos realizados no dia.</li>
    </ul>
   </td>
   <td>Verificar se a proprietária consegue visualizar corretamente a situação dos atendimentos do dia.</td>
   <td>
    <ol>
     <li>Realizar login como proprietária.</li>
     <li>Acessar o dashboard ou agenda.</li>
     <li>Selecionar o dia desejado.</li>
     <li>Visualizar os horários agendados.</li>
     <li>Visualizar os horários disponíveis.</li>
     <li>Visualizar os atendimentos realizados.</li>
    </ol>
   </td>
   <td>A agenda deve apresentar corretamente os horários agendados, disponíveis e os atendimentos realizados no dia selecionado.</td>
   <td>[Nome do responsável]</td>
 </tr>
</table>

---

<table>
 <tr>
   <th>Caso de teste</th>
   <th>Requisitos associados</th>
   <th>Objetivo do teste</th>
   <th>Passos</th>
   <th>Critérios de êxito</th>
   <th>Responsável</th>
 </tr>

 <tr>
   <td>CT-13: Verificar o cadastro e configuração das profissionais.</td>
   <td>
    <ul>
     <li>RF-11: O sistema deve permitir o gerenciamento dos horários de trabalho das profissionais.</li>
    </ul>
   </td>
   <td>Verificar se a proprietária consegue cadastrar e configurar os horários de trabalho das profissionais.</td>
   <td>
    <ol>
     <li>Realizar login como proprietária.</li>
     <li>Acessar a área de administração.</li>
     <li>Selecionar uma profissional.</li>
     <li>Informar os horários de trabalho.</li>
     <li>Salvar as configurações.</li>
     <li>Acessar a agenda da profissional.</li>
    </ol>
   </td>
   <td>Os horários configurados devem ser armazenados e considerados na disponibilidade apresentada na agenda.</td>
   <td>[Nome do responsável]</td>
 </tr>
</table>

---

<table>
 <tr>
   <th>Caso de teste</th>
   <th>Requisitos associados</th>
   <th>Objetivo do teste</th>
   <th>Passos</th>
   <th>Critérios de êxito</th>
   <th>Responsável</th>
 </tr>

 <tr>
   <td>CT-14: Verificar o cadastro dos serviços e percentuais de repasse.</td>
   <td>
    <ul>
     <li>RF-04: O sistema deve utilizar o percentual definido para cada tipo de serviço no cálculo do repasse.</li>
    </ul>
   </td>
   <td>Verificar se a proprietária consegue cadastrar serviços e definir seus respectivos percentuais de repasse.</td>
   <td>
    <ol>
     <li>Realizar login como proprietária.</li>
     <li>Acessar a área de administração.</li>
     <li>Acessar o cadastro de serviços.</li>
     <li>Cadastrar ou editar um serviço.</li>
     <li>Informar o percentual de repasse correspondente.</li>
     <li>Salvar as informações.</li>
     <li>Realizar um atendimento utilizando o serviço configurado.</li>
    </ol>
   </td>
   <td>O serviço deve ser cadastrado corretamente e o percentual configurado deve ser utilizado posteriormente no cálculo do repasse.</td>
   <td>[Nome do responsável]</td>
 </tr>
</table>

---

<table>
 <tr>
   <th>Caso de teste</th>
   <th>Requisitos associados</th>
   <th>Objetivo do teste</th>
   <th>Passos</th>
   <th>Critérios de êxito</th>
   <th>Responsável</th>
 </tr>

 <tr>
   <td>CT-15: Verificar a integração entre agendamento, atendimento, repasse e financeiro.</td>
   <td>
    <ul>
     <li>RF-02: O cliente ou profissional deve poder realizar agendamentos.</li>
     <li>RF-03: O profissional deve poder registrar o atendimento realizado.</li>
     <li>RF-04: O sistema deve calcular o repasse de acordo com o tipo de serviço.</li>
     <li>RF-06: O sistema deve permitir registrar o pagamento do repasse.</li>
     <li>RF-08: O sistema deve consolidar as informações financeiras semanalmente.</li>
     <li>RF-10: O sistema deve apresentar as informações financeiras mensais.</li>
    </ul>
   </td>
   <td>Verificar se as informações registradas em um atendimento são refletidas corretamente nas demais funcionalidades do sistema.</td>
   <td>
    <ol>
     <li>Realizar um agendamento.</li>
     <li>Registrar o atendimento realizado.</li>
     <li>Informar a forma de pagamento.</li>
     <li>Verificar o cálculo do repasse.</li>
     <li>Registrar o pagamento do repasse.</li>
     <li>Acessar a área financeira.</li>
     <li>Consultar os dados do período.</li>
    </ol>
   </td>
   <td>As informações do agendamento, atendimento, pagamento, repasse e financeiro devem permanecer consistentes e refletir corretamente as operações realizadas.</td>
   <td>[Nome do responsável]</td>
 </tr>
</table>

#

## Registro dos Resultados

| Caso de Teste | Resultado | Observação |
|---|---|---|
| Caso de Teste | Resultado | Observação |
|---|---|---|
| CT-1 | Aprovado | Cadastro e login realizados com sucesso, conforme comportamento esperado. |
| CT-2 | [Aprovado/Reprovado] | [Observação] |
| CT-3 | [Aprovado/Reprovado] | [Observação] |
| CT-4 | [Aprovado/Reprovado] | [Observação] |
| CT-5 | [Aprovado/Reprovado] | [Observação] |
| CT-6 | [Aprovado/Reprovado] | [Observação] |
| CT-7 | [Aprovado/Reprovado] | [Observação] |
| CT-8 | [Aprovado/Reprovado] | [Observação] |
| CT-9 | [Aprovado/Reprovado] | [Observação] |
| CT-10 | [Aprovado/Reprovado] | [Observação] |
| CT-11 | [Aprovado/Reprovado] | [Observação] |
| CT-12 | [Aprovado/Reprovado] | [Observação] |
| CT-13 | [Aprovado/Reprovado] | [Observação] |
| CT-14 | [Aprovado/Reprovado] | [Observação] |
| CT-15 | [Aprovado/Reprovado] | [Observação] |
