"""Seed realistic demo data for hackathon presentation"""
from database import SessionLocal
import models
from datetime import datetime, timedelta
import random

db = SessionLocal()

def rand_date(days_back=30):
    return datetime.utcnow() - timedelta(days=random.randint(0, days_back), hours=random.randint(0, 23))

regions = db.query(models.Region).all()
modules = {m.domain: m for m in db.query(models.Module).all()}
games = db.query(models.Game).all()
challenges = db.query(models.PhotoChallenge).all()

def log(module_domain, region_id=None):
    m = modules.get(module_domain)
    if m:
        db.add(models.CollectionLog(module_id=m.id, status="success"))
        return m
    return None

# ── Social Media ──────────────────────────────────────────────────────────────
print("Seeding Social Media...")
platforms = ["facebook", "tiktok", "twitter", "instagram"]
hashtags = ["#Tunisie", "#Tunis", "#حياة_تونسية", "#Sousse", "#Sfax", "#EconomieTN",
            "#JeunessTunisie", "#RamadanTN", "#FoodTN", "#SportTN", "#ElectionsTN"]
sentiments = ["positif", "negatif", "neutre"]
weights_sent = [0.45, 0.25, 0.30]

for _ in range(300):
    region = random.choice(regions)
    entry = models.SocialMediaData(
        platform=random.choice(platforms),
        hashtag=random.choice(hashtags),
        sentiment=random.choices(sentiments, weights=weights_sent)[0],
        mentions=random.randint(10, 15000),
        region_id=region.id,
        captured_at=rand_date(30)
    )
    db.add(entry)
    m = modules["social_media"]
    db.add(models.BehavioralData(
        module_id=m.id, region_id=region.id,
        metric_name="social_post", metric_value=entry.mentions,
        age_group=random.choice(["18-25", "26-35", "36-50"]),
        gender=random.choice(["M", "F"]),
        collected_at=entry.captured_at
    ))

db.commit()
print("  ✓ 300 social media entries")

# ── Terrain Agents & Data ─────────────────────────────────────────────────────
print("Seeding Terrain...")
admin_user = db.query(models.User).first()
terrain_regions = random.sample(regions, 12)

agents = []
for i, region in enumerate(terrain_regions):
    zones = ["Zone Urbaine", "Zone Rurale", "Medina", "Banlieue", "Zone Industrielle"]
    agent = models.TerrainAgent(
        user_id=admin_user.id, region_id=region.id,
        zone=random.choice(zones), is_active=True
    )
    db.add(agent)
    agents.append(agent)
db.commit()
db.expire_all()
agents = db.query(models.TerrainAgent).all()

survey_answers = [
    '{"q1":"Oui","q2":"Non","q3":"Parfois","emploi":"Informel","transport":"Vélo"}',
    '{"q1":"Non","q2":"Oui","q3":"Souvent","emploi":"Salarié","transport":"Bus"}',
    '{"q1":"Oui","q2":"Oui","q3":"Toujours","emploi":"Agriculteur","transport":"Marche"}',
    '{"q1":"Non","q2":"Non","q3":"Jamais","emploi":"Chômeur","transport":"Voiture"}',
]
m_terrain = modules["terrain"]
for _ in range(220):
    agent = random.choice(agents)
    captured = rand_date(30)
    td = models.TerrainData(
        agent_id=agent.id, region_id=agent.region_id,
        location=f"GPS:{random.uniform(30, 37):.4f},{random.uniform(8, 11):.4f}",
        answers=random.choice(survey_answers), synced=True, captured_at=captured
    )
    db.add(td)
    db.add(models.BehavioralData(
        module_id=m_terrain.id, region_id=agent.region_id,
        metric_name="field_survey", metric_value=1,
        age_group=random.choice(["26-35", "36-50", "51-65", ">65"]),
        gender=random.choice(["M", "F", "other"]),
        collected_at=captured
    ))
db.commit()
print("  ✓ 12 agents, 220 terrain submissions")

