"""
Exemple 2 — Module IoT capteurs urbains
=========================================
Intègre des capteurs physiques (qualité air, bruit, trafic) au framework.
Utilise le mode batch pour optimiser les envois réseau.
"""
import sys
import random
import time
sys.path.insert(0, "..")
from behaviorlens_sdk import BehaviorLensClient, BehaviorLensModule


class IoTCapteurModule(BehaviorLensModule):
    DOMAIN = "iot_capteurs"
    NAME = "IoT Capteurs Urbains"
    DESCRIPTION = "Capteurs qualité air, bruit, trafic dans les villes tunisiennes"

    CAPTEURS = [
        {"id": "CAP-TUN-001", "type": "qualite_air", "region": "tunis", "unite": "µg/m³"},
        {"id": "CAP-TUN-002", "type": "bruit_urbain", "region": "tunis", "unite": "dB"},
        {"id": "CAP-SFX-001", "type": "trafic",       "region": "sfax",  "unite": "vehicules/h"},
        {"id": "CAP-SOU-001", "type": "qualite_air",  "region": "sousse","unite": "µg/m³"},
        {"id": "CAP-BIZ-001", "type": "trafic",       "region": "bizerte","unite": "vehicules/h"},
    ]

    def read_sensor(self, capteur: dict) -> float:
        """Lecture simulée — remplacer par GPIO/MQTT/API capteur réel."""
        if capteur["type"] == "qualite_air":
            return round(random.uniform(15, 120), 1)   # PM2.5 µg/m³
        elif capteur["type"] == "bruit_urbain":
            return round(random.uniform(45, 95), 1)    # dB
        else:
            return round(random.uniform(200, 2500), 0) # véhicules/h

    def collect(self):
        print("[IoT] Lecture des capteurs...")

        # Mode batch : accumule avant d'envoyer
        for capteur in self.CAPTEURS:
            valeur = self.read_sensor(capteur)
            self.client.add_to_batch(
                module_domain=self.DOMAIN,
                region_name=capteur["region"],
                metric_name=capteur["type"],
                metric_value=valeur,
                raw_data=f'{{"capteur":"{capteur["id"]}","valeur":{valeur},"unite":"{capteur["unite"]}"}}',
            )
            print(f"  📡 {capteur['id']} | {capteur['type']}: {valeur} {capteur['unite']}")

        # Envoi groupé au framework
        results = self.client.flush_batch()
        print(f"[IoT] {len(results)} mesures envoyées au framework\n")


if __name__ == "__main__":
    client = BehaviorLensClient("http://localhost:8000")
    client.login("admin@behaviorlens.tn", "admin123")

    # Enregistrer le nouveau module dans le framework
    module = IoTCapteurModule(client)
    module.register()

    # Collecte en continu toutes les 60 secondes
    # module.run(interval_seconds=60)

    # Ou une seule collecte pour la démo
    module.collect()
