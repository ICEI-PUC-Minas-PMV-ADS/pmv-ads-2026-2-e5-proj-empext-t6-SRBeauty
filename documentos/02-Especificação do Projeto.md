# Especificações do Projeto

## Perfis de Usuários

<table>
<tbody>
<tr>
<th colspan="2">Perfil 1: Aluno </th>
</tr>
<tr>
<td width="150px"><b>Descrição</b></td>
<td width="600px">
Aluno do ensino superior, seja educação pública ou privada. 
</td>
</tr>
<tr>
<td><b>Necessidades</b></td>
<td>
1. Acesso fácil e rápido a conteúdos didáticos de qualidade, sem custo adicional à sua vida acadêmica; 
2. Utilizar ambientes digitais em que esteja familiarizado; 
3. Conteúdos apresentados em mídias diversificadas;
4. Possibilidade de apoio de um monitor/tutor;
5. Exercícios de fixação com resolução. 
</td>
</tr>
</tbody>
</table>

<table>
<tbody>
<tr>
<th colspan="2">Perfil 2: Ex-aluno </th>
</tr>
<tr>
<td width="150px"><b>Descrição</b></td>
<td width="600px">
Ex-aluno do ensino superior. 
</td>
</tr>
<tr>
<td><b>Necessidades</b></td>
<td>
1. Entender as demandas dos alunos; 
2. Ambiente educacional para orientar e entrar em contato com os alunos.
</td>
</tr>
</tbody>
</table>


## Histórias de Usuários

Com base na análise das personas forma identificadas as seguintes histórias de usuários:

|EU COMO... `PERSONA`| QUERO/PRECISO ... `FUNCIONALIDADE`                                             |PARA ... `MOTIVO/VALOR`                 |
|--------------------|--------------------------------------------------------------------------------|----------------------------------------|
|Ex-aluno | ajudar estudantes de áreas diversas que estão com dificuldades nos estudos  | orientar e melhorar o desempenho acadêmico dos alunos. |
|Aluno | participar de uma atividade extra que emita certificados  | cumprir os créditos necessários para concluir a graduação.  |
|Aluno|acessar os materiais complementares do curso de uma maneira mais fácil  | otimizar o tempo de estudo e entender melhor o conteúdo.  |
|Aluno | sanar dúvidas que tenho sobre as matérias do curso com outros alunos ou ex-alunos   | entender melhor as matérias e criar uma rede de contatos. |
|Ex-aluno | auxiliar estudantes que estejam iniciando na área  | ajudar alunos que apresentem dificuldades semelhantes às que já tive. |
|Aluno |sanar todas as dúvidas de exercícios desde o início do curso | estar apto para as avaliações do primeiro semestre e assim não enfrentar maiores dificuldades ao longo do curso. |
|Aluno |procurar livros que me ajudem a ter melhor compreensão da matéria  | encontrar livros sobre determinadas matérias que tenham uma boa didática para iniciantes.|
|Aluno | consultar livros bem indicados por outros alunos   | ampliar meu conhecimento e conhecer pessoas com a mesma dificuldade. |
|Ex-aluno | compartilhar com os outros estudantes conhecimentos, e assim poder ajudar uns aos outros  | conectar com alunos e até poder formar amizades e grupos de estudos. |
|Aluno | aprender sobre conteúdos específicos da área com exemplos práticos e em mídias diferentes  | aplicar o conhecimento na prática.  |

## Project Model Canvas 

<img width="3174" height="2245" alt="ProjectModelCanvasA1 pdf" src="https://github.com/user-attachments/assets/73b1e1ba-c05d-47b3-92c2-5ae178b49563" />


## Requisitos

### Requisitos Funcionais

|ID    | Descrição do Requisito  | Prioridade |
|------|-----------------------------------------|----|
|RF-01| A aplicação deve permitir ao usuário cadastrar e fazer login em sua conta.   | ALTA | 
|RF-02| O sistema deve permitir que a Cliente consulte a disponibilidade de horários das profissionais.  | ALTA | 
|RF-03| O sistema deve permitir que a Cliente (ou a Profissional) agende um atendimento, impedindo conflito ou duplicidade de horário para a mesma profissional.    | ALTA |
|RF-04| O sistema deve permitir que a Profissional registre um atendimento realizado, incluindo o tipo de serviço prestado e a forma de pagamento (Pix, dinheiro ou cartão).    | MÉDIA |
|RF-05| O sistema deve calcular automaticamente o valor do repasse ao salão com base no percentual definido por tipo de serviço (ex.: cabeleireira 30%, manicure 20%), e não por profissional.  | ALTA |
|RF-06| Quando o pagamento for feito em cartão, o sistema deve permitir registrar a taxa da maquininha repassada à cliente.    | BAIXA |
|RF-07| O sistema deve permitir registrar quando o repasse de uma profissional ao salão foi efetivamente pago (equivalente ao "OK" hoje anotado na agenda física).    | MÉDIA |
|RF-08| O sistema deve permitir que a Proprietária registre despesas do salão (aluguel, água, energia, internet, materiais de uso e consumo, outras).   | MÉDIA |
|RF-09| O sistema deve permitir o fechamento financeiro semanal, consolidando entradas, saídas e resultado do período.  | ALTA |
|RF-10| O sistema deve permitir que a Proprietária consulte, diariamente: horários agendados, horários disponíveis e atendimentos realizados no dia.  | ALTA |
|RF-11| O sistema deve permitir que a Proprietária consulte, mensalmente: faturamento, total de despesas, valores recebidos e valores repassados pelas profissionais, e o resultado financeiro do mês.  | ALTA |
|RF-12| O sistema deve permitir o cadastro e a gestão dos horários de trabalho de cada profissional.   | MÉDIA |
|RF-13| O sistema deve autenticar os usuários de acordo com seu perfil (Cliente, Profissional, Proprietária).   | ALTA |

**Prioridade: Alta / Média / Baixa.  

### Requisitos Não Funcionais

|ID     | Descrição do Requisito  |Prioridade |
|-------|-------------------------|----|
|RNF-01| O sistema deve ser acessível via navegador web, com interface responsiva para uso em celular.  | ALTA | 
|RNF-02| O sistema deve impedir, em nível de banco de dados/regra de negócio, o agendamento duplicado no mesmo horário para a mesma profissional.  | ALTA | 
|RNF-03| As senhas dos usuários devem ser armazenadas de forma criptografada.  | ALTA | 
|RNF-04| O sistema deve responder às operações de agendamento e consulta em até 3 segundos em condições normais de uso.  | MÉDIA | 
|RNF-05| O sistema deve ter interface simples e intuitiva, adequada a usuárias sem familiaridade técnica avançada.  | MÉDIA | 
|RNF-06| O sistema deve estar disponível para uso durante o horário comercial do salão (alta disponibilidade em horário de funcionamento).  | ALTA | 
|RNF-07| O código-fonte e a documentação devem seguir os padrões definidos para entrega no GitHub Classroom.  | BAIXA | 
|RNF-08| O sistema deve manter histórico rastreável dos repasses e pagamentos, permitindo auditoria posterior (hoje feita por conferência de extrato bancário).  | ALTA | 



**Prioridade: Alta / Média / Baixa.

