import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(
    page_title="Profesyonel Finans Takip",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background-color: #0e1117;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #f0f2f6;
    }
    
    /* Card Styling */
    .stMetric {
        background-color: #1f2329;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #333;
    }
    
    /* Warning Box */
    .warning-box {
        padding: 10px;
        background-color: #3b2c1e;
        color: #ffaa00;
        border-radius: 5px;
        border-left: 5px solid #ffaa00;
        margin-bottom: 20px;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        background-color: #262730;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Application Title
st.title("💰 Profesyonel Finans ve Borsa Takip")

# Warning for Borsa Istanbul
st.markdown('<div class="warning-box">⚠️ <strong>Önemli Not:</strong> Borsa İstanbul hisseleri için sembolün sonuna <code>.IS</code> eklemeyi unutmayın (Örn: <code>THYAO.IS</code>, <code>GARAN.IS</code>).</div>', unsafe_allow_html=True)

# Helper Function for Analysis
def analyze_data(df):
    analysis_points = []
    sentiment_score = 0
    
    try:
        latest = df.iloc[-1]
        
        # 1. Trend Analysis (SMA 200)
        if 'SMA200' in df.columns and not pd.isna(latest['SMA200']):
            if latest['Close'] > latest['SMA200']:
                analysis_points.append(f"✅ **Ana Trend:** Fiyat 200 günlük ortalamanın üzerinde. Uzun vadeli trend **YUKARI** yönlüdür (Boğa Piyasası).")
                sentiment_score += 1
            else:
                analysis_points.append(f"🔻 **Ana Trend:** Fiyat 200 günlük ortalamanın altında. Uzun vadeli trend **AŞAĞI** yönlüdür (Ayı Piyasası).")
                sentiment_score -= 1
        else:
            analysis_points.append("ℹ️ **Ana Trend:** Yeterli veri olmadığı için SMA200 hesaplanamadı.")
            
        # 2. RSI Signal
        if 'RSI' in df.columns and not pd.isna(latest['RSI']):
            if latest['RSI'] > 70:
                analysis_points.append(f"⚠️ **RSI:** Değer {latest['RSI']:.2f}. Hisse **aşırı alınmış** bölgede (>70). Kâr satışı gelebilir, dikkatli olun.")
                sentiment_score -= 0.5
            elif latest['RSI'] < 30:
                analysis_points.append(f"🟢 **RSI:** Değer {latest['RSI']:.2f}. Hisse **aşırı satılmış** bölgede (<30). Tepki yükselişi beklenebilir.")
                sentiment_score += 0.5
            else:
                analysis_points.append(f"⚪ **RSI:** Değer {latest['RSI']:.2f}. Nötr bölgede seyrediyor.")
        
        # 3. Momentum (MACD)
        if 'MACD' in df.columns and 'Signal' in df.columns and not pd.isna(latest['MACD']) and not pd.isna(latest['Signal']):
            if latest['MACD'] > latest['Signal']:
                analysis_points.append(f"🚀 **Momentum:** MACD çizgisi Sinyal çizgisinin üzerinde. **Pozitif** momentum sinyali veriyor.")
                sentiment_score += 0.5
            else:
                analysis_points.append(f"📉 **Momentum:** MACD çizgisi Sinyal çizgisinin altında. **Negatif** momentum sinyali veriyor.")
                sentiment_score -= 0.5
                
        return "\n\n".join(analysis_points), sentiment_score

    except Exception as e:
        return f"Analiz hatası: {str(e)}", 0

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Piyasa Analizi", "💼 Portföyüm", "💸 Gelir/Gider", "🤖 AI Tahmin (Beta)"])

# ==================== TAB 1: PIYASA ANALIZI ====================
with tab1:
    # 1. Hisse Seçimi (En Üst)
    st.subheader("Hisse Senedi Analizi")
    
    # Stock Selection Menu
    stocks_list = ['Diğer...', 'THYAO.IS', 'GARAN.IS', 'ASELS.IS', 'AKBNK.IS', 'EREGL.IS', 'AAPL', 'TSLA', 'BTC-USD']
    col_sel, col_trash = st.columns([1, 4]) # Make selectbox not full width for aesthetics
    with col_sel:
        selected_stock = st.selectbox("Hisse Seçin", stocks_list, index=1)
    
    if selected_stock == 'Diğer...':
        ticker_input = st.text_input("Sembol Girin", value="THYAO.IS")
    else:
        ticker_input = selected_stock

    if ticker_input:
        try:
            ticker = yf.Ticker(ticker_input)
            info = ticker.info
            
            # 2. Şirket Özet Kartları (4 Kolon)
            st.markdown("---")
            
            def format_value(val):
                if val is None: return "N/A"
                if val > 1_000_000_000_000: return f"{val/1_000_000_000_000:.2f}T"
                if val > 1_000_000_000: return f"{val/1_000_000_000:.2f}B"
                if val > 1_000_000: return f"{val/1_000_000:.2f}M"
                return f"{val:,.2f}"

            # Data Extraction
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            previous_close = info.get('previousClose', info.get('regularMarketPreviousClose', current_price))
            currency = info.get('currency', '?')
            
            # Calculate Delta
            if current_price and previous_close:
                change = current_price - previous_close
                change_pct = (change / previous_close) * 100
                delta_str = f"{change:.2f} ({change_pct:.2f}%)"
            else:
                delta_str = None

            # Render Columns
            m1, m2, m3, m4 = st.columns(4)
            
            with m1:
                st.metric("Son Fiyat", f"{current_price} {currency}", delta=delta_str)
            with m2:
                st.metric("Piyasa Değeri", format_value(info.get('marketCap')))
            with m3:
                st.metric("F/K Oranı (PE)", info.get('trailingPE', 'N/A'))
            with m4:
                st.metric("Sektör", info.get('sector', 'Bilinmiyor'))
            
            # 3. Şirket Hakkında (Expander)
            with st.expander("📝 Şirket Hakkında (Özet)"):
                st.write(info.get('longBusinessSummary', 'Açıklama bulunamadı.'))
            
            st.markdown("---")

            # 4. Grafik Alanı
            # Time Interval Selection (Put in a clearer spot or integrated?)
            # Prompt said "Update Market Analysis tab... add cards... before chart".
            # I will put interval selector above chart as before.
            
            st.subheader(f"{ticker_input.upper()} Teknik Grafik")
            
            interval_options = ['1 Gün', '5 Dakika', '1 Saat', '1 Hafta', '1 Ay', '1 Yıl', '5 Yıl']
            selected_interval = st.selectbox("Grafik Aralığı", interval_options, index=0)

            # Logic for Interval and Period
            yf_params = {'interval': '1d', 'period': '1y'}
            
            if selected_interval == '5 Dakika':
                yf_params = {'interval': '5m', 'period': '1mo'}
            elif selected_interval == '1 Saat':
                yf_params = {'interval': '60m', 'period': '3mo'}
            elif selected_interval == '1 Gün':
                yf_params = {'interval': '1d', 'period': '1y'}
            elif selected_interval == '1 Hafta':
                yf_params = {'interval': '1wk', 'period': '5y'}
            elif selected_interval == '1 Ay':
                yf_params = {'interval': '1mo', 'period': 'max'}
            elif selected_interval == '1 Yıl':
                yf_params = {'interval': '1mo', 'period': 'max'}
            elif selected_interval == '5 Yıl':
                yf_params = {'interval': '1mo', 'period': 'max'}

            # Fetch Data
            df = ticker.history(interval=yf_params['interval'], period=yf_params['period'])
            
            if not df.empty:
                # Custom Filtering
                if selected_interval == '1 Yıl':
                    df = df.tail(12)
                elif selected_interval == '5 Yıl':
                    df = df.tail(60)

                from plotly.subplots import make_subplots

                # Placeholders for layout
                chart_placeholder = st.empty()
                
                # Indicator Options
                st.write("Göstergeler:")
                col_opt1, col_opt2, col_opt3, col_opt4 = st.columns(4)
                with col_opt1:
                    show_bollinger = st.checkbox("Bollinger", value=True)
                with col_opt2:
                    show_rsi = st.checkbox("RSI")
                with col_opt3:
                    show_macd = st.checkbox("MACD")
                with col_opt4:
                    show_cci = st.checkbox("CCI")
                
                # --- CALCULATIONS ---
                # 1. SMAs (Unconditional)
                df['SMA50'] = df['Close'].rolling(window=50).mean()
                df['SMA200'] = df['Close'].rolling(window=200).mean()
                
                # 2. Bollinger Bands (Conditional if only used for plot, but keeping conditional is fine if not used in report)
                if show_bollinger:
                    df['SMA20'] = df['Close'].rolling(window=20).mean()
                    df['BB_Upper'] = df['SMA20'] + (df['Close'].rolling(window=20).std() * 2)
                    df['BB_Lower'] = df['SMA20'] - (df['Close'].rolling(window=20).std() * 2)
                
                # 3. RSI (Unconditional for Report)
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).ewm(span=14, adjust=False).mean()
                loss = (-delta.where(delta < 0, 0)).ewm(span=14, adjust=False).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))

                # 4. MACD (Unconditional for Report)
                exp12 = df['Close'].ewm(span=12, adjust=False).mean()
                exp26 = df['Close'].ewm(span=26, adjust=False).mean()
                df['MACD'] = exp12 - exp26
                df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
                df['MACD_Hist'] = df['MACD'] - df['Signal']

                # 5. CCI (Conditional)
                if show_cci:
                    tp = (df['High'] + df['Low'] + df['Close']) / 3
                    sma_tp = tp.rolling(window=20).mean()
                    
                    # Mean Deviation calculation
                    def calculate_md(x):
                        return (x - x.mean()).abs().mean()
                    
                    mad = tp.rolling(window=20).apply(calculate_md)
                    mad = mad.replace(0, 0.001)
                    df['CCI'] = (tp - sma_tp) / (0.015 * mad)

                # --- PLOTTING LOGIC ---
                # Determine subplots
                rows_config = [{"type": "price", "height": 0.6}] # Main chart always first
                if show_rsi: rows_config.append({"type": "rsi", "height": 0.15})
                if show_macd: rows_config.append({"type": "macd", "height": 0.15})
                if show_cci: rows_config.append({"type": "cci", "height": 0.15})
                
                num_rows = len(rows_config)
                row_heights = [r["height"] for r in rows_config]
                subplot_titles = [f"{ticker_input.upper()} Fiyat"] + [r["type"].upper() for r in rows_config[1:]]

                fig = make_subplots(
                    rows=num_rows, cols=1, 
                    shared_xaxes=True, 
                    vertical_spacing=0.05,
                    row_heights=row_heights,
                    subplot_titles=subplot_titles
                )

                # Add Traces
                current_row = 1
                
                # 1. Main Price Chart
                fig.add_trace(go.Candlestick(
                    x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    name='Fiyat'
                ), row=current_row, col=1)
                
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='orange', width=1), name='SMA 50'), row=current_row, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='blue', width=1), name='SMA 200'), row=current_row, col=1)
                
                if show_bollinger and 'BB_Upper' in df.columns:
                    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='gray', width=1, dash='dash'), name='BB Üst'), row=current_row, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='gray', width=1, dash='dash'), name='BB Alt', fill='tonexty', fillcolor='rgba(200, 200, 200, 0.1)'), row=current_row, col=1)
                
                current_row += 1

                # 2. Indicators loops
                for config in rows_config[1:]:
                    plot_type = config["type"]
                    
                    if plot_type == "rsi":
                        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=1.5), name='RSI'), row=current_row, col=1)
                        fig.add_hline(y=70, line_dash="dash", line_color="red", row=current_row, col=1)
                        fig.add_hline(y=30, line_dash="dash", line_color="green", row=current_row, col=1)
                        fig.update_yaxes(range=[0, 100], row=current_row, col=1)
                    
                    elif plot_type == "macd":
                        # Histogram
                        colors = ['green' if v >= 0 else 'red' for v in df['MACD_Hist']]
                        fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], marker_color=colors, name='MACD Hist'), row=current_row, col=1)
                        # Lines
                        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='#2962FF', width=1.5), name='MACD'), row=current_row, col=1)
                        fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], line=dict(color='#FF6D00', width=1.5), name='Sinyal'), row=current_row, col=1)
                    
                    elif plot_type == "cci":
                        fig.add_trace(go.Scatter(x=df.index, y=df['CCI'], line=dict(color='cyan', width=1.5), name='CCI'), row=current_row, col=1)
                        fig.add_hline(y=100, line_dash="dash", line_color="red", row=current_row, col=1)
                        fig.add_hline(y=-100, line_dash="dash", line_color="green", row=current_row, col=1)
                    
                    current_row += 1

                # Layout Updates
                fig.update_layout(
                    title=f"{ticker_input.upper()} - {selected_interval} Detaylı Analiz",
                    xaxis_rangeslider_visible=False,
                    template="plotly_dark",
                    height=600 + (len(rows_config)-1)*150, # Dynamic height
                    margin=dict(l=20, r=20, t=60, b=20),
                    legend=dict(x=0, y=1, orientation="h")
                )
                
                chart_placeholder.plotly_chart(fig, use_container_width=True)
                
                # --- AI SMART ANALYSIS ASSISTANT ---
                st.subheader(f"🤖 {ticker_input.upper()} Akıllı Analiz Asistanı")
                
                # Call Helper Function
                final_report, sentiment_score = analyze_data(df)
                
                if final_report and final_report.strip():
                    if sentiment_score >= 1:
                        st.success(final_report)
                    elif sentiment_score <= -1:
                        st.error(final_report)
                    else:
                        st.info(final_report)
                else:
                    st.info("Veri bekleniyor... Yeterli veri oluştuğunda analiz burada görünecektir.")
            else:
                st.warning("Bu sembol için veri bulunamadı.")
                
        except Exception as e:
            st.error(f"Grafik oluşturulurken hata: {e}")