# ── IVR ───────────────────────────────────────────────────────────────────────
print("Seeding IVR...")
campaigns_data = [
    {"name": "Satisfaction Services Publics", "question": "Êtes-vous satisfait des services publics dans votre région?",
     "option_1": "Très satisfait", "option_2": "Satisfait", "option_3": "Pas satisfait", "option_4": "Très insatisfait"},
    {"name": "Transport en Commun", "question": "Comment évaluez-vous les transports en commun?",
     "option_1": "Excellent", "option_2": "Bon", "option_3": "Mauvais", "option_4": "Inexistant"},
    {"name": "Accès aux Soins", "question": "Avez-vous accès facilement aux soins de santé?",
     "option_1": "Oui toujours", "option_2": "Parfois", "option_3": "Rarement", "option_4": "Jamais"},
    {"name": "Situation Économique", "question": "Comment décrivez-vous votre situation économique actuelle?",
     "option_1": "Très bonne", "option_2": "Correcte", "option_3": "Difficile", "option_4": "Très difficile"},
]

campaigns = []
for c in campaigns_data:
    region = random.choice(regions)
    camp = models.IVRCampaign(
        name=c["name"], question=c["question"],
        option_1=c["option_1"], option_2=c["option_2"],
        option_3=c["option_3"], option_4=c["option_4"],
        region_id=region.id, target_age=">65", is_active=True,
        start_date=datetime.utcnow() - timedelta(days=20),
        end_date=datetime.utcnow() + timedelta(days=10)
    )
    db.add(camp)
    campaigns.append(camp)
db.commit()
db.expire_all()
campaigns = db.query(models.IVRCampaign).all()

m_ivr = modules["ivr"]
phone_prefixes = ["20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99"]
for _ in range(450):
    camp = random.choice(campaigns)
    region = random.choice(regions)
    responded = rand_date(20)
    resp = models.IVRResponse(
        campaign_id=camp.id,
        phone=f"+216{random.choice(phone_prefixes)}{random.randint(100000, 999999)}",
        response=random.choices(["1", "2", "3", "4"], weights=[0.15, 0.25, 0.35, 0.25])[0],
        region_id=region.id, duration_sec=random.randint(15, 90),
        responded_at=responded
    )
    db.add(resp)
    db.add(models.BehavioralData(
        module_id=m_ivr.id, region_id=region.id,
        metric_name="ivr_response", metric_value=int(resp.response),
        age_group=random.choice(["51-65", ">65"]),
        gender=random.choice(["M", "F"]),
        collected_at=responded
    ))
db.commit()
print("  ✓ 4 campaigns, 450 IVR responses")

# ── Commerce ──────────────────────────────────────────────────────────────────
print("Seeding Commerce...")
store_names = [
    ("Épicerie Ben Salah", "epicerie"), ("Supermarché Monoprix Tunis", "supermarche"),
    ("Pharmacie Centrale", "pharmacie"), ("Souk El Medina", "souk"),
    ("Épicerie Chez Hassan", "epicerie"), ("Supermarché Géant Sfax", "supermarche"),
    ("Souk Sfax Ancien", "souk"), ("Pharmacie du Nord", "pharmacie"),
    ("Épicerie Fatma", "epicerie"), ("Mini Market Sousse", "supermarche"),
    ("Souk de Kairouan", "souk"), ("Épicerie Hamdi", "epicerie"),
    ("Supermarché Carrefour", "supermarche"), ("Marché Central Bizerte", "souk"),
    ("Épicerie Nour", "epicerie"),
]
stores = []
for name, stype in store_names:
    region = random.choice(regions)
    s = models.Store(name=name, type=stype, region_id=region.id,
                     address=f"Rue {random.randint(1, 100)}, {region.name}", is_active=True)
    db.add(s)
    stores.append(s)
db.commit()
db.expire_all()
stores = db.query(models.Store).all()

