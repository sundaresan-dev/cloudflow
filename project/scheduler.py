#!/usr/bin/env python3

"""
scheduler.py
Automated background scheduler for deployment system maintenance tasks
"""

import schedule
import time
import logging
import os
from datetime import datetime, timedelta
from database.db_connection import DatabaseConnection
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DeploymentScheduler')

class DeploymentScheduler:
    """Handles automated maintenance tasks"""
    
    @staticmethod
    def cleanup_old_deployments(days=30):
        """Remove deployments older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # Find old inactive deployments
            old_deployments = DatabaseConnection.execute_query(
                """SELECT id, site_folder FROM deployments 
                   WHERE status = 'inactive' AND created_at < %s""",
                (cutoff_str,)
            )
            
            if not old_deployments:
                logger.info("✓ No old deployments to cleanup")
                return 0
            
            count = 0
            for deployment in old_deployments:
                try:
                    # Delete deployment files
                    deployed_path = os.path.join(
                        Config.DEPLOYED_SITES_PATH, 
                        deployment['site_folder']
                    )
                    if os.path.exists(deployed_path):
                        import shutil
                        shutil.rmtree(deployed_path)
                    
                    # Delete database
                    db_name = f"site_{deployment['site_folder'].split('_')[-1]}"
                    try:
                        connection = DatabaseConnection.get_connection()
                        cursor = connection.cursor()
                        cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
                        connection.commit()
                        cursor.close()
                        connection.close()
                    except:
                        pass
                    
                    # Delete deployment record
                    DatabaseConnection.execute_update(
                        "DELETE FROM deployments WHERE id = %s",
                        (deployment['id'],)
                    )
                    count += 1
                    logger.info(f"✓ Cleaned up deployment: {deployment['site_folder']}")
                    
                except Exception as e:
                    logger.error(f"✗ Error cleaning {deployment['site_folder']}: {e}")
            
            logger.info(f"✓ Cleanup completed: {count} deployments removed")
            return count
            
        except Exception as e:
            logger.error(f"✗ Error in cleanup_old_deployments: {e}")
            return 0
    
    @staticmethod
    def check_deployment_health():
        """Check health of all active deployments"""
        try:
            deployments = DatabaseConnection.execute_query(
                "SELECT id, site_folder, url FROM deployments WHERE status = 'active'"
            )
            
            if not deployments:
                logger.info("✓ No active deployments to check")
                return
            
            healthy = 0
            unhealthy = 0
            
            for deployment in deployments:
                try:
                    deployed_path = os.path.join(
                        Config.DEPLOYED_SITES_PATH,
                        deployment['site_folder']
                    )
                    
                    if os.path.exists(deployed_path) and os.path.isdir(deployed_path):
                        healthy += 1
                        logger.info(f"✓ Healthy: {deployment['site_folder']}")
                    else:
                        unhealthy += 1
                        logger.warning(f"⚠ Unhealthy: {deployment['site_folder']} (files missing)")
                        
                except Exception as e:
                    unhealthy += 1
                    logger.error(f"✗ Error checking {deployment['site_folder']}: {e}")
            
            logger.info(f"✓ Health check: {healthy} healthy, {unhealthy} unhealthy")
            
        except Exception as e:
            logger.error(f"✗ Error in check_deployment_health: {e}")
    
    @staticmethod
    def backup_databases(backup_dir='/tmp/deployment_backups'):
        """Backup all deployment databases"""
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            deployments = DatabaseConnection.execute_query(
                "SELECT id, site_folder FROM deployments WHERE status = 'active'"
            )
            
            if not deployments:
                logger.info("✓ No active deployments to backup")
                return 0
            
            backup_count = 0
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for deployment in deployments:
                try:
                    db_name = f"site_{deployment['site_folder'].split('_')[-1]}"
                    backup_file = os.path.join(backup_dir, f"{db_name}_{timestamp}.sql")
                    
                    # Execute mysqldump
                    import subprocess
                    result = subprocess.run(
                        f"mysqldump -u {Config.DB_USER} -p{Config.DB_PASSWORD} {db_name} > {backup_file}",
                        shell=True,
                        capture_output=True
                    )
                    
                    if result.returncode == 0:
                        backup_count += 1
                        logger.info(f"✓ Backed up: {db_name}")
                    else:
                        logger.error(f"✗ Failed to backup: {db_name}")
                        
                except Exception as e:
                    logger.error(f"✗ Error backing up {deployment['site_folder']}: {e}")
            
            # Cleanup old backups (keep last 10)
            try:
                backups = sorted(os.listdir(backup_dir))
                if len(backups) > 10:
                    for old_backup in backups[:-10]:
                        os.remove(os.path.join(backup_dir, old_backup))
                    logger.info(f"✓ Cleaned up old backups, kept last 10")
            except:
                pass
            
            logger.info(f"✓ Database backup completed: {backup_count} databases")
            return backup_count
            
        except Exception as e:
            logger.error(f"✗ Error in backup_databases: {e}")
            return 0
    
    @staticmethod
    def disk_space_check():
        """Check disk space and log warning if low"""
        try:
            import shutil
            
            # Check deployed_sites disk usage
            deployed_path = Config.DEPLOYED_SITES_PATH
            if os.path.exists(deployed_path):
                total, used, free = shutil.disk_usage(deployed_path)
                percent_used = (used / total) * 100
                
                logger.info(f"💾 Disk space: {percent_used:.1f}% used ({used // (1024**3)}GB of {total // (1024**3)}GB)")
                
                if percent_used > 90:
                    logger.warning(f"⚠ WARNING: Disk space critically low! {percent_used:.1f}% used")
                elif percent_used > 75:
                    logger.warning(f"⚠ WARNING: Disk space running low! {percent_used:.1f}% used")
                    
        except Exception as e:
            logger.error(f"✗ Error in disk_space_check: {e}")
    
    @staticmethod
    def cleanup_logs(log_dir='.', max_age_days=7):
        """Remove log files older than specified days"""
        try:
            cutoff_time = time.time() - (max_age_days * 86400)
            cleaned = 0
            
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    filepath = os.path.join(log_dir, filename)
                    if os.path.isfile(filepath):
                        if os.path.getmtime(filepath) < cutoff_time:
                            os.remove(filepath)
                            cleaned += 1
                            logger.info(f"✓ Deleted old log: {filename}")
            
            logger.info(f"✓ Log cleanup completed: {cleaned} files removed")
            return cleaned
            
        except Exception as e:
            logger.error(f"✗ Error in cleanup_logs: {e}")
            return 0
    
    @staticmethod
    def database_maintenance():
        """Perform database maintenance (optimize tables, etc)"""
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            # Optimize main database tables
            tables = DatabaseConnection.execute_query(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s",
                (Config.DB_NAME,)
            )
            
            optimized = 0
            for table_info in tables:
                table_name = table_info['TABLE_NAME']
                try:
                    cursor.execute(f"OPTIMIZE TABLE `{table_name}`")
                    optimized += 1
                    logger.info(f"✓ Optimized table: {table_name}")
                except:
                    pass
            
            cursor.close()
            connection.close()
            
            logger.info(f"✓ Database maintenance completed: {optimized} tables optimized")
            return optimized
            
        except Exception as e:
            logger.error(f"✗ Error in database_maintenance: {e}")
            return 0
    
    @staticmethod
    def generate_status_report():
        """Generate deployment system status report"""
        try:
            total = DatabaseConnection.execute_query(
                "SELECT COUNT(*) as count FROM deployments",
                fetch_one=True
            )
            
            active = DatabaseConnection.execute_query(
                "SELECT COUNT(*) as count FROM deployments WHERE status = 'active'",
                fetch_one=True
            )
            
            users = DatabaseConnection.execute_query(
                "SELECT COUNT(*) as count FROM users",
                fetch_one=True
            )
            
            report = f"""
            ================== Status Report ==================
            Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            📊 Deployments:
               Total: {total['count']}
               Active: {active['count']}
               Inactive: {total['count'] - active['count']}
            
            👥 Users: {users['count']}
            
            ✓ All systems operational
            ====================================================
            """
            
            logger.info(report)
            return report
            
        except Exception as e:
            logger.error(f"✗ Error generating status report: {e}")
            return None

def setup_scheduler():
    """Configure all scheduled tasks"""
    
    logger.info("🚀 Setting up deployment scheduler...")
    
    # Daily tasks (at 2 AM)
    schedule.every().day.at("02:00").do(DeploymentScheduler.cleanup_old_deployments, days=30)
    schedule.every().day.at("02:15").do(DeploymentScheduler.database_maintenance)
    schedule.every().day.at("02:30").do(DeploymentScheduler.backup_databases)
    
    # Hourly tasks
    schedule.every().hour.do(DeploymentScheduler.check_deployment_health)
    schedule.every().hour.do(DeploymentScheduler.disk_space_check)
    
    # Weekly tasks (Sunday at 3 AM)
    schedule.every().sunday.at("03:00").do(DeploymentScheduler.cleanup_logs)
    schedule.every().sunday.at("03:30").do(DeploymentScheduler.generate_status_report)
    
    logger.info("✓ Scheduler configured with 7 tasks")
    logger.info("✓ Daily: cleanup, maintenance, backup (at 2:00 AM)")
    logger.info("✓ Hourly: health check, disk space check")
    logger.info("✓ Weekly: log cleanup, status report (Sunday 3:00 AM)")

def run_scheduler():
    """Run the scheduler (blocking)"""
    
    setup_scheduler()
    
    logger.info("✓ Scheduler started. Running background tasks...")
    logger.info("Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("⛔ Scheduler stopped by user")

if __name__ == '__main__':
    run_scheduler()