# ==================== TAB 2: PORTFÖYÜM ====================
with tab2:
    st.subheader("Portföy Yönetimi")
    
    # Session State for Portfolio
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = pd.DataFrame(columns=['Sembol', 'Adet', 'Maliyet'])

    # Input Form
    with st.form("portfolio_form"):
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            p_symbol = st.text_input("Hisse Sembolü (Örn: ASELS.IS)").upper()
        with col_p2:
            p_qty = st.number_input("Adet", min_value=1, value=10)
        with col_p3:
            p_cost = st.number_input("Birim Maliyet", min_value=0.0, value=0.0, format="%.2f")
            
        submitted = st.form_submit_button("Ekle")
        
        if submitted and p_symbol:
            new_row = pd.DataFrame({'Sembol': [p_symbol], 'Adet': [p_qty], 'Maliyet': [p_cost]})
            st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_row], ignore_index=True)
            st.success(f"{p_symbol} portföye eklendi!")

    # Display and Calculate
    if not st.session_state.portfolio.empty:
        df_portfolio = st.session_state.portfolio.copy()
        
        # Calculate Current Values (Mock fetching to keep it fast, or real fetch)
        current_prices = []
        total_values = []
        profits = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, row in df_portfolio.iterrows():
            sym = row['Sembol']
            # status_text.text(f"{sym} verisi çekiliyor...")
            try:
                # Optimized: We could use batch fetching, but for simplicity loop is okay for small portfolio
                t = yf.Ticker(sym)
                info = t.info
                price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            except:
                price = 0
            
            current_prices.append(price)
            val = price * row['Adet']
            total_values.append(val)
            profits.append(val - (row['Maliyet'] * row['Adet']))
            progress_bar.progress((i + 1) / len(df_portfolio))
            
        progress_bar.empty()
        status_text.empty()
        
        df_portfolio['Güncel Fiyat'] = current_prices
        df_portfolio['Toplam Değer'] = total_values
        df_portfolio['Kar/Zarar'] = profits
        
        # Summary Metrics
        total_portfolio_value = df_portfolio['Toplam Değer'].sum()
        total_cost = (df_portfolio['Maliyet'] * df_portfolio['Adet']).sum()
        total_profit = total_portfolio_value - total_cost
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Toplam Portföy Değeri", f"{total_portfolio_value:,.2f}")
        m2.metric("Toplam Maliyet", f"{total_cost:,.2f}")
        m3.metric("Toplam Kar/Zarar", f"{total_profit:,.2f}", delta=f"{total_profit:,.2f}")
        
        # Data Table
        st.dataframe(df_portfolio.style.format({
            "Maliyet": "{:.2f}",
            "Güncel Fiyat": "{:.2f}", 
            "Toplam Değer": "{:.2f}",
            "Kar/Zarar": "{:.2f}"
        }), use_container_width=True)
        
        # Pie Chart
        st.subheader("Portföy Dağılımı")
        if total_portfolio_value > 0:
            fig_pie = px.pie(df_portfolio, values='Toplam Değer', names='Sembol', 
                             title='Varlık Dağılımı (Mevcut Değere Göre)',
                             hole=0.4,
                             color_discrete_sequence=px.colors.sequential.RdBu)
            fig_pie.update_layout(template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        # Delete Button (Simple implementation: Clear all)
        if st.button("Portföyü Temizle"):
            st.session_state.portfolio = pd.DataFrame(columns=['Sembol', 'Adet', 'Maliyet'])
            st.rerun()

# ==================== TAB 3: GELIR/GIDER ====================
with tab3:
    st.subheader("Bütçe Takibi")
    
    if 'budget' not in st.session_state:
        st.session_state.budget = pd.DataFrame(columns=['Tarih', 'Türü', 'Açıklama', 'Tutar'])
        
    with st.expander("Yeni İşlem Ekle", expanded=True):
        with st.form("budget_form"):
            b_date = st.date_input("Tarih", datetime.now())
            b_type = st.selectbox("Türü", ["Gelir", "Gider"])
            b_desc = st.text_input("Açıklama")
            b_amount = st.number_input("Tutar", min_value=0.0, format="%.2f")
            
            b_submit = st.form_submit_button("Kaydet")
            
            if b_submit and b_amount > 0:
                new_b_row = pd.DataFrame({
                    'Tarih': [b_date],
                    'Türü': [b_type],
                    'Açıklama': [b_desc],
                    'Tutar': [b_amount]
                })
                st.session_state.budget = pd.concat([st.session_state.budget, new_b_row], ignore_index=True)
                st.success("İşlem kaydedildi.")
                
    # Summary
    if not st.session_state.budget.empty:
        df_budget = st.session_state.budget
        income = df_budget[df_budget['Türü'] == 'Gelir']['Tutar'].sum()
        expense = df_budget[df_budget['Türü'] == 'Gider']['Tutar'].sum()
        balance = income - expense
        
        bc1, bc2, bc3 = st.columns(3)
        bc1.metric("Toplam Gelir", f"{income:,.2f}", delta_color="normal")
        bc2.metric("Toplam Gider", f"{expense:,.2f}", delta_color="inverse")
        bc3.metric("Net Durum", f"{balance:,.2f}", delta=f"{balance:,.2f}")
        
        st.dataframe(df_budget.sort_values(by='Tarih', ascending=False), use_container_width=True)
    else:
        st.info("Henüz bir işlem eklenmedi.")
# ==================== TAB 4: AI TAHMIN (BETA) ====================
with tab4:
    st.subheader("🤖 Monte Carlo Simülasyonu (Beta)")
    st.info("Bu modül, hissenin geçmiş volatilite ve getiri verilerine dayanarak 50 farklı gelecek senaryosu oluşturur. Olasılık dağılımını analiz etmenizi sağlar.")
    
    # Input for Tab 4
    col_ai1, col_ai2 = st.columns([1, 4])
    with col_ai1:
        ai_ticker = st.text_input("Hisse Sembolü", value="THYAO.IS", key="ai_ticker_mc")
    
    if st.button("Simülasyonu Başlat", key="ai_start_mc"):
        try:
            with st.spinner("Monte Carlo simülasyonu çalıştırılıyor (50 Senaryo)..."):
                # 1. Fetch Data
                import numpy as np
                tkr = yf.Ticker(ai_ticker)
                # Fetch 1 year for volatility calculation
                end_d = datetime.now()
                start_d = end_d - timedelta(days=365)
                df_mc = tkr.history(start=start_d, end=end_d)
                
                if not df_mc.empty and len(df_mc) > 30:
                    # 2. Prepare Statistics
                    # Log returns are additive and better for geometric brownian motion assumption
                    log_returns = np.log(1 + df_mc['Close'].pct_change())
                    
                    u = log_returns.mean()
                    var = log_returns.var()
                    
                    # Drift and Volatility
                    # Drift = u - (0.5 * var)
                    drift = u - (0.5 * var)
                    stdev = log_returns.std()
                    
                    # 3. Simulation Parameters
                    t_intervals = 30
                    iterations = 50
                    
                    # Initialize simulation array
                    daily_returns = np.exp(drift + stdev * np.random.normal(0, 1, (t_intervals, iterations)))
                    
                    # Starting price
                    last_price = df_mc['Close'].iloc[-1]
                    price_paths = np.zeros_like(daily_returns)
                    price_paths[0] = last_price
                    
                    for t in range(1, t_intervals):
                        price_paths[t] = price_paths[t-1] * daily_returns[t]
                        
                    # 4. Dates for X-axis
                    last_date = df_mc.index[-1].replace(tzinfo=None)
                    future_dates = [last_date + timedelta(days=i) for i in range(1, t_intervals + 1)]
                    
                    # 5. Calculate Statistics (Mean, 5%, 95%)
                    # price_paths shape is (days, iterations)
                    path_mean = np.mean(price_paths, axis=1)
                    path_max_95 = np.percentile(price_paths, 95, axis=1)
                    path_min_5 = np.percentile(price_paths, 5, axis=1)
                    
                    # Final Day Stats
                    final_mean = path_mean[-1]
                    final_best = path_max_95[-1]
                    final_worst = path_min_5[-1]
                    
                    # 6. Visualization
                    fig_mc = go.Figure()
                    
                    # Draw all 50 random paths (faint)
                    for i in range(iterations):
                        fig_mc.add_trace(go.Scatter(
                            x=future_dates, y=price_paths[:, i],
                            mode='lines',
                            line=dict(color='rgba(0, 176, 255, 0.15)', width=1),
                            showlegend=False,
                            hoverinfo='skip'
                        ))
                    
                    # Confidence Interval (Shaded Area)
                    # Upper Bound (Invisible line)
                    fig_mc.add_trace(go.Scatter(
                        x=future_dates, y=path_max_95,
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False,
                        name='En İyi Senaryo (%95)'
                    ))
                    # Lower Bound (Filled to Upper)
                    fig_mc.add_trace(go.Scatter(
                        x=future_dates, y=path_min_5,
                        mode='lines',
                        line=dict(width=0),
                        fill='tonexty',
                        fillcolor='rgba(255, 255, 255, 0.1)',
                        name='Güven Aralığı (%5-%95)',
                        showlegend=True
                    ))
                    
                    # Mean Path (Bold Red)
                    fig_mc.add_trace(go.Scatter(
                        x=future_dates, y=path_mean,
                        mode='lines',
                        name='Ortalama Senaryo',
                        line=dict(color='red', width=3)
                    ))
                    
                    fig_mc.update_layout(
                        title=f"{ai_ticker.upper()} - Monte Carlo Simülasyonu (30 Günlük Projeksiyon)",
                        xaxis_title="Tarih",
                        yaxis_title="Fiyat",
                        template="plotly_dark",
                        height=600,
                        hovermode="x unified"
                    )
                    
                    st.plotly_chart(fig_mc, use_container_width=True)
                    
                    # 7. Statistics Cards
                    st.markdown("### 📊 Simülasyon Sonuçları")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Senaryo Ortalaması", f"{final_mean:.2f}", delta=f"{(final_mean-last_price):.2f}")
                    c2.metric("En İyi Senaryo (%95)", f"{final_best:.2f}", delta_color="normal")
                    c3.metric("En Kötü Senaryo (%5)", f"{final_worst:.2f}", delta_color="inverse")
                    
                    st.markdown("### ⚠️ Yasal Uyarı")
                    st.warning("**Sorumluluk Reddi:** Bu simülasyon tamamen matematiksel olasılık hesaplarına dayanmaktadır (Geometrik Brownian Hareketi). Piyasadaki haber akışlarını, krizleri veya manipülasyonları ÖNGÖREMEZ. Sadece 'geçmiş volatilite devam ederse' olası aralığı gösterir. **Yatırım tavsiyesi değildir.**")
                    
                else:
                    st.error("Yeterli veri alınamadı. Hissenin en az 1 yıllık geçmiş verisi olmalıdır.")
        
        except Exception as e:
            st.error(f"Simülasyon hatası: {e}")
