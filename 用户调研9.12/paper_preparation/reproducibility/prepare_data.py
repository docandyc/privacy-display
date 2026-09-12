"""Paper-preparation audit only: preserve scores/exclusions; no inferential tests or manuscript writes.
Run from the project root after verify_scoring.cjs. Outputs stay in paper_preparation/.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict
import csv, hashlib, json, math, statistics, sys

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'privacy-display/webstudy'))
import analyze_study as rules
from assignment import assignment_for_registration_index, RATING_CONDITION_ORDER
SRC = ROOT / '用户调研9.12'
OUT = SRC / 'paper_preparation'
for d in ['audit', 'analysis_data', 'reproducibility']:
    (OUT / d).mkdir(exist_ok=True, parents=True)
data = json.loads((SRC / 'data.json').read_text())
basic = json.loads((SRC / 'cleaned/governance_summary.json').read_text())
for p, digest in basic['sha256'].items():
    assert hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == digest, f'Changed source: {p}'
score = json.loads((OUT / 'audit/scoring_recalculation.json').read_text())
assert not score['status_counts'].get('unexplained', 0)
score_rows = {(r['participant_id'], r['trial_index']): r for r in score['trial_audit']}
ps = {p['participant_id']: p for p in data['participants']}
formal_ids = sorted(pid for pid in ps if pid not in {1,2,3,4,5})
typing, ratings = defaultdict(list), defaultdict(list)
for key, dest in [('typing', typing), ('ratings', ratings)]:
    for r in data[key]:
        dest[r['participant_id']].append(dict(r, mask_meta_json=json.dumps(r['mask_meta'])))
    for rows in dest.values():
        rows.sort(key=lambda r:r.get('trial_index', r.get('order_index')))
included_ids = [pid for pid in formal_ids if not rules.participant_exclusions(ps[pid], typing[pid], ratings[pid])]
with (SRC / 'cleaned/participant_audit.csv').open(encoding='utf-8-sig') as f:
    prior_audit = {int(r['participant_id']): r for r in csv.DictReader(f)}
assert set(included_ids) == {pid for pid,r in prior_audit.items() if r['status']=='included'}
codes = {pid:prior_audit[pid]['participant_code'] for pid in included_ids}

def write(name, rows, fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader(); w.writerows(rows)

def dt(x): return datetime.fromisoformat(x.replace('Z', '+00:00'))
def eq(a,b): return a is not None and b is not None and math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-9)
def batch(p):
    day = p['started_at'][:10]
    return 'july' if day.startswith('2026-07') else 'sep08' if day=='2026-09-08' else 'sep10_12'
def latin(index):
    seq=[0,1,5,2,4,3]
    return [RATING_CONDITION_ORDER[(x+index)%6] for x in seq]

def signature(r):
    m=r['mask_meta']; a=m.get('anti_ocr',{})
    return {k:m.get(k) for k in ['mode','n','width','height','cycles','frame_count','per_cycle_slots','insert_inversion','inversion_alpha','epsilonPixels','gamma']} | {f'anti_{k}':a.get(k) for k in ['profile','stripe_width','stripe_alpha','glyph_alpha']}

checks=[]
def check(name, bad, n, scope='formal'):
    checks.append({'check':name,'scope':scope,'checked_units':n,'failures':len(bad),'participant_ids':';'.join(map(str,sorted(set(bad))))})
expected_configs={'control':(1,'none',False),'masked':(4,'mask+noise+anti-ocr+inversion',True), 'control_anchor':(1,'none',False),'n2_mask_noise':(2,'mask+noise',False),'n3_mask_noise':(3,'mask+noise',False),'n4_mask_noise':(4,'mask+noise',False),'n4_mask_only':(4,'mask-only',False),'deployed_full':(4,'mask+noise+anti-ocr+inversion',True)}
assignment_bad=[];typing_order_bad=[];rating_order_bad=[];repetition_bad=[];config_bad=[];duration_bad=[];latency_bad=[];timestamp_bad=[];view_clock_bad=[];meta_formula_bad=[];metadata_missing=[];refresh_bad=[]
event_audit=[];session_audit=[];config_groups=defaultdict(Counter)
for pid in formal_ids:
    p=ps[pid];t=typing[pid];rs=ratings[pid];sc=json.loads(p['screen_json']); a=assignment_for_registration_index(p['registration_index'])
    expected_order=['control','masked','masked','control'] if a['typing_order_index']==0 else ['masked','control','control','masked']
    if p['counterbalance_index']!=a['typing_order_index'] or p['rating_order_index']!=a['rating_order_index']: assignment_bad.append(pid)
    if [r['condition'] for r in t]!=expected_order or p['typing_order'] != ('ABBA' if a['typing_order_index']==0 else 'BAAB'): typing_order_bad.append(pid)
    if [r['condition_label'] for r in rs]!=latin(a['rating_order_index']):rating_order_bad.append(pid)
    reps=Counter()
    for r in t:
        reps[r['condition']]+=1
        if r['condition_repetition']!=reps[r['condition']]: repetition_bad.append(pid)
        if not eq(r['duration_s'],20):duration_bad.append(pid)
        if r['first_key_latency_ms'] is None or not 0<=r['first_key_latency_ms']<=r['duration_s']*1000:latency_bad.append(pid)
    start,end,consent=dt(p['started_at']),dt(p['submitted_at']),dt(p['consented_at'])
    if not start<=consent<=end:timestamp_bad.append(pid)
    if sc.get('refresh_runs') is None or len(sc['refresh_runs'])!=3 or any(run.get('hz',0)<200 for run in sc.get('refresh_runs',[])):refresh_bad.append(pid)
    prev=start
    for r in rs:
        vstart,vend=dt(r['view_started_at']),dt(r['view_submitted_at'])
        if not prev<=vstart<=vend<=end:timestamp_bad.append(pid)
        prev=vend
        if abs((vend-vstart).total_seconds()*1000-r['view_duration_ms'])>5:view_clock_bad.append(pid)
    for kind,rows in [('typing',t),('rating',rs)]:
        for r in rows:
            cond=r.get('condition',r.get('condition_label'));m=r['mask_meta'];n,components,inversion=expected_configs[cond]
            if r['n']!=n or r['requested_n']!=n or r['components']!=components or m.get('n')!=n or m.get('insert_inversion')!=inversion or m.get('mode')!=('source_control' if n==1 else 'temporal'):config_bad.append(pid)
            if inversion and (m.get('cycles')!=6 or m.get('inversion_alpha')!=.2 or m.get('anti_ocr',{}).get('profile')!='strong' or m.get('anti_ocr',{}).get('stripe_alpha')!=.1 or m.get('anti_ocr',{}).get('glyph_alpha')!=.12):config_bad.append(pid)
            config_groups[(kind,cond)][json.dumps(signature(r),sort_keys=True)]+=1
            needed=['timing_intervals','dropped_frames','dropped_frame_rate','mean_frame_interval_ms','observed_refresh_hz','observed_effective_cycle_hz','observed_full_cycle_hz']
            if any(m.get(k) is None for k in needed):metadata_missing.append(pid)
            else:
                denom=m['timing_intervals']+m['dropped_frames']
                if not all([eq(m['dropped_frame_rate'], m['dropped_frames']/denom if denom else 0),eq(m['observed_refresh_hz'],1000/m['mean_frame_interval_ms']),eq(m['observed_effective_cycle_hz'],m['observed_refresh_hz']/n),eq(m['observed_full_cycle_hz'],m['observed_refresh_hz']/m['per_cycle_slots'])]):meta_formula_bad.append(pid)
            event_audit.append({'participant_id':pid,'participant_code':codes.get(pid,''),'included':pid in codes,'batch_id':batch(p),'kind':kind,'condition':cond,'order_index':r.get('trial_index',r.get('order_index')),'view_duration_ms':r.get('view_duration_ms'),**{k:m.get(k) for k in ['observed_effective_cycle_hz','observed_full_cycle_hz','dropped_frame_rate','long_frame_intervals','max_frame_interval_ms']},'rating_base_below_50hz':kind=='rating' and n>1 and m.get('observed_effective_cycle_hz',math.inf)<50,'drop_over_1pct_review_only':m.get('dropped_frame_rate',0)>.01})
    session_audit.append({'participant_id':pid,'participant_code':codes.get(pid,''),'included':pid in codes,'date_utc':p['started_at'][:10],'batch_id':batch(p),'typing_order':p['typing_order'],'rating_order_index':p['rating_order_index'],'browser_version':p['user_agent'].split('Chrome/')[-1].split(' ')[0],'color_depth':sc.get('color_depth'),'screen_width':sc.get('width'),'screen_height':sc.get('height'),'device_pixel_ratio':sc.get('device_pixel_ratio'),'fullscreen_at_submission':sc.get('fullscreen'),'environment_confirmed':p['environment_confirmed'],'refresh_hz':p['refresh_hz'],'session_duration_min':(end-start).total_seconds()/60,'boundary_space_compatible_trials':sum(score_rows[(pid,r['trial_index'])]['status']!='direct_match' for r in t)})
for name,bad,n in [('assignment_indexes',assignment_bad,len(formal_ids)),('typing_order',typing_order_bad,len(formal_ids)),('latin_rating_order',rating_order_bad,len(formal_ids)),('typing_repetition_order',repetition_bad,len(formal_ids)*4),('condition_and_profile',config_bad,len(event_audit)),('typing_duration_20s',duration_bad,len(formal_ids)*4),('first_key_latency_range_and_presence',latency_bad,len(formal_ids)*4),('session_and_rating_timestamp_order',timestamp_bad,len(formal_ids)),('rating_duration_clock_within_5ms',view_clock_bad,len(formal_ids)*6),('timing_metadata_formulas',meta_formula_bad,len(event_audit)),('timing_metadata_completeness',metadata_missing,len(event_audit)),('three_refresh_runs_above_200hz',refresh_bad,len(formal_ids))]:check(name,bad,n)
write('audit/protocol_checks.csv',checks)
write('audit/session_audit.csv',session_audit)
write('audit/event_timing_audit.csv',event_audit)
write('audit/score_storage_audit.csv',[{k:v for k,v in r.items() if k!='compatible_candidates'}|{'compatible_candidates':json.dumps(r['compatible_candidates'])} for r in score['trial_audit']])
write('audit/configuration_signatures.csv',[{'kind':kind,'condition':cond,'trials':n,'signature_json':sig} for (kind,cond),counts in config_groups.items() for sig,n in counts.items()])
missing=[]
for scope,ids in [('formal',formal_ids),('included',included_ids)]:
    for field in ['name','student_id','major','age','gender','glasses','consented_at','started_at','submitted_at','environment_confirmed']:
        missing.append({'scope':scope,'field':field,'n':len(ids),'missing':sum(ps[pid].get(field) in (None,'') for pid in ids)})
write('audit/missingness.csv',missing)
balances=[]
for scope,ids in [('formal',formal_ids),('included',included_ids)]:
    for order in ['ABBA','BAAB']:
        for row in range(6):balances.append({'scope':scope,'typing_order':order,'rating_order_index':row,'n':sum(ps[pid]['typing_order']==order and ps[pid]['rating_order_index']==row for pid in ids)})
write('audit/counterbalance.csv',balances)

# Analysis datasets omit source PID, registration index, UUID, absolute dates/times, device fingerprints and free text.
participants=[]; trials=[]; means=[]; rlong=[]; rwide=[]; sensitivity=[]
low_rating_ids={r['participant_id'] for r in event_audit if r['included'] and r['rating_base_below_50hz']}
for pid in included_ids:
    p=ps[pid];code=codes[pid];b=batch(p)
    participants.append({'participant_code':code,'batch_id':b,'vision_correction':p['glasses'],'typing_order':p['typing_order'],'rating_order_index':p['rating_order_index']})
    meanrow={'participant_code':code,'batch_id':b,'typing_order':p['typing_order']}
    for cond in ['control','masked']:
        rows=[r for r in typing[pid] if r['condition']==cond]
        for metric in rules.TYPING_METRICS:meanrow[f'{cond}_{metric}']=statistics.mean(r[metric] for r in rows)
    for metric in rules.TYPING_METRICS:meanrow[f'delta_{metric}']=meanrow[f'masked_{metric}']-meanrow[f'control_{metric}']
    means.append(meanrow)
    for r in typing[pid]:
        keep=['condition','trial_index','condition_repetition','n','requested_n','components','duration_s','accuracy','wpm','cpm','attempted_chars','attempted_letters','correct_chars','correct_letters','total_chars','edit_distance','aligned_target_chars','msd_error_rate','scoring_method','first_key_latency_ms']
        trials.append({'participant_code':code,'batch_id':b,**{k:r[k] for k in keep},'text_storage_status':score_rows[(pid,r['trial_index'])]['status']})
    rw={'participant_code':code,'batch_id':b}
    for r in ratings[pid]:
        dims={'readability':r['readability'],'stability':r['flicker'],'immediate_comfort':r['fatigue']}
        rlong.append({'participant_code':code,'batch_id':b,'condition':r['condition_label'],'order_index':r['order_index'],'n':r['n'],'view_duration_ms':r['view_duration_ms'],**dims,'observed_base_cycle_hz':r['mask_meta']['observed_effective_cycle_hz'],'observed_full_cycle_hz':r['mask_meta']['observed_full_cycle_hz'],'dropped_frame_rate':r['mask_meta']['dropped_frame_rate']})
        for k,v in dims.items():rw[f"{r['condition_label']}_{k}"]=v
    rwide.append(rw)
    sensitivity.append({'participant_code':code,'main_sample':True,'batch_id':b,'rating_sensitivity_base_ge_50hz':pid not in low_rating_ids,'note':'rating-only exploratory subset; main sample unchanged'})
for name,rows in [('participants.csv',participants),('typing_trials.csv',trials),('typing_participant_means.csv',means),('rating_trials.csv',rlong),('rating_participant_wide.csv',rwide),('sensitivity_membership.csv',sensitivity)]:write('analysis_data/'+name,rows)

# Review flags are not new exclusion rules.
issues=[]
def issue(key,scope,evidence,action):issues.append({'issue':key,'scope':scope,'evidence':evidence,'action':action})
issue('batch_environment_change','formal','July: Chrome147/30bit; Sep08: Chrome147/32bit; Sep10-12: Chrome129/24bit','Keep batch_id; verify lab logs and use prespecified paired comparisons plus clearly exploratory batch sensitivity later; do not infer physical monitor identity from screen fields.')
issue('boundary_whitespace_removed','typing',f"{score['status_counts'].get('compatible_with_stripped_boundary_spaces',0)} of {len(data['typing'])} trials compatible with trimmed boundary spaces; zero unexplained score cases",'Preserve stored browser scores. Do not overwrite scores from trimmed text or present inferred padding as observed keystrokes.')
issue('rating_low_observed_base_cycle','included ratings','source pid '+','.join(map(str,sorted(low_rating_ids))),'Keep main exclusions unchanged; prepare complete-participant rating sensitivity removing affected participants only from that sensitivity.')
for r in session_audit:
    if r['included'] and r['session_duration_min']>30:issue('long_session_review_only',r['participant_code'],f"{r['session_duration_min']:.2f} minutes",'Retain: total session time includes pauses and is not a preregistered exclusion.')
for r in rlong:
    if r['condition']=='control_anchor' and r['readability']==1:issue('anchor_readability_one',r['participant_code'],'Unmasked anchor readability=1','Retain; the original plan explicitly forbids requiring anchor score=5.')
write('audit/review_flags.csv',issues)

def stats(values):
    return {'n':len(values),'min':min(values),'median':statistics.median(values),'max':max(values)} if values else {'n':0}
bybatch=[]
for b in sorted({batch(ps[pid]) for pid in formal_ids}):
    ids=[pid for pid in formal_ids if batch(ps[pid])==b];inc=[pid for pid in ids if pid in codes]
    bybatch.append({'batch_id':b,'formal_n':len(ids),'included_n':len(inc),'excluded_n':len(ids)-len(inc),'typing_ABBA':sum(ps[pid]['typing_order']=='ABBA' for pid in inc),'typing_BAAB':sum(ps[pid]['typing_order']=='BAAB' for pid in inc)})
write('audit/batch_summary.csv',bybatch)
included_events=[r for r in event_audit if r['included']]
summary={'snapshot':'9.12 paper preparation','raw_n':len(ps),'formal_n':len(formal_ids),'included_n':len(included_ids),'new_exclusions':0,'protocol_check_failures':{r['check']:r['failures'] for r in checks if r['failures']},'scoring_status_all':score['status_counts'],'scoring_status_included':dict(Counter(score_rows[(pid,r['trial_index'])]['status'] for pid in included_ids for r in typing[pid])),'scoring_affected_included_participants':sum(any(score_rows[(pid,r['trial_index'])]['status']!='direct_match' for r in typing[pid]) for pid in included_ids),'vision_correction':dict(Counter(ps[pid]['glasses'] for pid in included_ids)),'typing_order_formal':dict(Counter(ps[pid]['typing_order'] for pid in formal_ids)),'typing_order_included':dict(Counter(ps[pid]['typing_order'] for pid in included_ids)),'rating_low_base_cycle_source_ids':sorted(low_rating_ids),'rating_sensitivity_n':len(included_ids)-len(low_rating_ids),'batches':bybatch,'timing_by_condition':{cond:{'drop_rate':stats([r['dropped_frame_rate'] for r in included_events if r['kind']=='rating' and r['condition']==cond]),'base_cycle_hz':stats([r['observed_effective_cycle_hz'] for r in included_events if r['kind']=='rating' and r['condition']==cond]),'max_interval_ms':stats([r['max_frame_interval_ms'] for r in included_events if r['kind']=='rating' and r['condition']==cond]),'drop_over_1pct':sum(r['drop_over_1pct_review_only'] for r in included_events if r['kind']=='rating' and r['condition']==cond)} for cond in RATING_CONDITION_ORDER},'all_scored_typing_20_seconds':not duration_bad,'included_first_key_missing_or_invalid':sum(pid in codes for pid in latency_bad),'typing_target_lengths_formal':dict(Counter(len(r['target_text']) for pid in formal_ids for r in typing[pid])),'rating_stimulus_lengths_formal':dict(Counter(len(r['stimulus_text']) for pid in formal_ids for r in ratings[pid])),'typing_target_exhausted_included':sum(r['attempted_chars']>=r['total_chars'] for pid in included_ids for r in typing[pid]),'long_session_source_ids':[r['participant_id'] for r in session_audit if r['included'] and r['session_duration_min']>30]}
(OUT/'audit/preparation_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')

# Explicit dictionary for the analysis files, including direction and aggregation.
def describe(field):
    common={'participant_code':'本轮匿名代号；与既有 P001–P106 一致，原始 pid 映射仅见本地 audit。','batch_id':'july=7月；sep08=9月8日；sep10_12=9月10/12日。保留采集批次，不能据此分离日期、浏览器、色深的因果作用。','vision_correction':'glasses=框架眼镜；contacts=隐形眼镜；none=无矫正。','typing_order':'ABBA 或 BAAB，A=control、B=masked。','rating_order_index':'六阶平衡拉丁方行索引，0–5。','condition':'条件编码；typing 为 control/masked；rating 六种，参见分析计划。','trial_index':'计分打字呈现序号，0–3。','condition_repetition':'该打字条件第几次重复，1或2。','n':'实际子帧层数，control=1。','requested_n':'请求子帧层数；正式模式不自适应降低。','components':'存储的显示组件组合。','duration_s':'浏览器计分时长，秒。','accuracy':'MSD准确率，0–1，越高越好；不是简单 correct_chars/attempted_chars。','wpm':'正确字符/5/分钟，越高表示更快；结合准确率解释。','cpm':'正确字符/分钟，等于5×WPM，非独立的第二项速度证据。','attempted_chars':'计分时原始输入字符数，含空格。','attempted_letters':'计分时非空格输入字符数。','correct_chars':'最优前缀对齐中匹配字符数，含空格。','correct_letters':'对齐中匹配的非空格字符数。','total_chars':'计分时目标长度。','edit_distance':'最优目标前缀与输入的 Levenshtein 编辑距离。','aligned_target_chars':'选择的最优目标前缀长度。','msd_error_rate':'编辑距离/max(对齐前缀长度,尝试字符数,1)。','scoring_method':'原始计分版本 msd_target_prefix_v1。','first_key_latency_ms':'输入启用至首次非空输入的毫秒数；更短不自动表示更佳。','text_storage_status':'direct_match=导出文本可直接复算；compatible_with_stripped_boundary_spaces=与服务端去边界空格机制兼容，原始分数保留。','order_index':'评分呈现顺序，0–5。','view_duration_ms':'每个评分条件观看时长，毫秒。','readability':'可读性，1–5，越高越清晰。','stability':'稳定感，原字段 flicker，1–5，越高表示越少闪烁，不反向计分。','immediate_comfort':'即时视觉舒适感，原字段 fatigue，1–5，越高越舒适；不是临床疲劳量表。','observed_base_cycle_hz':'浏览器观测刷新率/n，Hz。','observed_full_cycle_hz':'浏览器观测刷新率/每周期时隙数；含反色的n=4配置分母为5，Hz。','dropped_frame_rate':'估计丢帧数/(已记录帧间隔数+估计丢帧数)，0–1。','main_sample':'原有规则纳入，全部为True。','rating_sensitivity_base_ge_50hz':'仅用于探索性评分敏感性分析，所有评分条件基本周期均≥50Hz的参与者。','note':'敏感性样本说明。'}
    if field in common:return common[field]
    for prefix in ['control_','masked_','delta_']:
        if field.startswith(prefix) and field[len(prefix):] in common:
            return ('两次条件内算术均值。' if prefix!='delta_' else 'masked条件均值减control条件均值。')+common[field[len(prefix):]]
    for cond in RATING_CONDITION_ORDER:
        if field.startswith(cond+'_'):return '条件 '+cond+' 的单次评分；'+common[field[len(cond)+1:]]
    raise ValueError('Missing dictionary: '+field)
dictionary=[]
for path in sorted((OUT/'analysis_data').glob('*.csv')):
    with path.open(encoding='utf-8-sig') as f:
        reader=csv.DictReader(f);rows=list(reader)
        assert len({r['participant_code'] for r in rows})==len(included_ids)
        for field in reader.fieldnames:dictionary.append({'file':path.name,'field':field,'definition':describe(field),'missing_values':sum(r[field]=='' for r in rows)})
        assert not {'participant_id','registration_index','student_id','name','session_uuid','user_agent','screen_json','target_text','typed_text'} & set(reader.fieldnames)
write('data_dictionary.csv',dictionary)
inputs=[SRC/'data.json',SRC/'privacy_display_study.csv',SRC/'cleaned/governance_summary.json',SRC/'cleaned/participant_audit.csv',ROOT/'用户调研实验结果/数据治理报告.md',ROOT/'paper/main.tex',ROOT/'paper-Chinese/main.tex']+[ROOT/'privacy-display/webstudy'/f for f in ['analyze_study.py','assignment.py','server.py','README.md','static/typing.js','static/design.js','static/mask.js','static/app.js','static/pseudoword.js']]
manifest={'created_at_utc':datetime.now(timezone.utc).isoformat(),'source_generated_at':data['generated_at'],'inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'policy':'Do not edit raw inputs or manuscript. Recorded scores retained; no newly applied exclusions; no inferential statistics.'}
(OUT/'audit/input_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='timing_by_condition'},ensure_ascii=False,indent=2))
