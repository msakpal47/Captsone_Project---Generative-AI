document.addEventListener('DOMContentLoaded', function () {
  var select = document.getElementById('symbol-select');
  var input = document.getElementById('symbol-input');
  var testBtn = document.getElementById('test-api');
  var testOut = document.getElementById('test-output');
  if (testBtn && testOut) {
    testBtn.addEventListener('click', function () {
      testOut.style.display = 'block';
      testOut.textContent = 'Testing...';
      fetch('/api/test')
        .then(function(r){ return r.json(); })
        .then(function(j){ testOut.textContent = JSON.stringify(j, null, 2); })
        .catch(function(e){ testOut.textContent = 'Error: ' + (e && e.message ? e.message : 'request failed'); });
    });
  }
  if (select && input) {
    var initV = (select.value || '').toUpperCase();
    if (initV && initV !== '_CUSTOM') {
      if (initV === '_ALL') { input.value = ''; }
      else { input.value = initV; }
      input.setAttribute('disabled', 'disabled');
    }
    select.addEventListener('change', function () {
      var v = select.value || '';
      if (v && v.toUpperCase() !== '_CUSTOM') {
        if (v.toUpperCase() === '_ALL') { input.value = ''; }
        else { input.value = v; }
        input.setAttribute('disabled', 'disabled');
      } else {
        input.removeAttribute('disabled');
      }
    });
  }
  var el = document.getElementById('sentiment-data');
  if (!el) return;
  var payload = {};
  try { payload = JSON.parse(el.textContent || '{}'); } catch (e) { payload = {}; }
  var ctxEl = document.getElementById('sentimentChart');
  if (!ctxEl) return;
  var ctx = ctxEl.getContext('2d');
  var data = [
    payload['Positive'] || 0,
    payload['Negative'] || 0,
    payload['Neutral'] || 0
  ];
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Positive', 'Negative', 'Neutral'],
      datasets: [{
        data: data,
        backgroundColor: ['#22c55e', '#ef4444', '#6b7280']
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' },
        tooltip: { enabled: true }
      }
    }
  });

  var trendEl = document.getElementById('trend-data');
  if (trendEl) {
    var trend = {};
    try { trend = JSON.parse(trendEl.textContent || '{}'); } catch (e) { trend = {}; }
    if (trend && trend.labels && trend.labels.length) {
      var tctx = document.getElementById('trendChart').getContext('2d');
      new Chart(tctx, {
        type: 'line',
        data: {
          labels: trend.labels,
          datasets: [
            {label:'Positive', data: trend.pos || [], borderColor:'#22c55e', backgroundColor:'rgba(34,197,94,0.2)', tension:0.2},
            {label:'Negative', data: trend.neg || [], borderColor:'#ef4444', backgroundColor:'rgba(239,68,68,0.2)', tension:0.2},
            {label:'Neutral', data: trend.neu || [], borderColor:'#6b7280', backgroundColor:'rgba(107,114,128,0.2)', tension:0.2}
          ]
        },
        options: {
          responsive: true,
          plugins: { legend: { position: 'bottom' } },
          scales: { x: { display: true }, y: { display: true, beginAtZero: true } }
        }
      });
    }
  }

  var priceEl = document.getElementById('price-data');
  if (priceEl) {
    var price = [];
    try { price = JSON.parse(priceEl.textContent || '[]'); } catch (e) { price = []; }
    if (price && price.length) {
      var labels = price.map(function(p){ return p.date; });
      var closes = price.map(function(p){ return p.close; });
      var pctx = document.getElementById('priceChart').getContext('2d');
      new Chart(pctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{ label:'Close', data: closes, borderColor:'#93c5fd', backgroundColor:'rgba(147,197,253,0.2)', tension:0.2 }]
        },
        options: {
          responsive: true,
          plugins: { legend: { position: 'bottom' } },
          scales: { x: { display: true }, y: { display: true } }
        }
      });
    }
  }
});
