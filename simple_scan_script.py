#!/usr/bin/env python3
"""
Scanner de wallets simplifié et stable - HyperEVM
Teste les tokens populaires sur tous les wallets
"""

import asyncio
import sys
import os
import time
import argparse
from datetime import datetime

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import Database
from core.rpc_manager import create_rpc_manager
from detection.token_detector import TokenDetector
from scanners.simple_smart_scanner import SimpleSmartWalletScanner, SimpleScanConfig


class SimpleWalletScanManager:
    """Gestionnaire du scan simplifié des wallets"""
    
    def __init__(self):
        self.db_manager = None
        self.rpc_manager = None
        self.token_detector = None
        self.simple_scanner = None
    
    async def initialize(self):
        """Initialise tous les composants"""
        print("🔧 Initialisation des composants...")
        
        # Base de données
        self.db_manager = Database()
        
        # RPC Manager
        self.rpc_manager = await create_rpc_manager(self.db_manager)
        
        # Token Detector
        self.token_detector = TokenDetector(self.rpc_manager)
        
        # Simple Scanner
        self.simple_scanner = SimpleSmartWalletScanner(
            self.rpc_manager, 
            self.db_manager, 
            self.token_detector
        )
        
        print("✅ Composants initialisés")
    
    async def ensure_rpc_connection(self) -> bool:
        """S'assure qu'une connexion RPC est disponible"""
        if not await self.rpc_manager.switch_rpc(force_retest=True):
            print("❌ Impossible de trouver un RPC fonctionnel")
            return False
        
        rpc_info = self.rpc_manager.get_current_rpc_info()
        print(f"🔗 RPC actif: {rpc_info['name']}")
        return True
    
    async def run_simple_scan(self, config: SimpleScanConfig):
        """Lance le scan simplifié complet"""
        try:
            # Initialiser
            await self.initialize()
            
            # Vérifier la connexion RPC
            if not await self.ensure_rpc_connection():
                return False
            
            # Afficher les stats avant scan
            await self.show_pre_scan_stats()
            
            # Lancer le scan simplifié
            print(f"\n🚀 Démarrage du scan simplifié à {datetime.now().strftime('%H:%M:%S')}")
            print(f"⚙️ Configuration:")
            print(f"   • Batch size: {config.batch_size} wallets")
            print(f"   • Tokens populaires: {config.popular_tokens_limit}")
            print(f"   • Token batch: {config.token_batch_size} tokens/wallet")
            print(f"   • Timeout: {config.scan_timeout}s par wallet")
            print(f"   • Retry: {config.retry_attempts} tentatives")
            
            stats = await self.simple_scanner.scan_all_wallets_simple(config)
            
            # Afficher les stats finales
            await self.show_post_scan_stats(stats)
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Scan interrompu par utilisateur")
            self.db_manager.update_scan_progress('interrupted')
            return False
        except Exception as e:
            print(f"❌ Erreur fatale: {e}")
            self.db_manager.update_scan_progress('error')
            return False
        finally:
            await self.cleanup()
    
    async def show_pre_scan_stats(self):
        """Affiche les statistiques avant scan"""
        # Stats des wallets
        total_wallets = len(self.db_manager.get_wallets_for_scan())
        total_tokens = len(self.db_manager.get_tokens_page(1, 10000))
        
        print("\n📊 ÉTAT ACTUEL:")
        print(f"   • Wallets totaux: {total_wallets:,}")
        print(f"   • Tokens connus: {total_tokens:,}")
        
        # Vérifier s'il y a déjà des données de scan
        try:
            scan_stats = self.db_manager.get_wallet_scan_stats()
            if scan_stats['scanned_wallets'] > 0:
                print(f"   • Wallets déjà scannés: {scan_stats['scanned_wallets']:,}")
                print(f"   • Holdings existants: {scan_stats['total_holdings']:,}")
        except:
            pass
    
    async def show_post_scan_stats(self, stats: dict):
        """Affiche les statistiques après scan"""
        print("\n📈 RÉSULTATS FINAUX:")
        
        try:
            scan_stats = self.db_manager.get_wallet_scan_stats()
            print(f"   • Total wallets scannés: {scan_stats['scanned_wallets']:,}")
            print(f"   • Holdings détectés: {scan_stats['total_holdings']:,}")
            print(f"   • Tokens uniques: {scan_stats['unique_tokens']:,}")
            print(f"   • Nouveaux tokens découverts: {stats.get('new_tokens_discovered', 0):,}")
            print(f"   • Vérifications effectuées: {stats.get('total_balance_checks', 0):,}")
            
            if stats.get('start_time'):
                elapsed = time.time() - stats.get('start_time', 0)
                print(f"   • Vitesse: {scan_stats['scanned_wallets'] / (elapsed/60):.1f} wallets/min")
        except Exception as e:
            print(f"   • Erreur calcul stats: {e}")
    
    async def cleanup(self):
        """Nettoie les ressources"""
        if self.rpc_manager:
            await self.rpc_manager.close()


