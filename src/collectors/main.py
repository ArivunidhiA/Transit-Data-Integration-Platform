import os
import time
import asyncio
import logging
from dotenv import load_dotenv

from src.collectors.mbta_collector import MbtACollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    collector = MbtACollector()
    logger.info("Starting MBTA data collector...")
    try:
        await collector.run()
    except KeyboardInterrupt:
        logger.info("Shutting down collector...")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 