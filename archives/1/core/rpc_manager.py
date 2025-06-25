"""
Gestionnaire RPC intelligent pour HyperEVM
Gestion automatique du switch, tests, et fallback
"""

import asyncio
import aiohttp
import time
from typing import Optional, Dict, Any, List
from config.settings import (
    RPC_ENDPOINTS, RPC_TIMEOUT, RPC_TEST_TIMEOUT, 
    RPC_MAX_FAILURES, RPC_RETEST_INTERVAL
)


class RPCManager:
    """Gestionnaire RPC intelligent avec auto-switch et fallback"""
    
    def __init__(self, db_manager=None):
        self.current_rpc = None
        self.current_rpc_name = ""
        self.session = None
        self.request_id = 0
        self.rpc_failures = {}
        self.last_rpc_test = 0
        self.db_manager = db_manager
        
    async def initialize(self):
        """Initialise la session HTTP"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        # Charger le dernier RPC utilisé si disponible
        if self.db_manager:
            _, saved_rpc = self.db_manager.get_checkpoint()
            if saved_rpc:
                self.current_rpc = saved_rpc
                # Extraire le nom du RPC
                for rpc_info in RPC_ENDPOINTS:
                    if rpc_info["url"] == saved_rpc:
                        self.current_rpc_name = rpc_info["name"]
                        break
                print(f"🔗 RPC restauré: {self.current_rpc_name}")
    
    async def close(self):
        """Ferme la session HTTP"""
        if self.session:
            await self.session.close()
    
    async def test_rpc_endpoint(self, rpc_info: Dict[str, Any]) -> Dict[str, Any]:
        """Teste un endpoint RPC"""
        url = rpc_info["url"]
        name = rpc_info["name"]
        
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": self.request_id
        }
        self.request_id += 1
        
        try:
            start_time = time.time()
            async with self.session.post(url, json=payload, timeout=RPC_TEST_TIMEOUT) as response:
                latency = time.time() - start_time
                
                if response.status != 200:
                    return {"success": False, "error": f"HTTP {response.status}", "latency": latency}
                
                result = await response.json()
                
                if "error" in result:
                    return {"success": False, "error": result['error']['message'], "latency": latency}
                
                latest_block = int(result.get("result", "0x0"), 16)
                
                return {
                    "success": True, 
                    "latest_block": latest_block, 
                    "latency": latency,
                    "name": name,
                    "url": url
                }
                
        except asyncio.TimeoutError:
            return {"success": False, "error": "Timeout", "latency": RPC_TEST_TIMEOUT}
        except Exception as e:
            return {"success": False, "error": str(e), "latency": RPC_TEST_TIMEOUT}
    
    async def find_best_rpc(self, verbose: bool = True) -> Optional[Dict[str, Any]]:
        """Trouve le meilleur RPC disponible"""
        if verbose:
            print("🔍 Recherche du meilleur RPC...")
        
        results = []
        for rpc_info in RPC_ENDPOINTS:
            if verbose:
                print(f"🔌 Test {rpc_info['name']}...", end=" ")
            
            result = await self.test_rpc_endpoint(rpc_info)
            result.update(rpc_info)
            results.append(result)
            
            if result["success"] and verbose:
                print(f"✅ {result['latency']:.2f}s")
            elif verbose:
                print(f"❌ {result['error']}")
        
        working_rpcs = [r for r in results if r["success"]]
        
        if not working_rpcs:
            if verbose:
                print("❌ Aucun RPC fonctionnel!")
            return None
        
        # Meilleur = priorité puis latence
        best_rpc = min(working_rpcs, key=lambda x: (x["priority"], x["latency"]))
        if verbose:
            print(f"🎯 Meilleur RPC: {best_rpc['name']} ({best_rpc['latency']:.2f}s)")
        
        return best_rpc
    
    async def switch_rpc(self, force_retest: bool = False, verbose: bool = True) -> bool:
        """Switch vers le meilleur RPC"""
        now = time.time()
        
        if not force_retest and self.current_rpc and (now - self.last_rpc_test) < RPC_RETEST_INTERVAL:
            return True
        
        best_rpc = await self.find_best_rpc(verbose)
        
        if not best_rpc:
            return False
        
        if not self.current_rpc or self.current_rpc != best_rpc["url"]:
            self.current_rpc = best_rpc["url"]
            self.current_rpc_name = best_rpc["name"]
            if verbose:
                print(f"🔄 Switch vers {self.current_rpc_name}")
            
            # Sauvegarder le choix si DB disponible
            if self.db_manager:
                self.db_manager.save_rpc_choice(self.current_rpc)
        
        self.last_rpc_test = now
        return True
    
    async def rpc_call(self, method: str, params: List = None, timeout: int = RPC_TIMEOUT) -> Optional[Any]:
        """Effectue un appel RPC avec fallback automatique"""
        if params is None:
            params = []
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.request_id
        }
        self.request_id += 1
        
        for attempt in range(2):
            if not self.current_rpc:
                if not await self.switch_rpc(force_retest=True):
                    return None
            
            try:
                async with self.session.post(self.current_rpc, json=payload, timeout=timeout) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")
                    
                    result = await response.json()
                    
                    if "error" in result:
                        error_msg = result['error']['message']
                        if "3000 archived blocks" in error_msg:
                            print(f"🚫 Quota épuisé sur {self.current_rpc_name}")
                            self.current_rpc = None
                            continue
                        return None
                    
                    # Succès - réinitialiser le compteur d'échecs
                    if self.current_rpc in self.rpc_failures:
                        del self.rpc_failures[self.current_rpc]
                    
                    return result.get("result")
                    
            except Exception as e:
                self.rpc_failures[self.current_rpc] = self.rpc_failures.get(self.current_rpc, 0) + 1
                
                if self.rpc_failures.get(self.current_rpc, 0) >= RPC_MAX_FAILURES:
                    print(f"🔄 Trop d'échecs sur {self.current_rpc_name}")
                    self.current_rpc = None
                
                if attempt == 0:
                    await self.switch_rpc(force_retest=True)
        
        return None
    
    async def get_latest_block(self) -> int:
        """Récupère le numéro du dernier bloc"""
        result = await self.rpc_call("eth_blockNumber")
        return int(result, 16) if result else 0
    
    async def get_block(self, block_number: int) -> Optional[Dict]:
        """Récupère un bloc complet avec transactions"""
        return await self.rpc_call("eth_getBlockByNumber", [hex(block_number), True])
    
    async def get_code(self, address: str) -> Optional[str]:
        """Récupère le code d'un contrat"""
        return await self.rpc_call("eth_getCode", [address, "latest"])
    
    async def call_contract(self, to: str, data: str) -> Optional[str]:
        """Effectue un appel de fonction sur un contrat"""
        return await self.rpc_call("eth_call", [{"to": to, "data": data}, "latest"])
    
    async def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict]:
        """Récupère le receipt d'une transaction"""
        return await self.rpc_call("eth_getTransactionReceipt", [tx_hash])
    
    def get_current_rpc_info(self) -> Dict[str, str]:
        """Retourne les infos du RPC actuel"""
        return {
            "name": self.current_rpc_name,
            "url": self.current_rpc or "None",
            "failures": str(self.rpc_failures.get(self.current_rpc, 0))
        }
    
    def should_retest_rpc(self) -> bool:
        """Vérifie s'il faut retester les RPCs"""
        return time.time() - self.last_rpc_test > RPC_RETEST_INTERVAL
    
    async def ensure_connection(self) -> bool:
        """S'assure qu'une connexion RPC est disponible"""
        if not self.session:
            await self.initialize()
        
        if not self.current_rpc:
            return await self.switch_rpc(force_retest=True)
        
        return True


# Fonctions utilitaires pour compatibilité
async def create_rpc_manager(db_manager=None) -> RPCManager:
    """Crée et initialise un gestionnaire RPC"""
    manager = RPCManager(db_manager)
    await manager.initialize()
    return manager