"""Seed initial data: régions tunisiennes + modules + jeux"""
from database import SessionLocal, engine
import models, uuid
from auth import get_password_hash

REGIONS = [
    {"name": "Tunis", "code": "TUN", "latitude": 36.8065, "longitude": 10.1815, "population": 693210},
    {"name": "Ariana", "code": "ARI", "latitude": 36.8625, "longitude": 10.1956, "population": 484012},
    {"name": "Ben Arous", "code": "BEN", "latitude": 36.7533, "longitude": 10.2289, "population": 705564},
    {"name": "Manouba", "code": "MAN", "latitude": 36.8086, "longitude": 10.0969, "population": 391000},
    {"name": "Nabeul", "code": "NAB", "latitude": 36.4511, "longitude": 10.7357, "population": 787920},
    {"name": "Zaghouan", "code": "ZAG", "latitude": 36.4028, "longitude": 10.1427, "population": 186000},
    {"name": "Bizerte", "code": "BIZ", "latitude": 37.2744, "longitude": 9.8739, "population": 568000},
    {"name": "Béja", "code": "BEJ", "latitude": 36.7333, "longitude": 9.1833, "population": 303000},
    {"name": "Jendouba", "code": "JEN", "latitude": 36.5011, "longitude": 8.7803, "population": 421000},
    {"name": "Kef", "code": "KEF", "latitude": 36.1822, "longitude": 8.7147, "population": 258000},
    {"name": "Siliana", "code": "SIL", "latitude": 36.0856, "longitude": 9.3708, "population": 238000},
    {"name": "Kairouan", "code": "KAI", "latitude": 35.6781, "longitude": 10.0969, "population": 570000},
    {"name": "Kasserine", "code": "KAS", "latitude": 35.1675, "longitude": 8.8306, "population": 439000},
    {"name": "Sidi Bouzid", "code": "SID", "latitude": 35.0386, "longitude": 9.4842, "population": 434000},
    {"name": "Sousse", "code": "SOU", "latitude": 35.8256, "longitude": 10.6369, "population": 674000},
    {"name": "Monastir", "code": "MON", "latitude": 35.7643, "longitude": 10.8113, "population": 547000},
    {"name": "Mahdia", "code": "MAH", "latitude": 35.5047, "longitude": 11.0622, "population": 397000},
    {"name": "Sfax", "code": "SFX", "latitude": 34.7400, "longitude": 10.7600, "population": 955421},
    {"name": "Gafsa", "code": "GAF", "latitude": 34.4250, "longitude": 8.7842, "population": 335000},
    {"name": "Tozeur", "code": "TOZ", "latitude": 33.9197, "longitude": 8.1335, "population": 109000},
    {"name": "Kébili", "code": "KEB", "latitude": 33.7042, "longitude": 8.9642, "population": 152000},
    {"name": "Gabès", "code": "GAB", "latitude": 33.8828, "longitude": 10.0982, "population": 342000},
    {"name": "Médenine", "code": "MED", "latitude": 33.3500, "longitude": 10.5000, "population": 478000},
    {"name": "Tataouine", "code": "TAT", "latitude": 32.9214, "longitude": 10.4519, "population": 147000},
]

MODULES = [
    {"name": "Social Media", "domain": "social_media", "description": "Scraping Facebook, TikTok, Twitter tunisien"},
    {"name": "Terrain", "domain": "terrain", "description": "Agents mobiles avec tablette, mode offline"},
    {"name": "IVR Téléphone", "domain": "ivr", "description": "Sondages automatisés par téléphone"},
    {"name": "Commerce POS", "domain": "commerce", "description": "Données de ventes épiceries, supermarchés, souks"},
    {"name": "Gamification", "domain": "gamification", "description": "Mini-jeux et rewards pour collecter données"},
    {"name": "Open Data", "domain": "open_data", "description": "Récupération automatique données publiques tunisiennes"},
    {"name": "Baromètre Humeur", "domain": "mood", "description": "Comment les Tunisiens se sentent chaque jour"},
    {"name": "Photo Challenge", "domain": "photo", "description": "Collecte visuelle via photos par région"},
]

GAMES = [
    {"name": "Quiz Patrimoine", "description": "Quiz sur le patrimoine tunisien", "target_age": "18-50", "points_reward": 15},
    {"name": "Carte Mentale", "description": "Dessine ta ville idéale", "target_age": "all", "points_reward": 20},
    {"name": "Sondage Express", "description": "5 questions rapides sur ton quartier", "target_age": "all", "points_reward": 10},
    {"name": "Devinettes Dialecte", "description": "Reconnais le dialecte tunisien par région", "target_age": "18-35", "points_reward": 12},
]

def seed():
    db = SessionLocal()

    # Regions
    for r in REGIONS:
        existing = db.query(models.Region).filter(models.Region.name == r["name"]).first()
        if existing:
            existing.code = r["code"]
            existing.latitude = r["latitude"]
            existing.longitude = r["longitude"]
            existing.population = r["population"]
        else:
            db.add(models.Region(**r))
    db.commit()
    print(f"✓ {len(REGIONS)} régions seeded")

    # Modules
    for m in MODULES:
        existing = db.query(models.Module).filter(models.Module.domain == m["domain"]).first()
        if not existing:
            db.add(models.Module(**m, api_key=str(uuid.uuid4())))
    db.commit()
    print(f"✓ {len(MODULES)} modules seeded")

    # Admin user
    if not db.query(models.User).filter(models.User.email == "admin@behaviorlens.tn").first():
        db.add(models.User(email="admin@behaviorlens.tn", password=get_password_hash("admin123"), role="admin"))
        db.commit()
        print("✓ Admin user créé: admin@behaviorlens.tn / admin123")

    # Games
    for g in GAMES:
        if not db.query(models.Game).filter(models.Game.name == g["name"]).first():
            db.add(models.Game(**g))
    db.commit()
    print(f"✓ {len(GAMES)} jeux seeded")

    # Photo challenges
    challenges = [
        {"title": "Mon Quartier en Photos", "description": "Capture la vie de ton quartier", "points": 30},
        {"title": "Architecture Tunisienne", "description": "Médinas, riads, et mosquées", "points": 40},
        {"title": "Cuisine du Terroir", "description": "Plats et marchés locaux", "points": 25},
    ]
    for c in challenges:
        if not db.query(models.PhotoChallenge).filter(models.PhotoChallenge.title == c["title"]).first():
            db.add(models.PhotoChallenge(**c))
    db.commit()
    print("✓ Photo challenges seeded")

    db.close()
    print("\n🎉 Seed terminé avec succès!")

if __name__ == "__main__":
    seed()
