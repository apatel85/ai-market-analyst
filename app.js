// Data Definitions
const OVERSEAS = {'^N225': 'Nikkei', '^FTSE': 'FTSE', '^GDAXI': 'DAX'};
const FUTURES = {'ES=F': 'S&P 500 Fut', 'NQ=F': 'Nasdaq Fut'};
const TREASURIES = {'^IRX': '13W (2Y Px)', '^TNX': '10 Year'};
const VIX = {'^VIX': 'VIX'};
const SECTORS = {'XLK': 'Tech', 'XLF': 'Finance', 'XLE': 'Energy', 'XLV': 'Health'};

const TOP_STOCKS = {
    'Tech': ['AAPL', 'MSFT', 'NVDA', 'AVGO', 'AMD'],
    'Finance': ['JPM', 'BAC', 'V', 'MA'],
    'Energy': ['XOM', 'CVX', 'COP'],
    'Health': ['UNH', 'JNJ', 'LLY']
};

// Since we can't easily hit Yahoo Finance API directly from browser due to CORS,
// we will generate realistic mock data that follows the exact requested logic.
// In a true production app, you would proxy Yahoo Finance through a Cloudflare Worker or backend.

function generateMockData(basePrice, vol) {
    const changePct = (Math.random() * vol * 2) - vol;
    const price = basePrice * (1 + (changePct/100));

    // Simulate high/low
    const high = price * (1 + (Math.random() * 0.01));
    const low = price * (1 - (Math.random() * 0.01));

    // Calculate Pivots
    const pivot = (high + low + price) / 3;
    const r1 = (2 * pivot) - low;
    const s1 = (2 * pivot) - high;

    return {
        price: price,
        change: changePct,
        pivot: pivot,
        r1: r1,
        s1: s1
    };
}

const mockDb = {};

function initMockData() {
    // Generate Overseas
    Object.entries(OVERSEAS).forEach(([k, v]) => mockDb[k] = generateMockData(35000, 1.5));
    // Generate Futures
    Object.entries(FUTURES).forEach(([k, v]) => mockDb[k] = generateMockData(5000, 1.0));
    // Generate Treasuries
    Object.entries(TREASURIES).forEach(([k, v]) => mockDb[k] = generateMockData(4.5, 2.0));
    // Generate VIX
    mockDb['^VIX'] = generateMockData(14.5, 5.0);

    // Generate Sectors & Stocks
    Object.entries(SECTORS).forEach(([k, v]) => {
        mockDb[k] = generateMockData(150, 1.5);
        if (TOP_STOCKS[v]) {
            TOP_STOCKS[v].forEach(stock => {
                // If sector is up, stock likely up
                const stockVol = 2.0;
                let c = (Math.random() * stockVol * 2) - stockVol;
                if (mockDb[k].change > 0) c = Math.abs(c);
                if (mockDb[k].change < 0) c = -Math.abs(c);

                const p = 100 + (Math.random() * 200);
                const h = p * 1.02;
                const l = p * 0.98;
                const piv = (h+l+p)/3;

                mockDb[stock] = {
                    price: p, change: c, pivot: piv, r1: (2*piv)-l, s1: (2*piv)-h
                };
            });
        }
    });
}

function renderMetricCard(name, data, showLevels = false) {
    const isPos = data.change >= 0;
    const colorClass = isPos ? 'positive' : 'negative';
    const sign = isPos ? '+' : '';

    let html = `
        <div class="metric-card">
            <div class="metric-name">${name}</div>
            <div class="metric-price">${data.price.toFixed(2)}</div>
            <div class="metric-change ${colorClass}">${sign}${data.change.toFixed(2)}%</div>
    `;

    if (showLevels) {
        html += `<div class="metric-levels">P: ${data.pivot.toFixed(2)} | R1: ${data.r1.toFixed(2)}</div>`;
    }
    html += `</div>`;
    return html;
}

