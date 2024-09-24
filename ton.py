from dedust import Asset, Factory, PoolType
from pytoniq import LiteBalancer

class Ton:
    def __init__(self):
        self.provider = LiteBalancer.from_mainnet_config(1)
    async def get_price(self, asset_in_address, asset_out_address, amount_in):
        await self.provider.start_up()

        asset_in = Asset.jetton(asset_in_address)
        asset_out = Asset.jetton(asset_out_address)

        pool = await Factory.get_pool(pool_type=PoolType.VOLATILE,
                                      assets=[asset_in, asset_out],
                                      provider=self.provider)
                                        
        price = (await pool.get_estimated_swap_out(asset_in=asset_in,
                                                   amount_in=amount_in,
                                                   provider=self.provider))

        await self.provider.close_all()
        return price

ton = Ton()
