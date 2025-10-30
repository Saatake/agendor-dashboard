"""
Cliente para API do Agendor CRM
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time
from config import API_BASE_URL, HEADERS


class AgendorClient:
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.headers = HEADERS
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            return {"data": []}
    
    def _get_all_pages(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict]:
        # busca todos os registros paginados
        all_data = []
        page = 1
        params = params or {}
        
        while True:
            params['page'] = page
            params['per_page'] = 100
            
            response = self._make_request(endpoint, params)
            
            if not response or 'data' not in response:
                break
            
            data = response['data']
            if not data:
                break
            
            all_data.extend(data)
            
            if len(data) < 100:
                break
            
            page += 1
            time.sleep(0.1)  # evita rate limiting
        
        return all_data
    
    def get_deals(self, status: Optional[str] = None) -> List[Dict]:
        params = {}
        if status:
            params['status'] = status
        
        return self._get_all_pages('deals', params)
    
    def get_deals_won(self) -> List[Dict]:
        return self.get_deals(status='won')
    
    def get_deals_lost(self) -> List[Dict]:
        return self.get_deals(status='lost')
    
    def get_deals_ongoing(self) -> List[Dict]:
        return self.get_deals(status='ongoing')
    
    def get_people(self) -> List[Dict]:
        return self._get_all_pages('people')
    
    def get_organizations(self) -> List[Dict]:
        return self._get_all_pages('organizations')
    
    def get_funnels(self) -> List[Dict]:
        response = self._make_request('funnels')
        return response.get('data', [])
    
    def get_products(self) -> List[Dict]:
        return self._get_all_pages('products')
    
    def get_users(self) -> List[Dict]:
        response = self._make_request('users')
        return response.get('data', [])
    
    def get_tasks(self, status: Optional[str] = None) -> List[Dict]:
        params = {}
        if status:
            params['status'] = status
        
        return self._get_all_pages('tasks', params)
    
    def test_connection(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}/users")
            return response.status_code == 200
        except:
            return False
