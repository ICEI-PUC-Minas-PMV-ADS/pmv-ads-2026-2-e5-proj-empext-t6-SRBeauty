# Módulos de Agenda, Serviços e Execução de Atendimentos

Os módulos estão integrados à aplicação Flask existente em `app.py` e expõem APIs JSON. A agenda tem interface web em `/agenda` e requer sessão Flask-Login para proprietárias e profissionais. As APIs de serviços e atendimentos mantêm o comportamento de autenticação preexistente. Pagamentos, caixa e comissões não são implementados aqui.

## Executar e testar

Na pasta `codigo-fonte`:

```powershell
python -m pip install -r requirements.txt
python app.py
```

A aplicação inicializa as tabelas ausentes com `db.create_all()`. O banco pode ser configurado por `DATABASE_URL`; sem essa variável, usa `srbeauty.db` nessa pasta. Para executar os testes automatizados sem alterar o banco local:

```powershell
python -m unittest discover -s tests -v
```

Após iniciar a aplicação e autenticar-se, abra `/agenda` para visualizar a agenda e gerenciar escalas e bloqueios, `/servicos` para o catálogo e `/atendimentos` para registrar e acompanhar execuções. As páginas reutilizam o menu lateral e as folhas de estilo do painel. Os dados de usuários disponíveis nas seleções de atendimento são consultados pelo servidor diretamente da tabela `usuarios`; os registros exibidos e criados na página continuam usando os endpoints reais da API descritos abaixo.

## Modelo e dependências de integração

- `Service` (`servicos`): catálogo com preço decimal, duração em minutos e desativação lógica.
- `Appointment` (`atendimentos`): cliente, profissional responsável, data agendada, status, horários de início/fim e duração real.
- `AppointmentService` (`atendimento_servicos`): serviços incluídos e snapshots do nome, preço cobrado, duração prevista e profissional que executou cada serviço.
- `ProfessionalSchedule` (`horarios_profissionais`): intervalos semanais recorrentes de cada profissional. Um dia pode ter vários intervalos; registre manhã e tarde em linhas diferentes para deixar o almoço indisponível.
- `AgendaBlock` (`bloqueios_agenda`): bloqueio datado com início, fim e motivo.
- `cliente_id` e `profissional_id` referenciam a tabela compartilhada `usuarios`. A API exige que o usuário exista e tenha o tipo `cliente` ou `profissional`, respectivamente.
- `agendamento_id` permanece uma referência externa opcional, sem chave estrangeira.
- Serviços catalogados são desativados em vez de apagados fisicamente, preservando as referências dos atendimentos e seu histórico.
- Horários e datas da agenda usam o fuso `America/Sao_Paulo`; datas e horas de atendimentos/bloqueios recebidas pela API devem incluir fuso explícito.
- A criação de atendimentos verifica o expediente configurado, bloqueios e conflitos de intervalo, usando a soma das durações previstas para cada profissional. Se nenhuma escala semanal foi configurada para a profissional, a validação de expediente é omitida por compatibilidade, mas conflitos com atendimentos e bloqueios continuam ativos.

No momento da criação do atendimento, o valor e o nome são copiados para cada item. Pode-se informar `valor_cobrado` diferente do preço atual para registrar o valor efetivamente combinado. Mudanças posteriores no catálogo não alteram o histórico. `profissional_id` pode ser especificado por item; caso omitido, usa o profissional responsável pelo atendimento. A criação retorna `409 Conflict` quando o intervalo se sobrepõe a outro atendimento ativo ou bloqueio, ou não cabe em um intervalo da escala já cadastrada.

## Endpoints

Todas as respostas usam JSON, exceto exclusões bem-sucedidas, que retornam `204 No Content`. Erros seguem `{"erro": "mensagem compreensível"}`. Os endpoints da agenda exigem autenticação: uma profissional só consulta e gerencia os próprios horários e bloqueios; a proprietária pode consultar e gerenciar todas as profissionais. Usuários clientes recebem `403`; requisições sem sessão recebem `401`.

### Agenda

