#!/usr/bin/env python3
"""
HyperEVM Smart Monitor - Version modulaire
Auto-Switch RPC + Détection wallet/contrat + Tokens ERC-20 + Stats d'activité
"""

import asyncio
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import CHECK_INTERVAL, BATCH_SIZE, MESSAGES, UPDATE_UNKNOWN_INTERVAL
from core.database import Database
from core.rpc_manager import create_rpc_manager
from detection.address_classifier import AddressClassifier
from detection.token_detector import TokenDetector
from processing.block_processor import BlockProcessor


class HyperEVMMonitor:
    """Moniteur principal HyperEVM"""
    
    def __init__(self):
        self.db_manager = None
        self.rpc_manager = None
        self.address_classifier = None
        self.token_detector = None
        self.block_processor = None
        self.current_block = None
        self.update_counter = 0
    
    async def initialize(self):
        """Initialise tous les composants"""
        print(MESSAGES['monitor_start'])
        print(MESSAGES['monitor_desc'])
        print(f"⚡ Check: {CHECK_INTERVAL}s | Batch: {BATCH_SIZE}")
        print("-" * 70)
        
        # Initialiser les composants
        self.db_manager = Database()
        self.rpc_manager = await create_rpc_manager(self.db_manager)
        self.address_classifier = AddressClassifier(self.rpc_manager)
        self.token_detector = TokenDetector(self.rpc_manager)
        self.block_processor = BlockProcessor(
            self.rpc_manager, 
            self.db_manager, 
            self.address_classifier, 
            self.token_detector
        )
        
        # Récupérer l'état de progression
        saved_block, _ = self.db_manager.get_checkpoint()
        if saved_block:
            self.current_block = saved_block
            print(f"📋 Reprise depuis bloc: {self.current_block:,}")
        else:
            print("🆕 Première exécution")
    
    async def ensure_rpc_connection(self) -> bool:
        """S'assure qu'une connexion RPC est disponible"""
        if not await self.rpc_manager.switch_rpc(force_retest=True):
            print("❌ Impossible de trouver un RPC fonctionnel")
            return False
        return True
    
    async def handle_new_blocks(self, latest_block: int) -> int:
        """Traite les nouveaux blocs disponibles"""
        if latest_block <= self.current_block:
            return 0
        
        new_blocks = latest_block - self.current_block
        print(f"\n📦 {new_blocks} nouveaux blocs ({self.current_block + 1:,} → {latest_block:,})")
        
        total_addresses = 0
        start_block = self.current_block + 1
        
        # Traitement par batches
        while start_block <= latest_block:
            end_block = min(start_block + BATCH_SIZE - 1, latest_block)
            
            addresses_found = await self.block_processor.process_block_batch(start_block, end_block)
            total_addresses += addresses_found
            
            # Mettre à jour le checkpoint
            self.current_block = end_block
            self.db_manager.save_checkpoint(end_block)
            
            start_block = end_block + 1
            await asyncio.sleep(0.1)  # Petite pause entre les batches
        
        if total_addresses > 0:
            rpc_info = self.rpc_manager.get_current_rpc_info()
            print(f"🎯 TOTAL: {total_addresses} adresses [{rpc_info['name']}]")
        
        return total_addresses
    
    async def perform_maintenance(self):
        """Effectue la maintenance périodique"""
        # Mise à jour des types inconnus
        await self.block_processor.update_unknown_types()
        
        # Retry des tokens échoués
        await self.block_processor.retry_failed_tokens()
        
        # Reset du compteur
        self.update_counter = 0
    
    async def monitoring_cycle(self):
        """Un cycle complet de monitoring"""
        try:
            # Récupérer le dernier bloc
            latest_block = await self.rpc_manager.get_latest_block()
            
            if not latest_block:
                print("❌ Impossible de récupérer le dernier bloc")
                return False
            
            # Première fois - initialiser le bloc de départ
            if self.current_block is None:
                self.current_block = latest_block
                self.db_manager.save_checkpoint(self.current_block)
                print(f"🎯 Surveillance démarrée au bloc {self.current_block:,}")
                return True
            
            # Traiter les nouveaux blocs
            if latest_block > self.current_block:
                await self.handle_new_blocks(latest_block)
            else:
                print("💤 Aucun nouveau bloc")
            
            # Maintenance périodique
            self.update_counter += 1
            if self.update_counter >= UPDATE_UNKNOWN_INTERVAL:
                await self.perform_maintenance()
            
            # Test RPC périodique
            if self.rpc_manager.should_retest_rpc():
                await self.rpc_manager.switch_rpc()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur cycle: {e}")
            await self.rpc_manager.switch_rpc(force_retest=True)
            return False
    
    async def run(self):
        """Lance le monitoring principal"""
        try:
            # Initialiser
            await self.initialize()
            
            # S'assurer qu'on a une connexion RPC
            if not await self.ensure_rpc_connection():
                return
            
            # Boucle principale
            while True:
                success = await self.monitoring_cycle()
                
                if not success:
                    print("⚠️ Cycle échoué, attente avant retry...")
                
                await asyncio.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n🛑 Arrêté par utilisateur")
        except Exception as e:
            print(f"❌ Erreur fatale: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Nettoie les ressources"""
        if self.rpc_manager:
            await self.rpc_manager.close()


async def main():
    """Point d'entrée principal"""
    monitor = HyperEVMMonitor()
    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())