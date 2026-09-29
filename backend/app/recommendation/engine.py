import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.item import Item
from app.models.category import Category
from app.models.interaction import Interaction
from app.models.rating import Rating
from app.models.preference import UserPreference
from app.models.recommendation import Recommendation
from app.config import settings

logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=1500)
        self.item_tfidf_matrix = None
        self.item_ids_order = []
        self.item_index_map = {}  # item_id -> index in matrix

    def build_content_model(self, db: Session):
        """Builds TF-IDF feature vectors for all items in the catalog."""
        items = db.query(Item).all()
        if not items:
            return

        corpus = []
        self.item_ids_order = []
        self.item_index_map = {}

        for idx, item in enumerate(items):
            cat_name = item.category.name if item.category else ""
            features_text = ""
            try:
                feat_list = json.loads(item.features or "[]")
                features_text = " ".join(feat_list)
            except Exception:
                features_text = item.features or ""

            # Combine title, category, tags, description, cloud provider, features
            text_doc = f"{item.name} {cat_name} {item.cloud_provider} {item.tags.replace(',', ' ')} {item.description} {features_text} {item.tier}"
            corpus.append(text_doc)
            self.item_ids_order.append(item.id)
            self.item_index_map[item.id] = idx

        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
        logger.info(f"Built TF-IDF matrix with {len(items)} items and {self.tfidf_matrix.shape[1]} features.")

    def get_similar_items(self, item_id: int, db: Session, limit: int = 6) -> List[Dict[str, Any]]:
        """Returns items similar to the given item based on content similarity."""
        if not hasattr(self, 'tfidf_matrix') or self.tfidf_matrix is None or item_id not in self.item_index_map:
            self.build_content_model(db)

        if item_id not in self.item_index_map:
            return []

        idx = self.item_index_map[item_id]
        item_vector = self.tfidf_matrix[idx]
        sim_scores = cosine_similarity(item_vector, self.tfidf_matrix).flatten()

        # Sort indices by descending similarity
        related_indices = sim_scores.argsort()[::-1]

        results = []
        target_item = db.query(Item).filter(Item.id == item_id).first()
        target_tags = set([t.strip().lower() for t in (target_item.tags or "").split(",") if t.strip()])

        for i in related_indices:
            other_id = self.item_ids_order[i]
            if other_id == item_id:
                continue
            
            other_item = db.query(Item).filter(Item.id == other_id).first()
            if not other_item:
                continue

            sim_score = float(sim_scores[i])
            other_tags = set([t.strip().lower() for t in (other_item.tags or "").split(",") if t.strip()])
            common_tags = target_tags.intersection(other_tags)

            if common_tags:
                reason = f"Shares {', '.join(list(common_tags)[:2])} with {target_item.name}"
            elif target_item and other_item.category_id == target_item.category_id:
                reason = f"Alternative solution in {target_item.category.name if target_item.category else 'this category'}"
            else:
                reason = "High architectural and technical profile similarity"

            results.append({
                "item_id": other_id,
                "score": round(sim_score, 4),
                "reason": reason,
                "algorithm": "content_based",
                "content_score": round(sim_score, 4),
                "collaborative_score": None
            })

            if len(results) >= limit:
                break

        return results

    def get_content_based_recommendations(
        self, user_id: int, db: Session, limit: int = 12
    ) -> List[Dict[str, Any]]:
        """Calculates personalized recommendations using TF-IDF and user profile vectors."""
        if not hasattr(self, 'tfidf_matrix') or self.tfidf_matrix is None:
            self.build_content_model(db)

        if not self.item_ids_order:
            return []

        # 1. Fetch user's interactions
        interactions = db.query(Interaction).filter(Interaction.user_id == user_id).all()
        ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
        preferences = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()

        # Build user vector
        user_vector = np.zeros((1, self.tfidf_matrix.shape[1]))
        total_weight = 0.0
        interacted_item_ids = set()
        liked_categories = []

        weight_map = {
            "view": 1.0,
            "click": 1.5,
            "like": 3.0,
            "add_to_cart": 4.0,
            "purchase": 5.0
        }

        for interaction in interactions:
            interacted_item_ids.add(interaction.item_id)
            if interaction.item_id in self.item_index_map:
                w = weight_map.get(interaction.interaction_type, 1.0)
                idx = self.item_index_map[interaction.item_id]
                user_vector += self.tfidf_matrix[idx].toarray() * w
                total_weight += w

        for r in ratings:
            interacted_item_ids.add(r.item_id)
            if r.item_id in self.item_index_map and r.rating >= 3.0:
                idx = self.item_index_map[r.item_id]
                w = (r.rating / 5.0) * 4.0
                user_vector += self.tfidf_matrix[idx].toarray() * w
                total_weight += w

        # Inject preferences if available
        if preferences:
            try:
                pref_cats = json.loads(preferences.preferred_categories or "[]")
                pref_tags = json.loads(preferences.preferred_tags or "[]")
                liked_categories.extend(pref_cats)
                pref_text = " ".join(pref_cats + pref_tags)
                if pref_text:
                    pref_vec = self.tfidf_vectorizer.transform([pref_text]).toarray()
                    user_vector += pref_vec * 3.0
                    total_weight += 3.0
            except Exception:
                pass

        if total_weight == 0:
            return self.get_cold_start_recommendations(user_id, db, limit)

        user_vector = user_vector / total_weight
        sim_scores = cosine_similarity(user_vector, self.tfidf_matrix).flatten()

        scored_candidates = []
        for idx, score in enumerate(sim_scores):
            item_id = self.item_ids_order[idx]
            # Boost score slightly if in preferred category
            item = db.query(Item).filter(Item.id == item_id).first()
            if not item:
                continue

            # Penalty for already purchased / heavily interacted items so we offer discovery
            penalty = 0.5 if item_id in interacted_item_ids else 1.0
            adjusted_score = float(score) * penalty

            # Reason generator
            reason = "Based on your technical interest profile"
            if item.category and item.category.name in liked_categories:
                reason = f"Matches your preferred domain '{item.category.name}'"
            elif item_id in interacted_item_ids:
                reason = "Recommended based on your recent activity"
            elif item.rating >= 4.5:
                reason = f"Top-rated {item.cloud_provider} service matching your tags"

            scored_candidates.append({
                "item_id": item_id,
                "score": round(adjusted_score, 4),
                "reason": reason,
                "algorithm": "content_based",
                "content_score": round(float(score), 4),
                "collaborative_score": None
            })

        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates[:limit]

    def get_collaborative_recommendations(
        self, user_id: int, db: Session, limit: int = 12
    ) -> List[Dict[str, Any]]:
        """User-Based Collaborative Filtering using Cosine Similarity on interaction/rating matrix."""
        # 1. Fetch all ratings and interactions
        ratings = db.query(Rating).all()
        interactions = db.query(Interaction).all()

        # Build user-item rating matrix
        all_user_ids = sorted(list(set([r.user_id for r in ratings] + [i.user_id for i in interactions] + [user_id])))
        all_item_ids = sorted(list(set([item.id for item in db.query(Item.id).all()])))

        if len(all_user_ids) < 2 or not all_item_ids:
            return self.get_cold_start_recommendations(user_id, db, limit)

        user_idx_map = {uid: i for i, uid in enumerate(all_user_ids)}
        item_idx_map = {iid: i for i, iid in enumerate(all_item_ids)}

        matrix = np.zeros((len(all_user_ids), len(all_item_ids)), dtype=np.float32)

        # Fill interactions
        weight_map = {"view": 1.0, "click": 1.5, "like": 3.0, "add_to_cart": 4.0, "purchase": 5.0}
        for inter in interactions:
            if inter.user_id in user_idx_map and inter.item_id in item_idx_map:
                u_idx = user_idx_map[inter.user_id]
                i_idx = item_idx_map[inter.item_id]
                w = weight_map.get(inter.interaction_type, 1.0)
                matrix[u_idx, i_idx] = max(matrix[u_idx, i_idx], w)

        # Fill explicit ratings (override or boost, normalized scale 1-5)
        for r in ratings:
            if r.user_id in user_idx_map and r.item_id in item_idx_map:
                u_idx = user_idx_map[r.user_id]
                i_idx = item_idx_map[r.item_id]
                matrix[u_idx, i_idx] = max(matrix[u_idx, i_idx], float(r.rating))

        target_u_idx = user_idx_map.get(user_id)
        if target_u_idx is None or np.sum(matrix[target_u_idx]) == 0:
            return self.get_cold_start_recommendations(user_id, db, limit)

        # Calculate cosine similarity between target user and all users
        target_vector = matrix[target_u_idx].reshape(1, -1)
        user_similarities = cosine_similarity(target_vector, matrix).flatten()

        # Zero out self similarity
        user_similarities[target_u_idx] = 0

        # Find top similar users (k=5)
        top_neighbor_indices = np.argsort(user_similarities)[::-1][:7]
        neighbor_sims = user_similarities[top_neighbor_indices]

        sim_sum = np.sum(neighbor_sims)
        if sim_sum == 0:
            return self.get_cold_start_recommendations(user_id, db, limit)

        # Predict ratings for items not yet interacted by target user
        predicted_scores = []
        user_interacted_items = set(np.where(matrix[target_u_idx] > 0)[0])

        for item_idx, iid in enumerate(all_item_ids):
            # calculate weighted rating from neighbors
            neighbor_ratings = matrix[top_neighbor_indices, item_idx]
            if np.sum(neighbor_ratings) > 0:
                weighted_rating = np.dot(neighbor_sims, neighbor_ratings) / sim_sum
                # Normalize score between 0 and 1
                norm_score = min(float(weighted_rating) / 5.0, 1.0)

                penalty = 0.6 if item_idx in user_interacted_items else 1.0
                final_score = norm_score * penalty

                predicted_scores.append({
                    "item_id": iid,
                    "score": round(final_score, 4),
                    "reason": "Popular among cloud engineers with similar architectural stacks",
                    "algorithm": "collaborative",
                    "content_score": None,
                    "collaborative_score": round(norm_score, 4)
                })

        predicted_scores.sort(key=lambda x: x["score"], reverse=True)
        if not predicted_scores:
            return self.get_cold_start_recommendations(user_id, db, limit)

        return predicted_scores[:limit]

    def get_hybrid_recommendations(
        self,
        user_id: int,
        db: Session,
        content_weight: Optional[float] = None,
        collab_weight: Optional[float] = None,
        limit: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Hybrid Recommendation Model:
        final_score = alpha * content_score + (1 - alpha) * collab_score
        """
        if content_weight is None:
            content_weight = settings.DEFAULT_CONTENT_WEIGHT
        if collab_weight is None:
            collab_weight = settings.DEFAULT_COLLAB_WEIGHT

        # Normalize weights
        total_w = content_weight + collab_weight
        if total_w > 0:
            content_weight /= total_w
            collab_weight /= total_w
        else:
            content_weight, collab_weight = 0.6, 0.4

        # Count user interactions
        user_interaction_count = db.query(Interaction).filter(Interaction.user_id == user_id).count()
        user_rating_count = db.query(Rating).filter(Rating.user_id == user_id).count()

        if (user_interaction_count + user_rating_count) < settings.MIN_INTERACTIONS_FOR_COLLAB:
            # Low history user -> blend cold-start & content
            content_recs = self.get_content_based_recommendations(user_id, db, limit=limit)
            cold_recs = self.get_cold_start_recommendations(user_id, db, limit=limit)
            
            combined = {}
            for r in content_recs:
                combined[r["item_id"]] = {
                    **r,
                    "score": round(r["score"] * 0.75, 4),
                    "algorithm": "hybrid_onboarding"
                }
            for r in cold_recs:
                iid = r["item_id"]
                if iid in combined:
                    combined[iid]["score"] = max(combined[iid]["score"], round(r["score"] * 0.9, 4))
                else:
                    combined[iid] = {
                        **r,
                        "algorithm": "hybrid_onboarding"
                    }
            result_list = list(combined.values())
            result_list.sort(key=lambda x: x["score"], reverse=True)
            return result_list[:limit]

        # Full Hybrid execution
        content_candidates = self.get_content_based_recommendations(user_id, db, limit=40)
        collab_candidates = self.get_collaborative_recommendations(user_id, db, limit=40)

        content_dict = {c["item_id"]: c for c in content_candidates}
        collab_dict = {c["item_id"]: c for c in collab_candidates}

        all_item_ids = set(content_dict.keys()).union(set(collab_dict.keys()))
        hybrid_results = []

        for iid in all_item_ids:
            c_score = content_dict.get(iid, {}).get("content_score", 0.0) or 0.0
            col_score = collab_dict.get(iid, {}).get("collaborative_score", 0.0) or 0.0

            final_score = (content_weight * c_score) + (collab_weight * col_score)

            # Formulate dynamic explainability reason
            if c_score > 0.4 and col_score > 0.4:
                reason = "Matches your tech preferences & highly endorsed by similar engineers"
            elif col_score > c_score:
                reason = "Trending among teams solving similar cloud scaling challenges"
            elif iid in content_dict:
                reason = content_dict[iid].get("reason", "Tailored to your cloud architecture stack")
            else:
                reason = "High hybrid alignment across community ratings and specifications"

            hybrid_results.append({
                "item_id": iid,
                "score": round(final_score, 4),
                "reason": reason,
                "algorithm": "hybrid",
                "content_score": round(c_score, 4),
                "collaborative_score": round(col_score, 4)
            })

        hybrid_results.sort(key=lambda x: x["score"], reverse=True)

        if not hybrid_results:
            return self.get_cold_start_recommendations(user_id, db, limit)

        # Audit/log top recommendations to DB asynchronously or synchronously
        try:
            self._log_recommendations(user_id, hybrid_results[:limit], "hybrid", db)
        except Exception as e:
            logger.warning(f"Could not log recommendations: {e}")

        return hybrid_results[:limit]

    def get_cold_start_recommendations(
        self, user_id: Optional[int], db: Session, limit: int = 12
    ) -> List[Dict[str, Any]]:
        """Handles cold start for new users or guests using preferences and popularity."""
        pref_categories = []
        if user_id:
            pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
            if pref and pref.preferred_categories:
                try:
                    pref_categories = json.loads(pref.preferred_categories)
                except Exception:
                    pass

        results = []
        # If user specified preferred categories during onboarding
        if pref_categories:
            cat_items = (
                db.query(Item)
                .join(Category)
                .filter(Category.name.in_(pref_categories))
                .order_by(desc(Item.rating), desc(Item.rating_count))
                .limit(limit)
                .all()
            )
            for item in cat_items:
                results.append({
                    "item_id": item.id,
                    "score": round(0.85 + (item.rating / 50.0), 4),
                    "reason": f"Top solution in your selected interest '{item.category.name}'",
                    "algorithm": "cold_start_preference",
                    "content_score": 0.8,
                    "collaborative_score": 0.5
                })

        # Fill remaining with global trending / top rated items
        if len(results) < limit:
            needed = limit - len(results)
            already_ids = [r["item_id"] for r in results]
            popular_items = (
                db.query(Item)
                .filter(~Item.id.in_(already_ids) if already_ids else True)
                .order_by(desc(Item.rating), desc(Item.rating_count))
                .limit(needed)
                .all()
            )
            for item in popular_items:
                results.append({
                    "item_id": item.id,
                    "score": round(0.70 + (item.rating / 50.0), 4),
                    "reason": f"Top rated {item.cloud_provider} service ({item.rating}★)",
                    "algorithm": "cold_start_popular",
                    "content_score": 0.5,
                    "collaborative_score": 0.5
                })

        return results[:limit]

    def get_trending_items(self, db: Session, limit: int = 8) -> List[Dict[str, Any]]:
        """Calculates trending items based on recent interaction velocity."""
        trending_query = (
            db.query(
                Interaction.item_id,
                func.count(Interaction.id).label("interaction_count")
            )
            .group_by(Interaction.item_id)
            .order_by(desc("interaction_count"))
            .limit(limit)
            .all()
        )

        results = []
        if trending_query:
            max_count = trending_query[0][1] if trending_query else 1
            for item_id, count in trending_query:
                item = db.query(Item).filter(Item.id == item_id).first()
                if item:
                    score = round(0.7 + (0.3 * (count / max_count)), 4)
                    results.append({
                        "item_id": item.id,
                        "score": score,
                        "reason": f"High engagement surge ({count} recent cloud interactions)",
                        "algorithm": "trending",
                        "content_score": score,
                        "collaborative_score": score
                    })

        # Fallback if interactions are scarce
        if len(results) < limit:
            already_ids = [r["item_id"] for r in results]
            fallback = (
                db.query(Item)
                .filter(~Item.id.in_(already_ids) if already_ids else True)
                .order_by(desc(Item.rating_count), desc(Item.rating))
                .limit(limit - len(results))
                .all()
            )
            for item in fallback:
                results.append({
                    "item_id": item.id,
                    "score": 0.75,
                    "reason": "Popular choice across cloud architects",
                    "algorithm": "trending",
                    "content_score": 0.75,
                    "collaborative_score": 0.75
                })

        return results[:limit]

    def _log_recommendations(self, user_id: int, recommendations: List[Dict[str, Any]], algo: str, db: Session):
        """Audits recommendations to the database for analytics."""
        for rec in recommendations[:5]:
            log = Recommendation(
                user_id=user_id,
                item_id=rec["item_id"],
                score=rec["score"],
                algorithm=rec.get("algorithm", algo),
                reason=rec.get("reason", "Personalized match")
            )
            db.add(log)
        db.commit()

recommendation_engine = RecommendationEngine()
