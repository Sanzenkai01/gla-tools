/* GLA Tools — web rewrite (vanilla JS)
   Mantém as três calculadoras originais: Experiência, Receitas, Cristais
   Pronto para ser publicado no GitHub Pages (index.html no root).
*/

// ----------------- Dados (portados do app.py) -----------------
const XP_TOTAL_BY_LEVEL = [
  0,0,98,199,388,790,1498,2565,4176,6397,9230,12956,17596,23083,29830,37795,46824,57498,69694,83153,98660,115993,134770,156016,179392,204375,232266,262591,294668,330110,368290,408349,452248,499189,548118,601744,658352,717039,780570,847751,917084,991790,1070450,1151317,1238104,1329149,1422438,1522212,1626548,1733147,1846814,1965347,2086144,2214610,2348246,2484129,2628300,2777945,2929802,3090584,3257144,3425863,3604162,3788543,3975012,4171734,4374842,4579949,4796000,5018741,5243374,5479660,5722940,5967987,6225414,6490139,6756488,7035962,7323038,7611577,7914004,8224337,8535954,8862240,9196736,9532319,9883370,10242935,10603372,10980094,11365634,11751813,12155112,12567533,12980342,13411124,13851332,14291659,14750830,15219731,15688464,16176930,16675430,17173457,17692124,18221129,18749338,19299112,19859528,20418807,21000594,21593327,22184564,22799270,23425226,24049309,24697840,25357925,26015742,26699004,27394124,28086563,28805462,29536523,30264472,31019914,31787822,32552169,33345060,34150721,34952354,35783600,36627920,37467727,38338234,39222119,40100988,41011662,41936018,42854837,43806584
];

const XP_POTION_BY_TIER = {
  "Diamante": {grande: 50000, media: 5000, pequena: 500},
  "Ouro": {grande: 100000, media: 10000, pequena: 1000},
  "Prata": {grande: 200000, media: 20000, pequena: 2000},
  "Bronze": {grande: 300000, media: 30000, pequena: 3000}
};

const RECEITAS = {
  "Paella de Camarão": {
    "Camarão Cru": [8, 300],
    "Folhas Verdes": [1, 15],
    "Tomates": [1, 10],
    "Água": [3, 5],
    "Trufa Branca": [3, 250],
    "Sal": [1, 10],
    "Pimenta": [1, 15],
    "Arroz": [2, 10],
    "Azeite": [1, 15]
  },
  "Frango Teriyaki": {
    "Galinha": [5, 300],
    "Pimenta": [1, 15],
    "Tomates": [3, 10],
    "Sal": [2, 10],
    "Azeite": [6, 15],
    "Folhas Verdes": [3, 15],
    "Alho": [3, 10],
    "Trufa Branca": [3, 250],
    "Creme de Leite": [3, 20]
  }
};

const CRYSTALS_PER_UP = {Emblema:2, Capacete:2, "Calça":2, Peito:4, Arma:4, Colar:4};
const SUCCESS_TABLE = {
  1:[0.35,3],2:[0.30,4],3:[0.25,5],4:[0.20,6],5:[0.22,5],6:[0.18,6],7:[0.14,8],8:[0.10,11],9:[0.10,11],10:[0.09,12],11:[0.08,13],12:[0.07,15],13:[0.06,17],14:[0.05,21],15:[0.04,26],16:[0.03,34]
};
const TRANSFER_COSTS = {
  4: {Capacete:1, Peito:2, "Calça":1, Emblema:1, Arma:2, Colar:2},
  8: {Capacete:3, Peito:5, "Calça":3, Emblema:3, Arma:5, Colar:5},
  12:{Capacete:6, Peito:10, "Calça":6, Emblema:6, Arma:10, Colar:10},
  16:{Capacete:10, Peito:15, "Calça":10, Emblema:10, Arma:15, Colar:15}
};

function get_transfer_cost(slot, level){
  if(level<=0) return 0;
  let key = level<=4?4: level<=8?8: level<=12?12:16;
  return (TRANSFER_COSTS[key] && TRANSFER_COSTS[key][slot]) ? TRANSFER_COSTS[key][slot] : 0;
}

function expected_attempts(p, guarantee){
  const q = 1 - p;
  let E = 0.0;
  for(let k=1;k<guarantee;k++){
    E += k * Math.pow(q, k-1) * p;
  }
  E += guarantee * Math.pow(q, guarantee-1);
  return E;
}

function expected_crystals_for_level(slot, level){
  if(level<1) return 0;
  if(level>16) level = 16;
  const [p, guarantee] = SUCCESS_TABLE[level];
  const attempts = expected_attempts(p, guarantee);
  return attempts * (CRYSTALS_PER_UP[slot] || 0);
}

function get_crystal_type_for_level(lvl){
  if(lvl>=1 && lvl<=4) return "Cristais do Céu";
  if(lvl>=5 && lvl<=8) return "Cristais do Sábio";
  if(lvl>=9 && lvl<=12) return "Cristais Carmesim";
  return "Cristais Radiante";
}

