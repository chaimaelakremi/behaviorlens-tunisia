/**
 * Exemple — Intégration application mobile (React Native / PWA)
 * ==============================================================
 * Comment une app mobile tunisienne pousse des données vers le framework.
 */
import { BehaviorLensClient, BehaviorLensModule } from '../behaviorlens-sdk.js'

class MobileAppModule extends BehaviorLensModule {
  static DOMAIN = 'mobile_app'
  static NAME = 'Application Mobile Citoyenne'
  static DESCRIPTION = 'Collecte via app mobile citoyens tunisiens'

  async collect() {
    // Simuler des actions utilisateurs depuis l'app mobile
    const userActions = [
      { action: 'signalement_voirie', region: 'tunis',    age: '26-35', gender: 'M' },
      { action: 'avis_commerce',      region: 'sfax',     age: '18-25', gender: 'F' },
      { action: 'sondage_transport',  region: 'sousse',   age: '36-50', gender: 'M' },
      { action: 'photo_quartier',     region: 'monastir', age: '<18',   gender: 'F' },
    ]

    for (const action of userActions) {
      await this.push({
        regionName: action.region,
        metricName: action.action,
        metricValue: 1,
        ageGroup: action.age,
        gender: action.gender,
        rawData: JSON.stringify({ source: 'mobile', timestamp: Date.now() }),
      })
      console.log(`  ✓ ${action.action} | ${action.region}`)
    }
  }
}

// Usage
const client = new BehaviorLensClient('http://localhost:8000')
await client.login('admin@behaviorlens.tn', 'admin123')

const module = new MobileAppModule(client)
await module.register()
await module.collect()

const stats = await client.getStats()
console.log(`\nFramework total: ${stats.total_records} enregistrements`)
