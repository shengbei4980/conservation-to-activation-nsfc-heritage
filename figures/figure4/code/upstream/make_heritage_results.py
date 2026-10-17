
import os, re, json, math, itertools, warnings
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch, Rectangle, Polygon
from matplotlib import font_manager
import networkx as nx

warnings.filterwarnings('ignore')

BASE = Path(os.environ.get("DATA_DIR", str(Path(__file__).resolve().parents[4] / "data")))
OUT = Path(__file__).resolve().parents[2] / "outputs" / "reproduced" / "upstream"
SRC = OUT / 'source_data'
FIG = OUT / 'figures'
TAB = OUT / 'tables'
SCR = OUT / 'scripts'
for d in [OUT, SRC, FIG, TAB, SCR]:
    d.mkdir(parents=True, exist_ok=True)

# Fonts and style
font_candidates = [r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\simhei.ttf', r'C:\Windows\Fonts\simsun.ttc']
font_name = 'DejaVu Sans'
for fp in font_candidates:
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp)
        font_name = font_manager.FontProperties(fname=fp).get_name()
        break
mpl.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': [font_name, 'Arial', 'DejaVu Sans'],
    'svg.fonttype': 'none',
    'pdf.fonttype': 42,
    'font.size': 7.5,
    'axes.spines.right': False,
    'axes.spines.top': False,
    'axes.linewidth': 0.7,
    'axes.unicode_minus': False,
    'legend.frameon': False,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
})

PALETTE = {
    'blue':'#4E79A7','lightblue':'#A0CBE8','orange':'#F28E2B','red':'#E15759',
    'green':'#59A14F','teal':'#76B7B2','purple':'#B07AA1','yellow':'#EDC948',
    'grey':'#9D9D9D','dark':'#2E2E2E','pale':'#F3F5F7','navy':'#253858'
}
cluster_colors = ['#E15759','#F28E2B','#59A14F','#4E79A7','#B07AA1','#76B7B2','#EDC948','#9C755F','#BAB0AC','#2CA02C']


def read_csv(fn):
    return pd.read_csv(BASE/fn, encoding='utf-8-sig')

llm = read_csv('heritage_llm_coding_results.csv')
raw = read_csv('nsfc_results_with_achievement_stat.csv')
# Normalize keys
llm['approval_no'] = llm['approval_no'].astype(str).str.strip()
raw['approval_no'] = raw['approval_no'].astype(str).str.strip()
# Filter in scope
llm_in = llm[llm['scope'].eq('in_scope')].copy()
df = llm_in.merge(raw, on='approval_no', how='left', suffixes=('', '_raw'))

# Convert numeric dates/outcomes
for c in ['期刊论文数量','会议论文数量','专著数量','专利','获奖','funding_amount']:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

df['start_year'] = pd.to_datetime(df['research_period_start'], errors='coerce').dt.year
df['end_year'] = pd.to_datetime(df['research_period_end'], errors='coerce').dt.year
# Use search_year as a fallback only for missing starts when present.
df['start_year_filled'] = df['start_year'].fillna(pd.to_numeric(df.get('search_year'), errors='coerce'))

def stage_from_start(y):
    if pd.isna(y): return '未标明'
    y = int(y)
    if y <= 2012: return '议程形成期'
    if y <= 2017: return '对象与方法扩展期'
    return '复合议程增强期'

df['stage'] = df['start_year_filled'].apply(stage_from_start)

# Functions
split_pat = re.compile(r'[;；、,，]+')
def split_tags(x):
    if pd.isna(x): return []
    vals = [v.strip() for v in split_pat.split(str(x)) if v.strip()]
    return [v for v in vals if v not in ['信息不足','证据不足','无数据','暂无','nan']]

def explode_counts(data, col, prefix=None):
    rows=[]
    for _, r in data.iterrows():
        for tag in split_tags(r[col]):
            rows.append({'approval_no':r['approval_no'], 'tag':tag})
    if not rows:
        return pd.DataFrame(columns=['tag','count'])
    out = pd.DataFrame(rows).groupby('tag').size().reset_index(name='count').sort_values('count', ascending=False)
    if prefix:
        out.to_csv(SRC/f'{prefix}.csv', index=False, encoding='utf-8-sig')
    return out

