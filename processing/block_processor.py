"""
Traitement des blocs et statistiques d'activité pour HyperEVM
"""

import asyncio
import time
from datetime import datetime
from typing import List, Dict, Set, Tuple
from core.utils import get_time_slot, get_date_from_timestamp


class BlockProcessor:
    """Processeur de blocs avec statistiques d'activité"""
    
    def __init__(self, rpc_manager, db_manager, address_classifier, token_detector):
        self.rpc_manager = rpc_manager
        self.db_manager = db_manager
        self.address_classifier = address_classifier
        self.token_detector = token_detector
    
    async def process_block_batch(self, start_block: int, end_block: int) -> int:
        """Traite un batch de blocs complet"""
        print(f"⚡ Batch {start_block:,} → {end_block:,} ({end_block - start_block + 1} blocs)")
        
        # Récupérer tous les blocs en parallèle
        blocks_data = await self._fetch_blocks_parallel(start_block, end_block)
        
        # Extraire adresses et préparer stats
        all_addresses, blocks_with_timestamps, stats = self._extract_data_from_blocks(
            blocks_data, start_block, end_block
        )
        
        # Traiter les nouvelles adresses
        addresses_saved = await self._process_new_addresses(all_addresses, end_block)
        
        # Sauvegarder stats d'activité
        if blocks_with_timestamps:
            time_slots = self._calculate_activity_stats(blocks_with_timestamps)
            self.db_manager.save_activity_stats(time_slots)
        
        print(f"  📊 {stats['successful_blocks']}/{stats['total_blocks']} blocs, "
              f"{stats['total_transactions']} tx, {addresses_saved} adresses")
        
        return addresses_saved
    
    async def _fetch_blocks_parallel(self, start_block: int, end_block: int) -> List:
        """Récupère les blocs en parallèle"""
        tasks = [
            self.rpc_manager.get_block(block_num) 
            for block_num in range(start_block, end_block + 1)
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def _extract_data_from_blocks(self, blocks_data: List, start_block: int, end_block: int) -> Tuple:
        """Extrait les données des blocs"""
        all_addresses = set()
        total_transactions = 0
        successful_blocks = 0
        blocks_with_timestamps = []
        
        for block_num, block_data in zip(range(start_block, end_block + 1), blocks_data):
            if isinstance(block_data, Exception) or not block_data:
                continue
            
            addresses, tx_count = self.address_classifier.extract_addresses_from_block(block_data)
            if addresses:
                all_addresses.update(addresses)
                total_transactions += tx_count
                successful_blocks += 1
                
                timestamp = int(block_data.get("timestamp", "0x0"), 16)
                blocks_with_timestamps.append((block_data, timestamp))
        
        stats = {
            'successful_blocks': successful_blocks,
            'total_blocks': end_block - start_block + 1,
            'total_transactions': total_transactions
        }
        
        return all_addresses, blocks_with_timestamps, stats
    
    async def _process_new_addresses(self, all_addresses: Set[str], current_block: int) -> int:
        """Traite les nouvelles adresses découvertes"""
        if not all_addresses:
            return 0
        
        # Filtrer les adresses nouvelles
        new_addresses = self.db_manager.filter_new_addresses(all_addresses)
        
        if not new_addresses:
            # Toutes les adresses sont déjà connues
            address_types = {addr: "unknown" for addr in all_addresses}
        else:
            # Classifier les nouvelles adresses
            address_types = await self.address_classifier.classify_addresses_batch(new_addresses)
            
            # Détecter les tokens dans les nouveaux contrats
            contracts = [addr for addr, addr_type in address_types.items() if addr_type == "contract"]
            if contracts:
                tokens_found = await self.token_detector.detect_tokens_batch(contracts, current_block)
                if tokens_found:
                    self.db_manager.save_tokens(tokens_found)
                    print(f"  🪙 {len(tokens_found)} nouveaux tokens détectés")
            
            # Afficher les stats de classification
            by_type = self.address_classifier.separate_by_type(address_types)
            print(f"  ✅ Types: {len(by_type['wallet'])} wallets, {len(by_type['contract'])} contrats")
        
        # Sauvegarder toutes les adresses
        last_timestamp = int(time.time())
        return self.db_manager.save_addresses(address_types, current_block, last_timestamp)
    
    def _calculate_activity_stats(self, blocks_with_timestamps: List) -> Dict:
        """Calcule les stats d'activité par tranches de temps"""
        time_slots = {}
        
        for block_data, timestamp in blocks_with_timestamps:
            if not block_data or "transactions" not in block_data:
                continue
                
            date = get_date_from_timestamp(timestamp)
            time_slot = get_time_slot(timestamp)
            key = (date, time_slot)
            
            if key not in time_slots:
                time_slots[key] = {'addresses': set(), 'transactions': 0}
            
            transactions = block_data.get("transactions", [])
            time_slots[key]['transactions'] += len(transactions)
            
            for tx in transactions:
                if tx.get("from"):
                    time_slots[key]['addresses'].add(tx["from"].lower())
                if tx.get("to"):
                    time_slots[key]['addresses'].add(tx["to"].lower())
        
        return time_slots
    
    async def update_unknown_types(self, limit: int = 100) -> None:
        """Met à jour les types d'adresses inconnus"""
        unknown_addresses = self.db_manager.get_unknown_addresses(limit)
        
        if unknown_addresses:
            print(f"🔄 Mise à jour de {len(unknown_addresses)} types inconnus...")
            
            address_types = await self.address_classifier.classify_addresses_batch(
                set(unknown_addresses)
            )
            
            self.db_manager.update_address_types(address_types)
            
            by_type = self.address_classifier.separate_by_type(address_types)
            print(f"  ✅ Mis à jour: {len(by_type['wallet'])} wallets, {len(by_type['contract'])} contrats")
    
    async def retry_failed_tokens(self, limit: int = 50) -> None:
        """Retente les tokens échoués"""
        failed_addresses = self.db_manager.get_failed_tokens(limit)
        
        if failed_addresses:
            print(f"🔄 Retry {len(failed_addresses)} tokens échoués...")
            
            for address in failed_addresses:
                # Récupérer le bloc actuel pour la recherche du créateur
                current_block = await self.rpc_manager.get_latest_block()
                
                token_data = await self.token_detector.retry_failed_token(address, current_block)
                if token_data:
                    self.db_manager.save_tokens({address: token_data})
                    print(f"  ✅ Token récupéré: {address}")
                else:
                    # Marquer la tentative
                    self.db_manager.mark_token_retry(address)