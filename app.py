import os
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template_string, request
import pandas as pd
import yfinance as yf

app = Flask(__name__)

PAGE = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>StockVision AI — NSE / BSE Market Lab</title>
<script src="https://unpkg.com/lightweight-charts@4.2.2/dist/lightweight-charts.standalone.production.js"></script>
<style>
:root{color-scheme:dark;--bg:#080d16;--panel:#101827;--panel2:#0c1421;--line:#1e2a3d;--muted:#8290a7;--text:#e8eef8;--green:#18c78a;--red:#f05e72;--blue:#5b9cff;--amber:#e9b65b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px Inter,ui-sans-serif,system-ui,Segoe UI,Arial}
header{height:66px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 24px;background:#0b1220;position:sticky;top:0;z-index:5}
.brand{display:flex;gap:11px;align-items:center;font-size:17px;font-weight:800;letter-spacing:.2px}.logo{width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,#1acb91,#397dff);display:grid;place-items:center;color:#06111b;font-weight:900}
.pill{border:1px solid var(--line);border-radius:30px;padding:7px 11px;color:var(--muted);font-size:12px}.status-dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--amber);margin-right:6px}
main{max-width:1600px;margin:auto;padding:22px;display:grid;gap:16px}.toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center}.search{display:flex;gap:8px;flex:1;min-width:260px}.search input{flex:1}
input,select,button{font:inherit;color:var(--text);background:#111c2d;border:1px solid #26354c;border-radius:9px;padding:11px 13px;min-height:42px}input:focus,select:focus{outline:1px solid var(--blue)}button{cursor:pointer;background:#172943}button.primary{background:#2469d8;border-color:#367ce9;font-weight:700}button:hover{filter:brightness(1.15)}.timeframes{display:flex;gap:5px;flex-wrap:wrap}.timeframes button{padding:8px 11px;min-height:36px;font-size:12px}.timeframes button.active{background:#1d477d;border-color:#4488e8;color:#fff}
.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.metric,.panel{background:var(--panel);border:1px solid var(--line);border-radius:13px}.metric{padding:15px 17px}.metric small{color:var(--muted);display:block;margin-bottom:8px}.metric strong{font-size:21px;letter-spacing:.2px}.positive{color:var(--green)}.negative{color:var(--red)}.muted{color:var(--muted)}
.layout{display:grid;grid-template-columns:minmax(0,1.8fr) minmax(300px,.85fr);gap:14px}.panel{padding:16px;min-width:0}.panel-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:13px}.panel-head h2{font-size:14px;margin:0}.chart-wrap{height:430px;position:relative}#chart{height:100%;width:100%}#tvFallback{display:none;position:absolute;inset:0;background:#101827}#tvFallback iframe{width:100%;height:100%;border:0;border-radius:8px}.subchart{height:90px;margin-top:4px}.side{display:grid;gap:14px;align-content:start}.signal{border-radius:10px;padding:13px;background:#111f30;border:1px solid var(--line)}.signal b{font-size:18px}.signal p{color:var(--muted);line-height:1.55;margin:8px 0 0}.tag{font-size:11px;padding:5px 8px;border-radius:20px;background:#172a41;color:#9fc4ff}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}.item{padding:10px 0;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:12px}.item:last-child{border:0}.item span:first-child{color:var(--muted)}.list{max-height:230px;overflow:auto}.empty{color:var(--muted);padding:16px 0}.notice{color:#b9a16f;font-size:12px;line-height:1.55;padding:12px 14px;border:1px solid #51442b;background:#211c13;border-radius:10px}
footer{color:var(--muted);font-size:11px;text-align:center;padding:6px 0 20px}
@media(max-width:950px){.layout{grid-template-columns:1fr}.metrics{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){header{padding:0 14px}main{padding:13px}.metrics{grid-template-columns:1fr 1fr}.metric strong{font-size:17px}.chart-wrap{height:330px}.panel{padding:12px}.pill.hide-mobile{display:none}}
.ai-panel{padding:0;overflow:hidden}.ai-head{padding:16px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;gap:10px}.ai-head h2{font-size:15px;margin:0}.ai-chat{padding:16px}.ai-messages{height:260px;overflow:auto;display:flex;flex-direction:column;gap:10px;margin-bottom:12px}.ai-msg{max-width:88%;padding:11px 13px;border-radius:12px;line-height:1.55;white-space:pre-wrap;overflow-wrap:anywhere}.ai-msg.bot{background:#17263a;border:1px solid #263a55;align-self:flex-start}.ai-msg.user{background:#1b4e8c;align-self:flex-end}.ai-compose{display:flex;gap:8px}.ai-compose textarea{flex:1;min-height:48px;max-height:120px;resize:vertical;background:#0b1422;border:1px solid #26354c;border-radius:10px;color:var(--text);padding:12px;font:inherit}.ai-compose button{min-width:88px}.ai-hints{display:flex;gap:7px;flex-wrap:wrap;margin:0 0 11px}.ai-hints button{font-size:11px;min-height:31px;padding:6px 9px;color:#a9c9f6}.ai-foot{font-size:11px;color:var(--muted);margin-top:9px;line-height:1.5}@media(max-width:560px){.ai-compose{flex-direction:column}.ai-compose button{width:100%}}</style></head>
<body>
<header><div class="brand"><div class="logo">SV</div>StockVision <span style="color:#68a7ff">AI</span></div><div class="pill"><span class="status-dot"></span><span id="marketStatus">Data connection pending</span></div></header>
<main>
 <div class="toolbar">
  <div class="search"><input id="symbol" aria-label="NSE or BSE stock symbol" value="RELIANCE" placeholder="Search symbol, e.g. RELIANCE"><select id="exchange" aria-label="Exchange"><option value="NS">NSE</option><option value="BO">BSE</option></select><button class="primary" id="analyze">Analyze</button></div>
  <div class="pill hide-mobile">INDIA · NSE / BSE</div>
 </div>
 <div class="timeframes" id="timeframes"></div>
 <section class="metrics">
  <div class="metric"><small>Last traded close</small><strong id="price">—</strong><div id="change" class="muted">Awaiting data</div></div>
  <div class="metric"><small>Session high / low</small><strong id="highlow">—</strong><div class="muted">Selected interval</div></div>
  <div class="metric"><small>Volume</small><strong id="volume">—</strong><div class="muted">Latest candle</div></div>
  <div class="metric"><small>Detected patterns</small><strong id="patternCount">—</strong><div class="muted">From loaded candles</div></div>
 </section>
 <section class="layout">
  <div class="panel">
   <div class="panel-head"><h2 id="chartTitle">RELIANCE · NSE</h2><span class="tag" id="intervalLabel">1D</span></div>
   <div class="chart-wrap"><div id="chart"></div><div id="tvFallback" aria-label="TradingView live chart"></div></div>
   <div class="subchart" id="volumeChart"></div>
  </div>
  <div class="side">
   <div class="panel"><div class="panel-head"><h2>AI technical summary</h2><span class="tag">Rule-based</span></div>
    <div class="signal"><b id="signal">Waiting for data</b><p id="signalText">Choose an Indian stock and timeframe to calculate a technical snapshot. This is educational information, not investment advice.</p></div>
    <div class="item"><span>RSI (14)</span><b id="rsi">—</b></div><div class="item"><span>Trend / EMA 20</span><b id="trend">—</b></div><div class="item"><span>Volume vs average</span><b id="volRatio">—</b></div>
   </div>
   <div class="panel"><div class="panel-head"><h2>Detected candlestick patterns</h2></div><div class="list" id="candlePatterns"><div class="empty">No analysis yet.</div></div></div>
  </div>
 </section>
 <section class="grid2">
  <div class="panel"><div class="panel-head"><h2>Chart patterns & levels</h2><span class="tag">Auto mapped</span></div><div id="chartPatterns" class="list"><div class="empty">Load a chart to detect structures.</div></div></div>
  <div class="panel"><div class="panel-head"><h2>Support & resistance</h2></div><div id="levels" class="list"><div class="empty">Levels will appear here.</div></div></div>
 </section>
 <section class="panel ai-panel"><div class="ai-head"><h2>Ask StockVision AI</h2><span class="tag">Simple-language assistant</span></div><div class="ai-chat"><div class="ai-messages" id="aiMessages" aria-live="polite"><div class="ai-msg bot">Hi! Ask me anything about the selected stock, charts, indicators, or market terms. I’ll explain it in simple language.</div></div><div class="ai-hints"><button type="button" data-prompt="Explain this stock's current chart in simple words.">Explain this chart</button><button type="button" data-prompt="What does RSI mean, and what is the current RSI telling us?">Explain RSI</button><button type="button" data-prompt="Explain the support and resistance levels.">Support & resistance</button><button type="button" data-prompt="What are the main risks and limitations in this analysis?">Main risks</button></div><div class="ai-compose"><textarea id="aiPrompt" rows="2" placeholder="Ask anything… e.g. What is RSI? Why did this stock fall today?"></textarea><button class="primary" id="aiSend" type="button">Ask AI</button></div><div class="ai-foot">Educational explanations only. Market data may be delayed. This assistant does not give personal buy/sell instructions or guarantee predictions.</div></div></section>
 <div class="notice">Market data is supplied by Yahoo Finance via yfinance and may be delayed, incomplete, rate-limited, or unavailable for some symbols and intervals. Signals are simple technical heuristics for learning only; they are not personalized financial advice, guaranteed predictions, or instructions to trade. No orders are placed.</div>
 <footer>StockVision AI · Independent educational analysis · Verify prices and data with your broker or exchange.</footer>
</main>
<script>
const intervals=['1m','5m','15m','30m','1h','4h','1D','1W','1M'];let interval='1D',candles=[],candleSeries,volSeries,chart,volChart,overlays=[];
const tf=document.getElementById('timeframes');intervals.forEach(t=>{let b=document.createElement('button');b.textContent=t;b.className=t===interval?'active':'';b.onclick=()=>{interval=t;[...tf.children].forEach(x=>x.classList.toggle('active',x.textContent===t));load()};tf.appendChild(b)});
function showTradingViewFallback(sym,exchange){const clean=sym.toUpperCase().replace(/\\.(NS|BO)$/,'');const tvSymbol=(exchange==='BO'?'BSE:':'NSE:')+clean;const tvInterval=({'1m':'1','5m':'5','15m':'15','30m':'30','1h':'60','4h':'240','1D':'D','1W':'W','1M':'M'})[interval]||'D';const host=document.getElementById('tvFallback');const params=new URLSearchParams({symbol:tvSymbol,interval:tvInterval,theme:'dark',style:'1',timezone:'Asia/Kolkata',locale:'en',withdateranges:'1',hide_side_toolbar:'0',allow_symbol_change:'1',details:'1',hotlist:'0',calendar:'0',studies:'Volume@tv-basicstudies'});host.innerHTML='<iframe title="TradingView chart" loading="eager" referrerpolicy="origin" src="https://www.tradingview.com/widgetembed/?'+params.toString()+'"></iframe>';host.style.display='block';document.getElementById('chart').style.visibility='hidden';}
function hideTradingViewFallback(){document.getElementById('tvFallback').style.display='none';document.getElementById('tvFallback').innerHTML='';document.getElementById('chart').style.visibility='visible';}
function fmt(n){return n==null?'—':Number(n).toLocaleString('en-IN',{maximumFractionDigits:2})}
function initCharts(){if(chart)return;const opts={layout:{background:{color:'#101827'},textColor:'#91a0b8'},grid:{vertLines:{color:'#1c293b'},horzLines:{color:'#1c293b'}},rightPriceScale:{borderColor:'#29364a'},timeScale:{borderColor:'#29364a',timeVisible:true},crosshair:{mode:1},width:document.getElementById('chart').clientWidth,height:430};chart=LightweightCharts.createChart(document.getElementById('chart'),opts);candleSeries=chart.addCandlestickSeries({upColor:'#18c78a',downColor:'#f05e72',borderUpColor:'#18c78a',borderDownColor:'#f05e72',wickUpColor:'#18c78a',wickDownColor:'#f05e72'});volChart=LightweightCharts.createChart(document.getElementById('volumeChart'),{...opts,height:90,timeScale:{visible:false}});volSeries=volChart.addHistogramSeries({priceFormat:{type:'volume'},priceScaleId:'',scaleMargins:{top:.1,bottom:0}});new ResizeObserver(()=>{chart.applyOptions({width:document.getElementById('chart').clientWidth});volChart.applyOptions({width:document.getElementById('volumeChart').clientWidth})}).observe(document.getElementById('chart'))}
function addRow(el,left,right,cls=''){let d=document.createElement('div');d.className='item';let a=document.createElement('span'),b=document.createElement('b');a.textContent=left;b.textContent=right;if(cls)b.className=cls;d.append(a,b);el.append(d)}
function detectCandles(d){let out=[];for(let i=Math.max(1,d.length-12);i<d.length;i++){let c=d[i],p=d[i-1],body=Math.abs(c.close-c.open),range=Math.max(c.high-c.low,.00001),upper=c.high-Math.max(c.open,c.close),lower=Math.min(c.open,c.close)-c.low;
if(body/range<.1)out.push(['Doji','Indecision',c.time]);
if(lower>body*2&&upper<body*.7&&c.close>c.open)out.push(['Hammer-like candle','Potential bullish reversal; needs confirmation',c.time]);
if(upper>body*2&&lower<body*.7&&c.close<c.open)out.push(['Shooting-star-like candle','Potential bearish reversal; needs confirmation',c.time]);
if(c.close>c.open&&p.close<p.open&&c.open<=p.close&&c.close>=p.open)out.push(['Bullish engulfing','Potential bullish reversal',c.time]);
if(c.close<c.open&&p.close>p.open&&c.open>=p.close&&c.close<=p.open)out.push(['Bearish engulfing','Potential bearish reversal',c.time]);}
return out.slice(-8)}
function sma(a,n){return a.length<n?null:a.slice(-n).reduce((s,x)=>s+x,0)/n}
function calcRsi(closes){if(closes.length<15)return null;let gains=0,loss=0;for(let i=closes.length-14;i<closes.length;i++){let v=closes[i]-closes[i-1];if(v>0)gains+=v;else loss-=v}let rs=(gains/14)/((loss/14)||.000001);return 100-100/(1+rs)}
function analyze(d){let closes=d.map(x=>x.close),last=d.at(-1),prev=d.at(-2),ema=sma(closes,20),rsi=calcRsi(closes),volAvg=sma(d.map(x=>x.volume||0),20),vr=volAvg?(last.volume||0)/volAvg:null;let highs=d.slice(-60).map(x=>x.high),lows=d.slice(-60).map(x=>x.low),res=Math.max(...highs),sup=Math.min(...lows);let bias='Neutral / wait',why='Mixed or insufficient technical evidence.';let score=0;if(ema&&last.close>ema)score++;if(ema&&last.close<ema)score--;if(rsi!==null){if(rsi>55)score++;if(rsi<45)score--}if(last.close>prev.close)score+=.5;else score-=.5;if(score>=1.5){bias='Bullish technical bias';why='Price and momentum indicators lean positive. Wait for independent confirmation; this is not a trade instruction.'}else if(score<=-1.5){bias='Bearish technical bias';why='Price and momentum indicators lean negative. This is not a short-selling instruction.'}
document.getElementById('signal').textContent=bias;document.getElementById('signal').className=score>=1.5?'positive':score<=-1.5?'negative':'';document.getElementById('signalText').textContent=why;document.getElementById('rsi').textContent=rsi===null?'—':rsi.toFixed(1);document.getElementById('trend').textContent=ema?(last.close>=ema?'Above EMA 20':'Below EMA 20'):'Need more candles';document.getElementById('volRatio').textContent=vr===null?'—':vr.toFixed(2)+'× average';
let cp=detectCandles(d),ce=document.getElementById('candlePatterns');ce.innerHTML='';cp.forEach(x=>addRow(ce,x[0],x[1]));if(!cp.length)ce.innerHTML='<div class="empty">No clear recent candle pattern detected.</div>';document.getElementById('patternCount').textContent=cp.length;
let levels=document.getElementById('levels');levels.innerHTML='';addRow(levels,'Support (60-candle low)',fmt(sup));addRow(levels,'Resistance (60-candle high)',fmt(res));addRow(levels,'Last close',fmt(last.close));
let pats=document.getElementById('chartPatterns');pats.innerHTML='';let recent=d.slice(-30),up=recent.at(-1).close>recent[0].close;let range=(res-sup)/Math.max(last.close,.00001);addRow(pats,range<.025?'Tight consolidation':'Recent 30-candle structure',range<.025?'Narrow range':'Directional / mixed');addRow(pats,'Short-term direction',up?'Higher net close':'Lower net close');addRow(pats,'Trendline check',up?'Rising net structure':'Falling net structure');addRow(pats,'Volume confirmation',vr!==null&&vr>1.5?'Above recent average':'No strong volume expansion');
candleSeries.setMarkers(cp.map(x=>({time:x[2],position:x[0].includes('Bearish')||x[0].includes('Shooting')?'aboveBar':'belowBar',color:x[0].includes('Bearish')||x[0].includes('Shooting')?'#f05e72':'#18c78a',shape:'circle',text:x[0]})))}
async function load(){let sym=document.getElementById('symbol').value.trim().toUpperCase().replace(/[^A-Z0-9.&_-]/g,'');if(!sym)return;document.getElementById('marketStatus').textContent='Fetching market data…';document.getElementById('chartTitle').textContent=sym+' · '+document.getElementById('exchange').value;document.getElementById('intervalLabel').textContent=interval;
try{let r=await fetch('/api/history?symbol='+encodeURIComponent(sym)+'&exchange='+document.getElementById('exchange').value+'&interval='+interval);let j=await r.json();if(!r.ok)throw Error(j.error||'Unable to load market data');candles=j.data;hideTradingViewFallback();initCharts();candleSeries.setData(candles);volSeries.setData(candles.map(x=>({time:x.time,value:x.volume||0,color:x.close>=x.open?'rgba(24,199,138,.55)':'rgba(240,94,114,.55)'})));chart.timeScale().fitContent();volChart.timeScale().fitContent();let last=candles.at(-1),first=candles.at(-2)||last,delta=last.close-first.close,pct=first.close?delta/first.close*100:0;
document.getElementById('price').textContent=fmt(last.close);let ch=document.getElementById('change');ch.textContent=(delta>=0?'+':'')+fmt(delta)+' ('+pct.toFixed(2)+'%) vs previous candle';ch.className=delta>=0?'positive':'negative';document.getElementById('highlow').textContent=fmt(last.high)+' / '+fmt(last.low);document.getElementById('volume').textContent=fmt(last.volume);document.getElementById('marketStatus').textContent=j.market_status+' · '+j.count+' candles';analyze(candles)
}catch(e){showTradingViewFallback(sym,document.getElementById('exchange').value);document.getElementById('marketStatus').textContent='TradingView chart · analysis data unavailable';document.getElementById('signal').textContent='Analysis data temporarily unavailable';document.getElementById('signalText').textContent='The independent TradingView chart is shown below. Yahoo Finance is rate-limiting analysis data right now, so RSI, volume metrics and pattern detection will return when that feed is available. Try again later.';document.getElementById('price').textContent='—';document.getElementById('change').textContent='Analysis feed unavailable';document.getElementById('highlow').textContent='—';document.getElementById('volume').textContent='—';document.getElementById('patternCount').textContent='—';}}

const aiMessages=document.getElementById('aiMessages');
function addAiMessage(text,who){const el=document.createElement('div');el.className='ai-msg '+who;el.textContent=text;aiMessages.appendChild(el);aiMessages.scrollTop=aiMessages.scrollHeight;return el}
async function askStockAI(){const box=document.getElementById('aiPrompt'),prompt=box.value.trim();if(!prompt)return;box.value='';addAiMessage(prompt,'user');const wait=addAiMessage('Thinking…','bot');document.getElementById('aiSend').disabled=true;try{const payload={prompt,symbol:document.getElementById('symbol').value.trim().toUpperCase(),exchange:document.getElementById('exchange').value,interval,metrics:{price:document.getElementById('price').textContent,change:document.getElementById('change').textContent,highLow:document.getElementById('highlow').textContent,volume:document.getElementById('volume').textContent,rsi:document.getElementById('rsi').textContent,trend:document.getElementById('trend').textContent,volumeRatio:document.getElementById('volRatio').textContent,technicalSummary:document.getElementById('signal').textContent,summaryText:document.getElementById('signalText').textContent,supportResistance:document.getElementById('levels').innerText,patterns:document.getElementById('candlePatterns').innerText}};const r=await fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const j=await r.json();wait.textContent=j.answer||j.error||'I could not prepare an answer. Please try again.'}catch(e){wait.textContent='I could not connect to the assistant. Please try again.'}finally{document.getElementById('aiSend').disabled=false;aiMessages.scrollTop=aiMessages.scrollHeight}}
document.getElementById('aiSend').addEventListener('click',askStockAI);document.getElementById('aiPrompt').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();askStockAI()}});document.querySelectorAll('[data-prompt]').forEach(b=>b.addEventListener('click',()=>{document.getElementById('aiPrompt').value=b.dataset.prompt;askStockAI()}));

