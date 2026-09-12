// Run from the project root. Reuses the unchanged browser scorer on every raw trial.
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = process.cwd();
const context = {window: {}};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(root, 'privacy-display/webstudy/static/typing.js'), 'utf8'), context);
const data = JSON.parse(fs.readFileSync(path.join(root, '用户调研9.12/data.json'), 'utf8'));
const mismatches = [];
const fieldCounts = {};
const trialAudit = [];
function matches(row, scored) {
 return Object.entries(scored).every(([key, value]) => typeof value === "number" ? Number.isFinite(row[key]) && Math.abs(row[key] - value) <= 1e-10 * Math.max(1, Math.abs(value)) : row[key] === value);
}
for (const row of data.typing) {
  const result = context.window.Typing.scoreTyping(row.target_text, row.typed_text, row.duration_s);
  const directMatch = matches(row, result);
  const missing = row.attempted_chars - row.typed_text.length;
  const candidates = [];
  if (!directMatch && Number.isInteger(missing) && missing > 0 && missing <= 4) {
    for (let leading = 0; leading <= missing; leading++) {
      const candidate = ' '.repeat(leading) + row.typed_text + ' '.repeat(missing-leading);
      if (matches(row, context.window.Typing.scoreTyping(row.target_text, candidate, row.duration_s)))
        candidates.push({leading_spaces:leading, trailing_spaces:missing-leading});
    }
  }
  trialAudit.push({participant_id:row.participant_id, trial_index:row.trial_index, direct_match:directMatch,
    status:directMatch ? 'direct_match' : candidates.length ? 'compatible_with_stripped_boundary_spaces' : 'unexplained',
    missing_boundary_characters:missing, compatible_candidates:candidates});
  for (const [field, expected] of Object.entries(result)) {
    fieldCounts[field] = (fieldCounts[field] || 0) + 1;
    const actual = row[field];
    const ok = typeof expected === 'number'
      ? Number.isFinite(actual) && Math.abs(actual - expected) <= 1e-10 * Math.max(1, Math.abs(expected))
      : actual === expected;
    if (!ok) mismatches.push({participant_id:row.participant_id, trial_index:row.trial_index, field, actual, expected});
  }
}
const report = {checked_trials:data.typing.length, checked_fields:fieldCounts, mismatch_count:mismatches.length, mismatches, trial_audit:trialAudit, status_counts:trialAudit.reduce((a,r)=>(a[r.status]=(a[r.status]||0)+1,a),{})};
fs.writeFileSync(path.join(root, '用户调研9.12/paper_preparation/audit/scoring_recalculation.json'), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({checked_trials:report.checked_trials, fields_per_trial:Object.keys(fieldCounts).length, mismatch_count:mismatches.length,status_counts:report.status_counts}));
if (report.status_counts.unexplained) process.exitCode = 1;
