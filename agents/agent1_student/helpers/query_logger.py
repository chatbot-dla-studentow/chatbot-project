"""
Moduł do logowania zapytań i odpowiedzi w Qdrant dla Agent_1
"""
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import logging

logger = logging.getLogger(__name__)

# Kategorie dla Agent_1
CATEGORIES = {
    "dane_osobowe": ["dane", "osobowe", "zmiana", "adres", "telefon", "email", "RODO", "ochrona"],
    "egzaminy": ["egzamin", "obrona", "praca", "dyplomowa", "sesja", "reklamacja", "ocena", "termin"],
    "rekrutacja": ["rekrutacja", "przyjęcie", "zmiana", "kierunek", "rezygnacja", "wznowienie", "skreślenie"],
    "stypendia": ["stypendium", "socjalne", "rektora", "niepełnosprawni", "sportowcy", "erasmus"],
    "urlopy_zwolnienia": ["urlop", "dziekański", "zwolnienie", "WF", "nieobecność"]
}

class QueryLogger:
    """Klasa do logowania zapytań w Qdrant"""
    
    def __init__(self, qdrant_client: QdrantClient, embedding_func):
        self.client = qdrant_client
        self.embedding_func = embedding_func
        self.query_collection = "agent1_query_logs"
        self.qa_collection = "agent1_qa_logs"
    
    def detect_category(self, text: str) -> str:
        """
        Wykrywa kategorię zapytania na podstawie słów kluczowych.
        Zwraca nazwę kategorii lub 'unknown'.
        """
        text_lower = text.lower()
        
        # Zlicz dopasowania dla każdej kategorii
        matches = {}
        for category, keywords in CATEGORIES.items():
            count = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            if count > 0:
                matches[category] = count
        
        # Zwróć kategorię z największą liczbą dopasowań
        if matches:
            return max(matches.items(), key=lambda x: x[1])[0]
        return "unknown"
    
    def log_query(self, query: str, category: Optional[str] = None, 
                  user_id: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
        """
        Loguje zapytanie użytkownika do Qdrant.
        
        Args:
            query: Tekst zapytania
            category: Kategoria (jeśli None, będzie wykryta automatycznie)
            user_id: ID użytkownika
            metadata: Dodatkowe metadane
        
        Returns:
            ID zapisanego logu
        """
        try:
            # Wykryj kategorię jeśli nie podano
            if category is None:
                category = self.detect_category(query)
            
            # Generuj embedding
            embedding = self.embedding_func(query)
            if not embedding:
                logger.error("Nie można wygenerować embeddingu dla zapytania")
                return None
            
            # Przygotuj metadane
            log_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            payload = {
                "query": query,
                "category": category,
                "timestamp": timestamp,
                "user_id": user_id or "anonymous",
                "log_id": log_id
            }
            
            if metadata:
                payload.update(metadata)
            
            # Zapisz do Qdrant
            point = PointStruct(
                id=log_id,
                vector=embedding,
                payload=payload
            )
            
            self.client.upsert(
                collection_name=self.query_collection,
                points=[point]
            )
            
            logger.info(f"Zapytanie zalogowane: {log_id} (kategoria: {category})")
            return log_id
            
        except Exception as e:
            logger.error(f"Błąd logowania zapytania: {e}")
            return None
    
    def log_qa_pair(self, query: str, answer: str, category: Optional[str] = None,
                    sources: Optional[List[str]] = None, score: Optional[float] = None,
                    user_id: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
        """
        Loguje parę pytanie-odpowiedź do Qdrant.
        
        Args:
            query: Pytanie użytkownika
            answer: Odpowiedź chatbota
            category: Kategoria
            sources: Lista źródeł użytych w odpowiedzi
            score: Score RAG
            user_id: ID użytkownika
            metadata: Dodatkowe metadane
        
        Returns:
            ID zapisanego logu
        """
        try:
            # Wykryj kategorię jeśli nie podano
            if category is None:
                category = self.detect_category(query)
            
            # Generuj embedding dla całego kontekstu (pytanie + odpowiedź)
            context = f"Pytanie: {query}\nOdpowiedź: {answer}"
            embedding = self.embedding_func(context)
            if not embedding:
                logger.error("Nie można wygenerować embeddingu dla QA pair")
                return None
            
            # Przygotuj metadane
            log_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            payload = {
                "query": query,
                "answer": answer,
                "category": category,
                "timestamp": timestamp,
                "user_id": user_id or "anonymous",
                "log_id": log_id,
                "sources": sources or [],
                "rag_score": score
            }
            
            if metadata:
                payload.update(metadata)
            
            # Zapisz do Qdrant
            point = PointStruct(
                id=log_id,
                vector=embedding,
                payload=payload
            )
            
            self.client.upsert(
                collection_name=self.qa_collection,
                points=[point]
            )
            
            logger.info(f"QA pair zalogowana: {log_id} (kategoria: {category})")
            return log_id
            
        except Exception as e:
            logger.error(f"Błąd logowania QA pair: {e}")
            return None
    
    def get_query_stats(self) -> Dict:
        """Zwraca statystyki zapytań"""
        try:
            collection_info = self.client.get_collection(self.query_collection)
            
            # Pobierz wszystkie punkty (do 10000)
            results = self.client.scroll(
                collection_name=self.query_collection,
                limit=10000
            )
            
            points = results[0] if results else []
            
            # Policz kategorie
            categories = {}
            for point in points:
                cat = point.payload.get("category", "unknown")
                categories[cat] = categories.get(cat, 0) + 1
            
            return {
                "total_queries": collection_info.points_count,
                "categories": categories
            }
        except Exception as e:
            logger.error(f"Błąd pobierania statystyk: {e}")
            return {"total_queries": 0, "categories": {}}
    
    def get_qa_stats(self) -> Dict:
        """Zwraca statystyki QA pairs"""
        try:
            collection_info = self.client.get_collection(self.qa_collection)
            
            results = self.client.scroll(
                collection_name=self.qa_collection,
                limit=10000
            )
            
            points = results[0] if results else []
            
            # Policz kategorie i średni score
            categories = {}
            scores = []
            for point in points:
                cat = point.payload.get("category", "unknown")
                categories[cat] = categories.get(cat, 0) + 1
                
                score = point.payload.get("rag_score")
                if score is not None:
                    scores.append(score)
            
            avg_score = sum(scores) / len(scores) if scores else 0
            
            return {
                "total_qa_pairs": collection_info.points_count,
                "categories": categories,
                "average_rag_score": round(avg_score, 3)
            }
        except Exception as e:
            logger.error(f"Błąd pobierania statystyk QA: {e}")
            return {"total_qa_pairs": 0, "categories": {}, "average_rag_score": 0}
    
    def search_similar_queries(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Wyszukuje podobne zapytania w historii.
        """
        try:
            embedding = self.embedding_func(query)
            if not embedding:
                return []
            
            results = self.client.query_points(
                collection_name=self.query_collection,
                query=embedding,
                limit=limit
            )
            
            similar = []
            for point in results.points:
                similar.append({
                    "query": point.payload.get("query"),
                    "category": point.payload.get("category"),
                    "timestamp": point.payload.get("timestamp"),
                    "score": point.score
                })
            
            return similar
            
        except Exception as e:
            logger.error(f"Błąd wyszukiwania podobnych zapytań: {e}")
            return []