products = [
    ("Pain", "Alimentation", 0.320), ("Huile d'olive", "Alimentation", 8.500),
    ("Lait", "Alimentation", 1.800), ("Tomates", "Légumes", 0.650),
    ("Pommes de terre", "Légumes", 0.480), ("Farine", "Alimentation", 1.200),
    ("Sucre", "Alimentation", 0.980), ("Couscous", "Alimentation", 2.500),
    ("Thon", "Conserves", 3.200), ("Harissa", "Condiments", 1.100),
    ("Eau minérale", "Boissons", 0.450), ("Café", "Boissons", 8.900),
    ("Sardines", "Poisson", 4.200), ("Semoule", "Alimentation", 1.800),
    ("Fromage kiri", "Laitier", 5.600), ("Yaourt", "Laitier", 0.850),
    ("Menthe", "Herbes", 0.280), ("Citrons", "Fruits", 0.750),
    ("Poulet", "Viande", 12.000), ("Merguez", "Viande", 9.500),
]
m_commerce = modules["commerce"]
for _ in range(800):
    store = random.choice(stores)
    product_name, category, base_price = random.choice(products)
    sold = rand_date(30)
    qty = random.randint(1, 50)
    price = round(base_price * random.uniform(0.9, 1.15), 3)
    sale = models.POSData(
        store_id=store.id, product_name=product_name, category=category,
        quantity=qty, price_dt=price,
        sold_at=(datetime.utcnow() - timedelta(days=random.randint(0, 30))).date(),
        created_at=sold
    )
    db.add(sale)
    db.add(models.BehavioralData(
        module_id=m_commerce.id, region_id=store.region_id,
        metric_name="pos_sale", metric_value=float(price) * qty,
        age_group=random.choice(["26-35", "36-50", "51-65"]),
        gender=random.choice(["M", "F"]),
        collected_at=sold
    ))
db.commit()
print("  ✓ 15 stores, 800 sales transactions")

# ── Players & Gamification ────────────────────────────────────────────────────
print("Seeding Gamification...")
nicknames = ["TunisHero", "SfaxGame", "ZaghouanKing", "BizertePlayer", "SousseStars",
             "KairouanFC", "GafsaMiner", "NabeulSun", "MahdiaSea", "JendoubaForest",
             "KefMountain", "SilianaPride", "MonastirPearl", "MahdiaBay", "GabesOasis",
             "MedenineStar", "TataouineSand", "KebiliDate", "TozeurPalm", "ArianaDream"]

players = []
m_game = modules["gamification"]
for i, nick in enumerate(nicknames):
    region = random.choice(regions)
    p = models.Player(
        phone=f"+2162{i:07d}",
        nickname=nick,
        region_id=region.id,
        age_group=random.choice(["<18", "18-25", "26-35", "36-50", "51-65"]),
        gender=random.choice(["M", "F"]),
        points_total=random.randint(50, 1200)
    )
    db.add(p)
    players.append(p)
db.commit()
db.expire_all()
players = db.query(models.Player).all()
games_list = db.query(models.Game).all()

for _ in range(380):
    player = random.choice(players)
    game = random.choice(games_list)
    played = rand_date(30)
    gs = models.GameSession(
        player_id=player.id, game_id=game.id,
        answers='{"q1":"A","q2":"B","q3":"C"}',
        points_earned=game.points_reward,
        played_at=played
    )
    db.add(gs)
    db.add(models.BehavioralData(
        module_id=m_game.id, region_id=player.region_id,
        metric_name="game_session", metric_value=game.points_reward,
        age_group=player.age_group, gender=player.gender,
        collected_at=played
    ))
db.commit()
print("  ✓ 20 players, 380 game sessions")

