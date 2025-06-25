"""
Gestion de la base de données pour HyperEVM Monitor
Version étendue avec scanner de wallets
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config.settings import DB_PATH


class Database:
    """Gestionnaire de base de données SQLite"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Initialise la base de données avec toutes les tables"""
        conn = sqlite3.connect(self.db_path)
        
        # Table principale des wallets
        conn.execute('''
            CREATE TABLE IF NOT EXISTS wallets (
                address TEXT PRIMARY KEY,
                address_type TEXT DEFAULT 'unknown',
                last_activity_block INTEGER,
                last_activity_timestamp INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des tokens ERC-20
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                address TEXT PRIMARY KEY,
                name TEXT,
                symbol TEXT,
                decimals INTEGER,
                total_supply TEXT,
                creator TEXT,
                status TEXT DEFAULT 'detected',
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_retry TIMESTAMP,
                FOREIGN KEY (address) REFERENCES wallets(address)
            )
        ''')
        
        # Checkpoint de progression
        conn.execute('''
            CREATE TABLE IF NOT EXISTS realtime_checkpoint (
                id INTEGER PRIMARY KEY DEFAULT 1,
                current_block INTEGER,
                current_rpc_url TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Stats d'activité par tranches de 5min
        conn.execute('''
            CREATE TABLE IF NOT EXISTS wallet_activity_stats (
                date TEXT,
                time_slot TEXT,
                active_wallets INTEGER,
                total_transactions INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (date, time_slot)
            )
        ''')
        
        # NOUVELLES TABLES POUR LE SCANNER DE WALLETS
        
        # Table des holdings de tokens par wallet
        conn.execute('''
            CREATE TABLE IF NOT EXISTS wallet_tokens (
                wallet_address TEXT,
                token_address TEXT,
                balance TEXT,
                balance_formatted TEXT,
                balance_usd TEXT DEFAULT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scan_status TEXT DEFAULT 'detected',
                PRIMARY KEY (wallet_address, token_address),
                FOREIGN KEY (wallet_address) REFERENCES wallets(address),
                FOREIGN KEY (token_address) REFERENCES tokens(address)
            )
        ''')
        
        # Table de progression du scan
        conn.execute('''
            CREATE TABLE IF NOT EXISTS wallet_scan_progress (
                id INTEGER PRIMARY KEY DEFAULT 1,
                total_wallets INTEGER DEFAULT 0,
                scanned_wallets INTEGER DEFAULT 0,
                current_wallet TEXT,
                started_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'idle'
            )
        ''')
        
        # Index pour les performances (originaux + nouveaux)
        conn.execute('CREATE INDEX IF NOT EXISTS idx_last_block ON wallets(last_activity_block)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_address_type ON wallets(address_type)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_stats_date ON wallet_activity_stats(date)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_tokens_discovered ON tokens(discovered_at)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_tokens_status ON tokens(status)')
        
        # Nouveaux index pour le scanner
        conn.execute('CREATE INDEX IF NOT EXISTS idx_wallet_tokens_wallet ON wallet_tokens(wallet_address)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_wallet_tokens_token ON wallet_tokens(token_address)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_wallet_tokens_updated ON wallet_tokens(last_updated)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_wallet_tokens_status ON wallet_tokens(scan_status)')
        
        conn.commit()
        conn.close()
    
    def get_checkpoint(self) -> Tuple[Optional[int], Optional[str]]:
        """Récupère le checkpoint de progression"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('SELECT current_block, current_rpc_url FROM realtime_checkpoint WHERE id = 1')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0], result[1]
        return None, None
    
    def save_checkpoint(self, block_number: int, rpc_url: str = None):
        """Sauvegarde le checkpoint"""
        conn = sqlite3.connect(self.db_path)
        if rpc_url:
            conn.execute('''
                INSERT OR REPLACE INTO realtime_checkpoint (id, current_block, current_rpc_url)
                VALUES (1, ?, ?)
            ''', (block_number, rpc_url))
        else:
            conn.execute('''
                UPDATE realtime_checkpoint SET current_block = ? WHERE id = 1
            ''', (block_number,))
        conn.commit()
        conn.close()
    
    def save_rpc_choice(self, rpc_url: str):
        """Sauvegarde le choix de RPC"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT OR REPLACE INTO realtime_checkpoint (id, current_rpc_url)
            VALUES (1, ?)
            ON CONFLICT(id) DO UPDATE SET current_rpc_url = ?
        ''', (rpc_url, rpc_url))
        conn.commit()
        conn.close()
    
    def filter_new_addresses(self, addresses: set) -> set:
        """Filtre les adresses nouvelles (non connues avec type != unknown)"""
        if not addresses:
            return set()
        
        conn = sqlite3.connect(self.db_path)
        placeholders = ','.join('?' * len(addresses))
        query = f"SELECT address FROM wallets WHERE address IN ({placeholders}) AND address_type != 'unknown'"
        
        cursor = conn.execute(query, list(addresses))
        existing = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        return addresses - existing
    
    def save_addresses(self, addresses_data: Dict[str, str], block_number: int, timestamp: int) -> int:
        """Sauvegarde les adresses avec leurs types"""
        if not addresses_data:
            return 0
            
        conn = sqlite3.connect(self.db_path)
        
        data = [(addr, addr_type, block_number, timestamp) for addr, addr_type in addresses_data.items()]
        
        conn.executemany('''
            INSERT OR REPLACE INTO wallets 
            (address, address_type, last_activity_block, last_activity_timestamp, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', data)
        
        conn.commit()
        conn.close()
        return len(addresses_data)
    
    def save_tokens(self, tokens_data: Dict[str, Dict]):
        """Sauvegarde les tokens détectés"""
        if not tokens_data:
            return
        
        conn = sqlite3.connect(self.db_path)
        
        for address, token_info in tokens_data.items():
            conn.execute('''
                INSERT OR REPLACE INTO tokens 
                (address, name, symbol, decimals, total_supply, creator, status, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, 'detected', CURRENT_TIMESTAMP)
            ''', (
                address,
                token_info.get('name', 'Unknown'),
                token_info.get('symbol', 'Unknown'),
                token_info.get('decimals', 0),
                token_info.get('totalSupply', '0'),
                token_info.get('creator', 'Unknown')
            ))
        
        conn.commit()
        conn.close()
    
    def get_unknown_addresses(self, limit: int = 100) -> List[str]:
        """Récupère les adresses avec type inconnu"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT address FROM wallets 
            WHERE address_type = 'unknown' 
            ORDER BY last_activity_block DESC 
            LIMIT ?
        ''', (limit,))
        
        addresses = [row[0] for row in cursor.fetchall()]
        conn.close()
        return addresses
    
    def update_address_types(self, address_types: Dict[str, str]):
        """Met à jour les types d'adresses"""
        if not address_types:
            return
        
        conn = sqlite3.connect(self.db_path)
        for address, addr_type in address_types.items():
            conn.execute('UPDATE wallets SET address_type = ? WHERE address = ?', (addr_type, address))
        conn.commit()
        conn.close()
    
    def get_failed_tokens(self, limit: int = 50) -> List[str]:
        """Récupère les tokens en échec à retenter"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT address FROM tokens 
            WHERE status = 'failed' 
            AND (last_retry IS NULL OR datetime(last_retry, '+1 hour') < datetime('now'))
            LIMIT ?
        ''', (limit,))
        
        addresses = [row[0] for row in cursor.fetchall()]
        conn.close()
        return addresses
    
    def mark_token_retry(self, address: str):
        """Marque une tentative de retry pour un token"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('UPDATE tokens SET last_retry = CURRENT_TIMESTAMP WHERE address = ?', (address,))
        conn.commit()
        conn.close()
    
    def save_activity_stats(self, time_slots: Dict[Tuple[str, str], Dict]):
        """Sauvegarde les stats d'activité"""
        if not time_slots:
            return
        
        conn = sqlite3.connect(self.db_path)
        
        for (date, time_slot), data in time_slots.items():
            conn.execute('''
                INSERT OR REPLACE INTO wallet_activity_stats 
                (date, time_slot, active_wallets, total_transactions, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (date, time_slot, len(data['addresses']), data['transactions']))
        
        conn.commit()
        conn.close()
    
    # ===== NOUVELLES MÉTHODES POUR LE SCANNER DE WALLETS ===== #
    
    def save_wallet_tokens(self, wallet_address: str, tokens_data: Dict[str, Dict]):
        """Sauvegarde les tokens d'un wallet"""
        if not tokens_data:
            return
        
        conn = sqlite3.connect(self.db_path)
        
        # Supprimer les anciens tokens de ce wallet
        conn.execute('DELETE FROM wallet_tokens WHERE wallet_address = ?', (wallet_address,))
        
        # Insérer les nouveaux tokens
        for token_address, token_info in tokens_data.items():
            balance = token_info.get('balance', '0')
            balance_formatted = token_info.get('balance_formatted', '0')
            
            conn.execute('''
                INSERT INTO wallet_tokens 
                (wallet_address, token_address, balance, balance_formatted, last_updated)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (wallet_address, token_address, balance, balance_formatted))
        
        conn.commit()
        conn.close()
    
    def get_wallet_tokens(self, wallet_address: str) -> List[Dict]:
        """Récupère les tokens d'un wallet avec infos détaillées"""
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute('''
            SELECT 
                wt.token_address,
                wt.balance,
                wt.balance_formatted,
                wt.last_updated,
                t.name,
                t.symbol,
                t.decimals,
                t.total_supply
            FROM wallet_tokens wt
            LEFT JOIN tokens t ON wt.token_address = t.address
            WHERE wt.wallet_address = ?
            ORDER BY CAST(wt.balance as INTEGER) DESC
        ''', (wallet_address,))
        
        tokens = []
        for row in cursor.fetchall():
            tokens.append({
                'token_address': row[0],
                'balance': row[1],
                'balance_formatted': row[2] or '0',
                'last_updated': row[3],
                'name': row[4] or 'Unknown Token',
                'symbol': row[5] or 'UNK',
                'decimals': row[6] or 18,
                'total_supply': row[7] or '0'
            })
        
        conn.close()
        return tokens
    
    def get_wallet_details(self, wallet_address: str) -> Optional[Dict]:
        """Récupère les détails complets d'un wallet"""
        conn = sqlite3.connect(self.db_path)
        
        # Infos de base du wallet
        cursor = conn.execute('''
            SELECT address, address_type, last_activity_block, 
                   last_activity_timestamp, updated_at
            FROM wallets 
            WHERE address = ?
        ''', (wallet_address,))
        
        wallet_info = cursor.fetchone()
        if not wallet_info:
            conn.close()
            return None
        
        # Statistiques des tokens
        cursor = conn.execute('''
            SELECT 
                COUNT(*) as token_count,
                MAX(last_updated) as last_scan
            FROM wallet_tokens 
            WHERE wallet_address = ?
        ''', (wallet_address,))
        
        token_stats = cursor.fetchone()
        
        conn.close()
        
        try:
            last_activity = datetime.fromtimestamp(int(wallet_info[3])).strftime('%Y-%m-%d %H:%M:%S') if wallet_info[3] else 'N/A'
        except:
            last_activity = 'N/A'
        
        return {
            'address': wallet_info[0],
            'type': wallet_info[1],
            'last_activity_block': wallet_info[2],
            'last_activity_timestamp': wallet_info[3],
            'last_activity_formatted': last_activity,
            'updated_at': wallet_info[4],
            'token_count': token_stats[0] if token_stats else 0,
            'last_token_scan': token_stats[1] if token_stats else None
        }
    
    def get_wallets_for_scan(self, limit: int = 100000, offset: int = 0) -> List[str]:
        """Récupère les wallets à scanner (type='wallet' uniquement)"""
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute('''
            SELECT address FROM wallets 
            WHERE address_type = 'wallet'
            ORDER BY last_activity_block DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        wallets = [row[0] for row in cursor.fetchall()]
        conn.close()
        return wallets
    
    def get_wallet_scan_stats(self) -> Dict:
        """Statistiques du scan de wallets"""
        conn = sqlite3.connect(self.db_path)
        
        # Nombre total de wallets
        cursor = conn.execute("SELECT COUNT(*) FROM wallets WHERE address_type = 'wallet'")
        total_wallets = cursor.fetchone()[0]
        
        # Wallets scannés (avec au moins un token)
        cursor = conn.execute("SELECT COUNT(DISTINCT wallet_address) FROM wallet_tokens")
        scanned_wallets = cursor.fetchone()[0]
        
        # Tokens uniques détectés
        cursor = conn.execute("SELECT COUNT(DISTINCT token_address) FROM wallet_tokens")
        unique_tokens = cursor.fetchone()[0]
        
        # Holdings totaux
        cursor = conn.execute("SELECT COUNT(*) FROM wallet_tokens")
        total_holdings = cursor.fetchone()[0]
        
        # Progression actuelle
        cursor = conn.execute("SELECT * FROM wallet_scan_progress WHERE id = 1")
        progress = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_wallets': total_wallets,
            'scanned_wallets': scanned_wallets,
            'unique_tokens': unique_tokens,
            'total_holdings': total_holdings,
            'scan_progress': {
                'status': progress[6] if progress else 'idle',
                'current_wallet': progress[3] if progress else None,
                'progress_percent': round((progress[2] / progress[1] * 100) if progress and progress[1] > 0 else 0, 1)
            } if progress else None
        }
    
    def update_scan_progress(self, status: str, current_wallet: str = None, 
                            scanned: int = None, total: int = None):
        """Met à jour la progression du scan"""
        conn = sqlite3.connect(self.db_path)
        
        if total is not None:
            # Nouveau scan
            conn.execute('''
                INSERT OR REPLACE INTO wallet_scan_progress 
                (id, total_wallets, scanned_wallets, current_wallet, started_at, status)
                VALUES (1, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            ''', (total, scanned or 0, current_wallet, status))
        else:
            # Mise à jour
            if scanned is not None:
                conn.execute('''
                    UPDATE wallet_scan_progress 
                    SET scanned_wallets = ?, current_wallet = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = 1
                ''', (scanned, current_wallet, status))
            else:
                conn.execute('''
                    UPDATE wallet_scan_progress 
                    SET current_wallet = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = 1
                ''', (current_wallet, status))
        
        conn.commit()
        conn.close()
    
    # ===== MÉTHODES WEB VIEWER (originales) ===== #
    
    def get_wallet_count(self, search: str = None, address_type: str = None) -> int:
        """Compte le nombre de wallets avec filtres"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT COUNT(*) FROM wallets WHERE 1=1"
        params = []
        
        if search:
            query += " AND address LIKE ?"
            params.append(f'%{search}%')
        
        if address_type:
            query += " AND address_type = ?"
            params.append(address_type)
        
        cursor = conn.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_wallets_page(self, page: int = 1, per_page: int = 50, search: str = None, address_type: str = None) -> List[Dict]:
        """Récupère une page de wallets"""
        offset = (page - 1) * per_page
        
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT address, address_type, last_activity_block, last_activity_timestamp, updated_at
            FROM wallets 
            WHERE 1=1
        '''
        params = []
        
        if search:
            query += " AND address LIKE ?"
            params.append(f'%{search}%')
        
        if address_type:
            query += " AND address_type = ?"
            params.append(address_type)
        
        query += " ORDER BY last_activity_block DESC LIMIT ? OFFSET ?"
        params.extend([per_page, offset])
        
        cursor = conn.execute(query, params)
        
        wallets = []
        for row in cursor.fetchall():
            address, addr_type, block, timestamp, updated = row
            
            try:
                activity_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'N/A'
            except:
                activity_date = 'N/A'
                
            wallets.append({
                'address': address,
                'type': addr_type or 'unknown',
                'last_block': f"{block:,}" if block else 'N/A',
                'last_activity': activity_date,
                'updated_at': updated
            })
        
        conn.close()
        return wallets
    
    def get_type_statistics(self) -> Dict:
        """Statistiques par type d'adresse"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT 
                address_type,
                COUNT(*) as count,
                MAX(last_activity_block) as latest_block
            FROM wallets 
            GROUP BY address_type
            ORDER BY count DESC
        ''')
        
        stats = {}
        total = 0
        for row in cursor.fetchall():
            addr_type, count, latest_block = row
            stats[addr_type or 'unknown'] = {
                'count': count,
                'latest_block': latest_block
            }
            total += count
        
        stats['total'] = total
        conn.close()
        return stats
    
    def get_token_count(self, search: str = None, status: str = None) -> int:
        """Compte le nombre de tokens"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT COUNT(*) FROM tokens WHERE 1=1"
        params = []
        
        if search:
            query += " AND (name LIKE ? OR symbol LIKE ? OR address LIKE ?)"
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        cursor = conn.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_tokens_page(self, page: int = 1, per_page: int = 50, search: str = None, status: str = None) -> List[Dict]:
        """Récupère une page de tokens"""
        offset = (page - 1) * per_page
        
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT address, name, symbol, decimals, total_supply, creator, status, discovered_at
            FROM tokens 
            WHERE 1=1
        '''
        params = []
        
        if search:
            query += " AND (name LIKE ? OR symbol LIKE ? OR address LIKE ?)"
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY discovered_at DESC LIMIT ? OFFSET ?"
        params.extend([per_page, offset])
        
        cursor = conn.execute(query, params)
        
        tokens = []
        for row in cursor.fetchall():
            address, name, symbol, decimals, total_supply, creator, status, discovered = row
            
            try:
                discovered_date = datetime.fromisoformat(discovered.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            except:
                discovered_date = discovered or 'N/A'
            
            tokens.append({
                'address': address,
                'name': name or 'Unknown',
                'symbol': symbol or 'UNK',
                'decimals': decimals or 0,
                'total_supply': total_supply or '0',
                'creator': creator or 'Unknown',
                'status': status,
                'discovered_at': discovered_date
            })
        
        conn.close()
        return tokens
    
    def get_token_statistics(self) -> Dict:
        """Statistiques des tokens"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT 
                status,
                COUNT(*) as count
            FROM tokens 
            GROUP BY status
            ORDER BY count DESC
        ''')
        
        stats = {}
        total = 0
        for row in cursor.fetchall():
            status, count = row
            stats[status] = count
            total += count
        
        stats['total'] = total
        conn.close()
        return stats
    
    def get_activity_stats_for_date(self, date: str) -> List[Dict]:
        """Stats d'activité pour une date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT time_slot, active_wallets, total_transactions
            FROM wallet_activity_stats 
            WHERE date = ?
            ORDER BY time_slot
        ''', (date,))
        
        stats = []
        for row in cursor.fetchall():
            time_slot, active_wallets, total_transactions = row
            stats.append({
                'time_slot': time_slot,
                'active_wallets': active_wallets,
                'total_transactions': total_transactions
            })
        
        conn.close()
        return stats
    
    def get_available_dates(self) -> List[str]:
        """Dates disponibles pour les stats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT DISTINCT date 
            FROM wallet_activity_stats 
            ORDER BY date DESC
        ''')
        
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()
        return dates
    
    def get_daily_summary(self, limit: int = 7) -> List[Dict]:
        """Résumé quotidien"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT 
                date,
                SUM(active_wallets) as total_wallets,
                SUM(total_transactions) as total_tx,
                COUNT(*) as time_slots,
                MAX(active_wallets) as peak_wallets
            FROM wallet_activity_stats 
            GROUP BY date
            ORDER BY date DESC
            LIMIT ?
        ''', (limit,))
        
        summary = []
        for row in cursor.fetchall():
            date, total_wallets, total_tx, slots, peak = row
            try:
                date_formatted = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
            except:
                date_formatted = date
                
            summary.append({
                'date': date,
                'date_formatted': date_formatted,
                'total_wallets': total_wallets,
                'total_transactions': total_tx,
                'time_slots': slots,
                'peak_wallets': peak
            })
        
        conn.close()
        return summary
    
    def get_activity_overview(self) -> Dict:
        """Vue d'ensemble de l'activité"""
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute('''
            SELECT 
                COUNT(DISTINCT date) as total_days,
                SUM(active_wallets) as total_wallet_activities,
                SUM(total_transactions) as total_transactions,
                AVG(active_wallets) as avg_wallets_per_slot,
                MAX(active_wallets) as max_wallets_per_slot
            FROM wallet_activity_stats
        ''')
        
        overview = cursor.fetchone()
        conn.close()
        
        return {
            'total_days': overview[0] or 0,
            'total_wallet_activities': overview[1] or 0,
            'total_transactions': overview[2] or 0,
            'avg_wallets_per_slot': round(overview[3] or 0, 1),
            'max_wallets_per_slot': overview[4] or 0
        }