import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. Konfigürasyon ve Tema
st.set_page_config(page_title="Professional Finance Dashboard", layout="wide", page_icon="📈")

# Özel CSS (Bloomberg Terminal Karanlık Tema)
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stSelectbox, .stDateInput {
        color: #fafafa;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #00ff00;
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

# Genişletilmiş Hisse Listesi (BIST 100 + Kripto + Döviz/Emtia)
symbol_list = [
    # BIST 100 Örneklem
    'AEFES.IS', 'AGHOL.IS', 'AHGAZ.IS', 'AKBNK.IS', 'AKCNS.IS', 'AKFGY.IS', 'AKSA.IS', 'AKSEN.IS', 'ALARK.IS',
    'ALBRK.IS', 'ALFAS.IS', 'ARCLK.IS', 'ASELS.IS', 'ASTOR.IS', 'BERA.IS', 'BIMAS.IS', 'BIOEN.IS', 'BRSAN.IS', 'BRYAT.IS',
    'BUCIM.IS', 'CANTE.IS', 'CCOLA.IS', 'CEMTS.IS', 'CIMSA.IS', 'CWENE.IS', 'DOAS.IS', 'DOHOL.IS', 'ECILC.IS',
    'EGEEN.IS', 'EKGYO.IS', 'ENJSA.IS', 'ENKAI.IS', 'EREGL.IS', 'EUPWR.IS', 'EUREN.IS', 'FROTO.IS', 'GARAN.IS',
    'GENIL.IS', 'GESAN.IS', 'GLYHO.IS', 'GSDHO.IS', 'GUBRF.IS', 'GWIND.IS', 'HALKB.IS', 'HEKTS.IS', 'IPEKE.IS',
    'ISCTR.IS', 'ISDMR.IS', 'ISGYO.IS', 'ISMEN.IS', 'IZENR.IS', 'KCAER.IS', 'KCHOL.IS', 'KONTR.IS', 'KONYA.IS',
    'KOZAA.IS', 'KOZAL.IS', 'KRDMD.IS', 'KZBGY.IS', 'MAVI.IS', 'MGROS.IS', 'MIATK.IS', 'ODAS.IS', 'OTKAR.IS',
    'OYAKC.IS', 'PENTA.IS', 'PETKM.IS', 'PGSUS.IS', 'PSGYO.IS', 'QUAGR.IS', 'SAHOL.IS', 'SASA.IS', 'SAYAS.IS',
    'SDTTR.IS', 'SISE.IS', 'SKBNK.IS', 'SMRTG.IS', 'SOKM.IS', 'TAVHL.IS', 'TCELL.IS', 'THYAO.IS', 'TKFEN.IS',
    'TOASO.IS', 'TSKB.IS', 'TTKOM.IS', 'TTRAK.IS', 'TUKAS.IS', 'TUPRS.IS', 'TURSG.IS', 'ULKER.IS', 'VAKBN.IS',
    'VESBE.IS', 'VESTL.IS', 'YEOTK.IS', 'YKBNK.IS', 'YYLGD.IS', 'ZOREN.IS',
    # Kripto
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD', 'DOGE-USD', 'AVAX-USD',
    # Döviz & Emtia
    'USDTRY=X', 'EURTRY=X', 'GBPTRY=X', 'XAUUSD=X', 'XAGUSD=X', 'GC=F', 'CL=F'
]
symbol_list.sort() # Alfabetik sıra

selected_ticker = st.sidebar.selectbox("Hisse/Coin Seçin:", symbol_list, index=symbol_list.index('BTC-USD') if 'BTC-USD' in symbol_list else 0)

start_date = st.sidebar.date_input("Başlangıç Tarihi", datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input("Bitiş Tarihi", datetime.now())

# 3. Veri Çekme Fonksiyonu
@st.cache_data(ttl=15)
def get_data(ticker, start, end):
    try:
        df = yf.download(ticker, start=start, end=end, progress=False)
        
        # MultiIndex Düzeltmesi
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        if df.empty:
            return None
        return df
    except Exception as e:
        return None

# Veriyi Yükle
df = get_data(selected_ticker, start_date, end_date)

if df is None or df.empty:
    st.error(f"⚠️ {selected_ticker} için veri bulunamadı veya sembol hatalı.")
    st.stop()

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

df['RSI'] = calculate_rsi(df)
df['MACD'], df['Signal'] = calculate_macd(df)

# 5. Arayüz Sekmeleri
tab1, tab2, tab3 = st.tabs(["📊 Piyasa Özeti", "📈 Teknik Analiz", "🎲 AI Tahmin (Monte Carlo)"])

with tab1:
    st.subheader(f"{selected_ticker} Piyasa Özeti")
    
    # Metrik Kartları
    last_price = df['Close'].iloc[-1]
    if isinstance(last_price, pd.Series): 
        last_price = last_price.iloc[0]
        
    prev_price = df['Close'].iloc[-2]
    if isinstance(prev_price, pd.Series):
        prev_price = prev_price.iloc[0]
        
    daily_change = ((last_price - prev_price) / prev_price) * 100
    
    col1, col2 = st.columns(2)
    col1.metric("Güncel Fiyat", f"{last_price:.2f}", f"{daily_change:.2f}%")
    
    # Candlestick Grafiği
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name=selected_ticker)])
    
    fig.update_layout(template='plotly_dark', title=f'{selected_ticker} Fiyat Hareketleri', height=600)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Teknik İndikatörler")
    
    # RSI Grafiği
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
    fig_rsi.update_layout(template='plotly_dark', title='RSI (Göreceli Güç Endeksi)', height=300)
    st.plotly_chart(fig_rsi, use_container_width=True)
    
    # MACD Grafiği
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')))
    fig_macd.add_trace(go.Scatter(x=df.index, y=df['Signal'], name='Sinyal', line=dict(color='orange')))
    fig_macd.update_layout(template='plotly_dark', title='MACD', height=300)
    st.plotly_chart(fig_macd, use_container_width=True)
    
    # Analiz Kutusu
    current_rsi = df['RSI'].iloc[-1]
    if isinstance(current_rsi, pd.Series):
        current_rsi = current_rsi.iloc[0]
        
    analysis_text = ""
    if current_rsi < 30:
        analysis_text = "🟢 **AL Sinyali:** RSI aşırı satım bölgesinde (<30). Fiyatın yükselme ihtimali var."
        box_color = "success"
    elif current_rsi > 70:
        analysis_text = "🔴 **SAT Sinyali:** RSI aşırı alım bölgesinde (>70). Fiyatın düşme ihtimali var."
        box_color = "error"
    else:
        analysis_text = "⚪ **Nötr:** RSI güvenli bölgede. Trend takibi yapılmalı."
        box_color = "info"
        
    if box_color == "success":
        st.success(analysis_text)
    elif box_color == "error":
        st.error(analysis_text)
    else:
        st.info(analysis_text)

