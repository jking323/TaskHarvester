"""
Background Email Monitoring Service
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from ..models.database import get_db_session
from ..models.action_items import ProcessingLog
from .email_processor import EmailProcessor
from .wrike_integration import WrikeIntegration


class BackgroundMonitor:
    """Background service for automated email processing and monitoring"""
    
    def __init__(self, email_processor: EmailProcessor):
        self.email_processor = email_processor
        self.wrike_integration = WrikeIntegration()
        self.is_running = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Monitoring configuration
        self.check_interval = 300  # 5 minutes
        self.process_emails_interval = 1800  # 30 minutes
        self.sync_wrike_interval = 3600  # 1 hour
        
        self.last_email_check = None
        self.last_wrike_sync = None
        
        # Statistics
        self.stats = {
            "monitoring_started": None,
            "total_monitoring_cycles": 0,
            "emails_processed": 0,
            "action_items_found": 0,
            "wrike_tasks_created": 0,
            "last_error": None,
            "uptime_seconds": 0
        }
    
    async def start_monitoring(self):
        """Start the background monitoring service"""
        if self.is_running:
            print("[MONITOR] Background monitoring already running")
            return
        
        self.is_running = True
        self.stats["monitoring_started"] = datetime.utcnow()
        
        print("[MONITOR] Starting background email monitoring...")
        print(f"[MONITOR] Email check interval: {self.check_interval}s")
        print(f"[MONITOR] Email processing interval: {self.process_emails_interval}s")
        print(f"[MONITOR] Wrike sync interval: {self.sync_wrike_interval}s")
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
    async def stop_monitoring(self):
        """Stop the background monitoring service"""
        if not self.is_running:
            return
        
        print("[MONITOR] Stopping background monitoring...")
        self.is_running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Calculate uptime
        if self.stats["monitoring_started"]:
            uptime = datetime.utcnow() - self.stats["monitoring_started"]
            self.stats["uptime_seconds"] = uptime.total_seconds()
        
        print("[MONITOR] Background monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        try:
            while self.is_running:
                cycle_start = datetime.utcnow()
                
                try:
                    await self._run_monitoring_cycle()
                    self.stats["total_monitoring_cycles"] += 1
                    
                except Exception as e:
                    error_msg = f"Monitoring cycle error: {str(e)}"
                    self.stats["last_error"] = error_msg
                    print(f"[ERROR] {error_msg}")
                
                # Wait for next cycle
                await asyncio.sleep(self.check_interval)
                
        except asyncio.CancelledError:
            print("[MONITOR] Monitoring loop cancelled")
        except Exception as e:
            print(f"[ERROR] Monitoring loop failed: {e}")
    
    async def _run_monitoring_cycle(self):
        """Run a single monitoring cycle"""
        now = datetime.utcnow()
        
        # Check if it's time to process emails
        if (self.last_email_check is None or 
            (now - self.last_email_check).total_seconds() >= self.process_emails_interval):
            
            await self._process_recent_emails()
            self.last_email_check = now
        
        # Check if it's time to sync with Wrike
        if (self.last_wrike_sync is None or 
            (now - self.last_wrike_sync).total_seconds() >= self.sync_wrike_interval):
            
            await self._sync_action_items_to_wrike()
            self.last_wrike_sync = now
    
    async def _process_recent_emails(self):
        """Process recent emails for action items"""
        try:
            print("[MONITOR] Checking for recent emails to process...")
            
            db_session = get_db_session()
            
            # Check for recent unprocessed emails (simulate for demo)
            # In production, this would check for new emails since last processing
            processing_result = {
                "emails_processed": 0,
                "action_items_found": 0
            }
            
            # Simulate email processing
            print(f"[MONITOR] Processed {processing_result['emails_processed']} emails, "
                  f"found {processing_result['action_items_found']} action items")
            
            self.stats["emails_processed"] += processing_result["emails_processed"]
            self.stats["action_items_found"] += processing_result["action_items_found"]
            
            db_session.close()
            
        except Exception as e:
            print(f"[ERROR] Email processing failed: {e}")
    
    async def _sync_action_items_to_wrike(self):
        """Sync high-confidence action items to Wrike"""
        try:
            print("[MONITOR] Syncing action items to Wrike...")
            
            db_session = get_db_session()
            
            # Sync high-confidence action items
            sync_result = await self.wrike_integration.sync_action_items_to_wrike(
                db_session=db_session,
                confidence_threshold=0.8,  # Higher threshold for automatic sync
                limit=5  # Process a few at a time
            )
            
            synced_count = sync_result.get("synced_count", 0)
            if synced_count > 0:
                print(f"[MONITOR] Synced {synced_count} action items to Wrike")
                self.stats["wrike_tasks_created"] += synced_count
            
            db_session.close()
            
        except Exception as e:
            print(f"[ERROR] Wrike sync failed: {e}")
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get current monitoring statistics"""
        current_stats = self.stats.copy()
        
        if self.stats["monitoring_started"]:
            if self.is_running:
                uptime = datetime.utcnow() - self.stats["monitoring_started"]
                current_stats["uptime_seconds"] = uptime.total_seconds()
            
            current_stats["monitoring_started"] = self.stats["monitoring_started"].isoformat()
        
        current_stats["is_running"] = self.is_running
        current_stats["last_email_check"] = self.last_email_check.isoformat() if self.last_email_check else None
        current_stats["last_wrike_sync"] = self.last_wrike_sync.isoformat() if self.last_wrike_sync else None
        
        return current_stats
    
    async def trigger_email_processing(self) -> Dict[str, Any]:
        """Manually trigger email processing"""
        print("[MONITOR] Manual email processing triggered")
        await self._process_recent_emails()
        return {"message": "Email processing completed", "triggered_at": datetime.utcnow().isoformat()}
    
    async def trigger_wrike_sync(self) -> Dict[str, Any]:
        """Manually trigger Wrike synchronization"""
        print("[MONITOR] Manual Wrike sync triggered")
        await self._sync_action_items_to_wrike()
        return {"message": "Wrike sync completed", "triggered_at": datetime.utcnow().isoformat()}