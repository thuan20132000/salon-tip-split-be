from enum import Enum


class PaymentMethodEnums(Enum):
  CASH = "cash"
  DEBIT = "debit"
  DISC_5_PERCENT_CASH = "disc_5_percent_cash"
  DISC_5_PERCENT_DEBIT = "disc_5_percent_debit"
  LOYALTY = "loyalty"
  HAPPY_HOUR = "happy_hour"
  COMBINATION_CASH_DEBIT = "combination_cash_debit"
  GIFT_CARD = "gift_card"
  GIFT_CARD_CASH = "gift_card_cash"
  GIFT_CARD_DEBIT = "gift_card_debit"