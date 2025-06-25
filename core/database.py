"""
Gestion de la base de données pour HyperEVM Monitor
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
        
        # Index pour les performances
        conn.execute('CREATE INDEX IF NOT EXISTS idx_last_block ON wallets(last_activity_block)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_address_type ON wallets(address_type)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_stats_date ON wallet_activity_stats(date)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_tokens_discovered ON tokens(discovered_at)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_tokens_status ON tokens(status)')
        
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
    
    # Méthodes pour le web viewer
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