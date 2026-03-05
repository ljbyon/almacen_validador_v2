import streamlit as st
import pandas as pd
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dismac · Email Sender",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
  }
  .stApp {
    background: #0f1117;
    color: #e8eaf0;
  }
  .block-container { padding-top: 2rem; }

  /* Header banner */
  .header-banner {
    background: linear-gradient(135deg, #1a1f2e 0%, #0d1321 100%);
    border: 1px solid #2a3a5c;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  .header-banner h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    color: #4fc3f7;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .header-banner p { margin: 0.2rem 0 0; color: #7a8ba0; font-size: 0.9rem; }

  /* Metric cards */
  .metric-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
  .metric-card {
    flex: 1;
    background: #161b27;
    border: 1px solid #263047;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
  }
  .metric-card .val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: #4fc3f7;
  }
  .metric-card .lbl { font-size: 0.75rem; color: #7a8ba0; text-transform: uppercase; letter-spacing: 1px; }

  /* Status badges */
  .badge-ok   { background:#0d3b2e; color:#4caf90; border:1px solid #1d6b50; border-radius:6px; padding:2px 8px; font-size:0.78rem; font-family:'IBM Plex Mono',monospace; }
  .badge-err  { background:#3b0d0d; color:#e57373; border:1px solid #6b1d1d; border-radius:6px; padding:2px 8px; font-size:0.78rem; font-family:'IBM Plex Mono',monospace; }
  .badge-pend { background:#2a2a0d; color:#ffd54f; border:1px solid #5a5012; border-radius:6px; padding:2px 8px; font-size:0.78rem; font-family:'IBM Plex Mono',monospace; }

  /* Log box */
  .log-box {
    background: #0a0d14;
    border: 1px solid #1e2a3a;
    border-radius: 8px;
    padding: 1rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    color: #b0c4d8;
    max-height: 320px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.6;
  }
  .log-ok  { color: #4caf90; }
  .log-err { color: #e57373; }
  .log-inf { color: #4fc3f7; }

  /* Template box */
  .template-preview {
    background: #111827;
    border-left: 3px solid #4fc3f7;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    color: #c8d8e8;
    white-space: pre-wrap;
    line-height: 1.7;
  }

  /* Streamlit widget overrides */
  .stButton > button {
    background: #1565c0;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding: 0.6rem 1.4rem;
    transition: background 0.2s;
  }
  .stButton > button:hover { background: #1976d2; }
  div[data-testid="stFileUploader"] {
    background: #161b27;
    border: 1px dashed #2a3a5c;
    border-radius: 10px;
    padding: 0.5rem;
  }
  .stTextArea textarea, .stTextInput input {
    background: #161b27 !important;
    color: #e8eaf0 !important;
    border: 1px solid #2a3a5c !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
  }
  .stDataFrame { border-radius: 8px; overflow: hidden; }
  label { color: #7a8ba0 !important; font-size: 0.82rem !important; text-transform: uppercase; letter-spacing: 0.8px; }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
  <div>
    <h1>✉ DISMAC · Bulk Email Sender</h1>
    <p>Load an Excel file → preview rows → customize template → send</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Secrets ──────────────────────────────────────────────────────────────────
try:
    EMAIL_HOST     = st.secrets["EMAIL_HOST"]
    EMAIL_PORT     = int(st.secrets["EMAIL_PORT"])
    EMAIL_USER     = st.secrets["EMAIL_USER"]
    EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
    secrets_ok = True
except Exception:
    secrets_ok = False

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    # Secrets status
    if secrets_ok:
        st.markdown(f"<span class='badge-ok'>✓ SMTP configured</span><br><small style='color:#7a8ba0'>{EMAIL_USER}</small>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='badge-err'>✗ Secrets missing</span>", unsafe_allow_html=True)
        st.caption("Add EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD to `.streamlit/secrets.toml`")

    st.divider()
    st.markdown("### 📧 Recipients")
    recipient_col = st.text_input("Column used as To address", value="EMAIL", placeholder="e.g. EMAIL")
    cc_address    = st.text_input("CC (optional)", placeholder="cc@example.com")
    subject_tpl   = st.text_input("Subject template", value="Pedido {PEDIDO} – {NOMBRE CLIENTE}")
    delay_ms      = st.slider("Delay between emails (ms)", 0, 3000, 500, 100)

    st.divider()
    st.markdown("### 🧪 Test mode")
    test_mode      = st.toggle("Send to a test address instead", value=True)
    test_recipient = st.text_input("Test recipient email", value=EMAIL_USER if secrets_ok else "")

# ─── Default email template ───────────────────────────────────────────────────
DEFAULT_TEMPLATE = """\
Estimado/a {NOMBRE CLIENTE},

Por medio del presente correo le informamos sobre el estado de su pedido:

  • N° Pedido   : {PEDIDO}
  • Orden de Compra : {OC}
  • Regional    : {REGIONAL}

─── Detalle del Producto ───────────────────────────────
  Código      : {CÓDIGO DEL PRODUCTO}
  Descripción : {DESCRIPCIÓN}
  Cantidad    : {CANT}

─── Observación ────────────────────────────────────────
  {OBSERVACIÓN}

Quedamos a su disposición para cualquier consulta.

Saludos cordiales,
Equipo Dismac
"""

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📂  Load Data", "✏️  Email Template", "🚀  Send"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 – Load Data
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    uploaded = st.file_uploader("Drop your Excel file here (.xlsx / .xls)", type=["xlsx", "xls"])

    if uploaded:
        try:
            df = pd.read_excel(uploaded, sheet_name=0, dtype=str).fillna("")
            st.session_state["df"] = df

            required_cols = ["PEDIDO","OC","NOMBRE CLIENTE","CÓDIGO DEL PRODUCTO",
                             "DESCRIPCIÓN","CANT","OBSERVACIÓN","REGIONAL"]
            missing = [c for c in required_cols if c not in df.columns]

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Rows", len(df))
            col_b.metric("Columns", len(df.columns))
            col_c.metric("Missing cols", len(missing))

            if missing:
                st.warning(f"⚠️ Expected columns not found: `{'`, `'.join(missing)}`")
            else:
                st.success("✅ All required columns detected.")

            st.dataframe(df, use_container_width=True, height=380)

        except Exception as e:
            st.error(f"Could not read file: {e}")
    else:
        st.info("Upload an Excel file to get started.")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 – Email Template
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("Use `{COLUMN_NAME}` placeholders — they are replaced with each row's values.")
    template_body = st.text_area("Email body template", value=DEFAULT_TEMPLATE, height=380)
    st.session_state["template"] = template_body

    st.divider()
    st.markdown("**Preview** – pick a row to render:")
    df_loaded = st.session_state.get("df")
    if df_loaded is not None and len(df_loaded) > 0:
        preview_idx = st.number_input("Row index (0-based)", 0, len(df_loaded)-1, 0)
        row = df_loaded.iloc[preview_idx].to_dict()
        try:
            rendered = template_body.format(**{k: v for k, v in row.items()})
            st.markdown(f"<div class='template-preview'>{rendered}</div>", unsafe_allow_html=True)
        except KeyError as e:
            st.error(f"Unknown placeholder {e} in template.")
    else:
        st.markdown("<div class='template-preview'><i>Load a file in the first tab to preview a rendered email.</i></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 – Send
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    df_loaded  = st.session_state.get("df")
    template   = st.session_state.get("template", DEFAULT_TEMPLATE)

    if df_loaded is None:
        st.info("Load an Excel file in the first tab before sending.")
    elif not secrets_ok:
        st.error("SMTP credentials are not configured. Check `.streamlit/secrets.toml`.")
    else:
        # Summary metrics
        n_rows = len(df_loaded)
        has_email_col = recipient_col in df_loaded.columns
        filled = (df_loaded[recipient_col].str.strip() != "").sum() if has_email_col else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("Total rows", n_rows)
        m2.metric(f"Rows with '{recipient_col}'", filled if has_email_col else "—")
        m3.metric("Mode", "🧪 Test" if test_mode else "🟢 Live")

        if not has_email_col:
            st.warning(f"Column `{recipient_col}` not found in the file. Adjust it in the sidebar.")

        st.divider()

        send_btn = st.button("▶  Send emails", disabled=(not has_email_col))

        log_placeholder  = st.empty()
        prog_placeholder = st.empty()

        if send_btn:
            logs       = []
            sent_ok    = 0
            sent_fail  = 0
            rows_valid = df_loaded[df_loaded[recipient_col].str.strip() != ""]

            context = ssl.create_default_context()

            def add_log(msg, kind="inf"):
                tag = {"ok":"log-ok","err":"log-err","inf":"log-inf"}.get(kind,"")
                logs.append(f"<span class='{tag}'>{msg}</span>")
                log_html = "<div class='log-box'>" + "\n".join(logs) + "</div>"
                log_placeholder.markdown(log_html, unsafe_allow_html=True)

            add_log(f"[INFO] Connecting to {EMAIL_HOST}:{EMAIL_PORT} …")

            try:
                server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=15)
                server.ehlo()
                server.starttls(context=context)
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                add_log(f"[OK]   Authenticated as {EMAIL_USER}", "ok")

                total = len(rows_valid)
                for idx, (_, row) in enumerate(rows_valid.iterrows()):
                    to_addr = test_recipient if test_mode else row[recipient_col].strip()
                    row_dict = row.to_dict()

                    # Build subject
                    try:
                        subject = subject_tpl.format(**{k: v for k, v in row_dict.items()})
                    except KeyError:
                        subject = f"Pedido {row_dict.get('PEDIDO','')}"

                    # Build body
                    try:
                        body = template.format(**{k: v for k, v in row_dict.items()})
                    except KeyError as e:
                        add_log(f"[WARN] Row {idx}: missing placeholder {e}, skipping.", "err")
                        sent_fail += 1
                        continue

                    msg = MIMEMultipart("alternative")
                    msg["From"]    = EMAIL_USER
                    msg["To"]      = to_addr
                    msg["Subject"] = subject
                    if cc_address.strip():
                        msg["Cc"] = cc_address.strip()
                    msg.attach(MIMEText(body, "plain", "utf-8"))

                    recipients = [to_addr] + ([cc_address.strip()] if cc_address.strip() else [])

                    try:
                        server.sendmail(EMAIL_USER, recipients, msg.as_string())
                        add_log(f"[OK]   Row {idx+1}/{total}  →  {to_addr}  |  {subject[:55]}", "ok")
                        sent_ok += 1
                    except Exception as e:
                        add_log(f"[ERR]  Row {idx+1}/{total}  →  {to_addr}  |  {e}", "err")
                        sent_fail += 1

                    prog_placeholder.progress((idx + 1) / total)
                    time.sleep(delay_ms / 1000)

                server.quit()
                add_log(f"[INFO] Done. Sent: {sent_ok}  |  Failed: {sent_fail}")
                if sent_fail == 0:
                    st.success(f"✅ All {sent_ok} emails sent successfully!")
                else:
                    st.warning(f"Sent {sent_ok}, failed {sent_fail}. See log above.")

            except smtplib.SMTPAuthenticationError:
                add_log("[ERR]  SMTP authentication failed. Check credentials.", "err")
                st.error("Authentication error.")
            except Exception as e:
                add_log(f"[ERR]  Connection error: {e}", "err")
                st.error(f"Could not connect: {e}")