from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.api import Invoice, Assets, CurrencyType

from ..settings import settings


class CryptoPay:
    def __init__(self):
        # Используйте необходимый тип сети для ваших задач, а также сохраните токен crypto bot в файле .env
        self.crypto_pay = AioCryptoPay(token=settings.crypto_bot_token, network=Networks.TEST_NET)


    async def create_invoice(self, amount: int) -> Invoice:
        return await self.crypto_pay.create_invoice(
            amount=amount,
            currency_type=CurrencyType.FIAT,
            asset=Assets.USDT,
            fiat="RUB",
        )


    async def delete_invoice(self, invoice_id: int) -> bool:
        return await self.crypto_pay.delete_invoice(invoice_id=invoice_id)


    async def check_invoice(self, invoice_id: int) -> Invoice:
        return await self.crypto_pay.get_invoices(
            invoice_ids=invoice_id,
            count=1,
        )
