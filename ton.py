from dedust import Asset, Factory, PoolType
import json
from pytoniq import LiteBalancer
import asyncio

async def main():
    provider = LiteBalancer.from_mainnet_config(1)
    await provider.start_up()

    SCALE_ADDRESS = "EQBlqsm144Dq6SjbPI4jjZvA1hqTIP3CvHovbIfW_t-SCALE"

    TON = Asset.native()
    SCALE = Asset.jetton(SCALE_ADDRESS)

    pool = await Factory.get_pool(pool_type=PoolType.VOLATILE,
                                  assets=[TON, SCALE],
                                  provider=provider)
                                    
    price = (await pool.get_estimated_swap_out(asset_in=TON,
                                               amount_in=int(10*1e9),
                                               provider=provider))
    print(price)

    await provider.close_all()

asyncio.run(main())