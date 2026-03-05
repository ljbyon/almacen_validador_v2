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


  /* Login card */
  .login-card {
    background: #ffffff;
    border: 1px solid #e2e6f0;
    border-radius: 16px;
    padding: 2.6rem 2.8rem 2rem;
    width: 100%;
    max-width: 420px;
    margin: 8vh auto 0;
    box-shadow: 0 4px 24px rgba(30,34,60,0.09);
    text-align: center;
  }
  .login-card h2 {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1e2230;
    margin: 0.4rem 0 0.2rem;
  }
  .login-card p { color: #7b829a; font-size: 0.86rem; margin: 0 0 1.6rem; }

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

# ─── Autenticación ───────────────────────────────────────────────────────────
def check_credentials(username: str, password: str) -> bool:
    try:
        users = st.secrets["users"]
        return users.get(username) == password
    except Exception:
        return False

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = ""

if not st.session_state["authenticated"]:
    st.markdown("""
    <div class="login-card">
      <div style="font-size:2rem;margin-bottom:0.4rem">✉️</div>
      <h2>DISMAC ALMACEN · Acceso</h2>
      <p>Ingrese sus credenciales para continuar</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar", use_container_width=True)

    if submitted:
        if check_credentials(username, password):
            st.session_state["authenticated"] = True
            st.session_state["auth_user"] = username
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")
    st.stop()

# ─── Encabezado ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
  <div class="header-icon">✉️</div>
  <div>
    <h1>DISMAC ALMACEN · Envío Masivo de Correos Longtail y Marketplace</h1>
    <p>Cargar un archivo Excel → Previsualizar → Enviar</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Logout ──────────────────────────────────────────────────────────────────
col_logout = st.columns([8, 1])[1]
if col_logout.button("Cerrar sesión"):
    st.session_state["authenticated"] = False
    st.rerun()

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

# ─── Plantilla MARKETPLACE ───────────────────────────────────────────────────
TEMPLATE_MARKETPLACE = """\
<div style="font-family: Arial, sans-serif; font-size: 14px; color: #1e2230; line-height: 1.7; max-width: 600px;">

  <p style="margin: 0 0 16px;"><strong>Confirmacion de Recepcion Fisica de Pedido</strong></p>

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

# ─── Plantilla LONGTAIL ───────────────────────────────────────────────────────
TEMPLATE_LONGTAIL = """\
<div style="font-family: Arial, sans-serif; font-size: 14px; color: #1e2230; line-height: 1.7; max-width: 600px;">

  <p style="margin: 0 0 16px;">Estimados,<br>
  <strong>Pedido LONGTAIL</strong></p>

  <p style="margin: 0 0 4px; font-weight: 700; color: #2d3a8c; border-bottom: 1px solid #dde2f5; padding-bottom: 4px;">
    Detalle del Pedido
  </p>
  <ul style="margin: 8px 0 16px; padding-left: 20px;">
    <li><strong>N° Pedido:</strong> {PEDIDO}</li>
    <li><strong>N° Orden de Compra:</strong> {OC}</li>
    <li><strong>N° Control:</strong> {NUMERO CONTROL}</li>
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

REQUIRED_MARKETPLACE = [
    "PEDIDO", "OC", "NOMBRE CLIENTE", "CÓDIGO DEL PRODUCTO",
    "DESCRIPCIÓN", "CANT", "OBSERVACIÓN", "REGIONAL", "EMAIL", "CC"
]
REQUIRED_LONGTAIL = [
    "PEDIDO", "OC", "NUMERO CONTROL", "CÓDIGO DEL PRODUCTO",
    "DESCRIPCIÓN", "CANT", "OBSERVACIÓN", "REGIONAL", "EMAIL", "CC"
]

SUBJECT_MARKETPLACE = "Pedido Marketplace – {OC}"
SUBJECT_LONGTAIL    = "Pedido Longtail – {OC}"

def find_sheet(xl, keyword):
    """Return (sheet_name, DataFrame) for the sheet whose name contains keyword (case-insensitive), or (None, None)."""
    for name in xl.sheet_names:
        if keyword.upper() in name.upper():
            return name, xl.parse(name, dtype=str).fillna("")
    return None, None

# ─── Pestañas ─────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📂  Cargar Archivo", "🚀  Enviar"])

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
            xl = pd.ExcelFile(uploaded)
            sheet_longtail_name,    df_lt = find_sheet(xl, "LONGTAIL")
            sheet_marketplace_name, df_mp = find_sheet(xl, "MARKETPLACE")

            if df_lt is None and df_mp is None:
                st.error("No se encontraron hojas con 'LONGTAIL' o 'MARKETPLACE' en su nombre.")
            else:
                st.session_state["df_longtail"]    = df_lt
                st.session_state["df_marketplace"] = df_mp

                # ── LONGTAIL preview ──
                if df_lt is not None:
                    st.markdown(f"#### 📄 Hoja Longtail — *{sheet_longtail_name}*")
                    missing_lt = [c for c in REQUIRED_LONGTAIL if c not in df_lt.columns]
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Filas", len(df_lt))
                    c2.metric("Columnas", len(df_lt.columns))
                    c3.metric("Columnas faltantes", len(missing_lt))
                    if missing_lt:
                        st.warning(f"⚠️ Columnas faltantes en Longtail: {', '.join(missing_lt)}")
                    else:
                        st.success("✅ Todas las columnas requeridas de Longtail detectadas.")
                    st.dataframe(df_lt, use_container_width=True, height=260)
                else:
                    st.warning("No se encontró una hoja con 'LONGTAIL' en su nombre.")

                st.divider()

                # ── MARKETPLACE preview ──
                if df_mp is not None:
                    st.markdown(f"#### 📄 Hoja Marketplace — *{sheet_marketplace_name}*")
                    missing_mp = [c for c in REQUIRED_MARKETPLACE if c not in df_mp.columns]
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Filas", len(df_mp))
                    c2.metric("Columnas", len(df_mp.columns))
                    c3.metric("Columnas faltantes", len(missing_mp))
                    if missing_mp:
                        st.warning(f"⚠️ Columnas faltantes en Marketplace: {', '.join(missing_mp)}")
                    else:
                        st.success("✅ Todas las columnas requeridas de Marketplace detectadas.")
                    st.dataframe(df_mp, use_container_width=True, height=260)
                else:
                    st.warning("No se encontró una hoja con 'MARKETPLACE' en su nombre.")

        except Exception as e:
            st.error(f"No se pudo leer el archivo: {e}")
    else:
        st.info("Cargue un archivo Excel para comenzar.")

# ══════════════════════════════════════════════════════════════════════════════
# PESTAÑA 2 – Enviar
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    df_lt = st.session_state.get("df_longtail")
    df_mp = st.session_state.get("df_marketplace")

    if df_lt is None and df_mp is None:
        st.info("Cargue un archivo Excel en la primera pestaña antes de enviar.")
    elif not secrets_ok:
        st.error("Las credenciales SMTP no están configuradas.")
    else:
        # Build list of sheet batches to process
        batches = []
        if df_lt is not None and "EMAIL" in df_lt.columns:
            batches.append({
                "label":    "Longtail",
                "df":       df_lt,
                "template": TEMPLATE_LONGTAIL,
                "subject":  SUBJECT_LONGTAIL,
            })
        if df_mp is not None and "EMAIL" in df_mp.columns:
            batches.append({
                "label":    "Marketplace",
                "df":       df_mp,
                "template": TEMPLATE_MARKETPLACE,
                "subject":  SUBJECT_MARKETPLACE,
            })

        total_rows = sum(
            int((b["df"]["EMAIL"].str.strip() != "").sum()) for b in batches
        )

        # Summary metrics
        cols = st.columns(len(batches) + 1)
        cols[0].metric("Total destinatarios", total_rows)
        for i, b in enumerate(batches):
            n = int((b["df"]["EMAIL"].str.strip() != "").sum())
            cols[i + 1].metric(f"Hoja {b['label']}", n)

        if not batches:
            st.warning("Ninguna hoja tiene la columna `EMAIL`.")

        st.divider()
        send_btn = st.button("▶  Enviar correos", disabled=(not batches))

        log_placeholder  = st.empty()
        prog_placeholder = st.empty()

        if send_btn:
            logs      = []
            sent_ok   = 0
            sent_fail = 0

            # Count total valid rows across both sheets for progress bar
            all_rows_count = sum(
                int((b["df"]["EMAIL"].str.strip() != "").sum()) for b in batches
            )
            processed = 0

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

                for batch in batches:
                    label       = batch["label"]
                    template    = batch["template"]
                    subject_tpl = batch["subject"]
                    has_cc      = "CC" in batch["df"].columns
                    rows_valid  = batch["df"][batch["df"]["EMAIL"].str.strip() != ""]
                    batch_total = len(rows_valid)

                    add_log(f"[INFO] ── Procesando hoja {label} ({batch_total} filas) ──")

                    for idx, (_, row) in enumerate(rows_valid.iterrows()):
                        to_addr  = row["EMAIL"].strip()
                        cc_addr  = row["CC"].strip() if has_cc else ""
                        row_dict = row.to_dict()

                        # Split multiple addresses separated by semicolons
                        to_list = [a.strip() for a in to_addr.split(";") if a.strip()]
                        cc_list = [a.strip() for a in cc_addr.split(";") if a.strip()]

                        try:
                            subject = subject_tpl.format(**{k: v for k, v in row_dict.items()})
                        except KeyError:
                            subject = f"Pedido {label} – {row_dict.get('OC', '')}"

                        try:
                            body_html = template.format(**{k: v for k, v in row_dict.items()})
                        except KeyError as e:
                            add_log(f"[WARN] {label} fila {idx+1}: marcador faltante {e}, se omite.", "err")
                            sent_fail += 1
                            processed += 1
                            prog_placeholder.progress(processed / all_rows_count)
                            continue

                        msg = MIMEMultipart("alternative")
                        msg["From"]    = EMAIL_USER
                        msg["To"]      = ", ".join(to_list)
                        msg["Subject"] = subject
                        if cc_list:
                            msg["Cc"] = ", ".join(cc_list)
                        msg.attach(MIMEText(body_html, "html", "utf-8"))

                        recipients = to_list + cc_list

                        try:
                            server.sendmail(EMAIL_USER, recipients, msg.as_string())
                            cc_info = f"  CC: {', '.join(cc_list)}" if cc_list else ""
                            add_log(f"[OK]   {label} {idx+1}/{batch_total}  →  {', '.join(to_list)}{cc_info}  |  {subject[:48]}", "ok")
                            sent_ok += 1
                        except Exception as e:
                            add_log(f"[ERR]  {label} {idx+1}/{batch_total}  →  {to_addr}  |  {e}", "err")
                            sent_fail += 1

                        processed += 1
                        prog_placeholder.progress(processed / all_rows_count)
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