"""
Exemple 1 — Module de scraping social media
============================================
Simule un collecteur de données Facebook/TikTok tunisien.
En production, remplace la génération aléatoire par du vrai scraping.
"""
import sys
import random
sys.path.insert(0, "..")
from behaviorlens_sdk import BehaviorLensClient, BehaviorLensModule


class SocialScraperModule(BehaviorLensModule):
    DOMAIN = "social_media"
    NAME = "Social Media Scraper"
    DESCRIPTION = "Scraping Facebook, TikTok, Twitter tunisien"

    HASHTAGS = [
        "#Tunisie", "#Tunis", "#حياة_تونسية", "#Sousse",
        "#Sfax", "#EconomieTN", "#JeunessTunisie",
    ]
    PLATFORMS = ["facebook", "tiktok", "twitter", "instagram"]

    def collect(self):
        print(f"[SocialScraper] Collecte en cours...")

        # ── En production: remplace par ton vrai scraper ──────────────────────
        scraped_posts = [
            {
                "platform": random.choice(self.PLATFORMS),
                "hashtag": random.choice(self.HASHTAGS),
                "mentions": random.randint(50, 10000),
                "sentiment": random.choices(
                    ["positif", "negatif", "neutre"],
                    weights=[0.4, 0.2, 0.4]
                )[0],
                "region": random.choice(["tunis", "sfax", "sousse", "kairouan"]),
            }
            for _ in range(10)
        ]
        # ─────────────────────────────────────────────────────────────────────

        for post in scraped_posts:
            self.push(
                region_name=post["region"],
                metric_name="social_post",
                metric_value=post["mentions"],
                raw_data=str(post),
                age_group="18-25",
            )
            print(f"  ✓ {post['platform']} | {post['hashtag']} | {post['mentions']} mentions")

        print(f"[SocialScraper] {len(scraped_posts)} posts envoyés au framework\n")


if __name__ == "__main__":
    client = BehaviorLensClient("http://localhost:8000")
    client.login("admin@behaviorlens.tn", "admin123")

    module = SocialScraperModule(client)
    module.collect()

    stats = client.get_stats()
    print(f"Framework total: {stats['total_records']} enregistrements")