| Método e caminho | Descrição | Respostas principais |
|---|---|---|
| `GET /api/horarios?profissional_id=<id>` | Lista intervalos semanais; parâmetro opcional para a proprietária | `200`, `400`, `403`, `404` |
| `POST /api/horarios` | Cria um intervalo de escala | `201`, `400`, `403`, `409` |
| `POST /api/horarios/lote` | Cria o mesmo intervalo para vários dias da semana de uma vez | `201`, `400`, `403`, `409` |
| `GET /api/horarios/<id>` | Consulta um intervalo | `200`, `403`, `404` |
| `PUT /api/horarios/<id>` | Atualiza dia e intervalo | `200`, `400`, `403`, `404`, `409` |
| `DELETE /api/horarios/<id>` | Remove um intervalo | `204`, `403`, `404` |
| `GET /api/bloqueios?profissional_id=<id>` | Lista bloqueios da agenda | `200`, `400`, `403`, `404` |
| `POST /api/bloqueios` | Cria bloqueio de agenda | `201`, `400`, `403`, `409` |
| `GET /api/bloqueios/<id>` | Consulta um bloqueio | `200`, `403`, `404` |
| `PUT /api/bloqueios/<id>` | Atualiza período e motivo | `200`, `400`, `403`, `404`, `409` |
| `DELETE /api/bloqueios/<id>` | Remove um bloqueio | `204`, `403`, `404` |
| `GET /api/agenda/diaria?data=AAAA-MM-DD` | Agenda diária da data local; aceita `profissional_id` | `200`, `400`, `403`, `404` |
| `GET /api/agenda/semanal?semana=AAAA-MM-DD` | Semana de segunda a domingo que contém a data; aceita `profissional_id` | `200`, `400`, `403`, `404` |

`dia_semana` usa `0` para segunda-feira e `6` para domingo. Horários da escala seguem `HH:MM`; intervalos não podem se sobrepor. Exemplo de criação de horário:

```json
{
  "profissional_id": 2,
  "dia_semana": 0,
  "inicio": "09:00",
  "fim": "12:00"
}
```

Para aplicar o mesmo intervalo em vários dias de uma vez, envie `dias_semana` para `POST /api/horarios/lote`. Por exemplo, segunda a sábado:

```json
{
  "profissional_id": 2,
  "dias_semana": [0, 1, 2, 3, 4, 5],
  "inicio": "09:00",
  "fim": "12:00"
}
```

O lote é validado como uma operação única: se houver sobreposição em qualquer um dos dias, nenhum horário é gravado.

Cadastre outro intervalo para o mesmo dia, por exemplo `13:00`–`18:00`, para representar o almoço.

Bloqueios usam `inicio` e `fim` ISO 8601 com fuso e `motivo` (até 120 caracteres):

```json
{
  "profissional_id": 2,
  "inicio": "2026-10-09T14:00:00-03:00",
  "fim": "2026-10-09T16:00:00-03:00",
  "motivo": "Consulta médica"
}
```

As visões diárias e semanais retornam `inicio`, `fim`, `eventos`, `horarios` e `profissionais`. Cada evento indica `tipo` (`atendimento` ou `bloqueio`) e seu período. Sem `profissional_id`, a proprietária recebe as profissionais; a profissional autenticada recebe somente seus próprios dados. Datas não informadas usam a data atual em `America/Sao_Paulo`.

### Serviços

| Método e caminho | Descrição | Respostas principais |
|---|---|---|
| `GET /api/servicos` | Lista serviços ativos, por nome | `200` |
| `GET /api/servicos?incluir_inativos=true` | Inclui serviços desativados | `200`, `400` |
| `POST /api/servicos` | Cadastra serviço | `201`, `400` |
| `GET /api/servicos/<id>` | Consulta serviço | `200`, `404` |
| `PUT /api/servicos/<id>` | Atualiza nome, descrição, preço, duração e, opcionalmente, `ativo` | `200`, `400`, `404` |
| `DELETE /api/servicos/<id>` | Desativa o serviço sem apagar histórico | `204`, `404` |

Campos obrigatórios para criação/atualização: `nome` (1–120 caracteres), `preco` (não negativo, até duas casas decimais) e `duracao_minutos` (inteiro positivo). `descricao` é opcional (até 1000 caracteres); em `PUT`, envie todos os campos requeridos.