def value_counts_df(data, col, name, prefix=None):
    out = data[col].fillna('信息不足').astype(str).value_counts().reset_index()
    out.columns=[name,'count']
    out['percent']=out['count']/len(data)*100
    if prefix:
        out.to_csv(SRC/f'{prefix}.csv', index=False, encoding='utf-8-sig')
    return out

# Core summaries
summary = {}
summary['n_in_scope'] = int(len(df))
summary['n_raw'] = int(len(llm))
summary['n_out_scope'] = int((llm['scope']!='in_scope').sum())
summary['start_year_min'] = int(np.nanmin(df['start_year_filled']))
summary['start_year_max'] = int(np.nanmax(df['start_year_filled']))
summary['end_year_min'] = int(np.nanmin(df['end_year']))
summary['end_year_max'] = int(np.nanmax(df['end_year']))
summary['outcome_totals'] = {c:int(df[c].sum()) for c in ['期刊论文数量','会议论文数量','专著数量','专利','获奖'] if c in df}

df.to_csv(SRC/'analysis_dataset_in_scope.csv', index=False, encoding='utf-8-sig')

vc_project = value_counts_df(df, 'search_category', 'project_type', 'project_type_counts')
vc_discipline = value_counts_df(df, 'search_code', 'discipline_code', 'discipline_code_counts')
vc_object = value_counts_df(df, 'heritage_objects', 'heritage_object', 'heritage_object_counts')
vc_orientation = value_counts_df(df, 'research_orientations', 'research_orientation', 'research_orientation_counts')
vc_method = value_counts_df(df, 'primary_method_orientation', 'method_orientation', 'method_orientation_counts')
vc_stage = value_counts_df(df, 'stage', 'stage', 'stage_counts')
vc_turn = value_counts_df(df, 'turn_type', 'turn_type', 'turn_type_counts')
vc_function = value_counts_df(df, 'primary_knowledge_function', 'knowledge_function', 'knowledge_function_counts')

# Top multi-tag counts
tag_theme = explode_counts(df, 'research_theme_tags', 'research_theme_tag_counts')
tag_method = explode_counts(df, 'method_tags', 'method_tag_counts')
tag_agenda = explode_counts(df, 'agenda_turn_tags', 'agenda_turn_tag_counts')
tag_outcome_path = explode_counts(df, 'outcome_pathway', 'outcome_path_counts')

# Cross tabs and stage profiles
obj_ori = pd.crosstab(df['heritage_objects'], df['research_orientations'])
obj_ori.to_csv(SRC/'object_by_orientation_matrix.csv', encoding='utf-8-sig')
ori_method = pd.crosstab(df['research_orientations'], df['primary_method_orientation'])
ori_method.to_csv(SRC/'orientation_by_method_matrix.csv', encoding='utf-8-sig')
ori_stage = pd.crosstab(df['stage'], df['research_orientations'])
ori_stage = ori_stage.reindex(['议程形成期','对象与方法扩展期','复合议程增强期']).fillna(0).astype(int)
ori_stage.to_csv(SRC/'stage_by_orientation_matrix.csv', encoding='utf-8-sig')
obj_stage = pd.crosstab(df['stage'], df['heritage_objects']).reindex(['议程形成期','对象与方法扩展期','复合议程增强期']).fillna(0).astype(int)
obj_stage.to_csv(SRC/'stage_by_object_matrix.csv', encoding='utf-8-sig')
method_stage = pd.crosstab(df['stage'], df['primary_method_orientation']).reindex(['议程形成期','对象与方法扩展期','复合议程增强期']).fillna(0).astype(int)
method_stage.to_csv(SRC/'stage_by_method_matrix.csv', encoding='utf-8-sig')
turn_object = pd.crosstab(df['turn_type'], df['heritage_objects'])
turn_object.to_csv(SRC/'turn_by_object_matrix.csv', encoding='utf-8-sig')
turn_func = pd.crosstab(df['turn_type'], df['primary_knowledge_function'])
turn_func.to_csv(SRC/'turn_by_knowledge_function_matrix.csv', encoding='utf-8-sig')

# Outcomes by groups
out_cols=['期刊论文数量','会议论文数量','专著数量','专利','获奖']
out_by_orientation = df.groupby('research_orientations')[out_cols].agg(['sum','mean','median']).round(2)
out_by_orientation.to_csv(SRC/'outcomes_by_orientation.csv', encoding='utf-8-sig')
out_by_code = df.groupby('search_code')[out_cols].agg(['sum','mean','median']).round(2)
out_by_code.to_csv(SRC/'outcomes_by_discipline_code.csv', encoding='utf-8-sig')
out_by_type = df.groupby('search_category')[out_cols].agg(['sum','mean','median']).round(2)
out_by_type.to_csv(SRC/'outcomes_by_project_type.csv', encoding='utf-8-sig')

