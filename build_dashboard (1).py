import pandas as pd, json
df = pd.read_csv("cleaned_sales_with_segments.csv", parse_dates=["Order_Date"])
L = {k: sorted(df[c].astype(str).unique(), key=lambda x: (x=="Unknown", x)) for k, c in
     dict(city="City", cat="Category", gen="Gender", age="Age_Group", seg="Segment").items()}
rows = []
for r in df.itertuples():
    m = r.Order_Date.month if r.Order_Date.year == 2025 else 0
    rows.append([m, L["city"].index(r.City), L["cat"].index(r.Category), L["gen"].index(r.Gender),
                 L["age"].index(r.Age_Group), L["seg"].index(r.Segment), int(r.Quantity), round(r.Total_Sales)])
html = r'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>ApexPlanet Sales Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{--bg:#f4f6fa;--card:#fff;--tx:#1b2433;--mu:#5d6b82;--bd:#dde3ec;--ac:#2f5597;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f1624;--card:#18223a;--tx:#e8edf7;--mu:#9aa8c2;--bd:#2a3858;--ac:#7aa2f7}}
:root[data-theme="dark"]{--bg:#0f1624;--card:#18223a;--tx:#e8edf7;--mu:#9aa8c2;--bd:#2a3858;--ac:#7aa2f7}
html{scroll-padding-top:env(safe-area-inset-top,0px)}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:14px/1.45 system-ui,-apple-system,"Segoe UI",Arial,sans-serif;padding:16px}
h1{font-size:20px;margin:0 0 2px}p.sub{margin:0 0 14px;color:var(--mu);font-size:12px}
.filters{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:14px}
.filters label{font-size:11px;color:var(--mu);display:flex;flex-direction:column;gap:3px}
select,button{font:inherit;padding:6px 8px;border:1px solid var(--bd);border-radius:6px;background:var(--card);color:var(--tx)}
button{cursor:pointer;align-self:flex-end}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:14px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:12px}
.kpi b{display:block;font-size:22px;color:var(--ac)}.kpi span{font-size:11px;color:var(--mu)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.card h2{font-size:13px;margin:0 0 8px}.cv{position:relative;height:230px}
.wide{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:12px}th,td{padding:6px 8px;border-bottom:1px solid var(--bd);text-align:right;white-space:nowrap}th:first-child,td:first-child{text-align:left}
th{color:var(--mu);font-weight:600}.note{font-size:11px;color:var(--mu);margin-top:10px}
</style></head><body>
<h1>ApexPlanet Sales Dashboard</h1>
<p class="sub">Interactive view of 1,000 orders (cleaned Task 1 data). Revenue in INR (assumed), shown in millions. Pick filters to explore.</p>
<div class="filters" id="filters"></div>
<div class="kpis">
<div class="card kpi"><b id="k1">-</b><span>Total revenue (M)</span></div>
<div class="card kpi"><b id="k2">-</b><span>Average order value (K)</span></div>
<div class="card kpi"><b id="k3">-</b><span>Units per order</span></div>
<div class="card kpi"><b id="k4">-</b><span>Top category share</span></div>
<div class="card kpi"><b id="k5">-</b><span>Last month growth (MoM)</span></div>
</div>
<div class="grid">
<div class="card"><h2>Monthly revenue, 2025 (M)</h2><div class="cv"><canvas id="c1"></canvas></div></div>
<div class="card"><h2>Revenue by category (M)</h2><div class="cv"><canvas id="c2"></canvas></div></div>
<div class="card"><h2>Revenue by city (M)</h2><div class="cv"><canvas id="c3"></canvas></div></div>
<div class="card"><h2>Revenue share by segment</h2><div class="cv"><canvas id="c4"></canvas></div></div>
<div class="card"><h2>Revenue by age group (M)</h2><div class="cv"><canvas id="c5"></canvas></div></div>
<div class="card wide"><h2>Segment deep-dive</h2><table id="tb"></table></div>
</div>
<p class="note">Segments: Big Spenders (high price, high quantity), Premium Single-Item (high price, low quantity), Bulk Value Buyers (low price, high quantity), Light Buyers (low price, low quantity). Split points are the median unit price (25.4K) and median quantity (5). Monthly chart covers 2025 orders only.</p>
<script>
const L=__L__,R=__R__,F={city:"City",cat:"Category",gen:"Gender",age:"Age group",seg:"Segment"},IDX={city:1,cat:2,gen:3,age:4,seg:5};
const MN=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],sel={};
const fd=document.getElementById("filters");
for(const k in F){const lb=document.createElement("label");lb.textContent=F[k];const s=document.createElement("select");
s.innerHTML="<option value=\"-1\">All</option>"+L[k].map((v,i)=>"<option value=\""+i+"\">"+v+"</option>").join("");
s.onchange=()=>{sel[k]=+s.value;draw()};sel[k]=-1;lb.appendChild(s);fd.appendChild(lb)}
const rb=document.createElement("button");rb.textContent="Reset";rb.onclick=()=>{fd.querySelectorAll("select").forEach(s=>s.value="-1");for(const k in sel)sel[k]=-1;draw()};fd.appendChild(rb);
const PAL=["#2f5597","#e07a3f","#3a9d7a","#c2476b","#8a6fd1","#d6a92e","#4aa3c8","#7a8a99"];
function css(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim()}
const CH={};
function mk(id,type,opt){const c=new Chart(document.getElementById(id),{type,data:{labels:[],datasets:[{data:[],backgroundColor:PAL,borderColor:PAL[0],tension:.3}]},
options:Object.assign({responsive:true,maintainAspectRatio:false,plugins:{legend:{display:type==="doughnut",labels:{color:css("--tx")}}},
scales:type==="doughnut"?{}:{x:{ticks:{color:css("--mu")},grid:{display:false}},y:{ticks:{color:css("--mu")},grid:{color:css("--bd")},beginAtZero:true}}},opt||{})});CH[id]=c}
mk("c1","line");mk("c2","bar");mk("c3","bar");mk("c4","doughnut");mk("c5","bar");
function agg(rows,i){const o={};rows.forEach(r=>o[r[i]]=(o[r[i]]||0)+r[7]);return o}
function setC(id,labels,vals){const c=CH[id];c.data.labels=labels;c.data.datasets[0].data=vals;
if(id==="c1"){c.data.datasets[0].backgroundColor="rgba(47,85,151,.15)";c.data.datasets[0].borderColor=PAL[0];c.data.datasets[0].fill=true}
c.update()}
const M=v=>(v/1e6).toFixed(1);
function draw(){
const rows=R.filter(r=>{for(const k in IDX)if(sel[k]>=0&&r[IDX[k]]!==sel[k])return false;return true});
const rev=rows.reduce((a,r)=>a+r[7],0),n=rows.length,u=rows.reduce((a,r)=>a+r[6],0);
document.getElementById("k1").textContent=n?M(rev):"-";
document.getElementById("k2").textContent=n?(rev/n/1e3).toFixed(0):"-";
document.getElementById("k3").textContent=n?(u/n).toFixed(1):"-";
const cat=agg(rows,2),top=Math.max(0,...Object.values(cat));
document.getElementById("k4").textContent=n?(top/rev*100).toFixed(1)+"%":"-";
const mo=Array(12).fill(0);rows.forEach(r=>{if(r[0])mo[r[0]-1]+=r[7]});
let g="-";for(let i=11;i>0;i--){if(mo[i]>0&&mo[i-1]>0){g=((mo[i]/mo[i-1]-1)*100).toFixed(1)+"% ("+MN[i]+")";break}}
document.getElementById("k5").textContent=g;
setC("c1",MN,mo.map(v=>+(v/1e6).toFixed(2)));
for(const [id,i,k] of [["c2",2,"cat"],["c3",1,"city"],["c5",4,"age"]]){const a=agg(rows,i),keys=Object.keys(a).map(Number);
 if(id!=="c5")keys.sort((x,y)=>a[y]-a[x]);setC(id,keys.map(j=>L[k][j]),keys.map(j=>+(a[j]/1e6).toFixed(2)))}
const sg=agg(rows,5),sk=Object.keys(sg).map(Number);setC("c4",sk.map(j=>L.seg[j]),sk.map(j=>+(sg[j]/1e6).toFixed(2)));
let h="<tr><th>Segment</th><th>Orders</th><th>% orders</th><th>Revenue (M)</th><th>% revenue</th><th>AOV (K)</th></tr>";
L.seg.forEach((s,j)=>{const x=rows.filter(r=>r[5]===j),sr=x.reduce((a,r)=>a+r[7],0);if(!x.length)return;
h+="<tr><td>"+s+"</td><td>"+x.length+"</td><td>"+(x.length/n*100).toFixed(1)+"%</td><td>"+M(sr)+"</td><td>"+(sr/rev*100).toFixed(1)+"%</td><td>"+(sr/x.length/1e3).toFixed(0)+"</td></tr>"});
document.getElementById("tb").innerHTML=n?h:"<tr><td>No orders match these filters.</td></tr>"}
draw();
</script></body></html>'''
html = html.replace("__L__", json.dumps(L)).replace("__R__", json.dumps(rows, separators=(",", ":")))
open("sales_dashboard.html", "w").write(html)
print(len(html), L)
