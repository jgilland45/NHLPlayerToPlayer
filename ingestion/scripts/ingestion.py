import argparse
import logging
import sys
from pathlib import Path
import asyncio

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.helpers import test_for_season_202526

async def main(debug: bool = False):
    """
    Main function to run the test for the 2025-26 season.
    """
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    game_storage_list = await test_for_season_202526()
    print(f"Test for 2025-26 season completed. Number of GameStorage objects: {len(game_storage_list or [])}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest NHL game data for the 2025-26 season.")
    parser.add_argument("--debug", action="store_true", help="Enable detailed request logging.")
    args = parser.parse_args()
    asyncio.run(main(debug=args.debug))