// ----------------- Utilitários -----------------
const $ = id => document.getElementById(id);
function fmt(n){return (typeof n === 'number')? n.toLocaleString('pt-BR') : n}

// ----------------- Experiência -----------------
function xp_needed(n1,n2){
  if(n1<1 || n1>=n2 || n2>140) return null;
  return XP_TOTAL_BY_LEVEL[n2] - XP_TOTAL_BY_LEVEL[n1];
}
function potions_for_xp(xp, tier){
  const vals = XP_POTION_BY_TIER[tier];
  xp = Math.floor(xp);
  const grandes = Math.floor(xp/vals.grande);
  let rem = xp % vals.grande;
  const medias = Math.floor(rem/vals.media);
  rem = rem % vals.media;
  const pequenas = Math.floor(rem/vals.pequena);
  return {grandes, medias, pequenas};
}

function renderExp(){
  const n1 = parseInt($('exp-nivel-inicio').value,10);
  const n2 = parseInt($('exp-nivel-fim').value,10);
  const tier = $('exp-tier').value;
  const container = $('exp-result');
  container.innerHTML = '';
  if(Number.isNaN(n1) || Number.isNaN(n2) || n1<1 || n2>140 || n1>=n2){
    container.textContent = '❌ Nível inválido — 1 ≤ Inicial < Final ≤ 140';
    return;
  }
  const xp = xp_needed(n1,n2);
  const p = potions_for_xp(xp,tier);
  const html = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
      <div><strong>⭐ ${tier}</strong> • Nível ${n1} → ${n2}</div>
      <div><small>XP Total: <strong>${fmt(xp)}</strong></small></div>
    </div>
    <div class="result-body">
      <div class="potions" style="gap:28px;align-items:center;">
        <div style="text-align:center"><img src="Bigexppot.png" alt="grande"><div style="margin-top:8px;font-weight:700;color:var(--accent)">× ${fmt(p.grandes)}</div><div style="font-size:12px;color:var(--muted)">Grande</div></div>
        <div style="text-align:center"><img src="Medexppot.png" alt="média"><div style="margin-top:8px;font-weight:700;color:var(--accent)">× ${fmt(p.medias)}</div><div style="font-size:12px;color:var(--muted)">Média</div></div>
        <div style="text-align:center"><img src="Smallexppot.png" alt="pequena"><div style="margin-top:8px;font-weight:700;color:var(--accent)">× ${fmt(p.pequenas)}</div><div style="font-size:12px;color:var(--muted)">Pequena</div></div>
      </div>
    </div>
  `;
  container.innerHTML = html;
}

$('exp-calc').addEventListener('click', ()=>{
  renderExp();
  saveState();
});

// ----------------- Receitas -----------------
function initReceitas(){
  const sel = $('rcp-select');
  sel.innerHTML = Object.keys(RECEITAS).map(k => `<option>${k}</option>`).join('');
  // restore
  const saved = localStorage.getItem('gla_receita');
  if(saved) sel.value = saved;
}
function calcularReceita(){
  const receita = $('rcp-select').value;
  const qtd = parseInt($('rcp-qtd').value,10) || 0;
  const valor = parseInt($('rcp-valor').value,10) || 0;
  const data = RECEITAS[receita];
  let custo = 0;
  let texto = `📋 ${receita}\n${'─'.repeat(32)}\n\n`;
  for(const item of Object.keys(data)){
    const [quantiaPorUnidade, valorUnitario] = data[item];
    const totalQuantia = quantiaPorUnidade * qtd;
    const custoItem = Math.floor(totalQuantia * Number(valorUnitario));
    custo += custoItem;
    texto += `• ${item}: ${totalQuantia} unidades — Custo: ${fmt(custoItem)} berry (preço unitário: ${valorUnitario})\n`;
  }
  const venda = qtd * valor;
  const taxa = Math.floor(venda * 0.03);
  const lucro = venda - custo - taxa;
  texto += `\n${'─'.repeat(32)}\nCusto: ${fmt(custo)}\nVenda: ${fmt(venda)}\nTaxa (3%): ${fmt(taxa)}\n💰 Lucro: ${fmt(lucro)}`;
  $('rcp-result').textContent = texto;
  // persistir seleção e campos
  localStorage.setItem('gla_receita', receita);
  localStorage.setItem('gla_receita_qtd', String(qtd));
  localStorage.setItem('gla_receita_valor', String(valor));
}
$('rcp-calc').addEventListener('click', calcularReceita);

// restore receita inputs
window.addEventListener('load', ()=>{
  initReceitas();
  const q = localStorage.getItem('gla_receita_qtd'); if(q) $('rcp-qtd').value = q;
  const v = localStorage.getItem('gla_receita_valor'); if(v) $('rcp-valor').value = v;
});

// ----------------- Cristais -----------------
function calcularCristais(){
  const slot = $('cr-slot').value;
  let current = parseInt($('cr-level').value,10) || 0; current = Math.max(0, Math.min(16, current));
  const valCeu = parseInt($('val-ceu').value,10) || 0;
  const valSabio = parseInt($('val-sabio').value,10) || 0;
  const valCarmesim = parseInt($('val-carmesim').value,10) || 0;
  const valRad = parseInt($('val-radiante').value,10) || 0;
  const mapping = {"Cristais do Céu":valCeu, "Cristais do Sábio":valSabio, "Cristais Carmesim":valCarmesim, "Cristais Radiante":valRad};
  const resultado = [];
  let totalAvg = 0; let totalMax = 0; let totalCostLow = 0; let totalCostHigh = 0;
  for(let lvl = current+1; lvl<=16; lvl++){
    const [p, guarantee] = SUCCESS_TABLE[lvl];
    const avg = expected_crystals_for_level(slot, lvl);
    const max_cr = CRYSTALS_PER_UP[slot] * guarantee;
    const low = Math.floor(avg);
    const high = Math.floor(max_cr);
    const crystalType = get_crystal_type_for_level(lvl);
    const valor = mapping[crystalType] || 0;
    const costLow = low * valor;
    const costHigh = high * valor;
    resultado.push({lvl,low,high,crystalType,valor,costLow,costHigh});
    totalAvg += avg; totalMax += max_cr; totalCostLow += costLow; totalCostHigh += costHigh;
  }
  // monta saída
  let out = `🔧 ${slot} — Nível atual +${current}\n`;
  const transfer = get_transfer_cost(slot, current);
  out += `Custo para transferir o boost: ${transfer} gemas\n\n`;
  if(resultado.length===0) out += 'Nenhum nível acima do atual.\n';
  resultado.forEach(r => {
    out += `Média para o nível +${r.lvl}: ${fmt(r.low)} a ${fmt(r.high)} cristais (tipo: ${r.crystalType}) → ${fmt(r.costLow)} a ${fmt(r.costHigh)} berry\n`;
  });
  out += `\nTotal (média somada): ${fmt(Math.floor(totalAvg))} a ${fmt(Math.floor(totalMax))} cristais → ${fmt(Math.floor(totalCostLow))} a ${fmt(Math.floor(totalCostHigh))} berry\n`;
  out += `\nNota: médias calculadas usando chance por nível e pity garantido.`;
  $('cr-result').textContent = out;
  // persistir
  localStorage.setItem('gla_cr_slot', slot);
  localStorage.setItem('gla_cr_level', String(current));
  localStorage.setItem('gla_cr_vals', JSON.stringify({valCeu,valSabio,valCarmesim,valRad}));
}
$('cr-calc').addEventListener('click', calcularCristais);

// restore cristais inputs on load
window.addEventListener('load', ()=>{
  const s = localStorage.getItem('gla_cr_slot'); if(s) $('cr-slot').value = s;
  const lv = localStorage.getItem('gla_cr_level'); if(lv) $('cr-level').value = lv;
  const vals = localStorage.getItem('gla_cr_vals');
  if(vals){ try{ const o = JSON.parse(vals); $('val-ceu').value = o.valCeu||0; $('val-sabio').value = o.valSabio||0; $('val-carmesim').value = o.valCarmesim||0; $('val-radiante').value = o.valRad||0;}catch(e){} }
});

// ----------------- Tabs & state -----------------
function activateTab(name){
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelector(`#${name}`).classList.add('active');
  document.querySelector(`.tab[data-tab='${name}']`).classList.add('active');
  localStorage.setItem('gla_last_tab', name);
}
document.querySelectorAll('.tab').forEach(b => b.addEventListener('click', e => activateTab(b.dataset.tab)));

window.addEventListener('load', ()=>{
  const last = localStorage.getItem('gla_last_tab') || 'menu';
  if(['exp','receitas','cristais'].includes(last)) activateTab(last);
  // restore some defaults
  const savedTier = localStorage.getItem('gla_tier'); if(savedTier) $('exp-tier').value = savedTier;
  $('exp-tier').addEventListener('change', ()=> localStorage.setItem('gla_tier', $('exp-tier').value));
});

// quick save (called after some actions)
function saveState(){
  localStorage.setItem('gla_exp_n1', $('exp-nivel-inicio').value);
  localStorage.setItem('gla_exp_n2', $('exp-nivel-fim').value);
  localStorage.setItem('gla_tier', $('exp-tier').value);
}

// Restore exp values
window.addEventListener('load', ()=>{
  const n1 = localStorage.getItem('gla_exp_n1'); if(n1) $('exp-nivel-inicio').value = n1;
  const n2 = localStorage.getItem('gla_exp_n2'); if(n2) $('exp-nivel-fim').value = n2;
});

// Expose some functions for debugging (optional)
window._GLA = {xp_needed, potions_for_xp, expected_attempts};