# ── Open Data ─────────────────────────────────────────────────────────────────
print("Seeding Open Data...")
m_opendata = modules["open_data"]
sources = ["ins", "anme", "ministere_sante"]
for source in sources:
    for _ in range(15):
        fetched = rand_date(30)
        db.add(models.CollectionLog(module_id=m_opendata.id, status="success", created_at=fetched))
        db.add(models.BehavioralData(
            module_id=m_opendata.id, metric_name=f"opendata_{source}",
            raw_data=f'{{"source":"{source}","fetched":true}}',
            collected_at=fetched
        ))
db.commit()
print("  ✓ 45 open data fetches")

# ── Mood ──────────────────────────────────────────────────────────────────────
print("Seeding Mood...")
m_mood = modules["mood"]
mood_options = ["tres_bien", "bien", "neutre", "mal", "tres_mal"]
mood_weights = [0.15, 0.30, 0.25, 0.20, 0.10]
mood_scores = {"tres_bien": 5, "bien": 4, "neutre": 3, "mal": 2, "tres_mal": 1}
comments = [
    "Bonne journée aujourd'hui!", "Difficile économiquement", "Rien de spécial",
    "Content de voir ma famille", "Problèmes de transport", "Belle météo!",
    None, None, None
]

for _ in range(600):
    region = random.choice(regions)
    player = random.choice(players) if random.random() > 0.3 else None
    recorded = rand_date(30)
    mood_val = random.choices(mood_options, weights=mood_weights)[0]
    entry = models.MoodData(
        player_id=player.id if player else None,
        region_id=region.id, mood=mood_val,
        comment=random.choice(comments),
        recorded_at=recorded
    )
    db.add(entry)
    db.add(models.BehavioralData(
        module_id=m_mood.id, region_id=region.id,
        metric_name="mood_score", metric_value=mood_scores[mood_val],
        age_group=random.choice(["<18", "18-25", "26-35", "36-50", "51-65", ">65"]),
        gender=random.choice(["M", "F", "other", "unknown"]),
        collected_at=recorded
    ))
db.commit()
print("  ✓ 600 mood records")

# ── Photo ─────────────────────────────────────────────────────────────────────
print("Seeding Photo...")
m_photo = modules["photo"]
photo_urls = [
    "https://images.unsplash.com/photo-1539020140153-e479b8c22e70",
    "https://images.unsplash.com/photo-1528360983277-13d401cdc186",
    "https://images.unsplash.com/photo-1467803738586-46b7eb7b16a1",
    "https://images.unsplash.com/photo-1501854140801-50d01698950b",
    "https://images.unsplash.com/photo-1504198453500-8f7eafce9e94",
]
ai_analyses = [
    '{"label":"repas","description":"Repas traditionnel tunisien riche en légumes et épices","confidence":0.92}',
    '{"label":"transport","description":"Transport en commun, forte densité de passagers, heure de pointe","confidence":0.88}',
    '{"label":"quartier","description":"Quartier résidentiel bien entretenu, présence d espaces verts","confidence":0.85}',
    '{"label":"architecture","description":"Architecture médina, pierres dorées, calèche traditionnelle","confidence":0.90}',
    '{"label":"marché","description":"Marché animé, stands de fruits et légumes frais, ambiance authentique","confidence":0.87}',
]

challs = db.query(models.PhotoChallenge).all()
for _ in range(180):
    player = random.choice(players)
    challenge = random.choice(challs)
    region = random.choice(regions)
    submitted = rand_date(30)
    ps = models.PhotoSubmission(
        challenge_id=challenge.id, player_id=player.id,
        region_id=region.id,
        photo_url=random.choice(photo_urls),
        ai_analysis=random.choice(ai_analyses),
        points_given=challenge.points,
        submitted_at=submitted
    )
    db.add(ps)
    db.add(models.BehavioralData(
        module_id=m_photo.id, region_id=region.id,
        metric_name="photo_submission", metric_value=challenge.points,
        age_group=player.age_group, gender=player.gender,
        collected_at=submitted
    ))
db.commit()
print("  ✓ 180 photo submissions")

db.close()
print("\n🎉 Demo data seeded! Total: ~3030 behavioral records")
