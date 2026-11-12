(() => {
  const page = document.querySelector("#agendaPage");
  if (!page) return;

  const eventsContainer = document.querySelector("#agendaEvents");
  const dateInput = document.querySelector("#agendaDate");
  const rangeLabel = document.querySelector("#agendaRangeLabel");
  const notice = document.querySelector("#agendaNotice");
  const scheduleForm = document.querySelector("#scheduleForm");
  const blockForm = document.querySelector("#blockForm");
  const scheduleRows = document.querySelector("#scheduleRows");
  const blockRows = document.querySelector("#blockRows");
  const scheduleProfessional = document.querySelector("#scheduleProfessional");
  const blockProfessional = document.querySelector("#blockProfessional");
  const agendaProfessionalFilter = document.querySelector("#agendaProfessionalFilter");
  const professionals = JSON.parse(document.querySelector("#professionalDirectory").textContent);
  let view = "semanal";
  let schedules = [];
  let blocks = [];
  let noticeTimer;

  function localDateString(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  function parseLocalDate(value) {
    const [year, month, day] = value.split("-").map(Number);
    return new Date(year, month - 1, day);
  }

  function setLocalDateTime(input, value) {
    const date = new Date(value);
    const offset = date.getTimezoneOffset() * 60000;
    input.value = new Date(date.getTime() - offset).toISOString().slice(0, 16);
  }

  function formatDateTime(value) {
    return new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(new Date(value));
  }

  function formatTime(value) {
    return new Intl.DateTimeFormat("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(value));
  }

  function localIso(value) {
    return new Date(value).toISOString();
  }

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

  function showTableMessage(container, message, columns) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = columns;
    cell.className = "table-message";
    cell.textContent = message;
    row.append(cell);
    container.replaceChildren(row);
  }

  function renderAgenda(payload) {
    const start = parseLocalDate(payload.inicio);
    const days = view === "diaria" ? 1 : 7;
    const end = new Date(start);
    end.setDate(end.getDate() + days - 1);
    rangeLabel.textContent = days === 1
      ? new Intl.DateTimeFormat("pt-BR", { dateStyle: "full" }).format(start)
      : `${new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium" }).format(start)} – ${new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium" }).format(end)}`;

    const groups = [];
    for (let offset = 0; offset < days; offset += 1) {
      const day = new Date(start);
      day.setDate(day.getDate() + offset);
      groups.push({
        date: localDateString(day),
        weekday: (day.getDay() + 6) % 7,
        day,
      });
    }
    const sections = groups.map(({ date, weekday, day }) => {
      const section = document.createElement("section");
      section.className = "agenda-day";
      const heading = document.createElement("h3");
      heading.textContent = new Intl.DateTimeFormat("pt-BR", {
        weekday: "long",
        day: "numeric",
        month: "long",
      }).format(day);
      section.append(heading);

      const dayStart = new Date(day.getFullYear(), day.getMonth(), day.getDate());
      const dayEnd = new Date(day.getFullYear(), day.getMonth(), day.getDate() + 1);
      const dayEvents = payload.eventos.filter((event) => (
        new Date(event.inicio) < dayEnd && new Date(event.fim) > dayStart
      ));

      payload.profissionais.forEach((professional) => {
        const card = document.createElement("article");
        card.className = "professional-agenda-card";
        const professionalHeading = document.createElement("h4");
        professionalHeading.textContent = professional.nome;
        card.append(professionalHeading);

        const professionalSchedules = payload.horarios.filter((item) => (
          item.profissional_id === professional.id && item.dia_semana === weekday
        )).sort((first, second) => first.inicio.localeCompare(second.inicio));
        const shifts = document.createElement("p");
        shifts.className = "agenda-shifts";
        shifts.textContent = professionalSchedules.length
          ? `Escala: ${professionalSchedules.map((item) => `${item.inicio}–${item.fim}`).join(" · ")}`
          : "Sem horário de funcionamento cadastrado.";
        card.append(shifts);

        professionalSchedules.slice(1).forEach((schedule, index) => {
          const previousSchedule = professionalSchedules[index];
          if (previousSchedule.fim >= schedule.inicio) return;
          const lunchBreak = document.createElement("p");
          lunchBreak.className = "agenda-lunch-break";
          const label = document.createElement("strong");
          label.textContent = "Almoço / intervalo";
          const period = document.createElement("span");
          period.textContent = `${previousSchedule.fim}–${schedule.inicio}`;
          lunchBreak.append(label, period);
          card.append(lunchBreak);
        });

        const professionalEvents = dayEvents.filter((event) => (
          event.profissional_id === professional.id
        ));
        const availablePeriods = payload.disponibilidades.filter((period) => (
          period.data === date && period.profissional_id === professional.id
        ));
        if (professionalSchedules.length) {
          const availability = document.createElement("p");
          availability.className = "agenda-availability";
          availability.textContent = availablePeriods.length
            ? `Períodos livres: ${availablePeriods.map((period) => `${period.inicio}–${period.fim}`).join(" · ")}`
            : "Sem períodos livres nesta escala.";
          card.append(availability);
        }
        if (!professionalEvents.length) {
          const empty = document.createElement("p");
          empty.className = "agenda-empty";
          empty.textContent = professionalSchedules.length
            ? "Nenhum atendimento ou bloqueio."
            : "Nenhum atendimento, bloqueio ou escala.";
          card.append(empty);
        }
        professionalEvents.forEach((event) => {
          const item = document.createElement("div");
          item.className = `agenda-event ${event.tipo === "bloqueio" ? "blocked" : "booked"}`;
          const time = document.createElement("strong");
          time.textContent = `${formatTime(event.inicio)} – ${formatTime(event.fim)}`;
          const detail = document.createElement("div");
          const title = document.createElement("b");
          title.textContent = event.tipo === "bloqueio"
            ? event.motivo
            : `${event.cliente_nome || "Cliente"}${event.servicos.length ? ` · ${event.servicos.join(", ")}` : ""}`;
          detail.append(title);
          item.append(time, detail);
          card.append(item);
        });
        section.append(card);
      });
      return section;
    });
    eventsContainer.classList.toggle("is-daily", view === "diaria");
    eventsContainer.replaceChildren(...sections);
  }

  async function loadAgenda() {
    eventsContainer.replaceChildren();
    const selectedDate = dateInput.value || localDateString(new Date());
    const filter = agendaProfessionalFilter?.value;
    const query = new URLSearchParams();
    query.set(view === "diaria" ? "data" : "semana", selectedDate);
    if (filter) query.set("profissional_id", filter);
    try {
      const payload = await request(`/api/agenda/${view}?${query.toString()}`);
      renderAgenda(payload);
    } catch (error) {
      showTableMessage(eventsContainer, error.message, 1);
    }
  }

  function renderSchedules() {
    scheduleRows.replaceChildren();
    if (!schedules.length) {
      showTableMessage(scheduleRows, "Nenhum horário cadastrado para esta profissional.", 3);
      return;
    }
    schedules.forEach((schedule) => {
      const row = document.createElement("tr");
      const day = document.createElement("td");
      day.textContent = schedule.dia_semana_nome;
      const interval = document.createElement("td");
      interval.textContent = `${schedule.inicio} – ${schedule.fim}`;
      const actions = document.createElement("td");
      actions.className = "actions-heading";
      const edit = document.createElement("button");
      edit.type = "button";
      edit.className = "small-button";
      edit.textContent = "Editar";
      edit.addEventListener("click", () => {
        scheduleForm.elements.id.value = schedule.id;
        scheduleForm.querySelectorAll('[name="dias_semana"]').forEach((checkbox) => {
          checkbox.checked = Number(checkbox.value) === schedule.dia_semana;
          checkbox.disabled = Number(checkbox.value) !== schedule.dia_semana;
        });
        document.querySelector("#weekdaysMondayToSaturday").disabled = true;
        scheduleForm.elements.inicio.value = schedule.inicio;
        scheduleForm.elements.fim.value = schedule.fim;
        scheduleForm.querySelector('[type="submit"]').textContent = "Atualizar horário";
        document.querySelector("#cancelScheduleEdit").hidden = false;
        scheduleForm.scrollIntoView({ behavior: "smooth", block: "center" });
      });
      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "small-button danger";
      remove.textContent = "Excluir";
      remove.addEventListener("click", async () => {
        if (!window.confirm("Excluir este período de funcionamento?")) return;
        try {
          await request(`/api/horarios/${schedule.id}`, { method: "DELETE" });
          announce("Horário removido.");
          await loadManagementData();
          await loadAgenda();
        } catch (error) {
          announce(error.message, "error");
        }
      });
      actions.append(edit, remove);
      row.append(day, interval, actions);
      scheduleRows.append(row);
    });
  }

  function renderBlocks() {
    blockRows.replaceChildren();
    if (!blocks.length) {
      showTableMessage(blockRows, "Nenhum bloqueio cadastrado.", 3);
      return;
    }
    blocks.forEach((block) => {
      const row = document.createElement("tr");
      const period = document.createElement("td");
      period.textContent = `${formatDateTime(block.inicio)} – ${formatDateTime(block.fim)}`;
      const reason = document.createElement("td");
      reason.textContent = block.motivo;
      const actions = document.createElement("td");
      actions.className = "actions-heading";
      const edit = document.createElement("button");
      edit.type = "button";
      edit.className = "small-button";
      edit.textContent = "Editar";
      edit.addEventListener("click", () => {
        blockForm.elements.id.value = block.id;
        blockForm.elements.motivo.value = block.motivo;
        setLocalDateTime(blockForm.elements.inicio, block.inicio);
        setLocalDateTime(blockForm.elements.fim, block.fim);
        blockForm.querySelector('[type="submit"]').textContent = "Atualizar bloqueio";
        document.querySelector("#cancelBlockEdit").hidden = false;
        blockForm.scrollIntoView({ behavior: "smooth", block: "center" });
      });
      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "small-button danger";
      remove.textContent = "Excluir";
      remove.addEventListener("click", async () => {
        if (!window.confirm("Excluir este bloqueio?")) return;
        try {
          await request(`/api/bloqueios/${block.id}`, { method: "DELETE" });
          announce("Bloqueio removido.");
          await loadManagementData();
          await loadAgenda();
        } catch (error) {
          announce(error.message, "error");
        }
      });
      actions.append(edit, remove);
      row.append(period, reason, actions);
      blockRows.append(row);
    });
  }

  async function loadManagementData() {
    const scheduleId = scheduleProfessional.value;
    const blockId = blockProfessional.value;
    if (!scheduleId) {
      schedules = [];
      renderSchedules();
    } else {
      schedules = await request(`/api/horarios?profissional_id=${encodeURIComponent(scheduleId)}`);
      renderSchedules();
    }
    if (!blockId) {
      blocks = [];
      renderBlocks();
    } else {
      blocks = await request(`/api/bloqueios?profissional_id=${encodeURIComponent(blockId)}`);
      renderBlocks();
    }
  }

  document.querySelectorAll("[data-view]").forEach((button) => {
    button.addEventListener("click", () => {
      view = button.dataset.view;
      document.querySelectorAll("[data-view]").forEach((item) => item.classList.toggle("active", item === button));
      loadAgenda();
    });
  });
  dateInput.value = localDateString(new Date());
  dateInput.addEventListener("change", loadAgenda);
  agendaProfessionalFilter?.addEventListener("change", loadAgenda);
  document.querySelector("#previousPeriod").addEventListener("click", () => {
    const date = parseLocalDate(dateInput.value);
    date.setDate(date.getDate() + (view === "diaria" ? -1 : -7));
    dateInput.value = localDateString(date);
    loadAgenda();
  });
  document.querySelector("#nextPeriod").addEventListener("click", () => {
    const date = parseLocalDate(dateInput.value);
    date.setDate(date.getDate() + (view === "diaria" ? 1 : 7));
    dateInput.value = localDateString(date);
    loadAgenda();
  });
  document.querySelector("#todayButton").addEventListener("click", () => {
    dateInput.value = localDateString(new Date());
    loadAgenda();
  });
  scheduleProfessional.addEventListener("change", () => {
    loadManagementData().catch((error) => announce(error.message, "error"));
  });
  blockProfessional.addEventListener("change", () => {
    loadManagementData().catch((error) => announce(error.message, "error"));
  });

  document.querySelector("#weekdaysMondayToSaturday").addEventListener("click", () => {
    scheduleForm.querySelectorAll('[name="dias_semana"]').forEach((checkbox) => {
      if (!checkbox.disabled) checkbox.checked = Number(checkbox.value) <= 5;
    });
  });

  scheduleForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(scheduleForm);
    const id = formData.get("id");
    const weekdays = formData.getAll("dias_semana").map(Number);
    if (!weekdays.length) {
      announce("Selecione ao menos um dia da semana.", "error");
      return;
    }
    const payload = {
      profissional_id: Number(scheduleProfessional.value),
      dias_semana: weekdays,
      inicio: formData.get("inicio"),
      fim: formData.get("fim"),
    };
    try {
      if (id) {
        await request(`/api/horarios/${id}`, {
          method: "PUT",
          body: JSON.stringify({ ...payload, dia_semana: weekdays[0] }),
        });
      } else {
        await request("/api/horarios/lote", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }
      scheduleForm.reset();
      scheduleForm.elements.id.value = "";
      scheduleForm.querySelectorAll('[name="dias_semana"]').forEach((checkbox) => {
        checkbox.disabled = false;
      });
      document.querySelector("#weekdaysMondayToSaturday").disabled = false;
      scheduleForm.querySelector('[type="submit"]').textContent = "Salvar horários";
      document.querySelector("#cancelScheduleEdit").hidden = true;
      announce(id ? "Horário atualizado." : "Horários cadastrados.");
      await loadManagementData();
      await loadAgenda();
    } catch (error) {
      announce(error.message, "error");
    }
  });
  document.querySelector("#cancelScheduleEdit").addEventListener("click", () => {
    scheduleForm.reset();
    scheduleForm.elements.id.value = "";
    scheduleForm.querySelectorAll('[name="dias_semana"]').forEach((checkbox) => {
      checkbox.disabled = false;
    });
    document.querySelector("#weekdaysMondayToSaturday").disabled = false;
    scheduleForm.querySelector('[type="submit"]').textContent = "Salvar horários";
    document.querySelector("#cancelScheduleEdit").hidden = true;
  });

  blockForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(blockForm);
    const id = formData.get("id");
    const payload = {
      profissional_id: Number(blockProfessional.value),
      motivo: formData.get("motivo"),
      inicio: localIso(formData.get("inicio")),
      fim: localIso(formData.get("fim")),
    };
    try {
      await request(id ? `/api/bloqueios/${id}` : "/api/bloqueios", {
        method: id ? "PUT" : "POST",
        body: JSON.stringify(payload),
      });
      blockForm.reset();
      blockForm.elements.id.value = "";
      blockForm.querySelector('[type="submit"]').textContent = "Salvar bloqueio";
      document.querySelector("#cancelBlockEdit").hidden = true;
      await loadManagementData();
      await loadAgenda();
      announce(id ? "Bloqueio atualizado." : "Bloqueio cadastrado.");
    } catch (error) {
      announce(error.message, "error");
    }
  });
  document.querySelector("#cancelBlockEdit").addEventListener("click", () => {
    blockForm.reset();
    blockForm.elements.id.value = "";
    blockForm.querySelector('[type="submit"]').textContent = "Salvar bloqueio";
    document.querySelector("#cancelBlockEdit").hidden = true;
  });

  loadAgenda();
  loadManagementData().catch((error) => announce(error.message, "error"));
})();
