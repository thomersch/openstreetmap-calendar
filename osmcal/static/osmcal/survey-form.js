class SurveyForm extends HTMLElement {
  connectedCallback() {
    this._questions = window.appData && window.appData.questions ? window.appData.questions : [];
    this._initialCount = this._questions.length;
    this.render();
  }

  _addQuestion() {
    this._syncFromDOM();
    this._questions.push({ type: "TEXT", choices: [{}], text: "", mandatory: false });
    this.render();
  }

  _deleteQuestion(qi) {
    this._syncFromDOM();
    this._questions.splice(qi, 1);
    this.render();
  }

  _addChoice(qi) {
    this._syncFromDOM();
    this._questions[qi].choices.push({ text: "" });
    this.render();
  }

  _choiceLines(q) {
    return (q.choices || []).map((c) => c.text || "").join("\n");
  }

  _syncFromDOM() {
    this.querySelectorAll("[data-q-field]").forEach((el) => {
      const qi = parseInt(el.dataset.q);
      if (isNaN(qi) || !this._questions[qi]) return;
      const field = el.dataset.qField;
      if (field === "text") this._questions[qi].text = el.value;
      else if (field === "mandatory") this._questions[qi].mandatory = el.checked;
      else if (field === "type") this._questions[qi].type = el.value;
    });
    this.querySelectorAll("[data-ci]").forEach((el) => {
      const qi = parseInt(el.dataset.q);
      const ci = parseInt(el.dataset.ci);
      if (this._questions[qi]?.choices?.[ci] !== undefined) {
        this._questions[qi].choices[ci].text = el.value;
      }
    });
  }

  _esc(str) {
    return String(str).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  render() {
    const q = this._questions;
    let html = '<div class="event-question-input-column">';

    if (q.length === 0) {
      html += `
                <div>
                    <button class="btn" data-action="add-question" formnovalidate>Create Sign Up Survey</button>
                    <label class="event-question-form-helptext">You can ask the participants questions they will be asked to answer during event sign up, e.g. whether they'll join the after work party.</label>
                </div>`;
    }

    q.forEach((question, index) => {
      html += `
                <div class="event-question-form-block">
                    <h3>Question ${index + 1}${!question.frozen ? ` <button data-action="delete-question" data-q="${index}" class="btn-mini btn-negative" formnovalidate style="float:right">Delete Question</button>` : ""}</h3>
                    ${question.frozen ? '<div class="event-question-form-helptext" style="margin-bottom:1em;">Existing Questions cannot be changed.</div>' : ""}
                    <div class="event-question-line">
                        <label for="id_questions-${index}-question_text" class="event-question-label">Question Text</label>
                        <input name="questions-${index}-question_text" id="id_questions-${index}-question_text"
                            value="${this._esc(question.text || "")}"
                            placeholder="E.g. your full name"
                            ${question.frozen ? "disabled" : ""}
                            class="event-question-input" required
                            data-q="${index}" data-q-field="text">
                    </div>
                    <div class="event-question-line">
                        <label for="id_questions-${index}-mandatory" class="event-question-label">Required Answer</label>
                        <input name="questions-${index}-mandatory" id="id_questions-${index}-mandatory"
                            type="checkbox"
                            ${question.mandatory ? "checked" : ""}
                            ${question.frozen ? "disabled" : ""}
                            data-q="${index}" data-q-field="mandatory">
                    </div>
                    <div class="event-question-line">
                        <label for="id_questions-${index}-answer_type" class="event-question-label">Answer Type</label>
                        <select name="questions-${index}-answer_type" id="id_questions-${index}-answer_type"
                            ${question.frozen ? "disabled" : ""}
                            class="event-question-input"
                            data-q="${index}" data-q-field="type">
                            <option value="TEXT"${question.type === "TEXT" ? " selected" : ""}>Text</option>
                            <option value="CHOI"${question.type === "CHOI" ? " selected" : ""}>Choice</option>
                            <option value="BOOL"${question.type === "BOOL" ? " selected" : ""}>Boolean (yes or no)</option>
                        </select>
                    </div>`;

      if (question.type === "CHOI") {
        html += `
                    <div class="event-question-line">
                        <label class="event-question-label">Choices</label>
                        <ul class="event-question-choices">`;
        (question.choices || []).forEach((choice, ci) => {
          html += `<li><input value="${this._esc(choice.text || "")}"
                        ${question.frozen ? "disabled" : ""}
                        class="event-question-input"
                        data-q="${index}" data-ci="${ci}"></li>`;
        });
        html += "</ul>";
        if (!question.frozen) {
          html += `<button data-action="add-choice" data-q="${index}" class="btn-mini event-question-choice-button" formnovalidate>Add Choice</button>`;
        }
        html += `<textarea name="questions-${index}-choices" hidden>${this._esc(this._choiceLines(question))}</textarea>
                    </div>`;
      }

      html += "</div>"; // end event-question-form-block
    });

    if (q.length > 0) {
      html += `
                <div class="event-question-form-block">
                    <button class="btn" data-action="add-question" formnovalidate>Add Question to Survey</button>
                </div>`;
    }

    html += "</div>";
    html += `
            <input type="hidden" name="questions-TOTAL_FORMS" value="${q.length}">
            <input type="hidden" name="questions-INITIAL_FORMS" value="${this._initialCount}">
            <input type="hidden" name="questions-MIN_NUM_FORMS" value="0">
            <input type="hidden" name="questions-MAX_NUM_FORMS" value="1000">`;

    this.innerHTML = html;
    this._bindEvents();
  }

  _bindEvents() {
    this.querySelectorAll('[data-action="add-question"]').forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        this._addQuestion();
      });
    });

    this.querySelectorAll('[data-action="delete-question"]').forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        this._deleteQuestion(parseInt(btn.dataset.q));
      });
    });

    this.querySelectorAll('[data-action="add-choice"]').forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        this._addChoice(parseInt(btn.dataset.q));
      });
    });

    // Update choice textarea live without re-rendering
    this.querySelectorAll("[data-ci]").forEach((input) => {
      input.addEventListener("input", () => {
        const qi = parseInt(input.dataset.q);
        const ci = parseInt(input.dataset.ci);
        if (this._questions[qi]?.choices?.[ci] !== undefined) {
          this._questions[qi].choices[ci].text = input.value;
          const ta = this.querySelector(`textarea[name="questions-${qi}-choices"]`);
          if (ta) ta.value = this._choiceLines(this._questions[qi]);
        }
      });
    });

    // Re-render on answer type change to show/hide choices section
    this.querySelectorAll('[data-q-field="type"]').forEach((select) => {
      select.addEventListener("change", (e) => {
        const qi = parseInt(select.dataset.q);
        this._questions[qi].type = e.target.value;
        this.render();
      });
    });
  }
}

customElements.define("survey-form", SurveyForm);
