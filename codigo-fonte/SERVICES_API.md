# Módulo de Serviços e Execução de Atendimentos

Este módulo está integrado à aplicação Flask existente em `app.py` e expõe uma API JSON. Não implementa autenticação, agenda, pagamentos, caixa ou comissões. As rotas não adicionam um mecanismo próprio de autenticação; conecte-as ao controle de acesso fornecido pelo módulo responsável antes de disponibilizá-las em produção.

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

Após iniciar a aplicação e autenticar-se, abra `/servicos` para o catálogo e `/atendimentos` para registrar e acompanhar execuções. As páginas reutilizam o menu lateral e as folhas de estilo do painel. Os dados de usuários disponíveis nas seleções de atendimento são consultados pelo servidor diretamente da tabela `usuarios`; os registros exibidos e criados na página continuam usando os endpoints reais da API descritos abaixo.

## Modelo e dependências de integração

- `Service` (`servicos`): catálogo com preço decimal, duração em minutos e desativação lógica.
- `Appointment` (`atendimentos`): cliente, profissional responsável, data agendada, status, horários de início/fim e duração real.
- `AppointmentService` (`atendimento_servicos`): serviços incluídos e snapshots do nome, preço cobrado, duração prevista e profissional que executou cada serviço.
- `cliente_id` e `profissional_id` referenciam a tabela compartilhada `usuarios`. A API exige que o usuário exista e tenha o tipo `cliente` ou `profissional`, respectivamente.
- `agendamento_id` é uma referência externa opcional, sem chave estrangeira, pois o módulo de agenda ainda não foi integrado. Sua validação e sincronização devem ser acordadas com o responsável pela agenda.
- Serviços catalogados são desativados em vez de apagados fisicamente, preservando as referências dos atendimentos e seu histórico.

No momento da criação do atendimento, o valor e o nome são copiados para cada item. Pode-se informar `valor_cobrado` diferente do preço atual para registrar o valor efetivamente combinado. Mudanças posteriores no catálogo não alteram o histórico. `profissional_id` pode ser especificado por item; caso omitido, usa o profissional responsável pelo atendimento.

## Endpoints

Todas as respostas usam JSON, exceto a exclusão bem-sucedida, que retorna `204 No Content`. Erros seguem `{"erro": "mensagem compreensível"}`.

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
| `POST /api/atendimentos` | Registra atendimento no estado `aguardando` com um ou mais serviços | `201`, `400` |
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
2. Ao integrar agenda, a equipe responsável pode fornecer uma referência `agendamento_id` validada contra a entidade de agenda. Hoje é somente um identificador opcional, sem checagem de existência nem regras de disponibilidade/conflito.
3. Integrar a autenticação/controle de acesso do módulo responsável às rotas antes de produção; este módulo não emite tokens nem declara middleware de autenticação.
4. O módulo financeiro pode consumir `valor_cobrado` e os IDs do atendimento/serviço, e o módulo de comissões pode consumir `profissional_id` por item. Nenhum cálculo ou lançamento financeiro é feito aqui.

## Interface web

- `GET /servicos`: lista o catálogo, permite cadastrar/editar serviços e desativar serviços com confirmação.
- `GET /atendimentos`: permite filtrar/listar atendimentos, registrar vários serviços com seus valores e profissionais executores, consultar os detalhes e avançar o status para a próxima etapa válida.
- As páginas requerem a sessão Flask-Login já existente. A interface não cria contas nem substitui a autenticação.
- A listagem de clientes e profissionais é obtida de `usuarios` somente no servidor ao renderizar a página; não existe uma rota de usuários acrescentada por este módulo. Se uma das listas estiver vazia, integre primeiro os registros do módulo de usuários.
