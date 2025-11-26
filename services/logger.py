"""
Logging Service - CSV and file logging
Handles all trade, signal, snapshot, error, and audit logging
"""

import csv
import os
from datetime import datetime, timezone
from pathlib import Path
import traceback


class Logger:
    """Unified logging system"""
    
    def __init__(self, mode="paper", phase="paper"):
        """Initialize logger"""
        self.mode = mode
        self.phase = phase
        self.data_dir = Path("data")
        self.logs_dir = Path("logs")
        
        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Initialize CSV logs
        self._init_trade_log()
        self._init_signal_log()
        self._init_snapshot_log()
        self._init_error_log()
        self._init_audit_log()
        
        # Initialize bot log
        self.bot_log_path = self.logs_dir / "bot.log"
        
    def _init_trade_log(self):
        """Initialize trade log CSV"""
        self.trade_log_path = self.data_dir / "trade_log.csv"
        
        if not self.trade_log_path.exists():
            with open(self.trade_log_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'strategy', 'coin', 'action', 'price', 'quantity',
                    'pnl', 'trigger_reason', 'strategy_version', 'deployment_phase',
                    'execution_time_ms', 'slippage_percent', 'fee_usd', 'balance', 'notes'
                ])
                
    def _init_signal_log(self):
        """Initialize signal log CSV"""
        self.signal_log_path = self.data_dir / "signal_log.csv"
        
        if not self.signal_log_path.exists():
            with open(self.signal_log_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'strategy', 'coin', 'signal', 'rsi', 'ema_fast',
                    'ema_slow', 'atr', 'price', 'volume', 'trigger_met', 'blocked_reason'
                ])
                
    def _init_snapshot_log(self):
        """Initialize snapshot log CSV"""
        self.snapshot_log_path = self.data_dir / "snapshot_log.csv"
        
        if not self.snapshot_log_path.exists():
            with open(self.snapshot_log_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'conservative_value', 'aggressive_value', 'total_value',
                    'allocation_pct', 'pnl_conservative', 'pnl_aggressive', 'rebalance_due_in_days',
                    'last_skim_date'
                ])
                
    def _init_error_log(self):
        """Initialize error log CSV"""
        self.error_log_path = self.data_dir / "error_log.csv"
        
        if not self.error_log_path.exists():
            with open(self.error_log_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'error_type', 'severity', 'message', 'traceback', 'recovery_action'
                ])
                
    def _init_audit_log(self):
        """Initialize audit log CSV"""
        self.audit_log_path = self.data_dir / "audit_log.csv"
        
        if not self.audit_log_path.exists():
            with open(self.audit_log_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'action', 'user', 'details', 'old_value', 'new_value'
                ])
                
    def log_trade(self, strategy, coin, action, price, quantity, pnl=0, trigger_reason="",
                  strategy_version="1.0", execution_time_ms=0, slippage_percent=0,
                  fee_usd=0, balance=0, notes=""):
        """Log a trade to trade_log.csv"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        with open(self.trade_log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, strategy, coin, action, price, quantity, pnl, trigger_reason,
                strategy_version, self.phase, execution_time_ms, slippage_percent,
                fee_usd, balance, notes
            ])
            
        # Also log to bot.log
        self._log_to_file(f"TRADE: {action} {coin} @ ${price:.2f} | Reason: {trigger_reason}")
        
    def log_signal(self, strategy, coin, signal, rsi, ema_fast, ema_slow, atr, price,
                   volume, trigger_met=False, blocked_reason=""):
        """Log a signal to signal_log.csv"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        with open(self.signal_log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, strategy, coin, signal, rsi, ema_fast, ema_slow, atr,
                price, volume, trigger_met, blocked_reason
            ])
            
    def log_snapshot(self, conservative_value, aggressive_value, total_value, allocation_pct,
                     pnl_conservative, pnl_aggressive, rebalance_due_in_days,
                     last_skim_date=None):
        """Log a portfolio snapshot to snapshot_log.csv"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        with open(self.snapshot_log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, conservative_value, aggressive_value, total_value,
                allocation_pct, pnl_conservative, pnl_aggressive,
                rebalance_due_in_days, last_skim_date or ""
            ])
            
    def log_error(self, error_type, message, severity="ERROR", recovery_action=""):
        """Log an error to error_log.csv"""
        timestamp = datetime.now(timezone.utc).isoformat()
        tb = traceback.format_exc() if traceback.format_exc() != "NoneType: None\n" else ""
        
        with open(self.error_log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, error_type, severity, message, tb, recovery_action
            ])
            
        # Also log to bot.log
        self._log_to_file(f"ERROR [{severity}]: {error_type} - {message}")
        
    def log_audit(self, action, user="system", details="", old_value="", new_value=""):
        """Log an audit event to audit_log.csv"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        with open(self.audit_log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, action, user, details, old_value, new_value
            ])
            
    def _log_to_file(self, message):
        """Log to bot.log file"""
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(self.bot_log_path, 'a') as f:
            f.write(log_entry)
            
    def info(self, message):
        """Log info message"""
        self._log_to_file(f"INFO: {message}")
        
    def warning(self, message):
        """Log warning message"""
        self._log_to_file(f"WARNING: {message}")
        
    def error(self, message):
        """Log error message"""
        self._log_to_file(f"ERROR: {message}")
        self.log_error("GENERAL_ERROR", message, severity="ERROR")
