import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigürasyon ve Tema
st.set_page_config(page_title="Professional Finance Terminal", layout="wide", page_icon="📈")

# Özel CSS (Bloomberg Terminal Karanlık Tema)
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stSelectbox, .stDateInput, .stTextInput {
        color: #fafafa;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #00ff00;
    }
    /* AI Analist Kutusu */
    .ai-analyst-box {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00ff00;
        margin-top: 20px;
    }
    .ai-decision {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        border-radius: 5px;
        color: white;
    }
    .badge {
        background-color: #3b82f6;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 10px;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar ve Kontroller
st.sidebar.title("Kontrol Paneli")

# Otomatik Yenileme (60sn)
if st.sidebar.checkbox("🔴 Canlı Veri Modu (60sn)"):
    st_autorefresh(interval=60000, key="datarefresh")

# Manuel Yenileme
if st.sidebar.button("🔄 Verileri Şimdi Güncelle"):
    st.cache_data.clear()
    st.rerun()

# Genişletilmiş Hisse Listesi
symbol_list = [
    'ACSEL.IS', 'ADEL.IS', 'ADESE.IS', 'AEFES.IS', 'AFYON.IS', 'AGESA.IS', 'AGHOL.IS', 'AGYO.IS', 'AHGAZ.IS', 'AKBNK.IS',
    'AKCNS.IS', 'AKENR.IS', 'AKFGY.IS', 'AKGRT.IS', 'AKMGY.IS', 'AKSA.IS', 'AKSEN.IS', 'AKSGY.IS', 'AKSUE.IS', 'AKYHO.IS',
    'ALARK.IS', 'ALBRK.IS', 'ALCAR.IS', 'ALCTL.IS', 'ALFAS.IS', 'ALGYO.IS', 'ALKIM.IS', 'ALMAD.IS', 'ALTNY.IS', 'ANELE.IS',
    'ANGEN.IS', 'ANHYT.IS', 'ANSGR.IS', 'ARASE.IS', 'ARCLK.IS', 'ARDYZ.IS', 'ARENA.IS', 'ARSAN.IS', 'ARZUM.IS', 'ASELS.IS',
    'ASTOR.IS', 'ASUZU.IS', 'ATAGY.IS', 'ATAKP.IS', 'ATATP.IS', 'ATEKS.IS', 'ATLAS.IS', 'AVGYO.IS', 'AVHOL.IS', 'AVOD.IS',
    'AVTUR.IS', 'AYCES.IS', 'AYDEM.IS', 'AYEN.IS', 'AYES.IS', 'AYGAZ.IS', 'AZTEK.IS', 'BAGFS.IS', 'BAKAB.IS', 'BALAT.IS',
    'BANVT.IS', 'BARMA.IS', 'BASCM.IS', 'BASGZ.IS', 'BAYRK.IS', 'BEGYO.IS', 'BERA.IS', 'BEYAZ.IS', 'BFREN.IS', 'BIENY.IS',
    'BIGCH.IS', 'BIMAS.IS', 'BIOEN.IS', 'BIZIM.IS', 'BJKAS.IS', 'BLCYT.IS', 'BMSCH.IS', 'BMSTL.IS', 'BNTAS.IS', 'BOBET.IS',
    'BOSSA.IS', 'BRISA.IS', 'BRKO.IS', 'BRKSN.IS', 'BRKVY.IS', 'BRLSM.IS', 'BRMEN.IS', 'BRSAN.IS', 'BRYAT.IS', 'BSOKE.IS',
    'BTCIM.IS', 'BUCIM.IS', 'BURCE.IS', 'BURVA.IS', 'BVSAN.IS', 'BYDNR.IS', 'CANTE.IS', 'CASA.IS', 'CCOLA.IS', 'CELHA.IS',
    'CEMAS.IS', 'CEMTS.IS', 'CEOEM.IS', 'CIMSA.IS', 'CLEBI.IS', 'CMBTN.IS', 'CMENT.IS', 'CONSE.IS', 'COSMO.IS', 'CRDFA.IS',
    'CRFSA.IS', 'CUSAN.IS', 'CVKMD.IS', 'CWENE.IS', 'DAGHL.IS', 'DAGI.IS', 'DAPGM.IS', 'DARDL.IS', 'DENGE.IS', 'DERHL.IS',
    'DERIM.IS', 'DESA.IS', 'DESPC.IS', 'DEVA.IS', 'DGATE.IS', 'DGGYO.IS', 'DGNMO.IS', 'DIRIT.IS', 'DITAS.IS', 'DMSAS.IS',
    'DNISI.IS', 'DOAS.IS', 'DOBUR.IS', 'DOCO.IS', 'DOGUB.IS', 'DOHOL.IS', 'DOKTA.IS', 'DURDO.IS', 'DYOBY.IS', 'DZGYO.IS',
    'EBEBK.IS', 'ECILC.IS', 'ECZYT.IS', 'EDATA.IS', 'EDIP.IS', 'EGEEN.IS', 'EGGUB.IS', 'EGPRO.IS', 'EGSER.IS', 'EKGYO.IS',
    'EKIZ.IS', 'EKSUN.IS', 'ELITE.IS', 'EMKEL.IS', 'EMNIS.IS', 'ENJSA.IS', 'ENKAI.IS', 'ENSRI.IS', 'EPLAS.IS', 'ERBOS.IS',
    'ERCB.IS', 'EREGL.IS', 'ERSU.IS', 'ESCAR.IS', 'ESCOM.IS', 'ESEN.IS', 'ETILR.IS', 'ETYAT.IS', 'EUHOL.IS', 'EUKYO.IS',
    'EUPWR.IS', 'EUREN.IS', 'EUYO.IS', 'FADE.IS', 'FENER.IS', 'FLAP.IS', 'FMIZP.IS', 'FONET.IS', 'FORMT.IS', 'FRIGO.IS',
    'FROTO.IS', 'FZLGY.IS', 'GARAN.IS', 'GARFA.IS', 'GEDIK.IS', 'GEDZA.IS', 'GENIL.IS', 'GENTS.IS', 'GEREL.IS', 'GESAN.IS',
    'GLBMD.IS', 'GLRYH.IS', 'GLYHO.IS', 'GMTAS.IS', 'GOKNR.IS', 'GOLTS.IS', 'GOODY.IS', 'GOZDE.IS', 'GRNYO.IS', 'GSDDE.IS',
    'GSDHO.IS', 'GSRAY.IS', 'GUBRF.IS', 'GWIND.IS', 'GZNMI.IS', 'HALKB.IS', 'HATEK.IS', 'HDFGS.IS', 'HEDEF.IS', 'HEKTS.IS',
    'HKTM.IS', 'HLGYO.IS', 'HTTBT.IS', 'HUBVC.IS', 'HUNER.IS', 'HURGZ.IS', 'ICBCT.IS', 'IDEAS.IS', 'IDGYO.IS', 'IEYHO.IS',
    'IHAAS.IS', 'IHEVA.IS', 'IHGZT.IS', 'IHLAS.IS', 'IHLGM.IS', 'IHYAY.IS', 'IMASM.IS', 'INDES.IS', 'INFO.IS', 'INGRM.IS',
    'INTEM.IS', 'INVEO.IS', 'INVES.IS', 'IOVI.IS', 'IPEKE.IS', 'ISATR.IS', 'ISBTR.IS', 'ISBIR.IS', 'ISCTR.IS', 'ISDMR.IS',
    'ISFIN.IS', 'ISGSY.IS', 'ISGYO.IS', 'ISKPL.IS', 'ISKUR.IS', 'ISMEN.IS', 'ISSEN.IS', 'ISYAT.IS', 'ITTFH.IS', 'IZENR.IS',
    'IZFAS.IS', 'IZINV.IS', 'IZMDC.IS', 'JANTS.IS', 'KAPLM.IS', 'KARYE.IS', 'KATMR.IS', 'KAYSE.IS', 'KCAER.IS', 'KCHOL.IS',
    'KENT.IS', 'KERVN.IS', 'KERVT.IS', 'KFEIN.IS', 'KGYO.IS', 'KIMMR.IS', 'KLGYO.IS', 'KLKIM.IS', 'KLMSN.IS', 'KLNMA.IS',
    'KLRHO.IS', 'KMPUR.IS', 'KNFRT.IS', 'KONKA.IS', 'KONTR.IS', 'KONYA.IS', 'KOPOL.IS', 'KORDS.IS', 'KOZAA.IS', 'KOZAL.IS',
    'KRDMA.IS', 'KRDMB.IS', 'KRDMD.IS', 'KRGYO.IS', 'KRONT.IS', 'KRPLS.IS', 'KRSTL.IS', 'KRTEK.IS', 'KRVGD.IS', 'KSTUR.IS',
    'KTKYO.IS', 'KTSKR.IS', 'KUTPO.IS', 'KUYAS.IS', 'KZBGY.IS', 'KZGYO.IS', 'LIDER.IS', 'LIDFA.IS', 'LINK.IS', 'LKMNH.IS',
    'LOGO.IS', 'LUKSK.IS', 'MAALT.IS', 'MACKO.IS', 'MAGEN.IS', 'MAKIM.IS', 'MAKTK.IS', 'MANAS.IS', 'MARKA.IS', 'MARTI.IS',
    'MAVI.IS', 'MEDTR.IS', 'MEGAP.IS', 'MEPET.IS', 'MERCN.IS', 'MERIT.IS', 'MERKO.IS', 'METRO.IS', 'METUR.IS', 'MGROS.IS',
    'MIATK.IS', 'MIPAZ.IS', 'MMCAS.IS', 'MNDRS.IS', 'MNUHL.IS', 'MOBTL.IS', 'MPARK.IS', 'MRGYO.IS', 'MRSHL.IS', 'MSGYO.IS',
    'MTRKS.IS', 'MTRYO.IS', 'MUNDA.IS', 'NATURE.IS', 'NETAS.IS', 'NIBAS.IS', 'NTGAZ.IS', 'NTHOL.IS', 'NUGYO.IS', 'NUHCM.IS',
    'OBASE.IS', 'ODAS.IS', 'OFSYM.IS', 'ONCSM.IS', 'ORCAY.IS', 'ORGE.IS', 'ORMA.IS', 'OSMEN.IS', 'OSTIM.IS', 'OTKAR.IS',
    'OTTO.IS', 'OYAKC.IS', 'OYAYO.IS', 'OYLUM.IS', 'OYYAT.IS', 'OZBAL.IS', 'OZGYO.IS', 'OZKGY.IS', 'OZRDN.IS', 'OZSUB.IS',
    'PAGYO.IS', 'PAMEL.IS', 'PAPIL.IS', 'PARSN.IS', 'PASEU.IS', 'PCILT.IS', 'PEGYO.IS', 'PEKGY.IS', 'PENGD.IS', 'PENTA.IS',
    'PETKM.IS', 'PETUN.IS', 'PGSUS.IS', 'PINSU.IS', 'PKART.IS', 'PKENT.IS', 'PLTUR.IS', 'PNLSN.IS', 'PNSUT.IS', 'POLHO.IS',
    'POLTK.IS', 'PRDGS.IS', 'PRKAB.IS', 'PRKME.IS', 'PRZMA.IS', 'PSGYO.IS', 'QNBFL.IS', 'QUAGR.IS', 'RALYH.IS', 'RAYSG.IS',
    'RNPOL.IS', 'RODRG.IS', 'ROYAL.IS', 'RTALB.IS', 'RUBNS.IS', 'RYGYO.IS', 'RYSAS.IS', 'SAHOL.IS', 'SAMAT.IS', 'SANEL.IS',
    'SANFM.IS', 'SANKO.IS', 'SARKY.IS', 'SASA.IS', 'SAYAS.IS', 'SDTTR.IS', 'SEKFK.IS', 'SEKUR.IS', 'SELEC.IS', 'SELGD.IS',
    'SELVA.IS', 'SEYKM.IS', 'SILVR.IS', 'SISE.IS', 'SKBNK.IS', 'SKTAS.IS', 'SMART.IS', 'SMRTG.IS', 'SNGYO.IS', 'SNKRN.IS',
    'SNPAM.IS', 'SODSN.IS', 'SOKE.IS', 'SOKM.IS', 'SONME.IS', 'SRVGY.IS', 'SUMAS.IS', 'SUNTK.IS', 'SUWEN.IS', 'TATGD.IS',
    'TAVHL.IS', 'TBORG.IS', 'TCELL.IS', 'TDGYO.IS', 'TEKTU.IS', 'TERA.IS', 'TETMT.IS', 'TEZOL.IS', 'TGSAS.IS', 'THYAO.IS',
    'TKFEN.IS', 'TKNSA.IS', 'TLMAN.IS', 'TMPOL.IS', 'TMSN.IS', 'TNZTP.IS', 'TOASO.IS', 'TRCAS.IS', 'TRGYO.IS', 'TRILC.IS',
    'TSGYO.IS', 'TSKB.IS', 'TSPOR.IS', 'TTKOM.IS', 'TTRAK.IS', 'TUCLK.IS', 'TUKAS.IS', 'TUPRS.IS', 'TURGG.IS', 'TURSG.IS',
    'UFUK.IS', 'ULAS.IS', 'ULKER.IS', 'ULUFA.IS', 'ULUSE.IS', 'ULUUN.IS', 'UNLU.IS', 'USAK.IS', 'UYUM.IS', 'VAKBN.IS',
    'VAKFN.IS', 'VAKKO.IS', 'VANGD.IS', 'VBTYZ.IS', 'VERTU.IS', 'VERUS.IS', 'VESBE.IS', 'VESTL.IS', 'VKFYO.IS', 'VKGYO.IS',
    'VKING.IS', 'YAPRK.IS', 'YATAS.IS', 'YAYLA.IS', 'YEOTK.IS', 'YESIL.IS', 'YGGYO.IS', 'YGYO.IS', 'YKBNK.IS', 'YKSLN.IS',
    'YONGA.IS', 'YUNSA.IS', 'YYAPI.IS', 'YYLGD.IS', 'ZEDUR.IS', 'ZOREN.IS', 'ZRGYO.IS', 
    'BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 'XRP-USD', 'ADA-USD', 'DOGE-USD', 'AVAX-USD', 'TRX-USD', 'DOT-USD', 'MATIC-USD',
    'USDTRY=X', 'EURTRY=X', 'GBPTRY=X', 'XAUUSD=X', 'XAGUSD=X', 'GC=F', 'CL=F', 'SI=F', 'NG=F'
]
symbol_list.sort()

st.sidebar.markdown("### Hisse/Coin Seçimi")
search_ticker = st.sidebar.selectbox("Listeden Seç:", symbol_list, index=symbol_list.index('BTC-USD') if 'BTC-USD' in symbol_list else 0)
manual_ticker = st.sidebar.text_input("Veya Manuel Girin (Örn: AAPL):")

selected_ticker = manual_ticker.upper() if manual_ticker else search_ticker

# ---------------------------
# PERİYOT SEÇİCİ
# ---------------------------
st.sidebar.markdown("### Analiz Periyodu")
intervals = {
    "1 Gün (Orta Vade - Swing)": {"period": "1y", "interval": "1d", "mode": "SWING"},
    "1 Hafta (Uzun Vade - Yatırımcı)": {"period": "2y", "interval": "1wk", "mode": "YATIRIMCI"},
    "1 Ay (Makro Bakış)": {"period": "5y", "interval": "1mo", "mode": "YATIRIMCI"},
    "4 Saat (Trade)": {"period": "1y", "interval": "60m", "mode": "TRADER"},
    "1 Saat (Day Trade)": {"period": "6mo", "interval": "60m", "mode": "TRADER"},
    "15 Dakika (Scalp)": {"period": "1mo", "interval": "15m", "mode": "SCALPER"},
    "5 Dakika (Hızlı Scalp)": {"period": "5d", "interval": "5m", "mode": "SCALPER"}
}

period_selection = st.sidebar.selectbox("Zaman Dilimi Seçin:", list(intervals.keys()), index=0)
selected_params = intervals[period_selection]

# 3. Veri Çekme Fonksiyonu
@st.cache_data(ttl=15)
def get_data(ticker, period, interval):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        
        # MultiIndex Düzeltmesi
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Datetime index name fix
        df.index.name = 'Date'
        
        if df.empty:
            return None
        return df
    except Exception as e:
        return None

# PİYASA TARAMASI (BATCH DOWNLOAD)
@st.cache_data(ttl=300) # 5 dk cache
def get_market_trends():
    try:
        # We fetch 5 days to be safe against weekends/holidays
        tickers_str = " ".join(symbol_list)
        df_batch = yf.download(tickers_str, period="5d", group_by='ticker', progress=False)
        
        results = []
        
        for ticker in symbol_list:
            try:
                # Access data for this ticker safely
                if isinstance(df_batch.columns, pd.MultiIndex):
                    data = df_batch[ticker]
                else:
                    # Single ticker or flat structure fallback
                    data = df_batch if ticker == list(df_batch.columns)[0] else None
                
                if data is None or data.empty:
                    continue
                    
                # Drop NA and verify we have enough data
                data = data.dropna(subset=['Close'])
                if len(data) < 2:
                    continue
                
                last_close = data['Close'].iloc[-1]
                prev_close = data['Close'].iloc[-2]
                volume = data['Volume'].iloc[-1]
                
                pct_change = ((last_close - prev_close) / prev_close) * 100
                
                results.append({
                    "Symbol": ticker,
                    "Price": last_close,
                    "Change %": pct_change,
                    "Volume": volume
                })
            except Exception:
                continue
                
        results_df = pd.DataFrame(results)
        return results_df
            
    except Exception as e:
        return pd.DataFrame() # Return empty if fails

# Veriyi Yükle (Ana Sekmeler İçin)
df = get_data(selected_ticker, selected_params["period"], selected_params["interval"])

# 4. Teknik Analiz Hesaplamaları
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data, slow=26, fast=12, signal=9):
    exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def calculate_bollinger(data, window=20, no_of_std=2):
    rolling_mean = data['Close'].rolling(window).mean()
    rolling_std = data['Close'].rolling(window).std()
    upper_band = rolling_mean + (rolling_std * no_of_std)
    lower_band = rolling_mean - (rolling_std * no_of_std)
    return upper_band, rolling_mean, lower_band

