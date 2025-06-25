"""
Classification des adresses (wallet vs contrat) pour HyperEVM
"""

import asyncio
from typing import Dict, Set


class AddressClassifier:
    """Classificateur d'adresses"""
    
    def __init__(self, rpc_manager):
        self.rpc_manager = rpc_manager
    
    async def check_address_type(self, address: str) -> str:
        """Vérifie si une adresse est un wallet ou un contrat"""
        try:
            code = await self.rpc_manager.get_code(address)
            
            if code is None:
                return "unknown"
            
            return "wallet" if (code == "0x" or len(code) <= 2) else "contract"
                
        except:
            return "unknown"
    
    async def classify_addresses_batch(self, addresses: Set[str]) -> Dict[str, str]:
        """Classifie plusieurs adresses en parallèle"""
        if not addresses:
            return {}
        
        semaphore = asyncio.Semaphore(15)  # Limiter la concurrence
        
        async def classify_single(address):
            async with semaphore:
                return address, await self.check_address_type(address)
        
        tasks = [classify_single(addr) for addr in addresses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        address_types = {}
        for result in results:
            if isinstance(result, tuple) and len(result) == 2:
                addr, addr_type = result
                address_types[addr] = addr_type
        
        return address_types
    
    def extract_addresses_from_block(self, block_data: dict) -> tuple[Set[str], int]:
        """Extrait les adresses d'un bloc"""
        addresses = set()
        
        if not block_data or "transactions" not in block_data:
            return addresses, 0
            
        for tx in block_data["transactions"]:
            if tx.get("from"):
                addresses.add(tx["from"].lower())
            if tx.get("to"):
                addresses.add(tx["to"].lower())
        
        return addresses, len(block_data["transactions"])
    
    def separate_by_type(self, address_types: Dict[str, str]) -> Dict[str, Set[str]]:
        """Sépare les adresses par type"""
        by_type = {"wallet": set(), "contract": set(), "unknown": set()}
        
        for address, addr_type in address_types.items():
            by_type[addr_type].add(address)
        
        return by_type