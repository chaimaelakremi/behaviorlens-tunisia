from sqlalchemy import Column, Integer, BigInteger, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum("admin", "analyst", "viewer"), default="viewer")
    created_at = Column(DateTime, server_default=func.now())

class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), unique=True)
    latitude = Column(Float)
    longitude = Column(Float)
    population = Column(Integer)

class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    domain = Column(String(100), nullable=False)
    description = Column(Text)
    api_key = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class BehavioralData(Base):
    __tablename__ = "behavioral_data"
    id = Column(BigInteger, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    age_group = Column(Enum("<18", "18-25", "26-35", "36-50", "51-65", ">65"))
    gender = Column(Enum("M", "F", "other", "unknown"), default="unknown")
    metric_name = Column(String(200), nullable=False, default="generic")
    metric_value = Column(Numeric(15, 4))
    raw_data = Column(Text)
    collected_at = Column(DateTime, server_default=func.now())
    region = relationship("Region")
    module = relationship("Module")

class CollectionLog(Base):
    __tablename__ = "collection_logs"
    id = Column(BigInteger, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    records_count = Column(Integer, default=1)
    status = Column(Enum("success", "error"), default="success")
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class SocialMediaData(Base):
    __tablename__ = "social_media_data"
    id = Column(BigInteger, primary_key=True, index=True)
    platform = Column(Enum("facebook", "tiktok", "twitter", "instagram"), nullable=False)
    hashtag = Column(String(200))
    sentiment = Column(Enum("positif", "negatif", "neutre"), default="neutre")
    mentions = Column(Integer, default=0)
    region_id = Column(Integer, ForeignKey("regions.id"))
    captured_at = Column(DateTime, server_default=func.now())
    region = relationship("Region")

class TerrainAgent(Base):
    __tablename__ = "terrain_agents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    zone = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    region = relationship("Region")
    user = relationship("User")

class TerrainData(Base):
    __tablename__ = "terrain_data"
    id = Column(BigInteger, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("terrain_agents.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    location = Column(String(255))
    answers = Column(Text)
    synced = Column(Boolean, default=False)
    captured_at = Column(DateTime, server_default=func.now())
    agent = relationship("TerrainAgent")
    region = relationship("Region")

class IVRCampaign(Base):
    __tablename__ = "ivr_campaigns"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    question = Column(Text, nullable=False)
    option_1 = Column(String(100))
    option_2 = Column(String(100))
    option_3 = Column(String(100))
    option_4 = Column(String(100))
    region_id = Column(Integer, ForeignKey("regions.id"))
    target_age = Column(String(50))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    region = relationship("Region")

class IVRResponse(Base):
    __tablename__ = "ivr_responses"
    id = Column(BigInteger, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("ivr_campaigns.id"), nullable=False)
    phone = Column(String(20))
    response = Column(Enum("1", "2", "3", "4"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"))
    duration_sec = Column(Integer, default=0)
    responded_at = Column(DateTime, server_default=func.now())
    campaign = relationship("IVRCampaign")
    region = relationship("Region")

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    type = Column(Enum("epicerie", "supermarche", "pharmacie", "souk", "autre"))
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    address = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    region = relationship("Region")

class POSData(Base):
    __tablename__ = "pos_data"
    id = Column(BigInteger, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    category = Column(String(100))
    quantity = Column(Integer, default=0)
    price_dt = Column(Numeric(8, 3))
    sold_at = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    store = relationship("Store")

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    target_age = Column(String(50))
    points_reward = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True)
    nickname = Column(String(100))
    region_id = Column(Integer, ForeignKey("regions.id"))
    age_group = Column(Enum("<18", "18-25", "26-35", "36-50", "51-65", ">65"))
    gender = Column(Enum("M", "F", "other", "unknown"), default="unknown")
    points_total = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    region = relationship("Region")

class GameSession(Base):
    __tablename__ = "game_sessions"
    id = Column(BigInteger, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    answers = Column(Text)
    points_earned = Column(Integer, default=0)
    played_at = Column(DateTime, server_default=func.now())
    player = relationship("Player")
    game = relationship("Game")

class MoodData(Base):
    __tablename__ = "mood_data"
    id = Column(BigInteger, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    region_id = Column(Integer, ForeignKey("regions.id"))
    mood = Column(Enum("tres_bien", "bien", "neutre", "mal", "tres_mal"), nullable=False)
    comment = Column(Text)
    recorded_at = Column(DateTime, server_default=func.now())
    region = relationship("Region")
    player = relationship("Player")

class PhotoChallenge(Base):
    __tablename__ = "photo_challenges"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    points = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class PhotoSubmission(Base):
    __tablename__ = "photo_submissions"
    id = Column(BigInteger, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("photo_challenges.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    photo_url = Column(String(500))
    region_id = Column(Integer, ForeignKey("regions.id"))
    ai_analysis = Column(Text)
    points_given = Column(Integer, default=0)
    submitted_at = Column(DateTime, server_default=func.now())
    challenge = relationship("PhotoChallenge")
    region = relationship("Region")
