import streamlit as st
import pandas as pd
import os
import re
import qrcode
from io import BytesIO

# Soubor, kam si aplikace bude ukládat odkaz na aktuální kvíz
URL_FILE = "aktivni_kviz_url.txt"

# Výchozí tabulka
DEFAULT_URL = "https://docs.google.com/spreadsheets/d/1beqUxD2cOf2gzj20W42k1JIpytB0OuJS/export?format=xlsx&gid=1297757886"

def uloz_odkaz(url):
    with open(URL_FILE, "w") as f:
        f.write(url)

def nacti_odkaz():
    if os.path.exists(URL_FILE):
        with open(URL_FILE, "r") as f:
            obsah = f.read().strip()
            if obsah:
                return obsah
    return DEFAULT_URL

def uprav_google_odkaz(url):
    match_id = re.search(r"d/([a-zA-Z0-9-_]+)", url)
    if not match_id:
        return url
    id_tabulky = match_id.group(1)
    match_gid = re.search(r"gid=([0-9]+)", url)
    export_url = f"https://docs.google.com/spreadsheets/d/{id_tabulky}/export?format=xlsx"
    if match_gid:
        export_url += f"&gid={match_gid.group(1)}"
    return export_url

def generuj_qr_kod(url):
    """Vygeneruje QR kód jako obrázek z aktuální webové adresy aplikace."""
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

