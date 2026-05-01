"""
Exemple 3 — Module sondage SMS
================================
Reçoit des réponses SMS (via Twilio/Nexmo/local gateway) et les injecte
dans le framework BehaviorLens.
"""
import sys
import random
sys.path.insert(0, "..")
from behaviorlens_sdk import BehaviorLensClient, BehaviorLensModule


class SMSSurveyModule(BehaviorLensModule):
    DOMAIN = "sms_survey"
    NAME = "Sondage SMS"
    DESCRIPTION = "Collecte par SMS ciblant zones sans internet"

    QUESTIONS = {
        "Q1": {
            "text": "Avez-vous accès à l'eau potable? (1=Oui 2=Non 3=Parfois)",
            "metric": "acces_eau",
        },
        "Q2": {
            "text": "Qualité de l'électricité? (1=Bonne 2=Coupures 3=Absente)",
            "metric": "qualite_electricite",
        },
    }

    REGIONS_BY_PREFIX = {
        "71": "tunis", "73": "sfax", "74": "sousse",
        "75": "monastir", "76": "mahdia", "77": "kairouan",
        "78": "kasserine", "79": "sidi_bouzid",
    }

    def get_region_from_phone(self, phone: str) -> str:
        prefix = phone[4:6] if phone.startswith("+216") else phone[:2]
        return self.REGIONS_BY_PREFIX.get(prefix, "tunis")

    def process_incoming_sms(self, sms_list: list):
        """Traite une liste de SMS entrants depuis le gateway."""
        print(f"[SMS] Traitement de {len(sms_list)} SMS...")

        for sms in sms_list:
            phone = sms["from"]
            body = sms["body"].strip()
            question_id = sms.get("question_id", "Q1")

            if body not in ["1", "2", "3"]:
                print(f"  ⚠ Réponse invalide de {phone}: '{body}'")
                continue

            question = self.QUESTIONS.get(question_id, self.QUESTIONS["Q1"])
            region = self.get_region_from_phone(phone)

            self.push(
                region_name=region,
                metric_name=question["metric"],
                metric_value=int(body),
                raw_data=f'{{"phone":"{phone[-4:]}****","reponse":{body},"question":"{question_id}"}}',
                age_group=">65",
                gender="unknown",
            )
            print(f"  ✓ {phone[-4:]}**** | {question['metric']}: {body} | {region}")

    def collect(self):
        # ── Simulation SMS entrants (remplacer par ton gateway SMS réel) ──────
        fake_sms = [
            {"from": f"+2167{random.randint(1000000,9999999)}", "body": str(random.randint(1, 3)), "question_id": "Q1"}
            for _ in range(8)
        ]
        # ─────────────────────────────────────────────────────────────────────

        self.process_incoming_sms(fake_sms)
        print(f"[SMS] Collecte terminée\n")


if __name__ == "__main__":
    client = BehaviorLensClient("http://localhost:8000")
    client.login("admin@behaviorlens.tn", "admin123")

    module = SMSSurveyModule(client)
    module.register()
    module.collect()

    # Vérifier les stats du framework
    by_module = client.get_stats_by_module()
    for m in by_module:
        if m["count"] > 0:
            print(f"  {m['label']}: {m['count']} enregistrements")