with tab3:
    st.subheader("Monte Carlo Simülasyonu (30 Gün)")
    
    # Simülasyon Parametreleri
    days = 30
    simulations = 50
    
    # Get last close properly
    last_close = df['Close'].iloc[-1]
    if isinstance(last_close, pd.Series):
        last_close = last_close.iloc[0]

    # Calculate returns and volatility
    returns = df['Close'].pct_change().dropna()
    daily_vol = returns.std()
    if isinstance(daily_vol, pd.Series):
        daily_vol = daily_vol.iloc[0]
        
    # Simulation
    simulation_df = pd.DataFrame()
    
    for i in range(simulations):
        price_series = [last_close]
        for _ in range(days):
            price = price_series[-1] * (1 + np.random.normal(0, daily_vol))
            price_series.append(price)
        simulation_df[f'Sim_{i}'] = price_series
        
    # Plotting
    fig_mc = go.Figure()
    
    # Tüm senaryolar (Şeffaf)
    for col in simulation_df.columns:
        fig_mc.add_trace(go.Scatter(y=simulation_df[col], mode='lines', 
                                  line=dict(color='#3fb1ce', width=1), opacity=0.2, showlegend=False))
        
    # Ortalama Senaryo (Kalın)
    mean_path = simulation_df.mean(axis=1)
    fig_mc.add_trace(go.Scatter(y=mean_path, mode='lines', name='Ortalama Senaryo', 
                              line=dict(color='white', width=4)))
    
    fig_mc.update_layout(template='plotly_dark', title='Gelecek 30 Gün Fiyat Tahmini', 
                       xaxis_title='Gün', yaxis_title='Fiyat')
    st.plotly_chart(fig_mc, use_container_width=True)
    
    # İstatistik Kartları
    best_case = simulation_df.iloc[-1].quantile(0.95)
    worst_case = simulation_df.iloc[-1].quantile(0.05)
    avg_case = mean_path.iloc[-1]
    
    m1, m2, m3 = st.columns(3)
    m1.metric("En İyi Senaryo (95%)", f"{best_case:.2f}")
    m2.metric("Ortalama Tahmin", f"{avg_case:.2f}")
    m3.metric("En Kötü Senaryo (5%)", f"{worst_case:.2f}")
