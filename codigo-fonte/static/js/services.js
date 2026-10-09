(() => {
  const page = document.querySelector("#servicesPage");
  if (!page) return;

  const body = document.querySelector("#servicesTableBody");
  const notice = document.querySelector("#servicesNotice");
  const dialog = document.querySelector("#serviceDialog");
  const form = document.querySelector("#serviceForm");
  const formError = document.querySelector("#serviceFormError");
  const saveButton = document.querySelector("#saveServiceButton");
  const activeField = document.querySelector("#serviceActiveField");
  let editingId = null;
  let noticeTimer;

  const money = (value) => new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(Number(value));

  function announce(message, type = "success") {
    window.clearTimeout(noticeTimer);
    notice.textContent = message;
    notice.className = `notice ${type}`;
    notice.hidden = false;
    noticeTimer = window.setTimeout(() => { notice.hidden = true; }, 6000);
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

  function makeCell(content, className) {
    const cell = document.createElement("td");
    if (className) cell.className = className;
    if (content instanceof Node) cell.append(content);
    else cell.textContent = content;
    return cell;
  }

  function renderMessage(message) {
    const cell = document.createElement("td");
    cell.colSpan = 5;
    cell.className = "table-message";
    cell.textContent = message;
    const row = document.createElement("tr");
    row.append(cell);
    body.replaceChildren(row);
  }

  function renderService(service) {
    const row = document.createElement("tr");
    const name = document.createElement("span");
    name.className = "service-name";
    name.textContent = service.nome;
    const description = document.createElement("small");
    description.className = "service-description";
    description.textContent = service.descricao || "Sem descrição";
    const info = document.createElement("div");
    info.append(name, description);
    row.append(makeCell(info), makeCell(money(service.preco)), makeCell(`${service.duracao_minutos} min`));

    const badge = document.createElement("span");
    badge.className = `status-badge ${service.ativo ? "status-active" : "status-inactive"}`;
    badge.textContent = service.ativo ? "Ativo" : "Inativo";
    row.append(makeCell(badge));

    const actions = document.createElement("div");
    actions.className = "row-actions";
    const edit = document.createElement("button");
    edit.type = "button";
    edit.className = "small-button";
    edit.textContent = "Editar";
    edit.addEventListener("click", () => openEdit(service.id));
    actions.append(edit);
    if (service.ativo) {
      const deactivate = document.createElement("button");
      deactivate.type = "button";
      deactivate.className = "small-button danger";
      deactivate.textContent = "Desativar";
      deactivate.addEventListener("click", () => deactivateService(service));
      actions.append(deactivate);
    }
    row.append(makeCell(actions, "actions-heading"));
    body.append(row);
  }

  async function loadServices() {
    renderMessage("Carregando serviços…");
    try {
      const services = await request("/api/servicos?incluir_inativos=true");
      body.replaceChildren();
      if (!services.length) {
        renderMessage("Nenhum serviço cadastrado. Selecione “Novo serviço” para cadastrar o primeiro.");
        return;
      }
      services.forEach(renderService);
    } catch (error) {
      renderMessage(error.message);
    }
  }

  function resetForm() {
    form.reset();
    editingId = null;
    formError.hidden = true;
    formError.textContent = "";
    activeField.hidden = true;
    document.querySelector("#serviceDialogTitle").textContent = "Novo serviço";
    saveButton.textContent = "Salvar serviço";
  }

  function openCreate() {
    resetForm();
    dialog.showModal();
    form.elements.nome.focus();
  }

  async function openEdit(id) {
    resetForm();
    saveButton.disabled = true;
    saveButton.textContent = "Carregando…";
    dialog.showModal();
    try {
      const service = await request(`/api/servicos/${id}`);
      editingId = service.id;
      form.elements.nome.value = service.nome;
      form.elements.descricao.value = service.descricao;
      form.elements.preco.value = service.preco;
      form.elements.duracao_minutos.value = service.duracao_minutos;
      form.elements.ativo.checked = service.ativo;
      activeField.hidden = false;
      document.querySelector("#serviceDialogTitle").textContent = "Editar serviço";
      saveButton.textContent = "Salvar alterações";
      form.elements.nome.focus();
    } catch (error) {
      dialog.close();
      announce(error.message, "error");
    } finally {
      saveButton.disabled = false;
    }
  }

  async function deactivateService(service) {
    if (!window.confirm(`Deseja desativar “${service.nome}”? O serviço deixará de aparecer como opção para novos atendimentos.`)) return;
    try {
      await request(`/api/servicos/${service.id}`, { method: "DELETE" });
      announce("Serviço desativado.");
      await loadServices();
    } catch (error) {
      announce(error.message, "error");
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    formError.hidden = true;
    if (!form.reportValidity()) return;
    const price = Number(form.elements.preco.value);
    const duration = Number(form.elements.duracao_minutos.value);
    if (!Number.isFinite(price) || price < 0) {
      formError.textContent = "Informe um preço válido, igual ou superior a zero.";
      formError.hidden = false;
      return;
    }
    if (!Number.isInteger(duration) || duration <= 0) {
      formError.textContent = "A duração deve ser um número inteiro positivo de minutos.";
      formError.hidden = false;
      return;
    }
    const payload = {
      nome: form.elements.nome.value.trim(),
      descricao: form.elements.descricao.value.trim(),
      preco: form.elements.preco.value,
      duracao_minutos: duration,
    };
    if (editingId !== null) payload.ativo = form.elements.ativo.checked;

    saveButton.disabled = true;
    saveButton.textContent = "Salvando…";
    try {
      await request(editingId === null ? "/api/servicos" : `/api/servicos/${editingId}`, {
        method: editingId === null ? "POST" : "PUT",
        body: JSON.stringify(payload),
      });
      dialog.close();
      announce(editingId === null ? "Serviço cadastrado com sucesso." : "Serviço atualizado com sucesso.");
      await loadServices();
    } catch (error) {
      formError.textContent = error.message;
      formError.hidden = false;
    } finally {
      saveButton.disabled = false;
      saveButton.textContent = editingId === null ? "Salvar serviço" : "Salvar alterações";
    }
  });

  document.querySelector("#newServiceButton").addEventListener("click", openCreate);
  dialog.querySelectorAll("[data-close-dialog]").forEach((button) => {
    button.addEventListener("click", () => dialog.close());
  });
  dialog.addEventListener("close", resetForm);
  loadServices();
})();
