from agendor_client import AgendorClient
import pandas as pd

client = AgendorClient()
deals = client.get_deals()

included_ids = [37108680, 37108685, 37108711, 33290083, 34766997, 36556576]
excluded_ids = [35941469, 34841211]

print("=" * 80)
print("ANALISANDO DATAS DOS NEGÓCIOS")
print("=" * 80)

october_start = pd.Timestamp('2025-10-01')
october_end = pd.Timestamp('2025-10-31 23:59:59')

print(f"\nPeríodo: {october_start.date()} a {october_end.date()}")

def check_dates(deal_id, title):
    for deal in deals:
        if deal.get('id') == deal_id:
            created = pd.Timestamp(deal['createdAt']) if deal.get('createdAt') else None
            won = pd.Timestamp(deal['wonAt']) if deal.get('wonAt') else None
            start_time = pd.Timestamp(deal['startTime']) if deal.get('startTime') else None
            end_time = pd.Timestamp(deal['endTime']) if deal.get('endTime') else None
            
            if created and created.tz:
                created = created.tz_localize(None)
            if won and won.tz:
                won = won.tz_localize(None)
            if start_time and start_time.tz:
                start_time = start_time.tz_localize(None)
            if end_time and end_time.tz:
                end_time = end_time.tz_localize(None)
            
            print(f"\n{title}")
            print(f"  createdAt: {created.date() if created else 'N/A'} - Em out? {october_start <= created <= october_end if created else False}")
            print(f"  wonAt: {won.date() if won else 'N/A'} - Em out? {october_start <= won <= october_end if won else False}")
            print(f"  startTime: {start_time.date() if start_time else 'N/A'} - Em out? {october_start <= start_time <= october_end if start_time else False}")
            print(f"  endTime: {end_time.date() if end_time else 'N/A'} - Em out? {october_start <= end_time <= october_end if end_time else False}")
            break

print("\n📊 NEGÓCIOS INCLUÍDOS:")
print("-" * 80)
for deal in deals:
    if deal.get('id') in included_ids:
        check_dates(deal.get('id'), f"ID {deal.get('id')}: {deal.get('title')}")

print("\n\n❌ NEGÓCIOS EXCLUÍDOS:")
print("-" * 80)
for deal in deals:
    if deal.get('id') in excluded_ids:
        check_dates(deal.get('id'), f"ID {deal.get('id')}: {deal.get('title')}")