document.getElementById('analyze').onclick=load;document.getElementById('symbol').addEventListener('keydown',e=>{if(e.key==='Enter')load()});load();
</script></body></html>
"""

INTERVALS = {
    "1m": ("1m", "7d"), "5m": ("5m", "60d"), "15m": ("15m", "60d"),
    "30m": ("30m", "60d"), "1h": ("60m", "730d"), "4h": ("60m", "730d"),
    "1D": ("1d", "5y"), "1W": ("1wk", "10y"), "1M": ("1mo", "max")
}

@app.get("/")
def home():
    return render_template_string(PAGE)

@app.get("/health")
def health():
    return jsonify(status="ok", service="StockVision AI")

@app.get("/api/history")
def history():
    symbol = "".join(ch for ch in request.args.get("symbol", "RELIANCE").upper() if ch.isalnum() or ch in ".-_&")
    exchange = request.args.get("exchange", "NS").upper()
    interval = request.args.get("interval", "1D")
    if not symbol or exchange not in ("NS", "BO") or interval not in INTERVALS:
        return jsonify(error="Invalid symbol, exchange, or interval."), 400
    ticker = symbol if symbol.endswith((".NS", ".BO")) else f"{symbol}.{exchange}"
    yf_interval, period = INTERVALS[interval]
    try:
        df = yf.Ticker(ticker).history(period=period, interval=yf_interval, auto_adjust=False, actions=False)
        if df.empty:
            return jsonify(error=f"No price history returned for {ticker}. Check the symbol or try the other exchange."), 404
        if interval == "4h":
            df = df.resample("4h").agg({"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna(subset=["Open","High","Low","Close"])
        df = df.dropna(subset=["Open","High","Low","Close"])
        df.index = pd.to_datetime(df.index)
        rows = []
        for stamp, row in df.tail(1200).iterrows():
            ts = int(stamp.timestamp())
            rows.append({"time": ts, "open": round(float(row.Open), 4), "high": round(float(row.High), 4),
                         "low": round(float(row.Low), 4), "close": round(float(row.Close), 4),
                         "volume": int(row.Volume) if pd.notna(row.Volume) else 0})
        if not rows:
            return jsonify(error="No usable candles were returned."), 404
        return jsonify(symbol=ticker, interval=interval, data=rows, count=len(rows),
                       market_status="Yahoo Finance data · may be delayed")
    except Exception as exc:
        app.logger.exception("Market data request failed")
        return jsonify(error="Market data provider error. Please retry shortly or check the ticker."), 502

@app.post("/api/ask")
def ask():
    body = request.get_json(silent=True) or {}
    prompt = str(body.get("prompt", "")).strip()[:2000]
    if not prompt:
        return jsonify(error="Please enter a question."), 400

    symbol = str(body.get("symbol", "the selected stock"))[:40]
    exchange = str(body.get("exchange", "NS"))[:4]
    interval = str(body.get("interval", "1D"))[:8]
    metrics = body.get("metrics", {})
    if not isinstance(metrics, dict):
        metrics = {}
    context = "\n".join(
        f"{str(k)[:40]}: {str(v)[:300]}" for k, v in metrics.items()
    )

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if api_key:
        import json
        import urllib.request
        import urllib.error

        instructions = (
            "You are StockVision AI, a friendly educational stock-market explainer for beginners. "
            "Explain everything in very simple English, define technical words, and use short "
            "paragraphs and everyday examples. The user may be a minor: keep the conversation "
            "educational and age-appropriate. Do not tell the user what stock to buy, sell, or hold; "
            "do not give personalized investment recommendations, trading instructions, price targets, "
            "or guaranteed predictions. You may explain financial concepts, compare long-term and "
            "short-term investing as general concepts, and neutrally explain technical indicators. "
            "Never invent current prices, news, company facts, or data. Treat the supplied dashboard "
            "snapshot as possibly delayed or incomplete; clearly say when information is unavailable. "
            "Mention uncertainty and relevant risks. Do not claim to have checked live news or external "
            "sources unless the user supplied them."
        )
        user_input = (
            f"Selected stock: {symbol} ({exchange})\n"
            f"Selected timeframe: {interval}\n"
            f"Dashboard snapshot:\n{context or 'No dashboard metrics are currently available.'}\n\n"
            f"User question: {prompt}"
        )
        payload = {
            "model": os.environ.get("OPENAI_MODEL", "gpt-6.2-astra"),
            "instructions": instructions,
            "input": user_input,
            "max_output_tokens": 800,
            "store": False
        }
        req = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + api_key
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))

            answer = result.get("output_text", "")
            if not answer:
                parts = []
                for item in result.get("output", []):
                    if item.get("type") == "message":
                        for part in item.get("content", []):
                            if part.get("type") == "output_text":
                                parts.append(part.get("text", ""))
                answer = "\n".join(parts).strip()

            if not answer:
                app.logger.error("OpenAI returned no text: %s", result)
                return jsonify(answer="The AI service returned an empty answer. Please try again."), 502
            return jsonify(answer=answer, mode="openai")
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")[:1200]
            app.logger.error("OpenAI API HTTP error %s: %s", exc.code, details)
            if exc.code == 401:
                message = "OpenAI rejected the API key. Check that OPENAI_API_KEY is correct and active in Render."
            elif exc.code == 429:
                message = "The OpenAI API account has reached a usage limit or has no available API credits. Check API billing and limits."
            elif exc.code == 400:
                message = "The OpenAI request was rejected. Check the configured OPENAI_MODEL and try again."
            else:
                message = "The OpenAI service is temporarily unavailable. Please try again shortly."
            return jsonify(answer=message), 503
        except Exception:
            app.logger.exception("OpenAI assistant request failed")
            return jsonify(answer="I couldn't connect to OpenAI right now. Please try again shortly."), 503

    q = prompt.lower()
    definitions = {
        "rsi": "RSI means Relative Strength Index. It is a momentum meter from 0 to 100. Some chart users watch readings above 70 or below 30, but these are not automatic buy or sell signals.",
        "support": "Support is a price area where a stock has previously found buyers. Resistance is an area where it has previously faced selling. These levels can break, so they are not guarantees.",
        "resistance": "Resistance is a price area where a stock has previously struggled to move higher. It is not a guaranteed ceiling.",
        "candlestick": "A candlestick shows the opening, highest, lowest, and closing prices during one time period.",
        "doji": "A doji is a candle where opening and closing prices are very close. It can show indecision, but it cannot predict the next move by itself.",
        "volume": "Volume is the number of shares traded during a period. It can show how active trading was, but it does not predict direction by itself.",
        "ema": "EMA means Exponential Moving Average. It smooths price data and gives more weight to recent prices. It can help describe a trend, but it can lag behind sudden changes.",
        "moving average": "A moving average smooths price changes to make the general direction easier to see. It is a descriptive tool, not a prediction.",
        "bullish": "Bullish means the price direction or indicators look more positive. It does not mean the price must rise.",
        "bearish": "Bearish means the price direction or indicators look more negative. It does not mean the price must fall.",
        "pe ratio": "The P/E ratio compares a company's share price with its earnings per share. It is one valuation measure, not a complete picture of a company.",
        "market cap": "Market capitalization is the market value of a company's shares: share price multiplied by total shares."
    }
    answer = next((v for k, v in definitions.items() if k in q), None)
    if answer is None:
        answer = (
            "The OpenAI connection is not configured yet. Add OPENAI_API_KEY to the Render "
            "environment and redeploy to enable open-ended AI answers. I won't guess live prices or news."
        )
    return jsonify(answer=answer, mode="basic")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