async def test_single_wallet_simple(wallet_address: str = None, token_limit: int = 10):
    """Test du scan simplifié sur un seul wallet"""
    print("🧪 TEST SIMPLE SCAN - UN WALLET")
    print("=" * 40)
    
    # Initialisation
    db = Database()
    rpc = await create_rpc_manager(db)
    detector = TokenDetector(rpc)
    scanner = SimpleSmartWalletScanner(rpc, db, detector)
    
    # Prendre le premier wallet ou celui spécifié
    if wallet_address:
        test_wallet = wallet_address
    else:
        wallets = db.get_wallets_for_scan(1)
        if not wallets:
            print("❌ Aucun wallet trouvé")
            return
        test_wallet = wallets[0]
    
    print(f"🔍 Test du wallet: {test_wallet}")
    
    # Récupérer les tokens populaires
    popular_tokens = scanner.get_popular_tokens(token_limit)
    print(f"🪙 Test avec {len(popular_tokens)} tokens populaires")
    
    # Configuration de test
    config = SimpleScanConfig(
        token_batch_size=10,
        scan_timeout=60,
        retry_attempts=2
    )
    
    # Scanner
    result = await scanner.scan_wallet_tokens_simple(test_wallet, popular_tokens, config)
    
    if result:
        print(f"\n✅ SUCCÈS - {len(result)} tokens trouvés:")
        for token_addr, token_data in result.items():
            token_info = token_data.get('token_info', {})
            print(f"   🪙 {token_info.get('symbol', 'UNK')} ({token_info.get('name', 'Unknown')})")
            print(f"      Balance: {token_data['balance_formatted']}")
            print(f"      Contrat: {token_addr}")
    else:
        print("📭 Aucun token trouvé")
    
    await rpc.close()


def create_simple_config_from_args(args) -> SimpleScanConfig:
    """Crée la configuration depuis les arguments"""
    return SimpleScanConfig(
        batch_size=args.batch_size,
        popular_tokens_limit=args.popular_tokens,
        token_batch_size=args.token_batch,
        retry_attempts=args.retry,
        scan_timeout=args.timeout,
        detect_new_tokens=not args.skip_new_tokens
    )


async def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Scanner simplifié de tokens par wallet pour HyperEVM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python simple_scan_wallets.py                         # Scan simplifié standard
  python simple_scan_wallets.py --popular-tokens 50    # Plus de tokens à tester
  python simple_scan_wallets.py --test-wallet 0x123... # Test un wallet
  python simple_scan_wallets.py --fast                  # Mode rapide
        """
    )
    
    # Arguments de configuration
    parser.add_argument('--batch-size', type=int, default=25,
                       help='Nombre de wallets par batch (défaut: 25)')
    parser.add_argument('--popular-tokens', type=int, default=30,
                       help='Nombre de tokens populaires à tester (défaut: 30)')
    parser.add_argument('--token-batch', type=int, default=30,
                       help='Tokens vérifiés en parallèle (défaut: 30)')
    parser.add_argument('--retry', type=int, default=2,
                       help='Tentatives en cas d\'échec (défaut: 2)')
    parser.add_argument('--timeout', type=int, default=45,
                       help='Timeout par wallet en secondes (défaut: 45)')
    parser.add_argument('--skip-new-tokens', action='store_true',
                       help='Ne pas détecter les nouveaux tokens')
    
    # Modes prédéfinis
    parser.add_argument('--fast', action='store_true',
                       help='Mode rapide (moins de tokens, plus de parallélisme)')
    parser.add_argument('--thorough', action='store_true',
                       help='Mode approfondi (plus de tokens)')
    
    # Options de test
    parser.add_argument('--test-wallet', type=str,
                       help='Tester sur un wallet spécifique')
    parser.add_argument('--stats-only', action='store_true',
                       help='Afficher seulement les statistiques')
    
    args = parser.parse_args()
    
    # Modes prédéfinis
    if args.fast:
        args.batch_size = 50
        args.popular_tokens = 20
        args.token_batch = 40
        args.timeout = 30
    elif args.thorough:
        args.batch_size = 15
        args.popular_tokens = 50
        args.token_batch = 20
        args.timeout = 60
    
    # Affichage du header
    print("🚀 HYPEREVM SIMPLE WALLET TOKEN SCANNER")
    print("=" * 50)
    print(f"Démarré le {datetime.now().strftime('%Y-%m-%d à %H:%M:%S')}")
    print("📖 Méthode: Test des tokens populaires uniquement")
    
    # Test d'un wallet spécifique
    if args.test_wallet:
        await test_single_wallet_simple(args.test_wallet, args.popular_tokens)
        return
    
    # Afficher stats seulement
    if args.stats_only:
        db = Database()
        try:
            stats = db.get_wallet_scan_stats()
            print("\n📊 STATISTIQUES ACTUELLES:")
            print(f"   • Total wallets: {stats['total_wallets']:,}")
            print(f"   • Wallets scannés: {stats['scanned_wallets']:,}")
            print(f"   • Holdings: {stats['total_holdings']:,}")
            print(f"   • Tokens uniques: {stats['unique_tokens']:,}")
            
            if stats['scan_progress']:
                print(f"   • Statut: {stats['scan_progress']['status']}")
                print(f"   • Progression: {stats['scan_progress']['progress_percent']}%")
        except Exception as e:
            print(f"❌ Erreur lecture stats: {e}")
        return
    
    # Configuration
    config = create_simple_config_from_args(args)
    
    # Lancer le scan simplifié
    scanner = SimpleWalletScanManager()
    success = await scanner.run_simple_scan(config)
    
    if success:
        print("\n✅ Scan simplifié terminé avec succès!")
        print("🌐 Vous pouvez maintenant voir les résultats dans l'interface web")
        print("\n💡 Avantages du scan simplifié:")
        print("   • Rapide et stable")
        print("   • Teste seulement les tokens populaires")
        print("   • Moins de charge sur les RPC")
    else:
        print("\n❌ Scan échoué ou interrompu")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
