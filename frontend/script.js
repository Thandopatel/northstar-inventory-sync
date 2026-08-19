// TODO: frontend logic
const API_BASE = 'http://127.0.0.1:8000';

// Submit Webhook
document.getElementById('webhookForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const sku = document.getElementById('webhookSku').value;
  const product_name = document.getElementById('productName').value;
  const quantity = parseInt(document.getElementById('quantity').value, 10);
  const resultDiv = document.getElementById('webhookResult');

  try {
    const res = await fetch(`${API_BASE}/api/v1/webhooks/inventory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sku, product_name, quantity })
    });
    const data = await res.json();
    resultDiv.style.display = 'block';
    resultDiv.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    resultDiv.style.display = 'block';
    resultDiv.textContent = `Error connecting to backend: ${err.message}`;
  }
});

// Lookup Stock
document.getElementById('stockForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const sku = document.getElementById('checkSku').value;
  const resultDiv = document.getElementById('stockResult');

  try {
    const res = await fetch(`${API_BASE}/api/v1/stock/${sku}`);
    const data = await res.json();
    resultDiv.style.display = 'block';

    if (res.ok) {
      const badgeClass = data.in_stock ? 'in-stock' : 'out-of-stock';
      const badgeText = data.in_stock ? 'IN STOCK' : 'OUT OF STOCK';
      resultDiv.innerHTML = `
        <div>Status: <span class="badge ${badgeClass}">${badgeText}</span></div>
        <div style="margin-top: 8px;">SKU: ${data.sku}</div>
        <div>Quantity: ${data.quantity}</div>
      `;
    } else {
      resultDiv.textContent = JSON.stringify(data, null, 2);
    }
  } catch (err) {
    resultDiv.style.display = 'block';
    resultDiv.textContent = `Error connecting to backend: ${err.message}`;
  }
});