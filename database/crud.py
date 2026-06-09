import json
from sqlalchemy.exc import IntegrityError
from .models import SessionLocal, Category, Profession, Software, ItemRequest


ALLOWED_FIELDS = ["name", "type", "desc", "feature", "url", "youtube_tutorial"]


def get_all_categories():
    with SessionLocal() as db:
        categories = db.query(Category).all()
        return [{"id": c.id, "name": c.name} for c in categories]


def get_category_by_id(cat_id):
    with SessionLocal() as db:
        cat = db.query(Category).filter(Category.id == cat_id).first()
        return {"id": cat.id, "name": cat.name} if cat else None


def get_professions_by_category(cat_id):
    with SessionLocal() as db:
        professions = db.query(Profession).filter(Profession.category_id == cat_id).all()
        return [{"id": p.id, "category_id": p.category_id, "name": p.name} for p in professions]


def get_profession_by_id(prof_id):
    with SessionLocal() as db:
        prof = db.query(Profession).filter(Profession.id == prof_id).first()
        return {"id": prof.id, "category_id": prof.category_id, "name": prof.name} if prof else None


def get_software_by_profession(prof_id):
    with SessionLocal() as db:
        software = db.query(Software).filter(Software.profession_id == prof_id).all()
        return [{
            "id": s.id, "profession_id": s.profession_id, "name": s.name,
            "type": s.type, "desc": s.desc, "feature": s.feature, "url": s.url,
            "youtube_tutorial": s.youtube_tutorial
        } for s in software]


def get_software_by_id(sw_id):
    with SessionLocal() as db:
        s = db.query(Software).filter(Software.id == sw_id).first()
        return {
            "id": s.id, "profession_id": s.profession_id, "name": s.name,
            "type": s.type, "desc": s.desc, "feature": s.feature, "url": s.url,
            "youtube_tutorial": s.youtube_tutorial
        } if s else None


def add_category(cat_id, name):
    with SessionLocal() as db:
        try:
            db.add(Category(id=cat_id, name=name))
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            return False


def add_profession(prof_id, cat_id, name):
    with SessionLocal() as db:
        try:
            db.add(Profession(id=prof_id, category_id=cat_id, name=name))
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            return False


def add_software(prof_id, name, type_, desc, feature, url, youtube_tutorial=None):
    with SessionLocal() as db:
        db.add(Software(profession_id=prof_id, name=name, type=type_, desc=desc, feature=feature, url=url, youtube_tutorial=youtube_tutorial))
        db.commit()


def delete_category(cat_id):
    with SessionLocal() as db:
        db.query(Category).filter(Category.id == cat_id).delete()
        db.commit()


def delete_profession(prof_id):
    with SessionLocal() as db:
        db.query(Profession).filter(Profession.id == prof_id).delete()
        db.commit()


def delete_software(sw_id):
    with SessionLocal() as db:
        db.query(Software).filter(Software.id == sw_id).delete()
        db.commit()


def update_software_field(sw_id, field_name, new_value):
    if field_name not in ALLOWED_FIELDS:
        return False

    with SessionLocal() as db:
        db.query(Software).filter(Software.id == sw_id).update({field_name: new_value})
        db.commit()
        return True


def add_item_request(user_id, request_type, data_dict):
    with SessionLocal() as db:
        data_str = json.dumps(data_dict, ensure_ascii=False)
        req = ItemRequest(user_id=str(user_id), request_type=request_type, data=data_str, status="pending")
        db.add(req)
        db.commit()
        return True


def get_pending_requests():
    with SessionLocal() as db:
        requests = db.query(ItemRequest).filter(ItemRequest.status == "pending").all()
        return [{
            "id": r.id, "user_id": r.user_id, "request_type": r.request_type,
            "data": json.loads(r.data), "status": r.status
        } for r in requests]


def get_request_by_id(req_id):
    with SessionLocal() as db:
        r = db.query(ItemRequest).filter(ItemRequest.id == req_id).first()
        if r:
            return {
                "id": r.id, "user_id": r.user_id, "request_type": r.request_type,
                "data": json.loads(r.data), "status": r.status
            }
        return None


def update_request_status(req_id, status):
    with SessionLocal() as db:
        db.query(ItemRequest).filter(ItemRequest.id == req_id).update({"status": status})
        db.commit()
        return True

