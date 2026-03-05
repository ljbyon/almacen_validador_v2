import streamlit as st
import pandas as pd
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# ─── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Dismac · Envío de Correos",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Sans:wght@400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* Hide sidebar */
  [data-testid="stSidebar"]      { display: none !important; }
  [data-testid="collapsedControl"]{ display: none !important; }

  /* App background */
  .stApp { background: #f7f8fc; color: #1e2230; }
  .block-container { padding-top: 2.2rem; max-width: 1080px; }

  /* Header */
  .header-banner {
    background: #ffffff;
    border: 1px solid #e2e6f0;
    border-radius: 14px;
    padding: 1.4rem 2rem;
    margin-bottom: 1.8rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 1px 4px rgba(30,34,60,0.06);
  }
  .header-icon {
    background: #eef2ff;
    border-radius: 10px;
    width: 48px; height: 48px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; flex-shrink: 0;
  }
  .header-banner h1 {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.35rem;
    font-weight: 600;
    color: #1e2230;
    margin: 0;
  }
  .header-banner p { margin: 0.15rem 0 0; color: #7b829a; font-size: 0.88rem; }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background: transparent;
    gap: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    background: #ffffff;
    border: 1px solid #e2e6f0;
    border-radius: 8px;
    color: #4b5270;
    font-size: 0.88rem;
    font-weight: 500;
    padding: 0.4rem 1rem;
  }
  .stTabs [aria-selected="true"] {
    background: #4f63d2 !important;
    border-color: #4f63d2 !important;
    color: #ffffff !important;
  }
  .stTabs [data-baseweb="tab-border"] { display: none; }

  /* Metric cards */
  [data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e6f0;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    box-shadow: 0 1px 3px rgba(30,34,60,0.05);
  }
  [data-testid="stMetricLabel"] { color: #7b829a !important; font-size: 0.78rem !important; text-transform: uppercase; letter-spacing: 0.6px; }
  [data-testid="stMetricValue"] { color: #1e2230 !important; font-size: 1.6rem !important; font-weight: 600 !important; }

  /* Log box */
  .log-box {
    background: #ffffff;
    border: 1px solid #e2e6f0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-family: 'DM Mono', 'Courier New', monospace;
    font-size: 0.81rem;
    color: #3a4060;
    max-height: 340px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.75;
    box-shadow: 0 1px 3px rgba(30,34,60,0.04);
  }
  .log-ok  { color: #1a7a4a; font-weight: 500; }
  .log-err { color: #c0392b; font-weight: 500; }
  .log-inf { color: #2d5fa6; }

  /* Email preview frame */
  .email-preview-wrap {
    background: #ffffff;
    border: 1px solid #e2e6f0;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(30,34,60,0.06);
  }
  .email-preview-header {
    background: #f0f3fc;
    border-bottom: 1px solid #e2e6f0;
    padding: 0.6rem 1rem;
    font-size: 0.78rem;
    color: #7b829a;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.6px;
  }

  /* Buttons */
  .stButton > button {
    background: #4f63d2;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 0.55rem 1.6rem;
    transition: background 0.18s;
  }
  .stButton > button:hover   { background: #3d51be; }
  .stButton > button:disabled { background: #d0d4e8 !important; color: #9098b8 !important; }

  /* File uploader */
  div[data-testid="stFileUploader"] {
    background: #ffffff;
    border: 2px dashed #c8ceec;
    border-radius: 10px;
    padding: 0.5rem;
  }

  /* Text inputs */
  .stTextArea textarea, .stTextInput input {
    background: #ffffff !important;
    color: #1e2230 !important;
    border: 1px solid #d4d9ef !important;
    border-radius: 8px !important;
    font-size: 0.88rem !important;
  }
  .stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #4f63d2 !important;
    box-shadow: 0 0 0 3px rgba(79,99,210,0.12) !important;
  }

  /* Labels */
  label { color: #4b5270 !important; font-size: 0.82rem !important; font-weight: 500 !important; }

  /* Dataframe */
  .stDataFrame { border-radius: 10px; overflow: hidden; border: 1px solid #e2e6f0; }

  /* Divider */
  hr { border-color: #e8ebf5 !important; }

  /* Info / warning / success boxes */
  .stAlert { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ─── Encabezado ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
  <div class="header-icon">✉️</div>
  <div>
    <h1>DISMAC · Envío Masivo de Correos</h1>
    <p>Cargue un archivo Excel → previsualice → personalice la plantilla → envíe</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Credenciales SMTP ────────────────────────────────────────────────────────
try:
    EMAIL_HOST     = st.secrets["EMAIL_HOST"]
    EMAIL_PORT     = int(st.secrets["EMAIL_PORT"])
    EMAIL_USER     = st.secrets["EMAIL_USER"]
    EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
    secrets_ok = True
except Exception:
    secrets_ok = False
    st.error("Credenciales SMTP no configuradas. Verifique el archivo `.streamlit/secrets.toml`.")

# ─── Plantilla HTML por defecto ───────────────────────────────────────────────
DEFAULT_TEMPLATE_HTML = """\
<div style="font-family: Arial, sans-serif; font-size: 14px; color: #1e2230; line-height: 1.7; max-width: 600px;">

  <p style="margin: 0 0 16px;">Estimados,<br>
  <strong>Pedido MARKETPLACE</strong></p>

  <p style="margin: 0 0 4px; font-weight: 700; color: #2d3a8c; border-bottom: 1px solid #dde2f5; padding-bottom: 4px;">
    Datos del Cliente
  </p>
  <ul style="margin: 8px 0 16px; padding-left: 20px;">
    <li><strong>Nombre:</strong> {NOMBRE CLIENTE}</li>
  </ul>

  <p style="margin: 0 0 4px; font-weight: 700; color: #2d3a8c; border-bottom: 1px solid #dde2f5; padding-bottom: 4px;">
    Detalle del Pedido
  </p>
  <ul style="margin: 8px 0 16px; padding-left: 20px;">
    <li><strong>N° Orden de Compra:</strong> {OC}</li>
    <li><strong>Proveedor:</strong> {PEDIDO}</li>
    <li><strong>Regional:</strong> {REGIONAL}</li>
  </ul>

  <p style="margin: 0 0 4px; font-weight: 700; color: #2d3a8c; border-bottom: 1px solid #dde2f5; padding-bottom: 4px;">
    Detalle del Producto
  </p>
  <ul style="margin: 8px 0 16px; padding-left: 20px;">
    <li><strong>Código:</strong> {CÓDIGO DEL PRODUCTO}</li>
    <li><strong>Descripción:</strong> {DESCRIPCIÓN}</li>
    <li><strong>Cantidad:</strong> {CANT}</li>
  </ul>

  <p style="margin: 0 0 4px; font-weight: 700; color: #2d3a8c; border-bottom: 1px solid #dde2f5; padding-bottom: 4px;">
    Observación
  </p>
  <p style="margin: 8px 0 0; padding-left: 4px;">{OBSERVACIÓN}</p>

</div>"""

REQUIRED_COLS = [
    "PEDIDO", "OC", "NOMBRE CLIENTE", "CÓDIGO DEL PRODUCTO",
    "DESCRIPCIÓN", "CANT", "OBSERVACIÓN", "REGIONAL", "EMAIL", "CC"
]

DEFAULT_SUBJECT = "Pedido Marketplace – {OC}"

# ─── Pestañas ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📂  Cargar Archivo", "✏️  Plantilla de Correo", "🚀  Enviar"])

# ══════════════════════════════════════════════════════════════════════════════
# PESTAÑA 1 – Cargar archivo
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    uploaded = st.file_uploader(
        "Arrastre su archivo Excel aquí (.xlsx / .xls)",
        type=["xlsx", "xls"]
    )

    if uploaded:
        try:
            df = pd.read_excel(uploaded, sheet_name=0, dtype=str).fillna("")
            st.session_state["df"] = df

            missing = [c for c in REQUIRED_COLS if c not in df.columns]

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Filas", len(df))
            col_b.metric("Columnas", len(df.columns))
            col_c.metric("Columnas faltantes", len(missing))

            if missing:
                st.warning(f"⚠️ Columnas no encontradas: {', '.join(missing)}")
            else:
                st.success("✅ Todas las columnas requeridas fueron detectadas.")

            st.dataframe(df, use_container_width=True, height=400)

        except Exception as e:
            st.error(f"No se pudo leer el archivo: {e}")
    else:
        st.info("Cargue un archivo Excel para comenzar.")

# ══════════════════════════════════════════════════════════════════════════════
# PESTAÑA 2 – Plantilla de correo
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.caption("Use {NOMBRE_COLUMNA} como marcadores — serán reemplazados con los valores de cada fila.")

    subject_tpl = st.text_input("Asunto del correo", value=DEFAULT_SUBJECT)
    st.session_state["subject_tpl"] = subject_tpl

    template_body = st.text_area(
        "Cuerpo HTML de la plantilla",
        value=st.session_state.get("template", DEFAULT_TEMPLATE_HTML),
        height=480
    )
    st.session_state["template"] = template_body

# ══════════════════════════════════════════════════════════════════════════════
# PESTAÑA 3 – Enviar
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    df_loaded   = st.session_state.get("df")
    template    = st.session_state.get("template", DEFAULT_TEMPLATE_HTML)
    subject_tpl = st.session_state.get("subject_tpl", DEFAULT_SUBJECT)

    if df_loaded is None:
        st.info("Cargue un archivo Excel en la primera pestaña antes de enviar.")
    elif not secrets_ok:
        st.error("Las credenciales SMTP no están configuradas.")
    else:
        has_email_col   = "EMAIL" in df_loaded.columns
        has_cc_col      = "CC"    in df_loaded.columns
        rows_with_email = int((df_loaded["EMAIL"].str.strip() != "").sum()) if has_email_col else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("Total de filas", len(df_loaded))
        m2.metric("Filas con destinatario", rows_with_email if has_email_col else "—")
        m3.metric("Servidor SMTP", EMAIL_HOST)

        if not has_email_col:
            st.warning("La columna `EMAIL` no fue encontrada en el archivo.")

        st.divider()
        send_btn = st.button("▶  Enviar correos", disabled=(not has_email_col))

        log_placeholder  = st.empty()
        prog_placeholder = st.empty()

        if send_btn:
            logs      = []
            sent_ok   = 0
            sent_fail = 0
            rows_valid = df_loaded[df_loaded["EMAIL"].str.strip() != ""]

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode    = ssl.CERT_NONE

            def add_log(msg, kind="inf"):
                tag = {"ok": "log-ok", "err": "log-err", "inf": "log-inf"}.get(kind, "")
                logs.append(f"<span class='{tag}'>{msg}</span>")
                log_placeholder.markdown(
                    "<div class='log-box'>" + "\n".join(logs) + "</div>",
                    unsafe_allow_html=True
                )

            add_log(f"[INFO] Conectando a {EMAIL_HOST}:{EMAIL_PORT} …")

            try:
                server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=15)
                server.ehlo()
                server.starttls(context=context)
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                add_log(f"[OK]   Autenticado como {EMAIL_USER}", "ok")

                total = len(rows_valid)
                for idx, (_, row) in enumerate(rows_valid.iterrows()):
                    to_addr  = row["EMAIL"].strip()
                    cc_addr  = row["CC"].strip() if has_cc_col else ""
                    row_dict = row.to_dict()

                    # Asunto
                    try:
                        subject = subject_tpl.format(**{k: v for k, v in row_dict.items()})
                    except KeyError:
                        subject = f"Pedido Marketplace – {row_dict.get('OC', '')}"

                    # Cuerpo HTML
                    try:
                        body_html = template.format(**{k: v for k, v in row_dict.items()})
                    except KeyError as e:
                        add_log(f"[WARN] Fila {idx+1}: marcador faltante {e}, se omite.", "err")
                        sent_fail += 1
                        continue

                    msg = MIMEMultipart("alternative")
                    msg["From"]    = EMAIL_USER
                    msg["To"]      = to_addr
                    msg["Subject"] = subject
                    if cc_addr:
                        msg["Cc"] = cc_addr
                    msg.attach(MIMEText(body_html, "html", "utf-8"))

                    recipients = [to_addr] + ([cc_addr] if cc_addr else [])

                    try:
                        server.sendmail(EMAIL_USER, recipients, msg.as_string())
                        cc_info = f"  CC: {cc_addr}" if cc_addr else ""
                        add_log(f"[OK]   {idx+1}/{total}  →  {to_addr}{cc_info}  |  {subject[:50]}", "ok")
                        sent_ok += 1
                    except Exception as e:
                        add_log(f"[ERR]  {idx+1}/{total}  →  {to_addr}  |  {e}", "err")
                        sent_fail += 1

                    prog_placeholder.progress((idx + 1) / total)
                    time.sleep(1)

                server.quit()
                add_log(f"[INFO] Proceso finalizado. Enviados: {sent_ok}  |  Fallidos: {sent_fail}")

                if sent_fail == 0:
                    st.success(f"✅ Se enviaron {sent_ok} correos exitosamente.")
                else:
                    st.warning(f"Enviados: {sent_ok} — Fallidos: {sent_fail}. Revise el registro.")

            except smtplib.SMTPAuthenticationError:
                add_log("[ERR]  Autenticación fallida. Verifique las credenciales.", "err")
                st.error("Error de autenticación SMTP.")
            except Exception as e:
                add_log(f"[ERR]  Error de conexión: {e}", "err")
                st.error(f"No se pudo conectar: {e}")