Exemplo:

```http
POST /api/servicos
Content-Type: application/json
```

```json
{
  "nome": "Manicure",
  "descricao": "Manicure tradicional",
  "preco": "45.00",
  "duracao_minutos": 40
}
```

Resposta `201`:

```json
{
  "id": 1,
  "nome": "Manicure",
  "descricao": "Manicure tradicional",
  "preco": "45.00",
  "duracao_minutos": 40,
  "ativo": true,
  "criado_em": "2026-10-08T...",
  "atualizado_em": "2026-10-08T..."
}
```

### Atendimentos

| Método e caminho | Descrição | Respostas principais |
|---|---|---|
| `POST /api/atendimentos` | Registra atendimento no estado `aguardando` com um ou mais serviços | `201`, `400`, `409` |
| `GET /api/atendimentos` | Lista atendimentos, ordenados pela data agendada | `200` |
| `GET /api/atendimentos?status=aguardando` | Filtra por `aguardando`, `em_atendimento` ou `concluido` | `200`, `400` |
| `GET /api/atendimentos/<id>` | Consulta detalhes e snapshots dos serviços | `200`, `404` |
| `PATCH /api/atendimentos/<id>/status` | Avança o estado operacional | `200`, `400`, `404`, `409` |

Para criar, envie `cliente_id`, `profissional_id`, `agendado_para` em ISO 8601 com fuso explícito e uma lista não vazia de itens `servicos`. Cada item tem `servico_id` e pode conter `profissional_id` e `valor_cobrado`. `agendamento_id` e `observacoes` são opcionais.

```json
{
  "cliente_id": 1,
  "profissional_id": 2,
  "agendamento_id": 27,
  "agendado_para": "2026-10-09T10:00:00-03:00",
  "observacoes": "Preferência por esmalte claro.",
  "servicos": [
    {"servico_id": 1, "valor_cobrado": "42.00"},
    {"servico_id": 2, "profissional_id": 3}
  ]
}
```

O fluxo permitido é `aguardando → em_atendimento → concluido`. Para iniciar:

```json
{"status": "em_atendimento"}
```

O horário de início é registrado pelo servidor. Para concluir, informe o status; opcionalmente informe `concluido_em` (ISO 8601 com fuso), `duracao_real_minutos` (inteiro positivo) e `observacoes`. Se não for informada a hora de conclusão, o servidor registra a hora atual; se não for informada duração real, ela é calculada a partir dos horários, com mínimo de um minuto. Uma conclusão anterior ao início é rejeitada. Tentativas de pular ou repetir uma transição retornam `409`.

## Integração com os outros módulos

1. Manter a tabela `usuarios` compartilhada com IDs e tipos `cliente`/`profissional` conforme já existente; não criar tabelas paralelas de clientes ou profissionais.
2. `agendamento_id` continua opcional e sem checagem de existência; pode ser ligado a uma entidade de reserva futura.
3. As rotas novas da agenda usam a sessão Flask-Login e validam papéis de proprietária/profissional. As APIs de serviços/atendimentos conservam as regras de autenticação existentes no projeto.
4. O módulo financeiro pode consumir `valor_cobrado` e os IDs do atendimento/serviço, e o módulo de comissões pode consumir `profissional_id` por item. Nenhum cálculo ou lançamento financeiro é feito aqui.

## Interface web

- `GET /agenda`: mostra visões diária e semanal com cards separados para cada profissional, permite gerenciar intervalos de escala e bloqueios, e filtra a agenda por profissional para a proprietária.
- `GET /servicos`: lista o catálogo, permite cadastrar/editar serviços e desativar serviços com confirmação.
- `GET /atendimentos`: permite filtrar/listar atendimentos, registrar vários serviços com seus valores e profissionais executores, consultar os detalhes e avançar o status para a próxima etapa válida.
- As páginas requerem a sessão Flask-Login já existente. A interface não cria contas nem substitui a autenticação.
- A listagem de clientes e profissionais é obtida de `usuarios` somente no servidor ao renderizar a página; não existe uma rota de usuários acrescentada por este módulo. Se uma das listas estiver vazia, integre primeiro os registros do módulo de usuários.