function renderApp() {
    initMockData();

    // 1. Global
    let globHtml = '';
    Object.entries(OVERSEAS).forEach(([k, name]) => { globHtml += renderMetricCard(name, mockDb[k]); });
    document.getElementById('grid-global').innerHTML = globHtml;

    // 2. Futures
    let futHtml = '';
    Object.entries(FUTURES).forEach(([k, name]) => { futHtml += renderMetricCard(name, mockDb[k], true); });
    document.getElementById('grid-futures').innerHTML = futHtml;

    // 3. Rates
    let ratesHtml = '';
    Object.entries(TREASURIES).forEach(([k, name]) => { ratesHtml += renderMetricCard(name, mockDb[k]); });
    ratesHtml += renderMetricCard('VIX', mockDb['^VIX'], true);
    document.getElementById('grid-rates').innerHTML = ratesHtml;

    // Probability
    let avgChange = 0;
    let count = 0;
    Object.keys(FUTURES).forEach(k => { avgChange += mockDb[k].change; count++; });
    avgChange = avgChange / count;

    let prob = Math.min(Math.max(50 + (avgChange * 15), 10), 90);
    let dir = prob > 50 ? "BULLISH" : "BEARISH";
    let probEl = document.getElementById('marketProb');
    probEl.innerHTML = `Statistical Direction: ${dir} (Confidence: ${prob.toFixed(1)}%)`;
    probEl.className = `market-status ${prob > 50 ? 'bg-bull' : 'bg-bear'}`;

    // Sectors Accordion
    let secHtml = '';
    Object.entries(SECTORS).forEach(([k, name]) => {
        const d = mockDb[k];
        const isPos = d.change >= 0;
        const col = isPos ? 'positive' : 'negative';

        secHtml += `
            <button class="accordion">
                <span>${name} Sector</span>
                <span class="${col}">${isPos?'+':''}${d.change.toFixed(2)}%</span>
            </button>
            <div class="panel">
                <div style="margin-bottom: 10px; font-size: 0.85rem; color: #aaa;">
                    Pivot: ${d.pivot.toFixed(2)} | R1: ${d.r1.toFixed(2)} | S1: ${d.s1.toFixed(2)}
                </div>
        `;

        if (TOP_STOCKS[name]) {
            TOP_STOCKS[name].forEach(stock => {
                const sd = mockDb[stock];
                const scol = sd.change >= 0 ? 'positive' : 'negative';
                secHtml += `
                    <div class="stock-item">
                        <div><strong>${stock}</strong></div>
                        <div style="text-align: right">
                            <span class="${scol}">${sd.price.toFixed(2)} (${sd.change.toFixed(2)}%)</span><br>
                            <span class="stock-levels">P: ${sd.pivot.toFixed(2)}</span>
                        </div>
                    </div>
                `;
            });
        }
        secHtml += `</div>`;
    });
    document.getElementById('sectors-list').innerHTML = secHtml;

    // Attach accordion logic
    var acc = document.getElementsByClassName("accordion");
    for (let i = 0; i < acc.length; i++) {
        acc[i].onclick = function() {
            this.classList.toggle("active");
            var panel = this.nextElementSibling;
            panel.classList.toggle("show");
        }
    }

    // EOD Recap Logic
    let strongSectors = [];
    Object.entries(SECTORS).forEach(([k, name]) => {
        if(mockDb[k].change > 0) strongSectors.push(name);
    });

    let eodSec = document.getElementById('eod-sectors');
    let eodStk = document.getElementById('eod-stocks');

    if (strongSectors.length > 0) {
        eodSec.innerHTML = `<p>Sectors closing positive: <strong>${strongSectors.join(', ')}</strong></p>`;

        let stksHtml = '<p>Stocks from strong sectors showing relative strength:</p>';
        strongSectors.forEach(secName => {
            stksHtml += `<p><strong>${secName}:</strong><br>`;
            if (TOP_STOCKS[secName]) {
                let sStks = TOP_STOCKS[secName].filter(s => mockDb[s].change > 0);
                stksHtml += sStks.length > 0 ? sStks.join(', ') : 'None';
            }
            stksHtml += `</p>`;
        });
        eodStk.innerHTML = stksHtml;
    } else {
        eodSec.innerHTML = `<p>No sectors closed positive. Monitor for potential bounce.</p>`;
        eodStk.innerHTML = `<p>Defensive positioning recommended.</p>`;
    }

    // Mock News
    document.getElementById('newsFeed').innerHTML = `
        <li><a href="#">Federal Reserve hints at future rate decisions...</a></li>
        <li><a href="#">Tech sector rallies on new AI chip announcements...</a></li>
        <li><a href="#">Oil prices stabilize after inventory reports...</a></li>
        <li><a href="#">Earnings preview: What to expect from major banks...</a></li>
    `;
}

// Navigation Logic
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        // Remove active class from all buttons and tabs
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));

        // Add active to clicked and target
        const targetId = e.currentTarget.getAttribute('data-target');
        e.currentTarget.classList.add('active');
        document.getElementById(targetId).classList.add('active');
        window.scrollTo(0, 0);
    });
});

// Refresh Logic
document.getElementById('refreshBtn').addEventListener('click', () => {
    renderApp();

    // Quick visual feedback
    const btn = document.getElementById('refreshBtn');
    btn.style.color = '#00c805';
    setTimeout(() => { btn.style.color = '#ffffff'; }, 500);
});

// Init
window.onload = renderApp;
