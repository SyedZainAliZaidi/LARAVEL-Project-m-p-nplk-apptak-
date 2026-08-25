<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Admin — Discount & Pricing Rules</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; background: #f5f5f5; }
  h1 { color: #1a4d2e; }
  table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; margin-bottom: 30px; }
  th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 14px; }
  th { background: #1a4d2e; color: white; }
  .badge { padding: 3px 8px; border-radius: 4px; font-size: 12px; }
  .active { background: #d4edda; color: #155724; }
  .inactive { background: #f8d7da; color: #721c24; }
  form { background: white; padding: 20px; border-radius: 8px; }
  label { display: block; margin-top: 12px; font-weight: bold; font-size: 14px; }
  input, select, textarea { width: 100%; padding: 8px; margin-top: 4px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
  button { background: #1a4d2e; color: white; border: none; padding: 10px 18px; border-radius: 4px; cursor: pointer; margin-top: 16px; }
  button:hover { background: #123a22; }
  button.delete-btn { background: #b02a37; padding: 4px 10px; font-size: 12px; margin: 0; }
  #msg { padding: 10px; border-radius: 6px; margin-bottom: 16px; display: none; }
  #msg.success { background: #d4edda; color: #155724; display: block; }
  #msg.error { background: #f8d7da; color: #721c24; display: block; }
</style>
</head>
<body>

<h1>Admin — Discount & Pricing Rules</h1>
<p>Create, view, and remove discount/promo rules. No code changes required.</p>

<div id="msg"></div>

<table>
  <thead>
    <tr>
      <th>Name</th><th>Promo Code</th><th>Type</th><th>Value</th>
      <th>Valid From</th><th>Valid Until</th><th>Status</th><th></th>
    </tr>
  </thead>
  <tbody id="rules-body"></tbody>
</table>

<h2>Add New Rule</h2>
<form id="rule-form">
  <label>Name</label>
  <input type="text" id="name" required placeholder="e.g. Winter Promo">

  <label>Promo Code (optional)</label>
  <input type="text" id="promo_code" placeholder="e.g. WINTER20">

  <label>Discount Type</label>
  <select id="discount_type">
    <option value="percentage">Percentage (%)</option>
    <option value="fixed">Fixed Amount (Rs.)</option>
  </select>

  <label>Discount Value</label>
  <input type="number" id="discount_value" step="0.01" required placeholder="e.g. 15">

  <label>Valid From</label>
  <input type="date" id="valid_from" required>

  <label>Valid Until</label>
  <input type="date" id="valid_until" required>

  <label>Eligibility Criteria (optional)</label>
  <textarea id="eligibility_criteria" rows="2" placeholder="e.g. First-time customers only"></textarea>

  <label><input type="checkbox" id="is_active" checked style="width:auto; display:inline;"> Active</label>

  <button type="submit">Create Rule</button>
</form>

<script>
const API = '/api';

function showMsg(text, type) {
  const el = document.getElementById('msg');
  el.textContent = text;
  el.className = type;
  setTimeout(() => { el.style.display = 'none'; }, 4000);
}

async function loadRules() {
  const res = await fetch(`${API}/discount-rules`);
  const rules = await res.json();
  const tbody = document.getElementById('rules-body');

  if (rules.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8">No discount rules yet.</td></tr>';
    return;
  }

  tbody.innerHTML = rules.map(r => `
    <tr>
      <td>${r.name}</td>
      <td>${r.promo_code ?? '—'}</td>
      <td>${r.discount_type}</td>
      <td>${r.discount_type === 'percentage' ? r.discount_value + '%' : 'Rs. ' + r.discount_value}</td>
      <td>${r.valid_from}</td>
      <td>${r.valid_until}</td>
      <td><span class="badge ${r.is_active ? 'active' : 'inactive'}">${r.is_active ? 'Active' : 'Inactive'}</span></td>
      <td><button class="delete-btn" onclick="deleteRule(${r.id})">Delete</button></td>
    </tr>
  `).join('');
}

document.getElementById('rule-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const payload = {
    name: document.getElementById('name').value,
    promo_code: document.getElementById('promo_code').value || null,
    discount_type: document.getElementById('discount_type').value,
    discount_value: parseFloat(document.getElementById('discount_value').value),
    valid_from: document.getElementById('valid_from').value,
    valid_until: document.getElementById('valid_until').value,
    eligibility_criteria: document.getElementById('eligibility_criteria').value || null,
    is_active: document.getElementById('is_active').checked,
  };

  const res = await fetch(`${API}/discount-rules`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (res.ok) {
    showMsg('Rule created successfully.', 'success');
    e.target.reset();
    document.getElementById('is_active').checked = true;
    loadRules();
  } else {
    const err = await res.json();
    showMsg(err.message || 'Something went wrong.', 'error');
  }
});

async function deleteRule(id) {
  if (!confirm('Delete this rule?')) return;
  const res = await fetch(`${API}/discount-rules/${id}`, { method: 'DELETE' });
  if (res.ok) {
    showMsg('Rule deleted.', 'success');
    loadRules();
  } else {
    showMsg('Failed to delete rule.', 'error');
  }
}

loadRules();
</script>

</body>
</html>