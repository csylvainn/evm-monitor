"""
Détection de tokens ERC-20 pour HyperEVM
"""

import asyncio
from typing import Optional, Dict, Any
from config.settings import ERC20_FUNCTIONS, TOKEN_TIMEOUT, CREATOR_SEARCH_BLOCKS, CREATOR_SEARCH_STEP


class TokenDetector:
    """Détecteur de tokens ERC-20"""
    
    def __init__(self, rpc_manager):
        self.rpc_manager = rpc_manager
    
    async def check_if_token(self, contract_address: str) -> Optional[Dict[str, Any]]:
        """Vérifie si un contrat est un token ERC-20"""
        try:
            token_data = {}
            
            # Appeler chaque fonction ERC-20
            for func_name, signature in ERC20_FUNCTIONS.items():
                try:
                    result = await self.rpc_manager.rpc_call("eth_call", [
                        {"to": contract_address, "data": signature}, 
                        "latest"
                    ], timeout=TOKEN_TIMEOUT)
                    
                    if not result or result == "0x":
                        return None
                    
                    # Parser le résultat selon le type
                    parsed_value = self._parse_function_result(func_name, result)
                    if parsed_value is None:
                        return None
                    
                    token_data[func_name] = parsed_value
                
                except:
                    return None
            
            # Vérifier qu'on a toutes les données
            if len(token_data) == 4:
                return token_data
            else:
                return None
                
        except:
            return None
    
    def _parse_function_result(self, func_name: str, result: str) -> Optional[Any]:
        """Parse le résultat d'une fonction selon son type"""
        try:
            if func_name in ['name', 'symbol']:
                # String - décoder depuis les bytes
                return self._decode_string(result)
            
            elif func_name == 'decimals':
                # uint8
                return int(result, 16) if result != "0x" else 0
            
            elif func_name == 'totalSupply':
                # uint256
                return str(int(result, 16)) if result != "0x" else "0"
            
            return None
        except:
            return None
    
    def _decode_string(self, hex_data: str) -> str:
        """Décode une string depuis les données hex"""
        try:
            if len(hex_data) > 66:
                # Skip les 64 premiers chars (offset) puis 64 chars (length)
                data_part = hex_data[2:]  # Remove 0x
                if len(data_part) >= 128:
                    string_data = data_part[128:]
                    # Convertir hex en string
                    decoded = bytes.fromhex(string_data).decode('utf-8').rstrip('\x00')
                    return decoded[:50]  # Limiter la longueur
                else:
                    return "Unknown"
            else:
                return "Unknown"
        except:
            return "Unknown"
    
    async def get_contract_creator(self, contract_address: str, current_block: int) -> str:
        """Trouve le créateur d'un contrat"""
        try:
            # Chercher dans l'historique récent
            search_start = max(1, current_block - CREATOR_SEARCH_BLOCKS)
            
            for block_num in range(current_block, search_start - 1, -CREATOR_SEARCH_STEP):
                try:
                    block_data = await self.rpc_manager.get_block(block_num)
                    if not block_data or "transactions" not in block_data:
                        continue
                    
                    for tx in block_data["transactions"]:
                        # Transaction de création de contrat (to = null)
                        if tx.get("to") is None and tx.get("from"):
                            # Vérifier si cette tx a créé notre contrat
                            tx_receipt = await self.rpc_manager.get_transaction_receipt(tx["hash"])
                            if (tx_receipt and 
                                tx_receipt.get("contractAddress", "").lower() == contract_address.lower()):
                                return tx["from"]
                except:
                    continue
            
            return "Unknown"
        except:
            return "Unknown"
    
    async def detect_tokens_batch(self, contract_addresses: list, current_block: int) -> Dict[str, Dict]:
        """Détecte les tokens dans un batch de contrats"""
        if not contract_addresses:
            return {}
        
        semaphore = asyncio.Semaphore(10)  # Limiter la concurrence
        
        async def detect_single(address):
            async with semaphore:
                token_data = await self.check_if_token(address)
                if token_data:
                    # Récupérer le créateur
                    creator = await self.get_contract_creator(address, current_block)
                    token_data['creator'] = creator
                    return address, token_data
                return address, None
        
        tasks = [detect_single(addr) for addr in contract_addresses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        tokens_found = {}
        for result in results:
            if isinstance(result, tuple) and len(result) == 2:
                addr, token_data = result
                if token_data:
                    tokens_found[addr] = token_data
        
        return tokens_found
    
    async def retry_failed_token(self, address: str, current_block: int) -> Optional[Dict[str, Any]]:
        """Retente la détection d'un token échoué"""
        token_data = await self.check_if_token(address)
        if token_data:
            creator = await self.get_contract_creator(address, current_block)
            token_data['creator'] = creator
            return token_data
        return None


# Fonctions utilitaires
def format_supply(supply_str: str, decimals: int) -> str:
    """Formate le totalSupply avec decimals"""
    try:
        supply = int(supply_str)
        if decimals > 0:
            formatted = supply / (10 ** decimals)
            if formatted >= 1000000:
                return f"{formatted/1000000:.1f}M"
            elif formatted >= 1000:
                return f"{formatted/1000:.1f}K"
            else:
                return f"{formatted:.2f}"
        else:
            return f"{supply:,}"
    except:
        return supply_str

def format_number(value) -> str:
    """Formate un nombre avec séparateurs"""
    try:
        if isinstance(value, str):
            num = int(value)
        else:
            num = value
        return f"{num:,}"
    except:
        return str(value)