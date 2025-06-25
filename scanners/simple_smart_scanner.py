# scanners/simple_smart_scanner.py
"""
Scanner intelligent simplifié - Version stable et efficace
Au lieu d'analyser l'historique, on utilise une approche plus simple
"""

import asyncio
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from core.utils import PerformanceTimer, format_supply


@dataclass
class SimpleScanConfig:
    """Configuration simplifiée du scanner"""
    batch_size: int = 25           # Wallets par batch
    token_batch_size: int = 30     # Tokens à vérifier en parallèle
    popular_tokens_limit: int = 30 # Nombre de tokens populaires à tester
    retry_attempts: int = 2        # Tentatives en cas d'échec
    scan_timeout: int = 45         # Timeout par wallet
    detect_new_tokens: bool = True # Détecter les nouveaux tokens


class SimpleTokenBalanceDetector:
    """Détecteur de balances ERC-20 simplifié et optimisé"""
    
    def __init__(self, rpc_manager):
        self.rpc_manager = rpc_manager
        self.balance_signature = "0x70a08231"  # balanceOf(address)
    
    async def get_token_balance(self, token_address: str, wallet_address: str) -> Optional[str]:
        """Récupère la balance d'un token pour un wallet"""
        try:
            # Préparer l'appel balanceOf(wallet_address)
            wallet_padded = wallet_address[2:].zfill(64) if wallet_address.startswith('0x') else wallet_address.zfill(64)
            call_data = self.balance_signature + wallet_padded
            
            result = await asyncio.wait_for(
                self.rpc_manager.call_contract(token_address, call_data),
                timeout=2
            )
            
            if not result or result == "0x" or result == "0x0":
                return "0"
            
            # Convertir la réponse hex en decimal
            try:
                balance = int(result, 16)
                return str(balance)
            except ValueError:
                return "0"
                
        except:
            return None
    
    async def get_wallet_token_balances(self, wallet_address: str, 
                                      token_addresses: List[str], 
                                      config: SimpleScanConfig) -> Dict[str, str]:
        """Récupère les balances de tokens spécifiques pour un wallet"""
        semaphore = asyncio.Semaphore(config.token_batch_size)
        
        async def get_single_balance(token_addr):
            async with semaphore:
                for attempt in range(config.retry_attempts):
                    try:
                        balance = await self.get_token_balance(token_addr, wallet_address)
                        return token_addr, balance
                    except:
                        if attempt == config.retry_attempts - 1:
                            return token_addr, None
                        await asyncio.sleep(0.5)
        
        tasks = [get_single_balance(token_addr) for token_addr in token_addresses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrer les résultats valides (balance > 0)
        balances = {}
        for result in results:
            if isinstance(result, tuple) and len(result) == 2:
                token_addr, balance = result
                if balance is not None and balance != "0":
                    balances[token_addr] = balance
        
        return balances


class SimpleSmartWalletScanner:
    """Scanner simplifié qui teste les tokens populaires"""
    
    def __init__(self, rpc_manager, db_manager, token_detector):
        self.rpc_manager = rpc_manager
        self.db_manager = db_manager
        self.token_detector = token_detector
        self.balance_detector = SimpleTokenBalanceDetector(rpc_manager)
        self.stats = {
            'wallets_scanned': 0,
            'tokens_found': 0,
            'new_tokens_discovered': 0,
            'total_balance_checks': 0,
            'errors': 0,
            'start_time': None
        }
    
    def get_popular_tokens(self, limit: int = 30) -> List[str]:
        """Récupère les tokens les plus populaires/récents"""
        # Récupérer les tokens les plus récents (supposés plus populaires)
        tokens = self.db_manager.get_tokens_page(1, limit)
        return [token['address'] for token in tokens]
    
    async def get_token_info(self, token_address: str) -> Optional[Dict]:
        """Récupère les infos d'un token depuis la base ou les détecte"""
        # Essayer de récupérer depuis la base d'abord
        tokens = self.db_manager.get_tokens_page(1, 1, search=token_address)
        if tokens and len(tokens) > 0:
            return {
                'name': tokens[0].get('name', 'Unknown'),
                'symbol': tokens[0].get('symbol', 'UNK'),
                'decimals': tokens[0].get('decimals', 18),
                'total_supply': tokens[0].get('total_supply', '0')
            }
        
        # Token inconnu - essayer de le détecter
        if hasattr(self, 'detect_new_tokens') and self.detect_new_tokens:
            token_data = await self.token_detector.check_if_token(token_address)
            if token_data:
                # Sauvegarder le nouveau token
                self.db_manager.save_tokens({token_address: token_data})
                self.stats['new_tokens_discovered'] += 1
                return token_data
        
        return None
    
    async def scan_wallet_tokens_simple(self, wallet_address: str, 
                                       token_addresses: List[str], 
                                       config: SimpleScanConfig) -> Optional[Dict]:
        """Scan simplifié d'un wallet avec liste de tokens"""
        try:
            timer = PerformanceTimer().start()
            
            # Récupérer les balances de tous les tokens populaires
            balances = await asyncio.wait_for(
                self.balance_detector.get_wallet_token_balances(
                    wallet_address, token_addresses, config
                ),
                timeout=config.scan_timeout
            )
            
            self.stats['total_balance_checks'] += len(token_addresses)
            
            if not balances:
                return None
            
            # Enrichir avec les infos des tokens
            enriched_tokens = {}
            for token_address, balance in balances.items():
                # Récupérer les infos du token depuis la base
                token_info = await self.get_token_info(token_address)
                
                if token_info:
                    # Formater la balance avec les décimales
                    try:
                        decimals = int(token_info.get('decimals', 18))
                        balance_formatted = format_supply(balance, decimals)
                    except:
                        balance_formatted = balance
                    
                    enriched_tokens[token_address] = {
                        'balance': balance,
                        'balance_formatted': balance_formatted,
                        'token_info': token_info
                    }
            
            elapsed = timer.stop().elapsed()
            print(f"  ✅ {wallet_address[:8]}... → {len(enriched_tokens)} tokens ({elapsed:.2f}s)")
            
            return enriched_tokens
            
        except asyncio.TimeoutError:
            print(f"  ⏰ {wallet_address[:8]}... → Timeout")
            self.stats['errors'] += 1
            return None
        except Exception as e:
            print(f"  ❌ {wallet_address[:8]}... → Erreur: {e}")
            self.stats['errors'] += 1
            return None
    
    async def scan_wallet_batch_simple(self, wallet_addresses: List[str], 
                                     token_addresses: List[str],
                                     config: SimpleScanConfig) -> Dict[str, Dict]:
        """Scan simplifié d'un batch de wallets"""
        semaphore = asyncio.Semaphore(config.batch_size)
        
        async def scan_single_wallet(wallet_addr):
            async with semaphore:
                return wallet_addr, await self.scan_wallet_tokens_simple(
                    wallet_addr, token_addresses, config
                )
        
        tasks = [scan_single_wallet(addr) for addr in wallet_addresses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traiter les résultats
        wallet_tokens = {}
        for result in results:
            if isinstance(result, tuple) and len(result) == 2:
                wallet_addr, tokens = result
                if tokens:
                    wallet_tokens[wallet_addr] = tokens
                    self.stats['tokens_found'] += len(tokens)
        
        return wallet_tokens
    
    async def scan_all_wallets_simple(self, config: SimpleScanConfig = None) -> Dict:
        """Lance le scan simplifié de tous les wallets"""
        if config is None:
            config = SimpleScanConfig()
        
        self.stats['start_time'] = time.time()
        
        print("🚀 DÉMARRAGE DU SCAN SIMPLIFIÉ DES WALLETS")
        print("=" * 55)
        print("📖 Méthode: Test des tokens populaires seulement")
        
        # Récupérer les tokens populaires
        print(f"📋 Récupération des {config.popular_tokens_limit} tokens populaires...")
        popular_tokens = self.get_popular_tokens(config.popular_tokens_limit)
        print(f"✅ {len(popular_tokens)} tokens populaires à tester")
        
        # Récupérer tous les wallets à scanner
        print("👥 Récupération des wallets...")
        all_wallets = self.db_manager.get_wallets_for_scan()
        total_wallets = len(all_wallets)
        print(f"✅ {total_wallets} wallets à scanner")
        
        if not all_wallets:
            print("❌ Aucun wallet à scanner")
            return self.stats
        
        # Initialiser la progression
        self.db_manager.update_scan_progress('running', total=total_wallets, scanned=0)
        
        # Scanner par batches
        for i in range(0, total_wallets, config.batch_size):
            batch_wallets = all_wallets[i:i + config.batch_size]
            batch_num = (i // config.batch_size) + 1
            total_batches = (total_wallets + config.batch_size - 1) // config.batch_size
            
            print(f"\n📦 Batch {batch_num}/{total_batches} ({len(batch_wallets)} wallets)")
            
            # Scanner le batch
            wallet_tokens = await self.scan_wallet_batch_simple(
                batch_wallets, popular_tokens, config
            )
            
            # Sauvegarder les résultats
            for wallet_addr, tokens in wallet_tokens.items():
                # Convertir le format pour la base
                tokens_for_db = {}
                for token_addr, token_data in tokens.items():
                    tokens_for_db[token_addr] = {
                        'balance': token_data['balance'],
                        'balance_formatted': token_data['balance_formatted']
                    }
                
                self.db_manager.save_wallet_tokens(wallet_addr, tokens_for_db)
            
            # Mettre à jour les stats
            self.stats['wallets_scanned'] += len(batch_wallets)
            
            # Mettre à jour la progression
            progress_wallet = batch_wallets[0] if batch_wallets else None
            self.db_manager.update_scan_progress(
                'running', 
                current_wallet=progress_wallet,
                scanned=self.stats['wallets_scanned']
            )
            
            print(f"  📊 Wallets avec tokens: {len(wallet_tokens)}/{len(batch_wallets)}")
            
            # Petite pause entre les batches pour éviter la surcharge
            await asyncio.sleep(2)
        
        # Finaliser
        elapsed = time.time() - self.stats['start_time']
        self.db_manager.update_scan_progress('completed')
        
        print("\n" + "=" * 55)
        print("✅ SCAN SIMPLIFIÉ TERMINÉ")
        print(f"📊 Wallets scannés: {self.stats['wallets_scanned']}")
        print(f"🪙 Holdings trouvés: {self.stats['tokens_found']}")
        print(f"🔍 Vérifications effectuées: {self.stats['total_balance_checks']:,}")
        print(f"🆕 Nouveaux tokens: {self.stats['new_tokens_discovered']}")
        print(f"❌ Erreurs: {self.stats['errors']}")
        print(f"⏱️ Durée: {elapsed/60:.1f} minutes")
        print(f"🚀 Vitesse: {self.stats['wallets_scanned']/(elapsed/60):.1f} wallets/min")
        
        return self.stats
