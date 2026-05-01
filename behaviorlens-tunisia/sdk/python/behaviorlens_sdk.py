"""
BehaviorLens Tunisia — Python SDK
==================================
Permet à n'importe quelle source de données d'intégrer le framework.

Usage rapide:
    from behaviorlens_sdk import BehaviorLensClient

    client = BehaviorLensClient(base_url="http://localhost:8000")
    client.login("admin@behaviorlens.tn", "admin123")
    client.push("social_media", region_id=1, metric_name="mentions", metric_value=120)
"""

import requests
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger("behaviorlens")


class BehaviorLensClient:
    """Client SDK pour le framework BehaviorLens Tunisia."""

    AGE_GROUPS = ["<18", "18-25", "26-35", "36-50", "51-65", ">65"]
    GENDERS = ["M", "F", "other", "unknown"]
    REGIONS = {
        "tunis": 1, "ariana": 2, "ben_arous": 3, "manouba": 4,
        "nabeul": 5, "zaghouan": 6, "bizerte": 7, "beja": 8,
        "jendouba": 9, "kef": 10, "siliana": 11, "kairouan": 12,
        "kasserine": 13, "sidi_bouzid": 14, "sousse": 15, "monastir": 16,
        "mahdia": 17, "sfax": 18, "gafsa": 19, "tozeur": 20,
        "kebili": 21, "gabes": 22, "medenine": 23, "tataouine": 24,
    }

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._token: Optional[str] = None
        self._module_domain: Optional[str] = None
        self._batch: List[Dict] = []

    # ── Auth ──────────────────────────────────────────────────────────────────

    def login(self, email: str, password: str) -> "BehaviorLensClient":
        r = requests.post(f"{self.base_url}/api/auth/login",
                          json={"email": email, "password": password},
                          timeout=self.timeout)
        r.raise_for_status()
        self._token = r.json()["access_token"]
        logger.info("Connecté à BehaviorLens (%s)", self.base_url)
        return self

    def set_token(self, token: str) -> "BehaviorLensClient":
        self._token = token
        return self

    # ── Module registration ───────────────────────────────────────────────────

    def register_module(self, name: str, domain: str,
                        description: str = "", api_key: str = "") -> Dict:
        """Enregistre ce module dans le framework."""
        import uuid
        payload = {
            "name": name,
            "domain": domain,
            "description": description,
            "api_key": api_key or str(uuid.uuid4()),
        }
        r = self._post("/api/modules/register", payload)
        self._module_domain = domain
        logger.info("Module '%s' enregistré (id=%s)", domain, r.get("id"))
        return r

    def use_module(self, domain: str) -> "BehaviorLensClient":
        """Sélectionne le module actif pour les pushes suivants."""
        self._module_domain = domain
        return self

    # ── Data push ─────────────────────────────────────────────────────────────

    def push(self,
             module_domain: Optional[str] = None,
             region_id: Optional[int] = None,
             region_name: Optional[str] = None,
             metric_name: str = "event",
             metric_value: Optional[float] = None,
             raw_data: Optional[str] = None,
             age_group: Optional[str] = None,
             gender: Optional[str] = None) -> Dict:
        """
        Envoie une donnée comportementale au framework.

        Args:
            module_domain: domaine du module (ex: "social_media")
            region_id: id de la région (1-24)
            region_name: nom de la région en minuscules (ex: "tunis", "sfax")
            metric_name: nom de la métrique (ex: "mentions", "vente", "humeur")
            metric_value: valeur numérique optionnelle
            raw_data: données brutes en JSON string
            age_group: tranche d'âge parmi AGE_GROUPS
            gender: genre parmi GENDERS
        """
        domain = module_domain or self._module_domain
        if not domain:
            raise ValueError("module_domain requis — appelez use_module() ou passez module_domain=")

        if region_name and not region_id:
            region_id = self.REGIONS.get(region_name.lower().replace(" ", "_"))

        payload = {
            "module_domain": domain,
            "region_id": region_id,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "raw_data": raw_data,
            "age_group": age_group,
            "gender": gender,
        }
        return self._post("/api/collect", payload)

    # ── Batch mode ────────────────────────────────────────────────────────────

    def add_to_batch(self, **kwargs) -> "BehaviorLensClient":
        """Ajoute un enregistrement au batch courant."""
        self._batch.append(kwargs)
        return self

    def flush_batch(self) -> List[Dict]:
        """Envoie tous les enregistrements du batch et vide la file."""
        results = []
        for item in self._batch:
            try:
                results.append(self.push(**item))
            except Exception as e:
                logger.warning("Batch item failed: %s — %s", item, e)
        sent = len(self._batch)
        self._batch.clear()
        logger.info("Batch flushed: %d enregistrements envoyés", sent)
        return results

    # ── Stats ─────────────────────────────────────────────────────────────────

    def get_stats(self) -> Dict:
        return self._get("/api/stats")

    def get_stats_by_module(self) -> List[Dict]:
        return self._get("/api/stats/by-module")

    def get_stats_by_region(self) -> List[Dict]:
        return self._get("/api/stats/by-region")

    def get_modules(self) -> List[Dict]:
        return self._get("/api/modules")

    # ── HTTP helpers ──────────────────────────────────────────────────────────

    def _headers(self) -> Dict:
        if not self._token:
            raise RuntimeError("Non authentifié — appelez login() d'abord")
        return {"Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json"}

    def _post(self, path: str, payload: Dict) -> Dict:
        r = requests.post(f"{self.base_url}{path}",
                          json=payload, headers=self._headers(),
                          timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _get(self, path: str) -> Any:
        r = requests.get(f"{self.base_url}{path}",
                         headers=self._headers(),
                         timeout=self.timeout)
        r.raise_for_status()
        return r.json()


class BehaviorLensModule:
    """
    Classe de base pour créer un module BehaviorLens.
    Hériter de cette classe pour créer ton propre collecteur.

    Exemple:
        class MonModule(BehaviorLensModule):
            DOMAIN = "mon_module"
            NAME = "Mon Module"

            def collect(self):
                data = fetch_my_data()
                for item in data:
                    self.push(metric_name="ma_metrique",
                              metric_value=item["value"],
                              region_name=item["region"])
    """

    DOMAIN: str = ""
    NAME: str = ""
    DESCRIPTION: str = ""

    def __init__(self, client: BehaviorLensClient):
        self.client = client
        if self.DOMAIN:
            self.client.use_module(self.DOMAIN)

    def register(self) -> Dict:
        return self.client.register_module(
            name=self.NAME,
            domain=self.DOMAIN,
            description=self.DESCRIPTION,
        )

    def push(self, **kwargs) -> Dict:
        return self.client.push(module_domain=self.DOMAIN, **kwargs)

    def collect(self):
        raise NotImplementedError("Implémenter collect() dans ta sous-classe")

    def run(self, interval_seconds: int = 0):
        """Lance la collecte, en boucle si interval_seconds > 0."""
        logger.info("Module '%s' démarré", self.DOMAIN)
        while True:
            try:
                self.collect()
            except Exception as e:
                logger.error("Erreur collecte '%s': %s", self.DOMAIN, e)
            if interval_seconds <= 0:
                break
            logger.info("Prochain cycle dans %ds...", interval_seconds)
            time.sleep(interval_seconds)