# Summary tables for manuscript
summary_tables = {}
summary_tables['project_type'] = vc_project.to_dict('records')
summary_tables['discipline_code'] = vc_discipline.head(8).to_dict('records')
summary_tables['objects'] = vc_object.to_dict('records')
summary_tables['orientations'] = vc_orientation.to_dict('records')
summary_tables['methods'] = vc_method.to_dict('records')
summary_tables['stages'] = vc_stage.to_dict('records')
summary_tables['turns'] = vc_turn.to_dict('records')
summary_tables['functions'] = vc_function.to_dict('records')
summary_tables['top_themes'] = tag_theme.head(15).to_dict('records')
summary_tables['top_methods'] = tag_method.head(15).to_dict('records')
summary_tables['top_agenda_tags'] = tag_agenda.head(15).to_dict('records')
summary_tables['outcome_totals'] = summary['outcome_totals']
json.dump({'summary':summary,'tables':summary_tables}, open(OUT/'results_stats.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)

# Helpers for figures

def save_fig(fig, stem, dpi=600):
    fig.savefig(FIG/f'{stem}.svg', bbox_inches='tight')
    fig.savefig(FIG/f'{stem}.pdf', bbox_inches='tight')
    fig.savefig(FIG/f'{stem}.png', dpi=300, bbox_inches='tight')
    fig.savefig(FIG/f'{stem}.tiff', dpi=dpi, bbox_inches='tight')
    plt.close(fig)

def wrap_label(s, n=6):
    s=str(s)
    if len(s)<=n: return s
    return '\n'.join([s[i:i+n] for i in range(0,len(s),n)])

def hbar(ax, data, label_col, value_col='count', color='#4E79A7', title=None, max_items=8):
    d=data.head(max_items).iloc[::-1]
    ax.barh(range(len(d)), d[value_col], color=color, edgecolor='none', height=0.68)
    ax.set_yticks(range(len(d)))
    ax.set_yticklabels([wrap_label(x,7) for x in d[label_col]], fontsize=7)
    ax.set_xlabel('项目数')
    if title: ax.set_title(title, loc='left', fontsize=9, fontweight='bold')
    for i,v in enumerate(d[value_col]):
        ax.text(v+0.3, i, f'{int(v)}', va='center', fontsize=6.5)
    ax.grid(axis='x', color='#E6E8EB', lw=0.5)
    ax.set_axisbelow(True)

# Figure 1: overall map
fig = plt.figure(figsize=(7.2, 5.8), constrained_layout=False)
gs = fig.add_gridspec(2, 3, height_ratios=[1.0,1.15], width_ratios=[1,1,1.25], wspace=0.55, hspace=0.5)
ax1=fig.add_subplot(gs[0,0]); hbar(ax1, vc_object, 'heritage_object', color=PALETTE['blue'], title='a  遗产对象')
ax2=fig.add_subplot(gs[0,1]); hbar(ax2, vc_orientation, 'research_orientation', color=PALETTE['orange'], title='b  问题取向')
ax3=fig.add_subplot(gs[0,2]); hbar(ax3, vc_method, 'method_orientation', color=PALETTE['green'], title='c  方法取向')
# Network from object-orientation-method primary labels
G=nx.Graph()
for _,r in df.iterrows():
    o=f"O:{r['heritage_objects']}"; q=f"Q:{r['research_orientations']}"; m=f"M:{r['primary_method_orientation']}"
    for node, typ in [(o,'object'),(q,'orientation'),(m,'method')]:
        G.add_node(node, typ=typ, label=node.split(':',1)[1])
    for a,b in [(o,q),(q,m),(o,m)]:
        if G.has_edge(a,b): G[a][b]['weight']+=1
        else: G.add_edge(a,b, weight=1)
# prune weak edges only for display
H=nx.Graph()
for u,v,dct in G.edges(data=True):
    if dct['weight']>=2:
        H.add_edge(u,v,weight=dct['weight'])
        H.nodes[u].update(G.nodes[u]); H.nodes[v].update(G.nodes[v])
ax4=fig.add_subplot(gs[1,:])
pos=nx.spring_layout(H, seed=9, k=0.85, weight='weight', iterations=200)
typ_color={'object':PALETTE['blue'],'orientation':PALETTE['orange'],'method':PALETTE['green']}
# Draw pale edges
weights=np.array([d['weight'] for _,_,d in H.edges(data=True)]) if H.number_of_edges() else np.array([1])
for u,v,dct in H.edges(data=True):
    ax4.plot([pos[u][0],pos[v][0]],[pos[u][1],pos[v][1]], color='#C6CCD6', lw=0.25+1.2*dct['weight']/weights.max(), alpha=0.45, zorder=1)
node_freq={}
for node in H.nodes:
    prefix,label=node.split(':',1)
    if prefix=='O': node_freq[node]=int((df['heritage_objects']==label).sum())
    elif prefix=='Q': node_freq[node]=int((df['research_orientations']==label).sum())
    else: node_freq[node]=int((df['primary_method_orientation']==label).sum())
for typ in ['object','orientation','method']:
    nodelist=[n for n,d in H.nodes(data=True) if d['typ']==typ]
    sizes=[45+node_freq.get(n,1)*13 for n in nodelist]
    ax4.scatter([pos[n][0] for n in nodelist],[pos[n][1] for n in nodelist], s=sizes, c=typ_color[typ], alpha=0.84, edgecolor='white', linewidth=0.7, label={'object':'对象','orientation':'问题','method':'方法'}[typ], zorder=3)
for n in H.nodes:
    if node_freq.get(n,0)>=8:
        ax4.text(pos[n][0],pos[n][1]+0.035, H.nodes[n]['label'], ha='center', va='bottom', fontsize=7, color='#222222', zorder=4)
ax4.set_title('d  对象—问题—方法的项目级共现结构', loc='left', fontsize=9, fontweight='bold')
ax4.legend(loc='upper right', ncol=3, fontsize=7)
ax4.axis('off')
save_fig(fig, 'fig3_overall_agenda_structure')

# Figure 2: temporal evolution
stage_order=['议程形成期','对象与方法扩展期','复合议程增强期']
stage_labels={'议程形成期':'议程形成期\n(≤2012)','对象与方法扩展期':'对象与方法扩展期\n(2013–2017)','复合议程增强期':'复合议程增强期\n(≥2018)'}
fig = plt.figure(figsize=(7.2,5.7))
gs=fig.add_gridspec(2,2, height_ratios=[1,1.2], width_ratios=[1.2,1], hspace=0.45, wspace=0.42)
# annual bars
ax=fig.add_subplot(gs[0,0])
yearly=df.dropna(subset=['start_year_filled']).groupby(df['start_year_filled'].astype(int)).size()
yearly.to_csv(SRC/'annual_project_start_counts.csv', encoding='utf-8-sig')
ax.bar(yearly.index, yearly.values, color=PALETTE['navy'], alpha=0.82, width=0.8)
ax.set_title('a  项目起始年份分布', loc='left', fontsize=9, fontweight='bold')
ax.set_xlabel('起始年'); ax.set_ylabel('项目数')
ax.set_xticks(yearly.index); ax.set_xticklabels([str(int(x)) for x in yearly.index], rotation=45, ha='right', fontsize=6.6)
ax.grid(axis='y', color='#E6E8EB', lw=0.5); ax.set_axisbelow(True)
# stage orientation percent heatmap
ax=fig.add_subplot(gs[0,1])
heat=ori_stage.div(ori_stage.sum(axis=1), axis=0)*100
heat=heat[vc_orientation['research_orientation'].tolist()]
heat.to_csv(SRC/'stage_orientation_percent.csv', encoding='utf-8-sig')
im=ax.imshow(heat.values, cmap='Blues', aspect='auto', vmin=0, vmax=max(40, np.nanmax(heat.values)))
ax.set_xticks(range(len(heat.columns))); ax.set_xticklabels([wrap_label(c,4) for c in heat.columns], rotation=45, ha='right', fontsize=6.6)
ax.set_yticks(range(len(heat.index))); ax.set_yticklabels([stage_labels.get(s,s) for s in heat.index], fontsize=7)
ax.set_title('b  问题取向的阶段占比(%)', loc='left', fontsize=9, fontweight='bold')
for i in range(heat.shape[0]):
    for j in range(heat.shape[1]):
        val=heat.values[i,j]
        ax.text(j,i,f'{val:.0f}',ha='center',va='center',fontsize=6.2,color='white' if val>25 else '#1f1f1f')
fig.colorbar(im, ax=ax, shrink=0.75, pad=0.02)
# timeline bubble of top research themes
ax=fig.add_subplot(gs[1,:])
# Build stage x theme tag counts
top_tags=tag_theme.head(11)['tag'].tolist()
rows=[]
for st in stage_order:
    sub=df[df['stage']==st]
    for tag in top_tags:
        cnt=sum(tag in split_tags(x) for x in sub['research_theme_tags'])
        if cnt>0:
            rows.append({'stage':st,'tag':tag,'count':cnt})
timeline=pd.DataFrame(rows)
timeline.to_csv(SRC/'timeline_theme_bubbles.csv', index=False, encoding='utf-8-sig')
ypos={tag:i for i,tag in enumerate(top_tags[::-1])}
xpos={st:i for i,st in enumerate(stage_order)}
# draw stage vertical bands
for st,i in xpos.items():
    ax.axvline(i, color='#E8EBF0', lw=0.9, zorder=0)
for tag in top_tags:
    vals=timeline[timeline['tag']==tag]
    xs=[xpos[s] for s in vals['stage']]
    ys=[ypos[tag]]*len(xs)
    if len(xs)>1:
        ax.plot(xs, ys, color='#D3D8E2', lw=0.8, zorder=1)
for _,r in timeline.iterrows():
    ax.scatter(xpos[r['stage']], ypos[r['tag']], s=25+r['count']*25, color=cluster_colors[ypos[r['tag']]%len(cluster_colors)], alpha=0.78, edgecolor='white', linewidth=0.6, zorder=3)
ax.set_xlim(-0.35,2.35); ax.set_ylim(-0.8,len(top_tags)-0.2)
ax.set_xticks(range(3)); ax.set_xticklabels([stage_labels[s] for s in stage_order], fontsize=7)
ax.set_yticks(range(len(top_tags))); ax.set_yticklabels([wrap_label(t,9) for t in top_tags[::-1]], fontsize=7)
ax.set_title('c  主题标签的阶段性演化', loc='left', fontsize=9, fontweight='bold')
ax.grid(axis='y', color='#EEF0F4', lw=0.5)
save_fig(fig, 'fig4_temporal_evolution')

# Figure 3: agenda turns and reshaping
fig=plt.figure(figsize=(7.2,5.8))
gs=fig.add_gridspec(2,2, hspace=0.48, wspace=0.42)
ax=fig.add_subplot(gs[0,0]); hbar(ax, vc_turn, 'turn_type', color=PALETTE['purple'], title='a  研究转向类型', max_items=8)
# turn by object heatmap percent by row
ax=fig.add_subplot(gs[0,1])
mat=turn_object.loc[vc_turn['turn_type'].tolist(), vc_object['heritage_object'].tolist()].fillna(0)
matp=mat.div(mat.sum(axis=1).replace(0,np.nan),axis=0)*100
matp.to_csv(SRC/'turn_by_object_percent.csv', encoding='utf-8-sig')
im=ax.imshow(matp.values, cmap='Oranges', aspect='auto', vmin=0, vmax=np.nanmax(matp.values))
ax.set_xticks(range(matp.shape[1])); ax.set_xticklabels([wrap_label(c,4) for c in matp.columns], rotation=45, ha='right', fontsize=6)
ax.set_yticks(range(matp.shape[0])); ax.set_yticklabels([wrap_label(c,6) for c in matp.index], fontsize=6.5)
ax.set_title('b  转向类型与遗产对象(行占比%)', loc='left', fontsize=9, fontweight='bold')
fig.colorbar(im, ax=ax, shrink=0.72, pad=0.02)
# turn by knowledge function heatmap count
ax=fig.add_subplot(gs[1,0])
mat2=turn_func.loc[vc_turn['turn_type'].tolist(), vc_function['knowledge_function'].tolist()].fillna(0)
mat2.to_csv(SRC/'turn_by_function_counts.csv', encoding='utf-8-sig')
im=ax.imshow(mat2.values, cmap='Greens', aspect='auto')
ax.set_xticks(range(mat2.shape[1])); ax.set_xticklabels([wrap_label(c,4) for c in mat2.columns], rotation=45, ha='right', fontsize=6)
ax.set_yticks(range(mat2.shape[0])); ax.set_yticklabels([wrap_label(c,6) for c in mat2.index], fontsize=6.5)
ax.set_title('c  转向类型与知识功能(项目数)', loc='left', fontsize=9, fontweight='bold')
fig.colorbar(im, ax=ax, shrink=0.72, pad=0.02)
# role frequencies of key reshaping agendas from agenda_turn_tags
ax=fig.add_subplot(gs[1,1])
selected=['数字孪生','智能识别','公众参与','活化利用','风险预警','空间治理','意义阐释','预防保护','本体安全']
role_counts=[]
for tag in selected:
    role_counts.append({'agenda':tag,'count':int(sum(tag in split_tags(x) for x in df['agenda_turn_tags']))})
role_df=pd.DataFrame(role_counts).sort_values('count', ascending=True)
role_df.to_csv(SRC/'reshaping_agenda_tag_counts.csv', index=False, encoding='utf-8-sig')
ax.barh(range(len(role_df)), role_df['count'], color=[PALETTE['teal'] if x in ['数字孪生','智能识别'] else PALETTE['orange'] if x=='活化利用' else PALETTE['green'] if x in ['公众参与','空间治理'] else PALETTE['red'] if x=='风险预警' else PALETTE['grey'] for x in role_df['agenda']], height=0.68)
ax.set_yticks(range(len(role_df))); ax.set_yticklabels(role_df['agenda'], fontsize=7)
ax.set_xlabel('项目数'); ax.set_title('d  重塑性议题的出现频次', loc='left', fontsize=9, fontweight='bold')
for i,v in enumerate(role_df['count']): ax.text(v+0.3,i,str(v),va='center',fontsize=6.5)
ax.grid(axis='x', color='#E6E8EB', lw=0.5); ax.set_axisbelow(True)
save_fig(fig, 'fig5_compound_turns')

# Figure 4: outcomes
fig=plt.figure(figsize=(7.2,5.5))
gs=fig.add_gridspec(2,2, height_ratios=[0.9,1.2], wspace=0.44, hspace=0.48)
# totals
ax=fig.add_subplot(gs[0,0])
out_total=pd.DataFrame({'outcome':out_cols,'count':[df[c].sum() for c in out_cols]})
out_total.to_csv(SRC/'outcome_totals.csv', index=False, encoding='utf-8-sig')
ax.bar(range(len(out_total)), out_total['count'], color=[PALETTE['blue'],PALETTE['lightblue'],PALETTE['purple'],PALETTE['orange'],PALETTE['green']], width=0.7)
ax.set_xticks(range(len(out_total))); ax.set_xticklabels(['期刊\n论文','会议\n论文','专著','专利','获奖'], fontsize=7)
ax.set_ylabel('成果数量'); ax.set_title('a  结构化成果总量', loc='left', fontsize=9, fontweight='bold')
for i,v in enumerate(out_total['count']): ax.text(i, v+max(out_total['count'])*0.02, str(int(v)), ha='center', fontsize=6.8)
ax.grid(axis='y', color='#E6E8EB', lw=0.5); ax.set_axisbelow(True)
# outcome by project type mean
ax=fig.add_subplot(gs[0,1])
type_mean=df.groupby('search_category')[out_cols].mean().reindex(vc_project['project_type']).fillna(0)
type_mean.to_csv(SRC/'outcome_mean_by_project_type.csv', encoding='utf-8-sig')
bottom=np.zeros(len(type_mean))
colors=[PALETTE['blue'],PALETTE['lightblue'],PALETTE['purple'],PALETTE['orange'],PALETTE['green']]
for c,col in zip(out_cols,colors):
    ax.bar(range(len(type_mean)), type_mean[c], bottom=bottom, label=c.replace('数量',''), color=col, width=0.65)
    bottom += type_mean[c].values
ax.set_xticks(range(len(type_mean))); ax.set_xticklabels([wrap_label(x,5) for x in type_mean.index], rotation=0, fontsize=7)
ax.set_ylabel('平均成果数/项目'); ax.set_title('b  项目类型的平均成果结构', loc='left', fontsize=9, fontweight='bold')
ax.legend(fontsize=6.2, ncol=2, loc='upper right')
ax.grid(axis='y', color='#E6E8EB', lw=0.5); ax.set_axisbelow(True)
# outcome heatmap by orientation
ax=fig.add_subplot(gs[1,0])
ori_mean=df.groupby('research_orientations')[out_cols].mean().reindex(vc_orientation['research_orientation']).fillna(0)
ori_mean.to_csv(SRC/'outcome_mean_by_orientation.csv', encoding='utf-8-sig')
im=ax.imshow(ori_mean.values, cmap='Purples', aspect='auto')
ax.set_xticks(range(len(out_cols))); ax.set_xticklabels(['期刊','会议','专著','专利','获奖'], fontsize=7)
ax.set_yticks(range(len(ori_mean.index))); ax.set_yticklabels([wrap_label(x,5) for x in ori_mean.index], fontsize=7)
for i in range(ori_mean.shape[0]):
    for j in range(ori_mean.shape[1]):
        val=ori_mean.values[i,j]
        ax.text(j,i,f'{val:.1f}',ha='center',va='center',fontsize=6.2,color='white' if val>np.nanmax(ori_mean.values)*0.55 else '#222')
ax.set_title('c  问题取向的平均成果结构', loc='left', fontsize=9, fontweight='bold')
fig.colorbar(im, ax=ax, shrink=0.75, pad=0.02)
# non-paper outcomes from outcome_pathway tags
ax=fig.add_subplot(gs[1,1])
outpath=tag_outcome_path.copy()
select_order=['期刊论文','会议论文','专著','专利软著','软件数据库','标准导则','政策规划','人才培养','获奖']
outpath_map={row['tag']:row['count'] for _,row in outpath.iterrows()}
path_df=pd.DataFrame({'path':select_order,'count':[outpath_map.get(x,0) for x in select_order]}).sort_values('count', ascending=True)
path_df.to_csv(SRC/'outcome_pathway_tag_counts.csv', index=False, encoding='utf-8-sig')
ax.barh(range(len(path_df)), path_df['count'], color=PALETTE['teal'], height=0.65)
ax.set_yticks(range(len(path_df))); ax.set_yticklabels([wrap_label(x,5) for x in path_df['path']], fontsize=7)
ax.set_xlabel('涉及项目数'); ax.set_title('d  结题报告中的成果路径标签', loc='left', fontsize=9, fontweight='bold')
for i,v in enumerate(path_df['count']): ax.text(v+0.4,i,str(int(v)),va='center',fontsize=6.5)
ax.grid(axis='x', color='#E6E8EB', lw=0.5); ax.set_axisbelow(True)
save_fig(fig, 'fig6_outcome_pathways')

# Create manuscript tables
# Table 3 representative statistics
basic_summary = pd.DataFrame([
    ['有效项目数', summary['n_in_scope']],
    ['项目起始年范围', f"{summary['start_year_min']}–{summary['start_year_max']}"],
    ['项目结题年范围', f"{summary['end_year_min']}–{summary['end_year_max']}"],
    ['主要项目类型', f"{vc_project.iloc[0,0]} ({int(vc_project.iloc[0,1])})"],
    ['主要学科代码', f"{vc_discipline.iloc[0,0]} ({int(vc_discipline.iloc[0,1])})"],
    ['主要遗产对象', f"{vc_object.iloc[0,0]} ({int(vc_object.iloc[0,1])})"],
    ['主要问题取向', f"{vc_orientation.iloc[0,0]} ({int(vc_orientation.iloc[0,1])})"],
    ['主要方法取向', f"{vc_method.iloc[0,0]} ({int(vc_method.iloc[0,1])})"],
], columns=['指标','结果'])
basic_summary.to_csv(TAB/'table3_basic_result_summary.csv', index=False, encoding='utf-8-sig')

# Representative projects table: choose one high output or high confidence per turn type
reps=[]
for turn in vc_turn['turn_type'].head(6):
    sub=df[df['turn_type']==turn].copy()
    if sub.empty: continue
    sub['total_outputs']=sub[out_cols].sum(axis=1)
    row=sub.sort_values(['total_outputs','confidence'], ascending=[False,False]).iloc[0]
    reps.append({
        '研究转向': turn,
        '项目批准号': row['approval_no'],
        '项目名称': row.get('project_title') or row.get('project_name',''),
        '遗产对象': row['heritage_objects'],
        '问题取向': row['research_orientations'],
        '主要方法': row['primary_method_orientation'],
        '知识功能': row['primary_knowledge_function']
    })
rep_df=pd.DataFrame(reps)
rep_df.to_csv(TAB/'table4_representative_projects.csv', index=False, encoding='utf-8-sig')

print(json.dumps(summary, ensure_ascii=False, indent=2))
print('OUTPUT_DIR', str(OUT))

