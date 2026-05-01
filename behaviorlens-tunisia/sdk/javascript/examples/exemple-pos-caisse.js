/**
 * Exemple — Intégration caisse POS commerce
 * ===========================================
 * Plugin pour logiciel de caisse tunisien (Sema, WinPos, etc.)
 * Envoie chaque transaction au framework en temps réel.
 */
import { BehaviorLensClient } from '../behaviorlens-sdk.js'

class POSPlugin {
  constructor(storeId, regionName) {
    this.storeId = storeId
    this.regionName = regionName
    this.client = new BehaviorLensClient('http://localhost:8000')
  }

  async init(email, password) {
    await this.client.login(email, password)
    this.client.useModule('commerce')
    console.log(`[POS] Plugin initialisé pour commerce #${this.storeId} — ${this.regionName}`)
  }

  async onSale(transaction) {
    // Appelé à chaque vente depuis le logiciel de caisse
    const total = transaction.quantity * transaction.unitPrice

    await this.client.push({
      regionName: this.regionName,
      metricName: 'pos_vente',
      metricValue: total,
      rawData: JSON.stringify({
        store_id: this.storeId,
        product: transaction.product,
        qty: transaction.quantity,
        price: transaction.unitPrice,
        category: transaction.category,
      }),
      ageGroup: transaction.customerAge || null,
    })

    console.log(`  🧾 Vente: ${transaction.product} x${transaction.quantity} = ${total.toFixed(3)} TND`)
  }

  async onDayClose(summary) {
    // Envoi du bilan journalier
    await this.client.push({
      regionName: this.regionName,
      metricName: 'bilan_journalier',
      metricValue: summary.totalRevenue,
      rawData: JSON.stringify(summary),
    })
    console.log(`  📊 Bilan journalier: ${summary.totalRevenue.toFixed(3)} TND`)
  }
}

// Simulation d'une journée de ventes
const pos = new POSPlugin(1, 'sfax')
await pos.init('admin@behaviorlens.tn', 'admin123')

const ventes = [
  { product: 'Pain', quantity: 10, unitPrice: 0.32, category: 'Alimentation' },
  { product: 'Lait', quantity: 5,  unitPrice: 1.80, category: 'Laitier' },
  { product: 'Huile', quantity: 2, unitPrice: 8.50, category: 'Alimentation', customerAge: '36-50' },
  { product: 'Sucre', quantity: 3, unitPrice: 0.98, category: 'Alimentation' },
]

for (const vente of ventes) {
  await pos.onSale(vente)
}

await pos.onDayClose({
  totalRevenue: ventes.reduce((s, v) => s + v.quantity * v.unitPrice, 0),
  transactionCount: ventes.length,
  date: new Date().toISOString().split('T')[0],
})
