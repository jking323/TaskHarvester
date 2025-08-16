"""
Background Task Manager for processing emails and Teams messages
"""
import asyncio
from datetime import datetime
from typing import Optional

from ..utils.config import get_settings


class BackgroundTaskManager:
    """Manages background processing tasks"""
    
    def __init__(self):
        self.settings = get_settings()
        self.is_running = False
        self.tasks = []
        
    async def start(self):
        """Start background processing"""
        if self.is_running:
            return
            
        self.is_running = True
        print("🔄 Starting background task manager...")
        
        # Start email processing task
        email_task = asyncio.create_task(self._email_processing_loop())
        self.tasks.append(email_task)
        
        # Start Teams processing task  
        teams_task = asyncio.create_task(self._teams_processing_loop())
        self.tasks.append(teams_task)
        
        print("✅ Background tasks started")
    
    async def stop(self):
        """Stop background processing"""
        if not self.is_running:
            return
            
        self.is_running = False
        print("🛑 Stopping background tasks...")
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
            
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()
        
        print("✅ Background tasks stopped")
    
    async def _email_processing_loop(self):
        """Process emails periodically"""
        while self.is_running:
            try:
                print(f"📧 Processing emails at {datetime.now()}")
                # TODO: Implement email processing
                await asyncio.sleep(self.settings.email_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Email processing error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _teams_processing_loop(self):
        """Process Teams messages periodically"""
        while self.is_running:
            try:
                print(f"💬 Processing Teams messages at {datetime.now()}")
                # TODO: Implement Teams processing
                await asyncio.sleep(self.settings.teams_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Teams processing error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error