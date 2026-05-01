from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import date

class UserCreate(BaseModel):
    email: str
    password: str
    role: Optional[str] = "viewer"

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class CollectRequest(BaseModel):
    module_domain: str
    region_id: Optional[int] = None
    metric_name: str = "generic"
    metric_value: Optional[float] = None
    raw_data: Optional[str] = None
    age_group: Optional[str] = None
    gender: Optional[str] = None

class ModuleRegister(BaseModel):
    name: str
    domain: str
    description: Optional[str] = None
    api_key: str

class SocialMediaCollect(BaseModel):
    platform: str
    hashtag: Optional[str] = None
    sentiment: Optional[str] = "neutre"
    mentions: Optional[int] = 0
    region_id: Optional[int] = None

class TerrainSubmit(BaseModel):
    agent_id: int
    region_id: int
    location: Optional[str] = None
    answers: Optional[str] = None

class IVRCampaignCreate(BaseModel):
    name: str
    question: str
    option_1: Optional[str] = None
    option_2: Optional[str] = None
    option_3: Optional[str] = None
    option_4: Optional[str] = None
    region_id: Optional[int] = None
    target_age: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class IVRResponseCreate(BaseModel):
    campaign_id: int
    phone: Optional[str] = None
    response: str
    region_id: Optional[int] = None
    duration_sec: Optional[int] = 0

class StoreCreate(BaseModel):
    name: str
    type: str
    region_id: int
    address: Optional[str] = None

class SaleCreate(BaseModel):
    store_id: int
    product_name: str
    category: Optional[str] = None
    quantity: int
    price_dt: float
    sold_at: str

class GamePlay(BaseModel):
    player_id: int
    game_id: int
    answers: Optional[str] = None

class RewardConvert(BaseModel):
    player_id: int
    points: int
    reward_type: str

class MoodRecord(BaseModel):
    region_id: int
    mood: str
    comment: Optional[str] = None
    player_id: Optional[int] = None

class PhotoSubmit(BaseModel):
    challenge_id: int
    player_id: int
    region_id: Optional[int] = None
    photo_url: Optional[str] = None

class DatasetImport(BaseModel):
    source: str
    dataset_name: str
    data: List[Dict[str, Any]]
    region_id: Optional[int] = None