st.set_page_config(page_title="Rozsošský kvíz - Výsledky", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #ffffff; }
    h1 { text-align: center; color: #fca311; font-family: 'Arial Black', sans-serif; text-transform: uppercase; margin-bottom: 20px;}
    .stButton>button { width: 100%; font-weight: bold; background-color: #fca311; color: #000; border-radius: 8px; margin-bottom: 20px;}
    
    .team-card {
        background: linear-gradient(90deg, #1e1e1e 0%, #2a2a2a 100%);
        margin-bottom: 15px;
        padding: 15px 20px;
        border-radius: 10px;
        border-left: 5px solid #fca311;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    
    .team-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .team-name { font-size: 20px; font-weight: bold; width: 35%; }
    
    .team-details { 
        font-size: 14px; 
        width: 45%; 
        display: flex; 
        flex-direction: column; 
        justify-content: center;
        align-items: center;
        gap: 4px; 
    }
    .details-row {
        display: flex;
        gap: 15px;
        justify-content: center;
    }
    
    .hracu-badge { color: #98fb98; font-weight: bold; } 
    .runda-badge { color: #4dc9f6; font-weight: bold; }
    .trestne-badge { color: #ff4444; font-weight: bold; }
    .zolik-badge { color: #d7bde2; font-weight: bold; }
    
    .team-score { font-size: 28px; font-weight: 900; color: #fca311; width: 20%; text-align: right; }
    
    .rounds-container {
        display: flex;
        justify-content: space-between;
        background-color: rgba(255, 255, 255, 0.05);
        padding: 10px 15px;
        border-radius: 8px;
    }
    
    .round-box {
        display: flex;
        gap: 12px; 
        align-items: flex-start;
    }
    .round-left, .round-right {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .round-title {
        font-size: 11px;
        color: #aaaaaa;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .round-points {
        font-size: 17px;
        font-weight: bold;
        color: #ffffff;
    }
    .round-tip-label {
        font-size: 11px;
        color: #fca311;
        text-transform: uppercase;
        margin-bottom: 4px;
        font-weight: bold;
    }
    .round-tip-val {
        font-size: 17px;
        font-weight: bold;
        color: #fca311;
    }
    
    .rank-1 { border-left: 5px solid #ffd700; background: linear-gradient(90deg, #2a2200 0%, #3a3000 100%); }
    .rank-1 .team-score { color: #ffd700; }
    .rank-1 .rounds-container { background-color: rgba(255, 215, 0, 0.1); }
    </style>
""", unsafe_allow_html=True)

AKTUALNI_URL = nacti_odkaz()

# Zjištění reálné webové adresy aplikace
app_url = st.context.headers.get("Host", "")
if app_url:
    app_url = f"https://{app_url}"
else:
    app_url = "https://rozsossky-kviz.streamlit.app"

# --- TAJNÁ ADMINISTRACE V POSTRANNÍM PANELU ---
with st.sidebar:
    st.markdown("### Administrace")
    zadavane_heslo = st.text_input("Zadejte heslo pro administraci:", type="password")
    
    if zadavane_heslo == "admin123":
        st.markdown("---")
        st.markdown("#### Nastavení nového kvízu")
        novy_odkaz = st.text_input("Zkopírujte odkaz na novou Excel tabulku:")
        
        if st.button("💾 Uložit a přepnout na nový kvíz"):
            if novy_odkaz:
                upraveny_odkaz = uprav_google_odkaz(novy_odkaz)
                uloz_odkaz(upraveny_odkaz)
                st.cache_data.clear()
                st.success("Nový kvíz byl úspěšně nastaven!")
                st.rerun()

st.title("🏆 Rozsošský kvíz")

if zadavane_heslo == "admin123":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Zveřejnit výsledky z nového kola"):
            st.cache_data.clear()
            st.success("Data byla úspěšně zaktualizována všem hráčům!")

@st.cache_data
def nacti_data(url):
    df = pd.read_excel(url, sheet_name="Výsledková listina", engine="openpyxl", skiprows=20, header=None)
    df = df.dropna(how="all")
    return df

def format_body(val):
    if pd.isna(val) or str(val).strip() == "":
        return "-"
    try:
        return f"{float(val):.1f}".replace(".0", "")
    except ValueError:
        return str(val).replace("<", "&lt;").replace(">", "&gt;")

def get_val(row, idx):
    if idx < len(row):
        return row.iloc[idx]
    return float('nan')

def get_tip_html(tip_val):
    if tip_val != "-":
        return f"""
        <div class="round-right">
            <div class="round-tip-label">Tip</div>
            <div class="round-tip-val">{tip_val}</div>
        </div>
        """
    return ""

try:
    df = nacti_data(AKTUALNI_URL)
    
    for index, row in df.iterrows():
        poradi = index + 1
        
        raw_tym = get_val(row, 1)
        if pd.isna(raw_tym):
             continue
             
        tym = str(raw_tym).strip().replace("<", "&lt;").replace(">", "&gt;")
        
        if not tym or tym == "nan":
            continue
            
        k1 = format_body(get_val(row, 2))
        k2 = format_body(get_val(row, 6))
        k3 = format_body(get_val(row, 10))
        k4 = format_body(get_val(row, 15))
        k5 = format_body(get_val(row, 19))
        
        t1 = format_body(get_val(row, 3))
        t2 = format_body(get_val(row, 7))
        t3 = format_body(get_val(row, 11))
        t4 = format_body(get_val(row, 16))
        t5 = format_body(get_val(row, 20))
        
        runda = format_body(get_val(row, 12))
        celkem = format_body(get_val(row, 21))
        koef_hracu = get_val(row, 23)
        trestne = get_val(row, 24)
        
        raw_zolik = get_val(row, 25) 
        zolik_html = ""
        if pd.notna(raw_zolik) and str(raw_zolik).strip() not in ["", "-", "nan"] and not isinstance(raw_zolik, (int, float)):
            tema_zolika = str(raw_zolik).strip().replace("<", "&lt;").replace(">", "&gt;")
            zolik_html = f'<span class="zolik-badge">Žolík: {tema_zolika}</span>'
        
        hraci_html = ""
        try:
            if pd.notna(koef_hracu) and str(koef_hracu).strip() != "":
                pocet_hracu = int(round(float(koef_hracu) * 1000))
                if pocet_hracu > 0:
                    hraci_html = f'<span class="hracu-badge">Hráčů: {pocet_hracu}</span>'
        except ValueError:
            pass 
        
        runda_html = ""
        if runda != "-" and runda != "0":
            runda_html = f'<span class="runda-badge">Runda: {runda} b.</span>'
            
        trestne_html = ""
        if pd.notna(trestne) and isinstance(trestne, (int, float)) and trestne > 0:
            trestne_html = f'<span class="trestne-badge">Trestné: -{int(trestne)}</span>'
            
        if pd.isna(celkem):
            celkem_text = "0"
        else:
            celkem_text = format_body(celkem)
            
        css_class = "team-card rank-1" if poradi == 1 else "team-card"
        
        top_row_items = " ".join([item for item in [hraci_html, runda_html] if item])
        bottom_row_items = " ".join([item for item in [zolik_html, trestne_html] if item])
        
        top_row_html = f'<div class="details-row">{top_row_items}</div>' if top_row_items else ""
        bottom_row_html = f'<div class="details-row">{bottom_row_items}</div>' if bottom_row_items else ""
        
        html = f"""
        <div class="{css_class}">
            <div class="team-row">
                <div class="team-name">{poradi}. {tym}</div>
                <div class="team-details">
                    {top_row_html}
                    {bottom_row_html}
                </div>
                <div class="team-score">{celkem_text}</div>
            </div>
            <div class="rounds-container">
                <div class="round-box">
                    <div class="round-left">
                        <div class="round-title">1. kolo</div>
                        <div class="round-points">{k1}</div>
                    </div>
                    {get_tip_html(t1)}
                </div>
                <div class="round-box">
                    <div class="round-left">
                        <div class="round-title">2. kolo</div>
                        <div class="round-points">{k2}</div>
                    </div>
                    {get_tip_html(t2)}
                </div>
                <div class="round-box">
                    <div class="round-left">
                        <div class="round-title">3. kolo</div>
                        <div class="round-points">{k3}</div>
                    </div>
                    {get_tip_html(t3)}
                </div>
                <div class="round-box">
                    <div class="round-left">
                        <div class="round-title">4. kolo</div>
                        <div class="round-points">{k4}</div>
                    </div>
                    {get_tip_html(t4)}
                </div>
                <div class="round-box">
                    <div class="round-left">
                        <div class="round-title">5. kolo</div>
                        <div class="round-points">{k5}</div>
                    </div>
                    {get_tip_html(t5)}
                </div>
            </div>
        </div>
        """
        
        html = html.replace('\n', ' ')
        st.markdown(html, unsafe_allow_html=True)

    # --- QR KÓD NA ÚPLNÉM SPODKU STRÁNKY PRO VŠECHNY ---
    st.markdown("---")
    st.markdown("<h3 style='text-align: center; color: #fca311;'>📱 Sdílejte kvíz s ostatními!</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #aaaaaa;'>Naskenujte QR kód mobilem a ukažte ho u vedlejšího stolu.</p>", unsafe_allow_html=True)
    
    # Vycentrování QR kódu pomocí sloupců
    q_col1, q_col2, q_col3 = st.columns([1, 1, 1])
    with q_col2:
        qr_bytes = generuj_qr_kod(app_url)
        st.image(qr_bytes, use_container_width=True)

except Exception as e:
    st.error(f"Nepodařilo se načíst aktuální výsledky. Detail: {e}")