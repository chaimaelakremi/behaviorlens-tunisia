/**
 * BehaviorLens Tunisia — JavaScript SDK
 * ======================================
 * Compatible navigateur (ES Modules) et Node.js.
 *
 * @example
 * import { BehaviorLensClient } from './behaviorlens-sdk.js'
 *
 * const client = new BehaviorLensClient('http://localhost:8000')
 * await client.login('admin@behaviorlens.tn', 'admin123')
 * await client.push({ moduleDomain: 'social_media', metricName: 'mentions', metricValue: 450 })
 */

export class BehaviorLensClient {
  static REGIONS = {
    tunis: 1, ariana: 2, ben_arous: 3, manouba: 4,
    nabeul: 5, zaghouan: 6, bizerte: 7, beja: 8,
    jendouba: 9, kef: 10, siliana: 11, kairouan: 12,
    kasserine: 13, sidi_bouzid: 14, sousse: 15, monastir: 16,
    mahdia: 17, sfax: 18, gafsa: 19, tozeur: 20,
    kebili: 21, gabes: 22, medenine: 23, tataouine: 24,
  }

  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl.replace(/\/$/, '')
    this.token = null
    this._moduleDomain = null
    this._batch = []
  }

  // ── Auth ────────────────────────────────────────────────────────────────────

  async login(email, password) {
    const res = await this._request('POST', '/api/auth/login', { email, password }, false)
    this.token = res.access_token
    console.log(`[BehaviorLens] Connecté en tant que ${email}`)
    return this
  }

  setToken(token) {
    this.token = token
    return this
  }

  // ── Module ──────────────────────────────────────────────────────────────────

  async registerModule({ name, domain, description = '', apiKey = '' }) {
    const key = apiKey || crypto.randomUUID()
    const res = await this._request('POST', '/api/modules/register', {
      name, domain, description, api_key: key,
    })
    this._moduleDomain = domain
    console.log(`[BehaviorLens] Module '${domain}' enregistré (id=${res.id})`)
    return res
  }

  useModule(domain) {
    this._moduleDomain = domain
    return this
  }

  // ── Data push ───────────────────────────────────────────────────────────────

  /**
   * Envoie une donnée comportementale au framework.
   * @param {Object} opts
   * @param {string}  [opts.moduleDomain]  - domaine du module
   * @param {number}  [opts.regionId]      - id région (1-24)
   * @param {string}  [opts.regionName]    - nom région (ex: 'tunis', 'sfax')
   * @param {string}  opts.metricName      - nom de la métrique
   * @param {number}  [opts.metricValue]   - valeur numérique
   * @param {string}  [opts.rawData]       - JSON string données brutes
   * @param {string}  [opts.ageGroup]      - tranche d'âge
   * @param {string}  [opts.gender]        - genre
   */
  async push({ moduleDomain, regionId, regionName, metricName = 'event',
                metricValue, rawData, ageGroup, gender } = {}) {
    const domain = moduleDomain || this._moduleDomain
    if (!domain) throw new Error("moduleDomain requis — appelez useModule() ou passez moduleDomain")

    const rid = regionId ?? (regionName
      ? BehaviorLensClient.REGIONS[regionName.toLowerCase().replace(/ /g, '_')]
      : undefined)

    return this._request('POST', '/api/collect', {
      module_domain: domain,
      region_id: rid ?? null,
      metric_name: metricName,
      metric_value: metricValue ?? null,
      raw_data: rawData ?? null,
      age_group: ageGroup ?? null,
      gender: gender ?? null,
    })
  }

  // ── Batch ───────────────────────────────────────────────────────────────────

  addToBatch(opts) {
    this._batch.push(opts)
    return this
  }

  async flushBatch() {
    const results = []
    for (const item of this._batch) {
      try { results.push(await this.push(item)) }
      catch (e) { console.warn('[BehaviorLens] Batch item failed:', e.message) }
    }
    const count = this._batch.length
    this._batch = []
    console.log(`[BehaviorLens] Batch flushed: ${count} enregistrements`)
    return results
  }

  // ── Stats ───────────────────────────────────────────────────────────────────

  async getStats()         { return this._request('GET', '/api/stats') }
  async getStatsByModule() { return this._request('GET', '/api/stats/by-module') }
  async getStatsByRegion() { return this._request('GET', '/api/stats/by-region') }
  async getModules()       { return this._request('GET', '/api/modules') }

  // ── HTTP ────────────────────────────────────────────────────────────────────

  async _request(method, path, body = null, auth = true) {
    const headers = { 'Content-Type': 'application/json' }
    if (auth) {
      if (!this.token) throw new Error('Non authentifié — appelez login() d\'abord')
      headers['Authorization'] = `Bearer ${this.token}`
    }
    const res = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    })
    if (!res.ok) {
      const err = await res.text()
      throw new Error(`HTTP ${res.status}: ${err}`)
    }
    return res.json()
  }
}

/**
 * Classe de base pour créer un module BehaviorLens en JavaScript.
 *
 * @example
 * class MonModule extends BehaviorLensModule {
 *   static DOMAIN = 'mon_module'
 *   static NAME   = 'Mon Module'
 *
 *   async collect() {
 *     const data = await fetchMyData()
 *     for (const item of data) {
 *       await this.push({ metricName: 'ma_metrique', metricValue: item.value })
 *     }
 *   }
 * }
 */
export class BehaviorLensModule {
  static DOMAIN = ''
  static NAME = ''
  static DESCRIPTION = ''

  constructor(client) {
    this.client = client
    if (this.constructor.DOMAIN) {
      this.client.useModule(this.constructor.DOMAIN)
    }
  }

  async register() {
    return this.client.registerModule({
      name: this.constructor.NAME,
      domain: this.constructor.DOMAIN,
      description: this.constructor.DESCRIPTION,
    })
  }

  async push(opts) {
    return this.client.push({ moduleDomain: this.constructor.DOMAIN, ...opts })
  }

  async collect() {
    throw new Error('Implémenter collect() dans ta sous-classe')
  }

  async run(intervalMs = 0) {
    console.log(`[${this.constructor.DOMAIN}] Démarré`)
    await this.collect()
    if (intervalMs > 0) {
      setInterval(() => this.collect().catch(console.error), intervalMs)
    }
  }
}
