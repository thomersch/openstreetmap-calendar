class TimezoneWidget extends HTMLElement {
  connectedCallback() {
    this._tz = this.getAttribute("tz") || null;
    this._manuallySet = this._tz !== null;
    this._render();

    document.addEventListener("osmcal:location-change", (e) => {
      if (!this._manuallySet) {
        const [lon, lat] = e.detail.coordinates;
        fetch(`/api/internal/timezone?lat=${lat}&lon=${lon}`)
          .then((r) => (r.ok ? r.text() : null))
          .then((tz) => {
            if (tz) {
              this._tz = tz.trim();
              this._render();
            }
          });
      }
    });
  }

  _render() {
    const select = this.querySelector("select");

    // Remove any existing auto-message
    const existingMsg = this.querySelector("[data-tz-auto-msg]");
    if (existingMsg) existingMsg.remove();

    if (this._tz !== null || this._manuallySet) {
      if (select) {
        select.removeAttribute("hidden");
        if (this._tz) {
          for (const opt of select.options) {
            if (opt.value === this._tz || opt.text === this._tz) {
              opt.selected = true;
              break;
            }
          }
        }
      }
    } else {
      if (select) select.setAttribute("hidden", "");
      const msg = document.createElement("span");
      msg.dataset.tzAutoMsg = "";
      msg.innerHTML =
        'Will be automatically set, if location is set. <a href="#">Set manually</a> for events without physical location.';
      msg.querySelector("a").addEventListener("click", (e) => {
        e.preventDefault();
        this._manuallySet = true;
        this._render();
      });
      this.prepend(msg);
    }
  }
}

customElements.define("timezone-widget", TimezoneWidget);
