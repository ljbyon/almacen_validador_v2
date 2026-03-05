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
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

  html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

  [data-testid="stSidebar"] { display: none !important; }
  [data-testid="collapsedControl"] { display: none !important; }

  .stApp { background: #0f1117; color: #e8eaf0; }
  .block-container { padding-top: 2rem; max-width: 1100px; }

  .header-banner {
    background: linear-gradient(135deg, #1a1f2e 0%, #0d1321 100%);
    border: 1px solid #2a3a5c;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
  }
  .header-banner h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    color: #4fc3f7;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .header-banner p { margin: 0.3rem 0 0; color: #7a8ba0; font-size: 0.9rem; }

  .badge-ok  { background:#0d3b2e; color:#4caf90; border:1px solid #1d6b50; border-radius:6px; padding:2px 10px; font-size:0.78rem; font-family:'IBM Plex Mono',monospace; }
  .badge-err { background:#3b0d0d; color:#e57373; border:1px solid #6b1d1d; border-radius:6px; padding:2px 10px; font-size:0.78rem; font-family:'IBM Plex Mono',monospace; }

  .log-box {
    background: #0a0d14;
    border: 1px solid #1e2a3a;
    border-radius: 8px;
    padding: 1rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    color: #b0c4d8;
    max-height: 340px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.7;
  }
  .log-ok  { color: #4caf90; }
  .log-err { color: #e57373; }
  .log-inf { color: #4fc3f7; }

  .template-preview {
    background: #111827;
    border-left: 3px solid #4fc3f7;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.4rem;
    font-size: 0.87rem;
    font-family: 'IBM Plex Mono', monospace;
    color: #c8d8e8;
    white-space: pre-wrap;
    line-height: 1.8;
  }

  .stButton > button {
    background: #1565c0;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding: 0.6rem 1.6rem;
    transition: background 0.2s;
  }
  .stButton > button:hover { background: #1976d2; }
  .stButton > button:disabled { background: #2a3a5c !important; color: #5a6a7a !important; }

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

# ─── Encabezado ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
  <h1>✉ DISMAC · Envío Masivo de Correos</h1>
  <p>Cargue un archivo Excel → previsualice → personalice la plantilla → envíe</p>
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

# ─── Plantilla por defecto ────────────────────────────────────────────────────
DEFAULT_TEMPLATE = """\
Estimados,
Pedido MARKETPLACE

─── Datos del Cliente ───────────────────────────────
  \u2022 Nombre                 : {NOMBRE CLIENTE}

─── Detalle del Pedido ───────────────────────────────
  \u2022 N° Orden de Compra     : {OC}
  \u2022 Proveedor              : {PEDIDO}
  \u2022 Regional               : {REGIONAL}

─── Detalle del Producto ───────────────────────────────
  Código                   : {CÓDIGO DEL PRODUCTO}
  Descripción              : {DESCRIPCIÓN}
  Cantidad                 : {CANT}

─── Observación ────────────────────────────────────────
  {OBSERVACIÓN}"""

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
                st.warning(f"⚠️ Columnas no encontradas: `{'`, `'.join(missing)}`")
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
    st.markdown("Use `{NOMBRE_COLUMNA}` como marcadores — serán reemplazados con los valores de cada fila.")

    subject_tpl = st.text_input("Asunto del correo", value=DEFAULT_SUBJECT)
    st.session_state["subject_tpl"] = subject_tpl

    template_body = st.text_area(
        "Cuerpo de la plantilla",
        value=st.session_state.get("template", DEFAULT_TEMPLATE),
        height=400
    )
    st.session_state["template"] = template_body

    st.divider()
    st.markdown("**Vista previa** – seleccione una fila para renderizar:")
    df_loaded = st.session_state.get("df")
    if df_loaded is not None and len(df_loaded) > 0:
        preview_idx = st.number_input("Número de fila (desde 0)", 0, len(df_loaded) - 1, 0)
        row = df_loaded.iloc[preview_idx].to_dict()
        try:
            rendered = template_body.format(**{k: v for k, v in row.items()})
            st.markdown(f"<div class='template-preview'>{rendered}</div>", unsafe_allow_html=True)
        except KeyError as e:
            st.error(f"Marcador desconocido {e} en la plantilla.")
    else:
        st.markdown(
            "<div class='template-preview'><i>Cargue un archivo en la primera pestaña para previsualizar un correo.</i></div>",
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════════════════════════════════════
# PESTAÑA 3 – Enviar
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    df_loaded   = st.session_state.get("df")
    template    = st.session_state.get("template", DEFAULT_TEMPLATE)
    subject_tpl = st.session_state.get("subject_tpl", DEFAULT_SUBJECT)

    if df_loaded is None:
        st.info("Cargue un archivo Excel en la primera pestaña antes de enviar.")
    elif not secrets_ok:
        st.error("Las credenciales SMTP no están configuradas.")
    else:
        has_email_col = "EMAIL" in df_loaded.columns
        has_cc_col    = "CC"    in df_loaded.columns
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
            context.verify_mode = ssl.CERT_NONE

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

                    # Cuerpo
                    try:
                        body = template.format(**{k: v for k, v in row_dict.items()})
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
                    msg.attach(MIMEText(body, "plain", "utf-8"))

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