def calculate_cci(data, ndays=20): 
    tp = (data['High'] + data['Low'] + data['Close']) / 3 
    cci = (tp - tp.rolling(ndays).mean()) / (0.015 * tp.rolling(ndays).std()) 
    return cci

# Ana Tablar İçin Veri Varsa İndikatör Hesapla
if df is not None and not df.empty:
    df['RSI'] = calculate_rsi(df)
    df['MACD'], df['Signal'] = calculate_macd(df)
    df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = calculate_bollinger(df)
    df['CCI'] = calculate_cci(df)
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()

# 5. Arayüz Sekmeleri
tab1, tab2, tab3, tab4 = st.tabs(["📊 Piyasa Özeti & AI", "📈 Teknik İndikatörler", "🎲 Monte Carlo Simülasyonu", "🔥 Günün Trendleri"])

# --- TAB 1, 2, 3 SADECE VERİ VARSA ÇALIŞIR ---
if df is not None and not df.empty:
    with tab1:
        st.subheader(f"{selected_ticker} Piyasa Özeti ({selected_params['mode']} Modu)")
        
        last_price = df['Close'].iloc[-1]
        if isinstance(last_price, pd.Series): last_price = last_price.iloc[0]
            
        prev_price = df['Close'].iloc[-2]
        if isinstance(prev_price, pd.Series): prev_price = prev_price.iloc[0]
            
        daily_change = ((last_price - prev_price) / prev_price) * 100
        
        col1, col2 = st.columns(2)
        col1.metric("Güncel Fiyat", f"{last_price:.2f}", f"{daily_change:.2f}%")
        
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index,
                    open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    name=selected_ticker))
        
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='gray', width=1), name='BB Üst'))
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Middle'], line=dict(color='orange', width=1), name='BB Orta'))
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='gray', width=1), name='BB Alt'))

        fig.update_layout(template='plotly_dark', title=f'{selected_ticker} - {period_selection}', height=600)
        st.plotly_chart(fig, use_container_width=True)

        # AI Analist
        st.markdown("---")
        st.markdown(f'<div class="ai-analyst-box"><h3>🤖 Yapay Zeka Analiz Raporu</h3>', unsafe_allow_html=True)
        
        active_mode = selected_params["mode"]
        st.markdown(f'<span class="badge">{active_mode} ANALİZİ DEVREDE</span>', unsafe_allow_html=True)
        
        current_rsi = df['RSI'].iloc[-1]
        current_macd = df['MACD'].iloc[-1]
        current_signal = df['Signal'].iloc[-1]
        current_sma20 = df['SMA20'].iloc[-1]
        current_sma50 = df['SMA50'].iloc[-1]
        current_price = df['Close'].iloc[-1]
        
        signals = []
        score = 0 
        
        if active_mode == "SCALPER":
            if current_rsi < 30:
                signals.append("⚡ **SCALP FIRSATI:** RSI 30 altında! Anlık tepki alımı beklenebilir.")
                score += 3
            elif current_rsi > 70:
                signals.append("⚡ **DİKKAT:** RSI 70 üzerinde. Hızlı bir satış gelebilir.")
                score -= 3
            else:
                signals.append(f"⚪ **RSI:** {current_rsi:.1f} ile nötr. İşlem kovalamak için erken.")
                
            if current_macd > current_signal:
                signals.append("✅ **Momentum:** MACD pozitif, kısa vadeli alımlar destekleniyor.")
                score += 1
            else:
                signals.append("🔻 **Momentum:** MACD negatif, kısa vadeli baskı var.")
                score -= 1

        elif active_mode == "TRADER" or active_mode == "SWING":
            if current_price > current_sma20:
                signals.append("✅ **Trend:** Fiyat 20 periyotluk ortalamanın üzerinde. Yön yukarı.")
                score += 1
            else:
                signals.append("🔻 **Trend:** Fiyat kısa vade ortalamanın altında. Temkinli ol.")
                score -= 1
                
            if current_rsi < 30:
                signals.append("✅ **Dip Avı:** Aşırı satım bölgesindeyiz. Dönüş mumları ara.")
                score += 2
            elif current_rsi > 70:
                signals.append("🔻 **Kar Realizasyonu:** Fiyat şişmiş, düzeltme riski yüksek.")
                score -= 2

        elif active_mode == "YATIRIMCI":
            if current_sma20 > current_sma50:
                signals.append("✅ **Altın Vuruş:** Golden Cross aktif (Kısa vade ortalama, uzun vadeyi yukarı kesti).")
                score += 2
            elif current_sma20 < current_sma50:
                signals.append("🔻 **Death Cross:** Düşüş trendi baskın (Death Cross). Acele etme.")
                score -= 2
                
            if current_rsi < 40: 
                signals.append("✅ **Toplama Bölgesi:** RSI düşük seviyelerde, kademeli alım düşünülebilir.")
                score += 1
            elif current_rsi > 80:
                signals.append("🔻 **Aşırı Prim:** Çok hızlı yükselmiş, uzun vade için pahalı olabilir.")
                score -= 1

        for signal in signals:
            st.write(signal)

        decision_text = ""
        decision_color = ""
        
        if score >= 3:
            decision_text = "GÜÇLÜ AL 🚀"
            decision_color = "green"
        elif score >= 1:
            decision_text = "AL 🟢"
            decision_color = "lightgreen"
        elif score <= -3:
            decision_text = "GÜÇLÜ SAT 🛑"
            decision_color = "red"
        elif score <= -1:
            decision_text = "SAT 🔴"
            decision_color = "orange"
        else:
            decision_text = "NÖTR / BEKLE ⚪"
            decision_color = "gray"

        st.markdown(f'<div class="ai-decision" style="background-color:{decision_color};">{decision_text}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.subheader("Teknik İndikatörler")
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
        fig_rsi.update_layout(template='plotly_dark', title='RSI', height=250)
        st.plotly_chart(fig_rsi, use_container_width=True)
        
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')))
        fig_macd.add_trace(go.Scatter(x=df.index, y=df['Signal'], name='Sinyal', line=dict(color='orange')))
        fig_macd.update_layout(template='plotly_dark', title='MACD', height=250)
        st.plotly_chart(fig_macd, use_container_width=True)

        fig_cci = go.Figure()
        fig_cci.add_trace(go.Scatter(x=df.index, y=df['CCI'], name='CCI', line=dict(color='cyan')))
        fig_cci.add_hline(y=100, line_dash="dash", line_color="red")
        fig_cci.add_hline(y=-100, line_dash="dash", line_color="green")
        fig_cci.update_layout(template='plotly_dark', title='CCI', height=250)
        st.plotly_chart(fig_cci, use_container_width=True)

    with tab3:
        st.subheader("Monte Carlo Simülasyonu (30 Periyot)")
        days = 30
        simulations = 50
        last_close = df['Close'].iloc[-1]
        if isinstance(last_close, pd.Series): last_close = last_close.iloc[0]
        returns = df['Close'].pct_change().dropna()
        daily_vol = returns.std()
        simulation_df = pd.DataFrame()
        for i in range(simulations):
            price_series = [last_close]
            for _ in range(days):
                price = price_series[-1] * (1 + np.random.normal(0, daily_vol))
                price_series.append(price)
            simulation_df[f'Sim_{i}'] = price_series
        fig_mc = go.Figure()
        for col in simulation_df.columns:
            fig_mc.add_trace(go.Scatter(y=simulation_df[col], mode='lines', 
                                    line=dict(color='#3fb1ce', width=1), opacity=0.2, showlegend=False))
        mean_path = simulation_df.mean(axis=1)
        fig_mc.add_trace(go.Scatter(y=mean_path, mode='lines', name='Ortalama Senaryo', 
                                line=dict(color='white', width=4)))
        fig_mc.update_layout(template='plotly_dark', title='Simülasyon', xaxis_title='Süre', yaxis_title='Fiyat')
        st.plotly_chart(fig_mc, use_container_width=True)
        best_case = simulation_df.iloc[-1].quantile(0.95)
        worst_case = simulation_df.iloc[-1].quantile(0.05)
        avg_case = mean_path.iloc[-1]
        m1, m2, m3 = st.columns(3)
        m1.metric("En İyi Senaryo (95%)", f"{best_case:.2f}")
        m2.metric("Ortalama Tahmin", f"{avg_case:.2f}")
        m3.metric("En Kötü Senaryo (5%)", f"{worst_case:.2f}")
else:
    st.info("Veri yükleniyor veya bu sembol için seçilen periyotta veri yok.")

# --- TAB 4: MARKET SCANNER ---
with tab4:
    st.subheader("🔥 Günün Piyasa Trendleri")
    st.markdown("Bu modül, hisse listesindeki tüm sembolleri tarayarak **son kapanışa göre** en çok kazandıran ve kaybettirenleri listeler.")
    
    if st.button("🚀 PİYASAYI TARA (Başlat)"):
        with st.spinner("Piyasa verileri taranıyor... Bu işlem 10-15 saniye sürebilir."):
            market_df = get_market_trends()

        if not market_df.empty:
            # 3 Kategoriye Ayır
            top_gainers = market_df.sort_values(by="Change %", ascending=False).head(10)
            top_losers = market_df.sort_values(by="Change %", ascending=True).head(10)
            top_volume = market_df.sort_values(by="Volume", ascending=False).head(10)
            
            # Kolonları Formatla
            def format_df(d):
                d = d.copy()
                d['Price'] = d['Price'].map('{:.2f}'.format)
                d['Change %'] = d['Change %'].map('{:.2f}%'.format)
                d['Volume'] = d['Volume'].map('{:,.0f}'.format)
                return d
            
            col_gain, col_loss, col_vol = st.columns(3)
            
            with col_gain:
                st.success("🚀 En Çok Yükselenler")
                st.dataframe(format_df(top_gainers), hide_index=True, use_container_width=True)
                
            with col_loss:
                st.error("🔻 En Çok Düşenler")
                st.dataframe(format_df(top_losers), hide_index=True, use_container_width=True)
                
            with col_vol:
                st.info("📊 Hacim Liderleri")
                st.dataframe(format_df(top_volume), hide_index=True, use_container_width=True)
        else:
            st.warning("Veri alınamadı veya piyasa kapalı olabilir. Lütfen daha sonra tekrar deneyin.")
