(() => {
  const page = document.querySelector("#appointmentsPage");
  if (!page) return;

  const body = document.querySelector("#appointmentsTableBody");
  const notice = document.querySelector("#appointmentsNotice");
  const dialog = document.querySelector("#appointmentDialog");
  const form = document.querySelector("#appointmentForm");
  const formError = document.querySelector("#appointmentFormError");
  const saveButton = document.querySelector("#saveAppointmentButton");
  const detailsDialog = document.querySelector("#detailsDialog");
  const serviceRows = document.querySelector("#appointmentServiceRows");
  const statusFilter = document.querySelector("#statusFilter");
  const directory = JSON.parse(document.querySelector("#userDirectory").textContent);
  const users = new Map(
    [...directory.clientes, ...directory.profissionais].map((user) => [user.id, user.nome]),
  );
  let services = [];
  let noticeTimer;

  const money = (value) => new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(Number(value));
  const statusLabels = {
    aguardando: "Aguardando",
    em_atendimento: "Em atendimento",
    concluido: "Concluído",
  };

  function announce(message, type = "success") {
    window.clearTimeout(noticeTimer);
    notice.textContent = message;
    notice.className = `notice ${type}`;
    notice.hidden = false;
    noticeTimer = window.setTimeout(() => { notice.hidden = true; }, 7000);
  }

  async function request(url, options = {}) {
    const response = await fetch(url, {
      ...options,
      headers: { "Content-Type": "application/json", ...options.headers },
    });
    if (response.status === 204) return null;
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.erro || "Não foi possível concluir a operação.");
    return payload;
  }

  function cell(content, className) {
    const result = document.createElement("td");
    if (className) result.className = className;
    if (content instanceof Node) result.append(content);
    else result.textContent = content;
    return result;
  }

  function formatDate(value) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value || "—";
    return new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(date);
  }

  function renderAppointment(appointment) {
    const row = document.createElement("tr");
    const scheduled = document.createElement("span");
    scheduled.textContent = formatDate(appointment.agendado_para);
    const actual = document.createElement("small");
    actual.className = "muted-line";
    if (appointment.iniciado_em) actual.textContent = `Início: ${formatDate(appointment.iniciado_em)}`;
    if (appointment.concluido_em) actual.textContent += `${actual.textContent ? " · " : ""}Fim: ${formatDate(appointment.concluido_em)}`;
    const scheduleBlock = document.createElement("div");
    scheduleBlock.append(scheduled, actual);

    const serviceList = document.createElement("div");
    let total = 0;
    appointment.servicos.forEach((service) => {
      total += Number(service.valor_cobrado);
      const line = document.createElement("span");
      line.className = "appointment-service";
      line.append(document.createTextNode(service.nome_servico));
      const amount = document.createElement("small");
      amount.textContent = ` · ${money(service.valor_cobrado)}`;
      line.append(amount);
      serviceList.append(line);
    });
    const totalLine = document.createElement("strong");
    totalLine.className = "muted-line";
    totalLine.textContent = `Total: ${money(total)}`;
    serviceList.append(totalLine);

    const badge = document.createElement("span");
    badge.className = `status-badge status-${appointment.status}`;
    badge.textContent = statusLabels[appointment.status] || appointment.status;
    const actions = document.createElement("div");
    actions.className = "row-actions";
    const details = document.createElement("button");
    details.type = "button";
    details.className = "small-button";
    details.textContent = "Detalhes";
    details.addEventListener("click", () => showDetails(appointment.id));
    actions.append(details);
    if (appointment.status === "aguardando" || appointment.status === "em_atendimento") {
      const nextStatus = appointment.status === "aguardando" ? "em_atendimento" : "concluido";
      const next = document.createElement("button");
      next.type = "button";
      next.className = "small-button";
      next.textContent = nextStatus === "em_atendimento" ? "Iniciar" : "Concluir";
      next.addEventListener("click", () => advanceStatus(appointment, nextStatus));
      actions.append(next);
    }

    row.append(
      cell(scheduleBlock),
      cell(users.get(appointment.cliente_id) || `Cliente #${appointment.cliente_id}`),
      cell(users.get(appointment.profissional_id) || `Profissional #${appointment.profissional_id}`),
      cell(serviceList),
      cell(badge),
      cell(actions, "actions-heading"),
    );
    body.append(row);
  }

  async function loadAppointments() {
    const selected = statusFilter.value;
    body.replaceChildren();
    const loading = document.createElement("td");
    loading.colSpan = 6;
    loading.className = "table-message";
    loading.textContent = "Carregando atendimentos…";
    const loadingRow = document.createElement("tr");
    loadingRow.append(loading);
    body.append(loadingRow);
    try {
      const query = selected ? `?status=${encodeURIComponent(selected)}` : "";
      const appointments = await request(`/api/atendimentos${query}`);
      body.replaceChildren();
      if (!appointments.length) {
        const empty = document.createElement("td");
        empty.colSpan = 6;
        empty.className = "table-message";
        empty.textContent = selected
          ? "Não há atendimentos com este status."
          : "Nenhum atendimento registrado. Cadastre o primeiro atendimento para acompanhar sua execução.";
        const row = document.createElement("tr");
        row.append(empty);
        body.append(row);
        return;
      }
      appointments.forEach(renderAppointment);
    } catch (error) {
      body.replaceChildren();
      const empty = document.createElement("td");
      empty.colSpan = 6;
      empty.className = "table-message";
      empty.textContent = error.message;
      const row = document.createElement("tr");
      row.append(empty);
      body.append(row);
    }
  }

  function option(value, label) {
    const element = document.createElement("option");
    element.value = String(value);
    element.textContent = label;
    return element;
  }

  function refreshServiceOptions() {
    const selectedIds = [...serviceRows.querySelectorAll(".service-select")]
      .map((select) => select.value)
      .filter(Boolean);
    serviceRows.querySelectorAll(".service-select").forEach((select) => {
      const current = select.value;
      [...select.options].forEach((item) => {
        if (item.value) {
          item.disabled = item.value !== current && selectedIds.includes(item.value);
        }
      });
    });
  }

  function addServiceRow() {
    const row = document.createElement("div");
    row.className = "service-row";
    const select = document.createElement("select");
    select.className = "service-select";
    select.setAttribute("aria-label", "Serviço");
    select.required = true;
    select.append(option("", "Selecione um serviço"));
    services.forEach((service) => select.append(option(service.id, service.nome)));

    const price = document.createElement("input");
    price.className = "price-input";
    price.type = "number";
    price.min = "0";
    price.max = "99999999.99";
    price.step = "0.01";
    price.placeholder = "Preço cobrado";
    price.inputMode = "decimal";
    price.required = true;
    price.setAttribute("aria-label", "Valor cobrado em reais");

    const provider = document.createElement("select");
    provider.className = "provider-select";
    provider.setAttribute("aria-label", "Profissional que executou o serviço");
    provider.append(option("", "Profissional executora (responsável)"));
    directory.profissionais.forEach((user) => provider.append(option(user.id, user.nome)));

    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "remove-service";
    remove.textContent = "×";
    remove.setAttribute("aria-label", "Remover serviço");
    remove.addEventListener("click", () => {
      row.remove();
      refreshServiceOptions();
    });
    select.addEventListener("change", () => {
      const selectedService = services.find((service) => String(service.id) === select.value);
      price.value = selectedService ? selectedService.preco : "";
      refreshServiceOptions();
    });
    row.append(select, price, provider, remove);
    serviceRows.append(row);
    refreshServiceOptions();
  }

  function closeAndResetForm() {
    form.reset();
    formError.hidden = true;
    formError.textContent = "";
    serviceRows.replaceChildren();
    if (services.length) addServiceRow();
  }

  async function openCreate() {
    if (!directory.clientes.length || !directory.profissionais.length) {
      announce("Cadastre clientes e profissionais pela integração de Usuários antes de registrar atendimentos.", "error");
      return;
    }
    if (!services.length) {
      announce("Cadastre um serviço ativo antes de registrar atendimentos.", "error");
      return;
    }
    closeAndResetForm();
    dialog.showModal();
  }

  async function advanceStatus(appointment, nextStatus) {
    const verb = nextStatus === "em_atendimento" ? "iniciar" : "concluir";
    const label = nextStatus === "em_atendimento" ? "Em Atendimento" : "Concluído";
    if (!window.confirm(`Deseja ${verb} este atendimento? O status será alterado para “${label}”.`)) return;
    try {
      await request(`/api/atendimentos/${appointment.id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status: nextStatus }),
      });
      announce(`Atendimento atualizado: ${label.toLowerCase()}.`);
      await loadAppointments();
    } catch (error) {
      announce(error.message, "error");
    }
  }

  function detailBlock(title, content) {
    const block = document.createElement("section");
    block.className = "detail-block";
    const heading = document.createElement("h3");
    heading.textContent = title;
    block.append(heading, content);
    return block;
  }

  function paragraph(text) {
    const element = document.createElement("p");
    element.textContent = text;
    return element;
  }

  async function showDetails(id) {
    document.querySelector("#detailsSubtitle").textContent = "Carregando detalhes…";
    const content = document.querySelector("#appointmentDetails");
    content.replaceChildren();
    detailsDialog.showModal();
    try {
      const appointment = await request(`/api/atendimentos/${id}`);
      document.querySelector("#detailsSubtitle").textContent = `Atendimento #${appointment.id}`;
      const general = document.createElement("div");
      general.append(
        paragraph(`Status: ${statusLabels[appointment.status] || appointment.status}`),
        paragraph(`Cliente: ${users.get(appointment.cliente_id) || `Cliente #${appointment.cliente_id}`}`),
        paragraph(`Profissional responsável: ${users.get(appointment.profissional_id) || `Profissional #${appointment.profissional_id}`}`),
        paragraph(`Agendado para: ${formatDate(appointment.agendado_para)}`),
        paragraph(`Iniciado em: ${appointment.iniciado_em ? formatDate(appointment.iniciado_em) : "Ainda não iniciado"}`),
        paragraph(`Concluído em: ${appointment.concluido_em ? formatDate(appointment.concluido_em) : "Ainda não concluído"}`),
        paragraph(`Duração real: ${appointment.duracao_real_minutos ? `${appointment.duracao_real_minutos} minutos` : "Não registrada"}`),
      );
      if (appointment.agendamento_id) general.append(paragraph(`Referência de agendamento: #${appointment.agendamento_id}`));
      content.append(detailBlock("Resumo", general));

      const servicesBlock = document.createElement("div");
      let total = 0;
      appointment.servicos.forEach((service) => {
        total += Number(service.valor_cobrado);
        const line = document.createElement("div");
        line.className = "detail-service";
        const description = document.createElement("span");
        description.append(document.createTextNode(service.nome_servico));
        const provider = document.createElement("small");
        provider.textContent = `Executado por ${users.get(service.profissional_id) || `profissional #${service.profissional_id}`} · ${service.duracao_prevista_minutos} min`;
        description.append(provider);
        const value = document.createElement("strong");
        value.textContent = money(service.valor_cobrado);
        line.append(description, value);
        servicesBlock.append(line);
      });
      const totalLine = document.createElement("p");
      totalLine.textContent = `Total cobrado: ${money(total)}`;
      servicesBlock.append(totalLine);
      content.append(detailBlock("Serviços executados", servicesBlock));
      content.append(detailBlock("Observações", paragraph(appointment.observacoes || "Nenhuma observação registrada.")));
    } catch (error) {
      document.querySelector("#detailsSubtitle").textContent = "Não foi possível carregar";
      content.append(detailBlock("Erro", paragraph(error.message)));
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    formError.hidden = true;
    if (!form.reportValidity()) return;
    const rows = [...serviceRows.querySelectorAll(".service-row")];
    if (!rows.length) {
      formError.textContent = "Adicione pelo menos um serviço ao atendimento.";
      formError.hidden = false;
      return;
    }
    const seen = new Set();
    const items = [];
    for (const row of rows) {
      const serviceId = row.querySelector(".service-select").value;
      const priceInput = row.querySelector(".price-input");
      const providerId = row.querySelector(".provider-select").value;
      const price = Number(priceInput.value);
      if (seen.has(serviceId)) {
        formError.textContent = "Não repita o mesmo serviço no atendimento.";
        formError.hidden = false;
        return;
      }
      seen.add(serviceId);
      if (!Number.isFinite(price) || price < 0) {
        formError.textContent = "Informe um valor cobrado válido e não negativo para cada serviço.";
        formError.hidden = false;
        priceInput.focus();
        return;
      }
      const item = { servico_id: Number(serviceId), valor_cobrado: priceInput.value };
      if (providerId) item.profissional_id = Number(providerId);
      items.push(item);
    }
    const localDate = new Date(form.elements.agendado_para.value);
    if (Number.isNaN(localDate.getTime())) {
      formError.textContent = "Informe uma data e hora válidas.";
      formError.hidden = false;
      return;
    }
    const payload = {
      cliente_id: Number(form.elements.cliente_id.value),
      profissional_id: Number(form.elements.profissional_id.value),
      agendado_para: localDate.toISOString(),
      observacoes: form.elements.observacoes.value.trim(),
      servicos: items,
    };
    const bookingId = form.elements.agendamento_id.value.trim();
    if (bookingId) payload.agendamento_id = Number(bookingId);

    saveButton.disabled = true;
    saveButton.textContent = "Registrando…";
    try {
      await request("/api/atendimentos", { method: "POST", body: JSON.stringify(payload) });
      dialog.close();
      announce("Atendimento registrado com sucesso.");
      await loadAppointments();
    } catch (error) {
      formError.textContent = error.message;
      formError.hidden = false;
    } finally {
      saveButton.disabled = false;
      saveButton.textContent = "Registrar atendimento";
    }
  });

  document.querySelector("#newAppointmentButton").addEventListener("click", openCreate);
  document.querySelector("#addServiceButton").addEventListener("click", () => {
    if (serviceRows.querySelectorAll(".service-row").length >= services.length) {
      announce("Todos os serviços ativos já foram adicionados.", "info");
      return;
    }
    addServiceRow();
  });
  statusFilter.addEventListener("change", loadAppointments);
  [dialog, detailsDialog].forEach((element) => {
    element.querySelectorAll("[data-close-dialog]").forEach((button) => {
      button.addEventListener("click", () => element.close());
    });
  });
  dialog.addEventListener("close", closeAndResetForm);

  async function initialize() {
    try {
      services = await request("/api/servicos");
      if (!directory.clientes.length || !directory.profissionais.length) {
        announce("A lista de clientes ou profissionais está vazia. Integre usuários existentes antes de criar atendimentos.", "info");
      }
      await loadAppointments();
    } catch (error) {
      announce(error.message, "error");
      await loadAppointments();
    }
  }

  initialize();
})();
